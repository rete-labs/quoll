from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import textwrap
import unittest


TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR.parent / "scripts"))

from quollcheck import (  # noqa: E402
    Finding,
    Package,
    check_package,
    decision_lifetime_findings,
    load_package,
    prose_findings,
    semantic_findings,
)


PID = "pkg:quoll/example.com/demo"


class PackageFixtures:
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "current"
        self.baseline_root = Path(self.temporary.name) / "baseline"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, root: Path, relative: str, text: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")

    def make(
        self,
        files: dict[str, str] | None = None,
        *,
        baseline: bool = False,
        modules: tuple[str, ...] = ("mod",),
    ) -> Package:
        root = self.baseline_root if baseline else self.root
        self.write(
            root,
            "package.quoll.toml",
            f'id = "{PID}"\nedition = "0.4.0"\ndescription = "Demo."\ndependencies = []\n',
        )
        self.write(
            root,
            "modules.quoll.toml",
            "modules = [" + ", ".join(f'"{module}"' for module in modules) + "]\n",
        )
        self.write(root, "package.lock.quoll.toml", "dependencies = []\n")
        self.write(root, "demo.h.md", "Root.\n")
        for module in modules:
            leaf = module.rsplit("/", 1)[-1]
            self.write(root, f"{module}/{leaf}.h.md", "Module.\n")
        for relative, text in (files or {}).items():
            self.write(root, relative, text)
        return load_package(root, baseline=baseline)

    def pair(
        self,
        current: dict[str, str],
        committed: dict[str, str],
    ) -> tuple[Package, Package]:
        return self.make(current), self.make(committed, baseline=True)

    def rules(self, findings: list[Finding]) -> list[str]:
        return [finding.rule for finding in findings]

    def assert_rule(self, findings: list[Finding], rule: str, count: int = 1) -> None:
        matching = [finding for finding in findings if finding.rule == rule]
        self.assertEqual(count, len(matching), [str(finding) for finding in findings])


class LifetimeCase(PackageFixtures, unittest.TestCase):
    def test_unchanged_reflowed_entry_and_fresh_successor_are_valid(self) -> None:
        current, baseline = self.pair(
            {
                "mod/mod.h.md": "## Structure\n```\n  thing    current\n```\n",
                "mod/mod.decisions.md": """\
                    **D1. Original**
                    *Stated by* [thing]
                    *Superseded by* [D2]

                    **D2. Replacement**
                    *Stated by*   [thing]
                    """,
            },
            {
                "mod/mod.h.md": "## Structure\n```\n  thing    current\n```\n",
                "mod/mod.decisions.md": """\
                    **D1. Original**
                    *Stated by*   [thing]
                    """,
            },
        )
        self.assertEqual([], [str(finding) for finding in decision_lifetime_findings(current, baseline)])

    def test_in_place_text_edit_is_review_only_without_supersession(self) -> None:
        current, baseline = self.pair(
            {"mod/mod.decisions.md": "**D1. Changed**\n*Rejected* new\n"},
            {"mod/mod.decisions.md": "**D1. Original**\n*Rejected* old\n"},
        )
        self.assertEqual([], decision_lifetime_findings(current, baseline))
        findings = decision_lifetime_findings(current, baseline, review=True)
        self.assert_rule(findings, "lifetime.in-place-replacement")
        self.assertEqual("review", findings[0].severity)
        self.assertEqual("mod/mod.decisions.md", findings[0].path)
        self.assertEqual(1, findings[0].line)
        self.assertEqual([], check_package(current, baseline))
        aggregated = check_package(current, baseline, review=True)
        self.assertEqual(["lifetime.in-place-replacement"], self.rules(aggregated))
        self.assertEqual("review", aggregated[0].severity)

    def test_altered_history_with_a_successor_is_an_error(self) -> None:
        current, baseline = self.pair(
            {
                "mod/mod.h.md": "## Structure\n```\n  thing    current\n```\n",
                "mod/mod.decisions.md": """\
                    **D1. Altered**
                    *Superseded by* [D2]

                    **D2. Fresh successor**
                    *Stated by* [thing]
                    """,
            },
            {"mod/mod.decisions.md": "**D1. Original**\n"},
        )
        findings = check_package(current, baseline)
        self.assertEqual(["lifetime.in-place-replacement"], self.rules(findings))
        self.assertEqual("error", findings[0].severity)

    def test_altering_an_already_superseded_entry_is_an_error(self) -> None:
        current, baseline = self.pair(
            {
                "mod/mod.decisions.md": """\
                    **D1. Altered**
                    *Superseded by* [D2]

                    **D2. Existing successor**
                    """,
            },
            {
                "mod/mod.decisions.md": """\
                    **D1. Original**
                    *Superseded by* [D2]

                    **D2. Existing successor**
                    """,
            },
        )
        findings = check_package(current, baseline)
        self.assertEqual(["lifetime.in-place-replacement"], self.rules(findings))
        self.assertEqual("error", findings[0].severity)

    def test_committed_id_cannot_be_withdrawn(self) -> None:
        current, baseline = self.pair(
            {"mod/mod.decisions.md": "# No entries.\n"},
            {"mod/mod.decisions.md": "**D1. Original**\n"},
        )
        finding = decision_lifetime_findings(current, baseline)[0]
        self.assertEqual("lifetime.withdrawn", finding.rule)
        self.assertEqual("D1", finding.subject)

    def test_duplicate_ids_within_one_module_with_and_without_baseline(self) -> None:
        files = {
            "a/one.decisions.md": "**D1. First**\n",
            "a/two.decisions.md": "**D1. Second**\n",
        }
        for with_baseline in (False, True):
            with self.subTest(with_baseline=with_baseline):
                package = self.make(files, modules=("a",))
                baseline = self.make(files, baseline=True, modules=("a",)) if with_baseline else None
                findings = decision_lifetime_findings(package, baseline)
                self.assert_rule(findings, "lifetime.duplicate-id")
                duplicate = next(finding for finding in findings if finding.rule == "lifetime.duplicate-id")
                self.assertIn("a/one.decisions.md:1", duplicate.detail)
                self.assertIn("a/two.decisions.md:1", duplicate.detail)

    def test_duplicate_ids_across_modules_with_and_without_baseline(self) -> None:
        files = {
            "a/a.decisions.md": "**D1. First**\n",
            "b/b.decisions.md": "**D1. Second**\n",
        }
        for with_baseline in (False, True):
            with self.subTest(with_baseline=with_baseline):
                package = self.make(files, modules=("a", "b"))
                baseline = self.make(files, baseline=True, modules=("a", "b")) if with_baseline else None
                findings = decision_lifetime_findings(package, baseline)
                self.assert_rule(findings, "lifetime.duplicate-id")
                duplicate = next(finding for finding in findings if finding.rule == "lifetime.duplicate-id")
                self.assertIn("a/a.decisions.md:1", duplicate.detail)
                self.assertIn("b/b.decisions.md:1", duplicate.detail)

    def test_missing_and_self_successors_are_errors_without_a_baseline(self) -> None:
        package = self.make({
            "mod/mod.decisions.md": """\
                **D1. Missing**
                *Superseded by* [D2]

                **D3. Self**
                *Superseded by* [D3]
                """,
        })
        findings = decision_lifetime_findings(package)
        self.assert_rule(findings, "lifetime.successor-missing")
        self.assert_rule(findings, "lifetime.successor-self")

    def test_stale_successor_and_changed_committed_link(self) -> None:
        current, baseline = self.pair(
            {
                "mod/mod.decisions.md": """\
                    **D1. Original**
                    *Superseded by* [D2]

                    **D2. Existing**
                    """,
            },
            {
                "mod/mod.decisions.md": """\
                    **D1. Original**

                    **D2. Existing**
                    """,
            },
        )
        self.assert_rule(decision_lifetime_findings(current, baseline), "lifetime.successor-stale")

        changed, committed = self.pair(
            {"mod/mod.decisions.md": "**D1. Original**\n"},
            {
                "mod/mod.decisions.md": """\
                    **D1. Original**
                    *Superseded by* [D2]

                    **D2. Existing**
                    """,
            },
        )
        findings = decision_lifetime_findings(changed, committed)
        self.assert_rule(findings, "lifetime.successor-changed")

    def test_successor_cycles_are_reported_at_each_member(self) -> None:
        package = self.make({
            "mod/mod.decisions.md": """\
                **D1. First**
                *Superseded by* [D2]

                **D2. Second**
                *Superseded by* [D1]
                """,
        })
        self.assert_rule(decision_lifetime_findings(package), "lifetime.successor-cycle", 2)

    def test_root_decisions_filename_rename_preserves_module_identity(self) -> None:
        current, baseline = self.pair(
            {"new.decisions.md": "**D1. Original**\n"},
            {"old.decisions.md": "**D1. Original**\n"},
        )
        self.assertEqual([], decision_lifetime_findings(current, baseline))

    def test_restored_history_retires_old_references_from_current_checks(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  thing    current\n```\n",
            "mod/mod.decisions.md": """\
                **D1. Historical**
                *Stated by* [retired]
                *Superseded by* [D2]

                **D2. Restored**
                *Stated by* [thing]
                """,
        })
        self.assertEqual([], semantic_findings(package))
        self.assertEqual([], prose_findings(package))
        self.assertEqual([], decision_lifetime_findings(package))


class ProseCase(PackageFixtures, unittest.TestCase):
    def test_space_hyphen_plural_and_possessive_compounds(self) -> None:
        for variant in ("source locator", "source-locator", "source locators", "source locator's"):
            with self.subTest(variant=variant):
                package = self.make({
                    "mod/mod.h.md": f"""\
                        A {variant} in prose.
                        ## Structure
                        ```
                          source locator    defining name
                        ```
                        """,
                })
                findings = prose_findings(package)
                self.assert_rule(findings, "prose.bare-compound")
                self.assertTrue(all(finding.severity == "error" for finding in findings))

    def test_definitions_ordinary_words_literals_links_and_history_do_not_fire(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                An ordinary locator is not a default compound check.
                `source locator` and [source locator](https://example.com).
                ```text
                source-locator
                ```
                ## Structure
                ```
                  source locator    defining name
                  locator           ordinary single word
                ```
                """,
            "mod/mod.decisions.md": """\
                **D1. Historical source locator**
                *Superseded by* [D2]

                **D2. Current**
                """,
        })
        self.assertEqual([], [str(finding) for finding in prose_findings(package)])

    def test_qualified_unqualified_and_inflected_references_do_not_fire(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                [source locator], [mod.source locator], [source locator]s,
                [locator], [mod.locator], and [locator]s are already references.
                ## Structure
                ```
                  source locator    compound
                  locator           single
                ```
                """,
        })
        self.assertEqual([], prose_findings(package))
        self.assertEqual([], prose_findings(package, review=True))

    def test_own_and_one_ordinary_english_are_suppressed_but_locators_remain(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                An [item] of one name; in its own terms; reduced to one manifest;
                defines its own surface. A source locator and the source-locator remain.
                ## Structure
                ```
                  one name         ordinary determinative phrase
                  own terms        ordinary possessive phrase
                  one manifest     ordinary determinative phrase
                  own surface      ordinary possessive phrase
                  source locator   language item
                ```
                """,
        })
        findings = prose_findings(package)
        self.assert_rule(findings, "prose.bare-compound")
        self.assertEqual("source locator", findings[0].subject)
        self.assertIn("occurrence count 2", findings[0].detail)

    def test_own_and_one_guards_also_apply_to_review_words(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                Its own terms and one manifest.
                ## Structure
                ```
                  terms      ordinary word
                  manifest   ordinary word
                ```
                """,
        })
        self.assertEqual([], prose_findings(package, review=True))

    def test_single_words_are_review_only_and_core_words_are_excluded(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                A locator, locators, and an open question.
                ## Structure
                ```
                  locator    a thing
                  open       a core word
                ```
                """,
        })
        self.assertEqual([], prose_findings(package))
        findings = prose_findings(package, review=True)
        self.assert_rule(findings, "prose.bare-word")
        self.assertEqual({"locator"}, {finding.subject for finding in findings})
        self.assertTrue(all(finding.severity == "review" for finding in findings))

    def test_negative_definition_reports_rejected_evidence(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                ## Structure
                ```
                  manifest    does not contain generated files
                ```
                """,
            "mod/mod.decisions.md": """\
                **D1. Shape**
                *Stated by* [manifest]
                *Rejected* an exclusion inventory, because it repeats absence
                """,
        })
        finding = next(finding for finding in prose_findings(package) if finding.rule == "prose.negative-definition")
        self.assertEqual("review", finding.severity)
        self.assertIn("D1: Rejected present", finding.detail)

    def test_unqualified_stated_by_does_not_cross_module_identity(self) -> None:
        package = self.make(
            {
                "a/a.h.md": "## Structure\n```\n  manifest    does not contain generated files\n```\n",
                "b/b.h.md": "## Structure\n```\n  manifest    holds source files\n```\n",
                "b/b.decisions.md": """\
                    **B-1. Local shape**
                    *Stated by* [manifest]
                    *Rejected* generated files, because they are derived
                    """,
            },
            modules=("a", "b"),
        )
        finding = next(finding for finding in prose_findings(package) if finding.rule == "prose.negative-definition")
        self.assertEqual("a/a.h.md", finding.path)
        self.assertIn("no active Stated by decision", finding.detail)
        self.assertNotIn("B-1", finding.detail)

    def test_qualified_cross_module_stated_by_associates_the_same_item(self) -> None:
        package = self.make(
            {
                "a/a.h.md": "## Structure\n```\n  manifest    does not contain generated files\n```\n",
                "b/b.decisions.md": """\
                    **B-1. Cross-module shape**
                    *Stated by* [a.manifest]
                    *Rejected* generated files, because they are derived
                    """,
            },
            modules=("a", "b"),
        )
        finding = next(finding for finding in prose_findings(package) if finding.rule == "prose.negative-definition")
        self.assertEqual("a/a.h.md", finding.path)
        self.assertIn("B-1: Rejected present", finding.detail)

    def test_disappearing_negative_material_reminds_about_unchanged_rejected_text(self) -> None:
        current, baseline = self.pair(
            {
                "mod/mod.h.md": "## Structure\n```\n  manifest    holds source files\n```\n",
                "mod/mod.decisions.md": """\
                    **D1. Shape**
                    *Stated by* [manifest]
                    *Rejected* generated files, because they are derived
                    """,
            },
            {
                "mod/mod.h.md": "## Structure\n```\n  manifest    does not contain generated files\n```\n",
                "mod/mod.decisions.md": """\
                    **D1. Shape**
                    *Stated by* [manifest]
                    *Rejected* generated files, because they are derived
                    """,
            },
        )
        findings = prose_findings(current, baseline=baseline)
        self.assert_rule(findings, "prose.rejected-preservation")
        self.assertIn("verify the alternatives were preserved", findings[0].detail)


class AggregationCase(PackageFixtures, unittest.TestCase):
    def test_unchanged_baseline_findings_are_suppressed(self) -> None:
        current, baseline = self.pair(
            {"mod/mod.h.md": "A [missing].\n"},
            {"mod/mod.h.md": "A [missing].\n"},
        )
        self.assertEqual([], [str(finding) for finding in check_package(current, baseline)])

    def test_changed_finding_is_retained_without_printing_baseline(self) -> None:
        current, baseline = self.pair(
            {"mod/mod.h.md": "A [new missing].\n"},
            {"mod/mod.h.md": "A [old missing].\n"},
        )
        findings = check_package(current, baseline)
        self.assertEqual(["semantic.resolved"], self.rules(findings))
        self.assertEqual("new missing", findings[0].subject)

    def test_added_and_removed_identical_compound_occurrences_remain_visible(self) -> None:
        definition = "## Structure\n```\n  source locator    syntax\n```\n"
        current, baseline = self.pair(
            {"mod/mod.h.md": "A source locator. Another source locator.\n" + definition},
            {"mod/mod.h.md": "A source locator.\n" + definition},
        )
        findings = check_package(current, baseline)
        self.assertEqual(["prose.bare-compound"], self.rules(findings))
        self.assertIn("occurrence count 2", findings[0].detail)

        current, baseline = self.pair(
            {"mod/mod.h.md": "A source locator.\n" + definition},
            {"mod/mod.h.md": "A source locator. Another source locator.\n" + definition},
        )
        findings = check_package(current, baseline)
        self.assertEqual(["prose.bare-compound"], self.rules(findings))
        self.assertIn("occurrence count 1", findings[0].detail)

    def test_added_identical_review_word_occurrence_remains_visible(self) -> None:
        definition = "## Structure\n```\n  locator    a thing\n```\n"
        current, baseline = self.pair(
            {"mod/mod.h.md": "A locator. Another locator.\n" + definition},
            {"mod/mod.h.md": "A locator.\n" + definition},
        )
        findings = check_package(current, baseline, review=True)
        self.assertEqual(["prose.bare-word"], self.rules(findings))
        self.assertEqual("review", findings[0].severity)
        self.assertIn("occurrence count 2", findings[0].detail)

    def test_line_reflow_does_not_resurrect_a_finding(self) -> None:
        current, baseline = self.pair(
            {"mod/mod.h.md": "\n\nA [missing].\n"},
            {"mod/mod.h.md": "A [missing].\n"},
        )
        self.assertEqual([], check_package(current, baseline))

    def test_prose_reflow_is_suppressed_but_lifetime_is_not(self) -> None:
        current, baseline = self.pair(
            {
                "mod/mod.h.md": """\


                    A source locator.
                    ## Structure
                    ```
                      source locator    syntax
                    ```
                    """,
                "mod/mod.decisions.md": """\
                    **D1. Broken**
                    *Superseded by* [absent]
                    """,
            },
            {
                "mod/mod.h.md": """\
                    A source locator.
                    ## Structure
                    ```
                      source locator    syntax
                    ```
                    """,
                "mod/mod.decisions.md": """\
                    **D1. Broken**
                    *Superseded by* [absent]
                    """,
            },
        )
        findings = check_package(current, baseline)
        self.assertEqual(["lifetime.successor-missing"], self.rules(findings))

    def test_errors_precede_reviews_and_keys_are_deduplicated(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                A source locator and [missing].
                ## Structure
                ```
                  source locator    does not contain generated files
                ```
                """,
        })
        findings = check_package(package, review=True)
        self.assertEqual(len(findings), len({finding.key for finding in findings}))
        severities = [finding.severity for finding in findings]
        self.assertEqual(sorted(severities, key={"error": 0, "review": 1}.get), severities)
        self.assertIn("prose.bare-compound", self.rules(findings))
        self.assertIn("prose.negative-definition", self.rules(findings))

    def test_end_to_end_combines_all_four_families(self) -> None:
        current, baseline = self.pair(
            {
                "package.lock.quoll.toml": "dependencies = [\n",
                "mod/mod.h.md": """\
                    A source locator and [missing].
                    ## Structure
                    ```
                      source locator    syntax
                    ```
                    """,
                "mod/mod.decisions.md": "# Empty.\n",
            },
            {"mod/mod.decisions.md": "**D1. Committed**\n"},
        )
        rules = set(self.rules(check_package(current, baseline)))
        self.assertTrue(
            {"toml.syntax", "semantic.resolved", "prose.bare-compound", "lifetime.withdrawn"} <= rules,
            sorted(rules),
        )


if __name__ == "__main__":
    unittest.main()
