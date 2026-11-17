from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parent / "scripts"
PID = "pkg:quoll/example.com/demo"


class CommandFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.temp = Path(self.temporary.name)
        self.current = self.temp / "current"
        self.baseline = self.temp / "baseline"

    def write(self, root: Path, relative: str, text: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")

    def make_v04(
        self,
        root: Path,
        files: dict[str, str] | None = None,
        *,
        modules: tuple[str, ...] = ("mod",),
        dependencies: tuple[str, ...] = (),
        name: str = "demo",
    ) -> Path:
        package_id = PID if name == "demo" else f"pkg:quoll/example.com/{name}"
        dependency_text = ", ".join(f'"{dependency}"' for dependency in dependencies)
        self.write(
            root,
            "package.quoll.toml",
            f'id = "{package_id}"\nedition = "0.4.0"\ndescription = "Demo."\ndependencies = [{dependency_text}]\n',
        )
        self.write(
            root,
            "modules.quoll.toml",
            "modules = [" + ", ".join(f'"{module}"' for module in modules) + "]\n",
        )
        self.write(root, "package.lock.quoll.toml", "dependencies = []\n")
        self.write(root, f"{name}.h.md", "Root.\n")
        for module in modules:
            leaf = module.rsplit("/", 1)[-1]
            self.write(root, f"{module}/{leaf}.h.md", "Module.\n")
        for relative, text in (files or {}).items():
            self.write(root, relative, text)
        return root

    def run_command(self, script: str, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPTS / script), *(str(argument) for argument in arguments)],
            text=True,
            capture_output=True,
            check=False,
        )


class MainCommandCase(CommandFixtures):
    def test_exit_zero_one_and_two(self) -> None:
        self.make_v04(self.current)
        clean = self.run_command("check_package.py", self.current)
        self.assertEqual(0, clean.returncode, clean.stderr)
        self.assertIn("errors: 0; reviews: 0", clean.stdout)

        self.write(self.current, "mod/mod.h.md", "A [missing].\n")
        broken = self.run_command("check_package.py", self.current)
        self.assertEqual(1, broken.returncode)
        self.assertIn("semantic.resolved", broken.stdout)
        self.assertIn("errors: 1; reviews: 0", broken.stdout)

        usage = self.run_command("check_package.py")
        self.assertEqual(2, usage.returncode)
        self.assertIn("usage:", usage.stderr)

    def test_default_hides_reviews_and_review_prints_them_without_failing(self) -> None:
        self.make_v04(
            self.current,
            {
                "mod/mod.h.md": """\
                    A locator.
                    ## Structure
                    ```
                      locator    a thing
                    ```
                    """
            },
        )
        default = self.run_command("check_package.py", self.current)
        self.assertEqual(0, default.returncode, default.stdout + default.stderr)
        self.assertNotIn("prose.bare-word", default.stdout)
        self.assertIn("errors: 0; reviews: 0", default.stdout)

        review = self.run_command("check_package.py", self.current, "--review")
        self.assertEqual(0, review.returncode, review.stdout + review.stderr)
        self.assertIn("prose.bare-word", review.stdout)
        self.assertIn("errors: 0; reviews: 1", review.stdout)

    def test_baseline_suppresses_unchanged_and_never_prints_baseline_defects(self) -> None:
        files = {"mod/mod.h.md": "An [old absent].\n"}
        self.make_v04(self.current, files)
        self.make_v04(self.baseline, files)
        unchanged = self.run_command("check_package.py", self.current, "--base", self.baseline)
        self.assertEqual(0, unchanged.returncode, unchanged.stdout + unchanged.stderr)
        self.assertNotIn("old absent", unchanged.stdout)

        self.write(self.current, "mod/mod.h.md", "A [new absent].\n")
        changed = self.run_command("check_package.py", self.current, "--base", self.baseline)
        self.assertEqual(1, changed.returncode)
        self.assertIn("new absent", changed.stdout)
        self.assertNotIn("old absent", changed.stdout)

    def test_supplied_dependency_surface_resolves_current_references(self) -> None:
        dependency = self.make_v04(
            self.temp / "dependency",
            {"dep.h.md": '+++\n[exposes]\ndefault = "default"\n+++\n## Structure\n```\n  thing    provided\n```\n'},
            modules=(),
            name="dep",
        )
        self.make_v04(
            self.current,
            {"mod/mod.h.md": "A [dep.default.thing] and a [dep.default.missing].\n"},
            dependencies=("pkg:quoll/example.com/dep@v0.1.0",),
        )
        without = self.run_command("check_package.py", self.current)
        self.assertNotIn("semantic.resolved", without.stdout)
        supplied = self.run_command(
            "check_package.py", self.current, "--dependency", dependency
        )
        self.assertIn("semantic.resolved dep.default.missing", supplied.stdout)
        self.assertNotIn("semantic.resolved dep.default.thing", supplied.stdout)
        self.assertNotIn("Traceback", supplied.stderr)

        self.make_v04(
            self.baseline,
            {"mod/mod.h.md": "A [dep.default.thing] and a [dep.default.missing].\n"},
            dependencies=("pkg:quoll/example.com/dep@v0.1.0",),
        )
        filtered = self.run_command(
            "check_package.py",
            self.current,
            "--base",
            self.baseline,
            "--dependency",
            dependency,
        )
        self.assertNotIn("semantic.resolved", filtered.stdout)

    def test_malformed_package_is_a_finding_not_a_traceback(self) -> None:
        self.make_v04(self.current)
        self.write(self.current, "package.quoll.toml", "id = [\n")
        result = self.run_command("check_package.py", self.current)
        self.assertEqual(1, result.returncode)
        self.assertIn("toml.syntax", result.stdout)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_bare_command_filters_all_other_families(self) -> None:
        self.make_v04(
            self.current,
            {
                "mod/mod.h.md": """\
                    A source locator and a locator and [missing].
                    ## Structure
                    ```
                      source locator    syntax
                      locator           a thing
                    ```
                    """
            },
        )
        default = self.run_command("check_bare.py", self.current)
        self.assertEqual(1, default.returncode)
        self.assertIn("prose.bare-compound", default.stdout)
        self.assertNotIn("prose.bare-word", default.stdout)
        self.assertNotIn("semantic.resolved", default.stdout)

        review = self.run_command("check_bare.py", self.current, "--review")
        self.assertEqual(1, review.returncode)
        self.assertIn("prose.bare-compound", review.stdout)
        self.assertIn("prose.bare-word", review.stdout)
        self.assertNotIn("semantic.resolved", review.stdout)

    def test_check_part_is_always_a_migration_shim(self) -> None:
        for arguments in ((), ("header", "decisions", "MOD"), ("--help",)):
            with self.subTest(arguments=arguments):
                result = self.run_command("check_part.py", *arguments)
                self.assertEqual(2, result.returncode)
                self.assertIn(
                    "check_package.py CURRENT [--base BASELINE] [--review]",
                    result.stderr,
                )


class ReferenceSitesCase(CommandFixtures):
    def test_v04_discovery_changed_and_gone_item_and_decision_sites(self) -> None:
        old_files = {
            "demo.h.md": "Before [D1].\n",
            "demo.decisions.md": "**D1. Original**\n\n**D2. Removed**\n",
            "mod/mod.h.md": "## Structure\n```\n  thing    old\n  gone    old\n```\n",
        }
        new_files = {
            "demo.h.md": "Now [mod.thing], [mod.gone], [D1] and [D2].\n",
            "demo.decisions.md": "**D1. Revised**\n",
            "mod/mod.h.md": """\
                A local [thing] and [gone].
                ## Structure
                ~~~
                  thing    new
                ~~~
                """,
        }
        self.make_v04(self.baseline, old_files)
        self.make_v04(self.current, new_files)
        result = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("## mod.thing (changed)", result.stdout)
        self.assertIn("## mod.gone (gone)", result.stdout)
        self.assertIn("demo.h.md:1:", result.stdout)
        self.assertIn("mod/mod.h.md:1:", result.stdout)
        self.assertIn("## D1 (changed)", result.stdout)
        self.assertIn("## D2 (gone)", result.stdout)

    def test_toml_and_impl_relations_and_default_body_are_reported(self) -> None:
        self.make_v04(
            self.baseline,
            {"mod/mod.h.md": "## Structure\n```\n  thing    old\n```\n"},
            modules=("mod", "consumer"),
        )
        self.make_v04(
            self.current,
            {
                "mod/mod.h.md": "## Structure\n```\n  thing    new\n```\n",
                "mod/mod.body.md": """\
                    ## Rules
                    ```
                      impl [default]:
                        thing    pairing
                    ```
                    """,
                "consumer/consumer.h.md": """\
                    +++
                    includes = ["mod.default"]
                    +++
                    Consumer.
                    """,
                "consumer/consumer.body.md": """\
                    +++
                    implements = ["mod.default"]
                    +++
                    ## Flow
                    ```
                      work    uses [mod.thing]
                    ```
                    """,
            },
            modules=("mod", "consumer"),
        )
        result = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("## mod.thing (relations)", result.stdout)
        self.assertIn('consumer/consumer.h.md:2: includes = ["mod.default"]', result.stdout)
        self.assertIn('consumer/consumer.body.md:2: implements = ["mod.default"]', result.stdout)
        self.assertIn("mod/mod.body.md:3: impl [default]:", result.stdout)
        self.assertIn(
            "mod/mod.body.md: the body of [mod], implementing its default",
            result.stdout,
        )

    def test_renamed_root_decisions_files_correspond_by_module(self) -> None:
        self.make_v04(self.baseline, {"old.decisions.md": "**D1. Original**\n"})
        self.make_v04(self.current, {"new.decisions.md": "**D1. Original**\n"})
        unchanged = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, unchanged.returncode, unchanged.stderr)
        self.assertNotIn("## D1", unchanged.stdout)

        self.write(self.current, "new.decisions.md", "**D1. Revised**\n")
        changed = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertIn("## D1 (changed)", changed.stdout)

    def test_superseded_entries_are_neither_current_edits_nor_sites(self) -> None:
        self.make_v04(
            self.baseline,
            {
                "demo.decisions.md": "**D1. Original**\n",
                "mod/mod.h.md": "## Structure\n```\n  thing    old\n```\n",
            },
        )
        self.make_v04(
            self.current,
            {
                "demo.decisions.md": """\
                    **D1. Original**
                    *Superseded by* [D2]

                    **D2. Replacement**

                    **D3. Historical [thing]**
                    *Superseded by* [D4]

                    **D4. Current**
                    """,
                "mod/mod.h.md": "## Structure\n```\n  thing    new\n```\n",
            },
        )
        result = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("## mod.thing (changed)", result.stdout)
        self.assertNotIn("## D1", result.stdout)
        self.assertNotIn("demo.decisions.md:", result.stdout)

    def test_malformed_old_and_new_toml_fail_closed(self) -> None:
        for side in ("old", "new"):
            with self.subTest(side=side):
                old = self.make_v04(self.temp / f"{side}-old")
                new = self.make_v04(self.temp / f"{side}-new")
                broken = old if side == "old" else new
                self.write(broken, "package.quoll.toml", "id = [\n")
                result = self.run_command("ref_sites.py", old, new)
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertIn(f"{side.upper()}_DIR:", result.stderr)
                self.assertIn("package.quoll.toml", result.stderr)
                self.assertIn("toml.syntax", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_usage_errors_use_stderr_and_exit_two(self) -> None:
        result = self.run_command("ref_sites.py")
        self.assertEqual(2, result.returncode)
        self.assertIn("usage:", result.stderr)
        self.assertEqual("", result.stdout)


class BodyPairChangesCase(CommandFixtures):
    def pair_files(self, default: str, api: str) -> dict[str, str]:
        return {
            "mod/mod.h.md": "## Structure\n```\n  run    requirement\n```\n",
            "mod/api.h.md": "## Structure\n```\n  run    requirement\n```\n",
            "mod/mod.body.md": f"""\
                +++
                implements = ["api"]
                +++
                ## Rules
                ```
                  impl [default]:
                    run    {default}
                  impl [api]:
                    run    {api}
                ```
                """,
        }

    def test_each_same_named_pair_is_compared_independently(self) -> None:
        for relation in ("default", "api"):
            with self.subTest(relation=relation):
                self.make_v04(
                    self.baseline,
                    self.pair_files("old default", "unchanged api"),
                )
                changed = {
                    "default": "new default" if relation == "default" else "old default",
                    "api": "new api" if relation == "api" else "unchanged api",
                }
                self.make_v04(
                    self.current,
                    self.pair_files(changed["default"], changed["api"]),
                )
                result = self.run_command("ref_sites.py", self.baseline, self.current)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(
                    1,
                    result.stdout.count("## mod body: run (changed)"),
                    result.stdout,
                )

    def test_equivalent_relation_spellings_preserve_pair_identity(self) -> None:
        self.make_v04(
            self.baseline,
            self.pair_files("old default", "unchanged api"),
        )
        current_files = self.pair_files("new default", "unchanged api")
        current_files["mod/mod.body.md"] = (
            current_files["mod/mod.body.md"]
            .replace("impl [default]:", "impl [mod.default]:")
            .replace("impl [api]:", "impl [mod.api]:")
        )
        self.make_v04(self.current, current_files)
        for package in (self.baseline, self.current):
            checked = self.run_command("check_package.py", package)
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        result = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(1, result.stdout.count("## mod body: run (changed)"), result.stdout)
        self.assertNotIn("## mod body: run (gone)", result.stdout)
        self.assertNotIn("## mod body: run (new)", result.stdout)

    def test_genuinely_different_interfaces_do_not_share_pair_identity(self) -> None:
        for root, relation in ((self.baseline, "default"), (self.current, "api")):
            files = self.pair_files("unused default", "unused api")
            files["mod/mod.body.md"] = f"""\
                +++
                implements = ["api"]
                +++
                ## Rules
                ```
                  impl [{relation}]:
                    run    same statements
                ```
                """
            self.make_v04(root, files)
            checked = self.run_command("check_package.py", root)
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        result = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(1, result.stdout.count("## mod body: run (gone)"), result.stdout)
        self.assertEqual(1, result.stdout.count("## mod body: run (new)"), result.stdout)
        self.assertNotIn("## mod body: run (changed)", result.stdout)

    def test_unpaired_duplicates_retain_their_occurrence_identity(self) -> None:
        for occurrence in (0, 1):
            with self.subTest(occurrence=occurrence):
                old = ["old first", "old second"]
                new = list(old)
                new[occurrence] = f"new {occurrence}"

                def files(statements: list[str]) -> dict[str, str]:
                    return {
                        "mod/mod.body.md": (
                            "## Rules\n```\n"
                            f"  note    {statements[0]}\n"
                            f"  note    {statements[1]}\n"
                            "```\n"
                        )
                    }

                self.make_v04(self.baseline, files(old))
                self.make_v04(self.current, files(new))
                result = self.run_command("ref_sites.py", self.baseline, self.current)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(
                    1,
                    result.stdout.count("## mod body: note (changed)"),
                    result.stdout,
                )


class NamedRootFacadeCase(CommandFixtures):
    def test_reference_include_and_implements_sites_use_facade_name(self) -> None:
        consumer = {
            "consumer/consumer.h.md": """\
                +++
                includes = ["api"]
                +++
                A [api.thing].
                """,
            "consumer/consumer.body.md": """\
                +++
                implements = ["api"]
                +++
                ## Flow
                ```
                  work    uses [api.thing]
                ```
                """,
        }
        self.make_v04(
            self.baseline,
            {
                "api.h.md": "## Structure\n```\n  thing    old\n```\n",
                **consumer,
            },
            modules=("consumer",),
        )
        self.make_v04(
            self.current,
            {
                "api.h.md": "## Structure\n```\n  thing    new\n```\n",
                **consumer,
            },
            modules=("consumer",),
        )
        result = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("## demo.api.thing (changed)", result.stdout)
        self.assertIn("consumer/consumer.h.md:4: A [api.thing].", result.stdout)
        self.assertIn('consumer/consumer.h.md:2: includes = ["api"]', result.stdout)
        self.assertIn('consumer/consumer.body.md:2: implements = ["api"]', result.stdout)
        self.assertIn("## demo.api.thing (relations)", result.stdout)

    def test_internal_named_interface_keeps_module_qualified_spellings(self) -> None:
        consumer = {
            "consumer/consumer.h.md": """\
                +++
                includes = ["part.api"]
                +++
                A [part.api.thing].
                """,
            "consumer/consumer.body.md": """\
                +++
                implements = ["part.api"]
                +++
                Consumer.
                """,
        }
        self.make_v04(
            self.baseline,
            {
                "part/api.h.md": "## Structure\n```\n  thing    old\n```\n",
                **consumer,
            },
            modules=("part", "consumer"),
        )
        self.make_v04(
            self.current,
            {
                "part/api.h.md": "## Structure\n```\n  thing    new\n```\n",
                **consumer,
            },
            modules=("part", "consumer"),
        )
        result = self.run_command("ref_sites.py", self.baseline, self.current)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("consumer/consumer.h.md:4: A [part.api.thing].", result.stdout)
        self.assertIn('consumer/consumer.h.md:2: includes = ["part.api"]', result.stdout)
        self.assertIn(
            'consumer/consumer.body.md:2: implements = ["part.api"]',
            result.stdout,
        )


class FormatterCase(CommandFixtures):
    def test_rewraps_underfilled_statements_and_is_idempotent(self) -> None:
        original = (
            "Lead and [outside.reference] stay here.\n"
            "## Structure\n"
            "```\n"
            "  alpha    one two\n"
            "           three [four.five]\n"
            "  beta     already aligned\n"
            "```\n"
            "After the view.\n"
        )
        expected = (
            "Lead and [outside.reference] stay here.\n"
            "## Structure\n"
            "```\n"
            "  alpha    one two three [four.five]\n"
            "  beta     already aligned\n"
            "```\n"
            "After the view.\n"
        )
        self.write(self.current, "mod.h.md", original)
        first = self.run_command("fmt.py", self.current)
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertIn("formatted: 1", first.stdout)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))

        second = self.run_command("fmt.py", self.current)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertIn("formatted: 0", second.stdout)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))

    def test_wraps_to_one_hundred_and_preserves_maximum_width_lines(self) -> None:
        prefix = "  alpha    "
        first = prefix + "x" * 40
        continuation = " " * len(prefix) + "y" * (100 - len(first) - 1)
        maximum = "  beta     " + "z" * (100 - len("  beta     "))
        original = (
            "## Structure\n```\n"
            + first + "\n" + continuation + "\n"
            + maximum + "\n"
            + "```\n"
        )
        expected = (
            "## Structure\n```\n"
            + first + " " + continuation.strip() + "\n"
            + maximum + "\n"
            + "```\n"
        )
        self.write(self.current, "mod.h.md", original)
        result = self.run_command("fmt.py", self.current)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))
        self.assertTrue(all(len(line) <= 100 for line in expected.splitlines()))

    def test_preserves_code_spans_repeated_spaces_and_unbreakable_words(self) -> None:
        prefix = "  item    "
        original = (
            "## Structure\n```\n"
            + prefix + "before `code span`  after\n"
            + " " * len(prefix) + "[reference.name]\n"
            + "  long    " + "x" * 110 + "\n"
            + "```\n"
        )
        expected = (
            "## Structure\n```\n"
            + prefix + "before `code span`  after [reference.name]\n"
            + "  long    " + "x" * 110 + "\n"
            + "```\n"
        )
        self.write(self.current, "mod.h.md", original)
        result = self.run_command("fmt.py", self.current)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))

    def test_code_span_close_requires_an_exact_backtick_run(self) -> None:
        prefix = "  item    "
        span = "`before `` inside longer code`"
        original = (
            "## Structure\n```\n"
            + prefix + "x" * 70 + "\n"
            + " " * len(prefix) + span + " tail\n"
            + "```\n"
        )
        expected = (
            "## Structure\n```\n"
            + prefix + "x" * 70 + "\n"
            + " " * len(prefix) + span + " tail\n"
            + "```\n"
        )
        self.write(self.current, "mod.h.md", original)
        first = self.run_command("fmt.py", self.current)
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))
        second = self.run_command("fmt.py", self.current)
        self.assertIn("formatted: 0", second.stdout)

    def test_inline_link_destination_remains_atomic(self) -> None:
        prefix = "  item    "
        link = "[link](<foo) bar>)"
        original = (
            "## Structure\n```\n"
            + prefix + "x" * 75 + "\n"
            + " " * len(prefix) + link + " tail\n"
            + "```\n"
        )
        expected = (
            "## Structure\n```\n"
            + prefix + "x" * 75 + "\n"
            + " " * len(prefix) + link + " tail\n"
            + "```\n"
        )
        self.write(self.current, "mod.h.md", original)
        first = self.run_command("fmt.py", self.current)
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))
        second = self.run_command("fmt.py", self.current)
        self.assertIn("formatted: 0", second.stdout)

    def test_never_splits_a_multiword_reference(self) -> None:
        prefix = "  item    "
        original = (
            "## Structure\n```\n"
            + prefix + "x" * 70 + "\n"
            + " " * len(prefix) + "[multiword reference] after\n"
            + "```\n"
        )
        expected = (
            "## Structure\n```\n"
            + prefix + "x" * 70 + "\n"
            + " " * len(prefix) + "[multiword reference] after\n"
            + "```\n"
        )
        self.write(self.current, "mod.h.md", original)
        result = self.run_command("fmt.py", self.current)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))

    def test_formats_statements_that_start_on_continuation_lines(self) -> None:
        original = (
            "## Structure\n```\n"
            "  alpha\n"
            "      one two\n"
            "      three\n"
            "  beta\n"
            "      " + "word " * 24 + "end\n"
            "```\n"
        )
        expected = (
            "## Structure\n```\n"
            "  alpha\n"
            "      one two three\n"
            "  beta\n"
            "      " + "word " * 18 + "word\n"
            "      " + "word " * 5 + "end\n"
            "```\n"
        )
        self.write(self.current, "mod.h.md", original)
        first = self.run_command("fmt.py", self.current)
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        actual = (self.current / "mod.h.md").read_text(encoding="utf-8")
        self.assertEqual(expected, actual)
        self.assertTrue(all(len(line) <= 100 for line in actual.splitlines()))
        second = self.run_command("fmt.py", self.current)
        self.assertIn("formatted: 0", second.stdout)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))

    def test_changes_no_content_outside_the_grammar_defined_views(self) -> None:
        original = (
            "+++\r\nincludes = []\r\n+++\r\n"
            "Lead prose\r\n"
            "## Notes\r\n```\r\n  literal    do not join\r\n               these lines\r\n```\r\n"
            "## Structure\r\n~~~quoll\r\n  item    keep this\r\n~~~\r\n"
            "## Structure\r\n```\r\n  duplicate    not a view\r\n```\r\n"
            "Trailing prose without a final newline"
        )
        self.write(self.current, "mod.h.md", original)
        non_sources = ("mod.decisions.md", "README.md", ".hidden/mod.h.md", ".hidden.h.md")
        for relative in non_sources:
            self.write(
                self.current,
                relative,
                "## Structure\n```\n  alpha    one two\n           three\n```\n",
            )
        result = self.run_command("fmt.py", self.current)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("formatted: 0", result.stdout)
        self.assertEqual(original, (self.current / "mod.h.md").read_bytes().decode("utf-8"))
        for relative in non_sources:
            self.assertEqual(
                "## Structure\n```\n  alpha    one two\n           three\n```\n",
                (self.current / relative).read_text(encoding="utf-8"),
            )

    def test_ignores_view_syntax_inside_an_outer_literal_fence(self) -> None:
        original = (
            "## Notes\n"
            "~~~\n"
            "## Structure\n"
            "```\n"
            "  alpha    one two\n"
            "           three\n"
            "```\n"
            "~~~\n"
            "## Structure\n"
            "```\n"
            "  beta     one two\n"
            "           three\n"
            "```\n"
        )
        expected = original.replace("  beta     one two\n           three", "  beta     one two three")
        self.write(self.current, "mod.h.md", original)
        first = self.run_command("fmt.py", self.current)
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))
        second = self.run_command("fmt.py", self.current)
        self.assertIn("formatted: 0", second.stdout)

    def test_atx_heading_variants_open_views(self) -> None:
        for heading in ("## Structure", "   ## Structure ###"):
            with self.subTest(heading=heading):
                original = (
                    heading + "\n"
                    "```\n"
                    "  alpha    one two\n"
                    "           three\n"
                    "```\n"
                )
                expected = original.replace("  alpha    one two\n           three", "  alpha    one two three")
                self.write(self.current, "mod.h.md", original)
                first = self.run_command("fmt.py", self.current)
                self.assertEqual(0, first.returncode, first.stdout + first.stderr)
                self.assertEqual(expected, (self.current / "mod.h.md").read_text(encoding="utf-8"))
                second = self.run_command("fmt.py", self.current)
                self.assertIn("formatted: 0", second.stdout)

    def test_setext_heading_does_not_open_a_view(self) -> None:
        original = (
            "Structure\n"
            "--------\n"
            "```\n"
            "  alpha    one two\n"
            "           three\n"
            "```\n"
        )
        self.write(self.current, "mod.h.md", original)
        result = self.run_command("fmt.py", self.current)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("formatted: 0", result.stdout)
        self.assertEqual(original, (self.current / "mod.h.md").read_text(encoding="utf-8"))

    def test_real_rich_view_rewraps_and_is_idempotent(self) -> None:
        repository = TEST_DIR.parents[3]
        source = (repository / "language/model/rich.h.md").read_bytes()
        self.current.mkdir()
        (self.current / "rich.h.md").write_bytes(source)
        first = self.run_command("fmt.py", self.current)
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        formatted = (self.current / "rich.h.md").read_bytes()
        self.assertNotEqual(source, formatted)

        checked = self.run_command("check_blocks.py", self.current)
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        self.assertIn("problems: 0", checked.stdout)
        second = self.run_command("fmt.py", self.current)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertIn("formatted: 0", second.stdout)
        self.assertEqual(formatted, (self.current / "rich.h.md").read_bytes())

    def test_usage_errors_use_stderr_and_exit_two(self) -> None:
        for arguments in ((), (self.current / "missing",)):
            with self.subTest(arguments=arguments):
                result = self.run_command("fmt.py", *arguments)
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertIn("fmt.py", result.stderr)


if __name__ == "__main__":
    unittest.main()
