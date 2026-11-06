from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import textwrap
import unittest


TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR.parent / "scripts"))

from quollcheck import Finding, Package, load_package, semantic_findings  # noqa: E402


PID = "pkg:quoll/example.com/demo"


class PackageFixtures:
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.extra_temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self) -> None:
        self.temporary.cleanup()
        for temporary in self.extra_temporaries:
            temporary.cleanup()

    def write(self, relative: str, text: str, root: Path | None = None) -> None:
        path = (root or self.root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")

    def make(
        self,
        files: dict[str, str] | None = None,
        *,
        dependencies: list[str] | None = None,
        modules: tuple[str, ...] = ("mod",),
        defaults: bool = True,
        root: Path | None = None,
        pid: str = PID,
    ) -> Package:
        root = root or self.root
        dependency_text = ", ".join(f'"{dependency}"' for dependency in (dependencies or []))
        self.write(
            "package.quoll.toml",
            f'id = "{pid}"\nedition = "0.4.0"\ndescription = "Demo."\ndependencies = [{dependency_text}]\n',
            root,
        )
        self.write("modules.quoll.toml", "modules = [" + ", ".join(f'"{module}"' for module in modules) + "]\n", root)
        self.write("package.lock.quoll.toml", "dependencies = []\n", root)
        name = pid.rsplit("/", 1)[-1]
        if defaults:
            self.write(f"{name}.h.md", "Root.\n", root)
            for module in modules:
                leaf = module.rsplit("/", 1)[-1]
                self.write(f"{module}/{leaf}.h.md", "Module.\n", root)
        for relative, text in (files or {}).items():
            self.write(relative, text, root)
        return load_package(root)

    def dependency(self, name: str, files: dict[str, str] | None = None) -> Package:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        root = Path(temporary.name)
        pid = f"pkg:quoll/example.com/{name}"
        dependency_files = {
            f"{name}.h.md": "## Structure\n```\n  open    public\n```\n",
            **(files or {}),
        }
        return self.make(dependency_files, modules=(), root=root, pid=pid)

    def findings(self, package: Package, *dependencies: Package) -> list[Finding]:
        return semantic_findings(package, dependencies)

    def assert_rule(self, findings: list[Finding], rule: str, count: int | None = None) -> None:
        matching = [finding for finding in findings if finding.rule == rule]
        self.assertTrue(matching, f"missing {rule}; got {[str(finding) for finding in findings]}")
        if count is not None:
            self.assertEqual(count, len(matching), [str(finding) for finding in findings])


class ResolutionCase(PackageFixtures, unittest.TestCase):
    def test_valid_local_included_body_decision_and_restored_text(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                +++
                includes = ["api"]
                +++
                ## Structure
                ```
                  first    [run]
                ```
                """,
            "mod/api.h.md": """\
                ## Structure
                ```
                  run    nothing
                ```
                """,
            "mod/mod.body.md": """\
                ## Flow
                ```
                  impl [default]:
                    run    [first]
                ```
                """,
            "mod/mod.decisions.md": """\
                **D-1. Old**
                *Stated by* [missing]
                *Because* D-999 is retired with this entry.
                *Superseded by* [D-2]

                **D-2. Restored**
                *Stated by* [run]
                """,
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_unlisted_module_reference_does_not_evade_semantic_checking(self) -> None:
        package = self.make(
            {"orphan/orphan.h.md": "A [missing].\n"},
            modules=(),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.resolved", 1)
        self.assertEqual("orphan/orphan.h.md", next(finding.path for finding in findings if finding.rule == "semantic.resolved"))

    def test_bare_decision_ids_resolve_with_file_mnemonic_and_boundaries(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  thing    meaning\n```\n",
            "mod/mod.decisions.md": """\
                **D-1. First**
                *Stated by* [thing]
                *Because* D-2 and [D-2] land, while `D-999`, X-999, and the opening D-1 do not add sites.

                **D-2. Second**
                *Stated by* [thing]
                """,
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_missing_bare_decision_id_is_resolved_like_a_bracketed_one(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  thing    meaning\n```\n",
            "mod/mod.decisions.md": """\
                **D-1. Missing target**
                *Stated by* [thing]
                *Formerly* D-998
                *Because* D-999 does not exist.
                """,
        })
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.resolved", 1)
        self.assertEqual("D-999", next(finding.subject for finding in findings if finding.rule == "semantic.resolved"))

    def test_formerly_id_is_not_a_bare_decision_reference(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  thing    meaning\n```\n",
            "mod/mod.decisions.md": """\
                **D-2. Moved decision**
                *Stated by* [thing]
                *Formerly* D-1
                """,
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_unresolved_reference(self) -> None:
        package = self.make({"mod/mod.h.md": "A [missing].\n"})
        self.assert_rule(self.findings(package), "semantic.resolved", 1)

    def test_private_interface_of_sibling_is_out_of_sight(self) -> None:
        package = self.make(
            {
                "a/secret.private.h.md": "Secret.\n",
                "b/b.h.md": "A [a.secret].\n",
            },
            modules=("a", "b"),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.sight", 1)
        self.assertNotIn("semantic.resolved", {finding.rule for finding in findings})

    def test_interface_cannot_reference_body_item(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                ## Structure
                ```
                  visible    [hidden]
                ```
                """,
            "mod/mod.body.md": """\
                ## Flow
                ```
                  hidden    implementation
                ```
                """,
        })
        self.assert_rule(self.findings(package), "semantic.independent", 1)

    def test_root_facade_precedes_module_except_default_path(self) -> None:
        package = self.make(
            {
                "demo.h.md": """\
                    ## Structure
                    ```
                      choose    [api.facade]
                    ```
                    """,
                "api.h.md": """\
                    ## Structure
                    ```
                      facade    public
                    ```
                    """,
                "api/api.h.md": """\
                    ## Structure
                    ```
                      internal    private implementation face
                      facade      internal item with a competing public path
                    ```
                    """,
                "inspect.private.h.md": "An [api.default] and [api.internal].\n",
            },
            modules=("api",),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_ambiguous_default_dependency_leaf(self) -> None:
        package = self.make(
            {"mod/mod.h.md": "A [shared].\n"},
            dependencies=[
                "pkg:quoll/example.com/one/shared@v1.0.0",
                "pkg:quoll/example.com/two/shared@v2.0.0",
            ],
        )
        self.assert_rule(self.findings(package), "semantic.ambiguous", 1)

    def test_supplied_but_undeclared_dependency_is_hidden(self) -> None:
        dependency = self.dependency("external")
        package = self.make({"mod/mod.h.md": "An [external.open].\n"})
        findings = self.findings(package, dependency)
        self.assert_rule(findings, "semantic.dependency", 1)
        self.assertNotIn("semantic.resolved", {finding.rule for finding in findings})

    def test_same_leaf_different_package_id_cannot_supply_dependency(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        wrong = self.make(
            {"demo.h.md": "## Structure\n```\n  open    public\n```\n"},
            modules=(),
            root=Path(temporary.name),
            pid="pkg:quoll/other.example/demo",
        )
        package = self.make(
            {"mod/mod.h.md": "A [demo.open].\n"},
            dependencies=["pkg:quoll/example.com/demo@v1.0.0"],
        )
        findings = self.findings(package, wrong)
        self.assert_rule(findings, "semantic.dependency", 1)
        self.assertNotIn("semantic.resolved", {finding.rule for finding in findings})

    def test_unavailable_dependency_does_not_invent_missing_items(self) -> None:
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    [aliases]
                    extbase = "pkg:quoll/example.com/external@v1.0.0"
                    +++
                    References [external.absent] and [extbase.absent].
                    """
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])


class RelationCase(PackageFixtures, unittest.TestCase):
    def test_inclusion_cycle(self) -> None:
        package = self.make(
            {
                "a/a.h.md": '+++\nincludes = ["b.default"]\n+++\nA.\n',
                "b/b.h.md": '+++\nincludes = ["a.default"]\n+++\nB.\n',
            },
            modules=("a", "b"),
        )
        self.assert_rule(self.findings(package), "semantic.includes-cycle", 2)

    def test_interface_reference_cycle(self) -> None:
        package = self.make(
            {
                "a/a.h.md": "## Structure\n```\n  x    [b.x]\n```\n",
                "b/b.h.md": "## Structure\n```\n  x    [a.x]\n```\n",
            },
            modules=("a", "b"),
        )
        self.assert_rule(self.findings(package), "semantic.interface-cycle", 2)

    def test_mixed_inclusion_reference_cycle_uses_one_diagnostic_per_interface(self) -> None:
        package = self.make(
            {
                "a/a.h.md": '+++\nincludes = ["b.default"]\n+++\nA.\n',
                "b/b.h.md": "## Structure\n```\n  x    [a.default]\n```\n",
            },
            modules=("a", "b"),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.interface-cycle", 2)
        self.assertNotIn("semantic.includes-cycle", {finding.rule for finding in findings})

    def test_interface_self_reference_cycle_is_detected(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  x    [default]\n```\n",
        })
        self.assert_rule(self.findings(package), "semantic.interface-cycle", 1)

    def test_included_item_collision_is_ambiguous(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                +++
                includes = ["one", "two"]
                +++
                ## Structure
                ```
                  use    [thing]
                ```
                """,
            "mod/one.h.md": "## Structure\n```\n  thing    one\n```\n",
            "mod/two.h.md": "## Structure\n```\n  thing    two\n```\n",
        })
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.ambiguous", 1)
        self.assert_rule(findings, "semantic.unique-names")

    def test_qualified_local_default_item_collision_is_ambiguous(self) -> None:
        package = self.make({
            "mod/mod.h.md": '+++\nincludes = ["one", "two"]\n+++\nModule.\n',
            "mod/one.h.md": "## Structure\n```\n  thing    one\n```\n",
            "mod/two.h.md": "## Structure\n```\n  thing    two\n```\n",
            "inspect.private.h.md": "A [mod.thing].\n",
        })
        self.assert_rule(self.findings(package), "semantic.ambiguous", 1)

    def test_qualified_dependency_default_item_collision_is_ambiguous(self) -> None:
        dependency = self.dependency("external", {
            "external.h.md": '+++\nincludes = ["one", "two"]\n+++\nPublic.\n',
            "one.h.md": "## Structure\n```\n  thing    one\n```\n",
            "two.h.md": "## Structure\n```\n  thing    two\n```\n",
        })
        package = self.make(
            {"mod/mod.h.md": "An [external.thing].\n"},
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assert_rule(self.findings(package, dependency), "semantic.ambiguous", 1)

    def test_impl_must_land_on_implemented_interface(self) -> None:
        package = self.make({
            "mod/api.h.md": "## Structure\n```\n  run    contract\n```\n",
            "mod/mod.body.md": """\
                ## Flow
                ```
                  impl [api]:
                    run    implementation
                ```
                """,
        })
        self.assert_rule(self.findings(package), "semantic.relations", 1)

    def test_pair_requires_same_named_interface_item(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  run    contract\n```\n",
            "mod/mod.body.md": """\
                ## Flow
                ```
                  impl [default]:
                    other    implementation
                ```
                """,
        })
        self.assert_rule(self.findings(package), "semantic.paired", 1)
    def test_duplicate_pairs_use_resolved_interface_identity(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  run    contract\n```\n",
            "mod/mod.body.md": """\
                ## Flow
                ```
                  impl [default]:
                    run    first
                  impl [mod.default]:
                    run    second
                ```
                """,
        })
        self.assert_rule(self.findings(package), "semantic.unique-names", 1)

    def test_pairs_with_genuinely_different_interfaces_remain_valid(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  run    default contract\n```\n",
            "mod/api.h.md": "## Structure\n```\n  run    api contract\n```\n",
            "mod/mod.body.md": """\
                +++
                implements = ["api"]
                +++
                ## Flow
                ```
                  impl [default]:
                    run    first
                  impl [api]:
                    run    second
                ```
                """,
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])


class UseAndClosureCase(PackageFixtures, unittest.TestCase):
    def test_complete_uses_detects_added_grammar_model_reference(self) -> None:
        package = self.make(
            {
                "demo.body.md": """\
                    ## Rules
                    ```
                      layout alone     [model.module] providing [layout.default] [model.uses] no [model.interface]
                      model alone      [model.module] providing [model.default] [model.uses] no [model.interface]
                      grammar on one   [model.module] providing [grammar.default] [model.uses] the [model.interface]s of the [model.module]s providing [layout.default] alone
                    ```
                    """,
                "grammar/grammar.h.md": "## Structure\n```\n  added    [model.item]\n```\n",
                "model/model.h.md": "## Structure\n```\n  item    meaning\n  module    unit\n  uses    consumption\n  interface    contract\n```\n",
            },
            modules=("layout", "model", "grammar"),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.uses", 1)
        self.assertIn("undeclared model", next(finding.detail for finding in findings if finding.rule == "semantic.uses"))

    def test_complete_uses_accepts_resolved_declared_direction(self) -> None:
        package = self.make(
            {
                "demo.body.md": """\
                    ## Rules
                    ```
                      layout alone     [model.module] providing [layout.default] [model.uses] no [model.interface]
                      model alone      [model.module] providing [model.default] [model.uses] no [model.interface]
                      grammar on one   [model.module] providing [grammar.default] [model.uses] the [model.interface]s of the [model.module]s providing [layout.default] alone
                    ```
                    """,
                "grammar/grammar.h.md": "## Structure\n```\n  uses    [layout.item]\n```\n",
                "layout/layout.h.md": "## Structure\n```\n  item    syntax\n```\n",
                "model/model.h.md": "## Structure\n```\n  module    unit\n  uses    consumption\n  interface    contract\n```\n",
            },
            modules=("layout", "model", "grammar"),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_recursive_public_closure_reports_facade_and_included_sources(self) -> None:
        package = self.make({
            "api.h.md": """\
                +++
                includes = ["mod.default"]
                +++
                A facade exposing [mod.internal.escape].
                ## Structure
                ```
                  open    [mod.shared]
                ```
                """,
            "mod/mod.h.md": """\
                ## Structure
                ```
                  shared    [mod.internal.escape]
                ```
                """,
            "mod/internal.h.md": "## Structure\n```\n  escape    hidden\n```\n",
        })
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.public-closure", 2)
        self.assertEqual(
            {"api.h.md", "mod/mod.h.md"},
            {finding.path for finding in findings if finding.rule == "semantic.public-closure"},
        )

    def test_dependency_public_item_satisfies_public_closure(self) -> None:
        dependency = self.dependency("external")
        package = self.make(
            {"api.h.md": "## Structure\n```\n  open    [external.open]\n```\n"},
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package, dependency)])
    def test_dependency_included_item_satisfies_public_closure(self) -> None:
        dependency = self.dependency("external", {
            "external.h.md": '+++\nincludes = ["secret"]\n+++\nPublic.\n',
            "secret.private.h.md": "## Structure\n```\n  hidden    exposed by inclusion\n```\n",
        })
        package = self.make(
            {"api.h.md": "## Structure\n```\n  open    [external.hidden]\n```\n"},
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package, dependency)])


class AliasCase(PackageFixtures, unittest.TestCase):
    def test_same_major_ambiguity_and_selector_qualified_aliases(self) -> None:
        dependency = "pkg:quoll/example.com/shared"
        package = self.make(
            {
                "mod/mod.body.md": f"""\
                    +++
                    [aliases]
                    bad = "{dependency}"
                    one = "{dependency}@v1.0.0"
                    two = "{dependency}@v1.2.0"
                    first = "one.api"
                    second = "two.api.open"
                    +++
                    Aliases [first.open] and [second].
                    """
            },
            dependencies=[f"{dependency}@v1.0.0", f"{dependency}@v1.2.0"],
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.alias-ambiguous", 1)
        self.assertEqual("bad", next(finding.subject for finding in findings if finding.rule == "semantic.alias-ambiguous"))
        self.assertEqual(1, len(findings), [str(finding) for finding in findings])

    def test_partial_alias_selects_stable_exact_releases_only(self) -> None:
        dependency = "pkg:quoll/example.com/external"
        package = self.make(
            {
                "mod/mod.body.md": f'+++\n[aliases]\ndep = "{dependency}@v1.2"\n+++\nBody.\n',
            },
            dependencies=[f"{dependency}@v1.2.3"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

        cases = (
            ("v1.2", "v1.2.3-rc.1"),
            ("v0", "v0.0.0-20240102030405-abcdef123456"),
            ("v1.2", "v1.2.3-pre.0.20240102030405-abcdef123456"),
            ("v1.2", "v1.2.4-0.20240102030405-abcdef123456"),
        )
        for partial, declaration in cases:
            with self.subTest(declaration=declaration):
                package = self.make(
                    {
                        "mod/mod.body.md": f'+++\n[aliases]\ndep = "{dependency}@{partial}"\n+++\nBody.\n',
                    },
                    dependencies=[f"{dependency}@{declaration}"],
                )
                self.assert_rule(self.findings(package), "semantic.alias-target", 1)

    def test_alias_cycles_are_reported_at_each_alias(self) -> None:
        package = self.make({
            "mod/mod.body.md": """\
                +++
                [aliases]
                a = "b.api"
                b = "a.api"
                +++
                Body.
                """
        })
        self.assert_rule(self.findings(package), "semantic.alias-cycle", 2)

    def test_dependency_interface_item_aliases_and_landing(self) -> None:
        dependency = self.dependency("external", {
            "api.h.md": "## Structure\n```\n  run    contract\n```\n",
        })
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    [aliases]
                    dep = "pkg:quoll/example.com/external@v1.0.0"
                    api = "dep.api"
                    open = "dep.open"
                    +++
                    Land on [dep], [dep.default], [dep.api], [dep.api.run], [dep.open], [api.run], and [open].
                    """
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package, dependency)])

    def test_invalid_alias_and_dependency_continuation(self) -> None:
        dependency = self.dependency("external")
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    [aliases]
                    dep = "pkg:quoll/example.com/external@v1.0.0"
                    open = "dep.open"
                    bad = "open.more"
                    +++
                    Invalid [dep.default.open] and [open.more].
                    """
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        findings = self.findings(package, dependency)
        self.assert_rule(findings, "semantic.reference-form", 2)
        self.assert_rule(findings, "semantic.alias-target", 1)

    def test_alias_collides_with_local_item(self) -> None:
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    [aliases]
                    thing = "pkg:quoll/example.com/external@v1.0.0"
                    +++
                    ## Structure
                    ```
                      thing    local
                    ```
                    """
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assert_rule(self.findings(package), "semantic.alias-unique", 1)
    def test_alias_collides_with_included_local_item(self) -> None:
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    includes = ["api"]
                    [aliases]
                    thing = "pkg:quoll/example.com/external@v1.0.0"
                    +++
                    Module.
                    """,
                "mod/api.h.md": "## Structure\n```\n  thing    included\n```\n",
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assert_rule(self.findings(package), "semantic.alias-unique", 1)

    def test_unresolved_alias_target(self) -> None:
        package = self.make({
            "mod/mod.body.md": """\
                +++
                [aliases]
                absent = "pkg:quoll/example.com/absent@v1.0.0"
                +++
                Body.
                """
        })
        self.assert_rule(self.findings(package), "semantic.alias-target", 1)
    def test_unused_alias_still_requires_a_visible_target(self) -> None:
        package = self.make(
            {
                "a/secret.private.h.md": "Secret.\n",
                "b/b.body.md": '+++\n[aliases]\nbad = "a.secret"\n+++\nUnused alias.\n',
            },
            modules=("a", "b"),
        )
        self.assert_rule(self.findings(package), "semantic.alias-target", 1)

    def test_unused_qualified_alias_rejects_same_leaf_wrong_package_id(self) -> None:
        files = {
            "mod/mod.body.md": '+++\n[aliases]\napi = "demo.default"\n+++\nUnused alias.\n',
        }
        dependencies = ["pkg:quoll/example.com/demo@v1.0.0"]
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        wrong = self.make(
            {"demo.h.md": "## Structure\n```\n  open    public\n```\n"},
            modules=(),
            root=Path(temporary.name),
            pid="pkg:quoll/other.example/demo",
        )
        package = self.make(files, dependencies=dependencies)
        self.assert_rule(self.findings(package, wrong), "semantic.alias-target", 1)

        correct = self.dependency("demo")
        package = self.make(files, dependencies=dependencies)
        self.assertEqual([], [str(finding) for finding in self.findings(package, correct)])


class DecisionStatementCase(PackageFixtures, unittest.TestCase):
    def test_active_decision_requires_stated_by_first(self) -> None:
        package = self.make({
            "mod/mod.decisions.md": "**D-1. Missing field**\n*Because* no items are named.\n",
        })
        self.assert_rule(self.findings(package), "semantic.stated-by-form", 1)

    def test_stated_by_rejects_each_obsolete_join(self) -> None:
        for join in ("for", "by", "what waits", "the"):
            with self.subTest(join=join):
                package = self.make({
                    "mod/mod.h.md": "## Structure\n```\n  first    one\n  second   two\n```\n",
                    "mod/mod.decisions.md": f"""\
                        **D-1. Bad join**
                        *Stated by* [first] {join} [second]
                        """,
                })
                self.assert_rule(self.findings(package), "semantic.stated-by-form", 1)

    def test_stated_by_accepts_comma_and_and_item_landing(self) -> None:
        for stated_by in (
            "[first], [second]",
            "[first] and [second]",
            "[first], [second] and [third].",
        ):
            with self.subTest(stated_by=stated_by):
                package = self.make({
                    "mod/mod.h.md": "## Structure\n```\n  first    one\n  second   two\n  third    three\n```\n",
                    "mod/mod.decisions.md": f"""\
                        **D-1. Valid joins**
                        *Stated by* {stated_by}
                        """,
                })
                self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_every_stated_by_reference_lands_on_an_item(self) -> None:
        package = self.make({
            "mod/mod.decisions.md": """\
                **D-1. Decision target**
                *Stated by* [D-1]
                """,
        })
        self.assert_rule(self.findings(package), "semantic.stated-by-target", 1)

    def test_structure_item_cannot_use_a_later_item(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                ## Structure
                ```
                  first    [second]
                  second   definition
                ```
                """,
        })
        self.assert_rule(self.findings(package), "semantic.definition-order", 1)

    def test_item_definition_cycles_are_detected_but_self_naming_is_allowed(self) -> None:
        package = self.make({
            "mod/mod.body.md": """\
                ## Flow
                ```
                  first    [second]
                  second   [first]
                  tree     [tree]
                ```
                """,
        })
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.definition-cycle", 2)
        self.assertEqual(
            {"first", "second"},
            {finding.subject for finding in findings if finding.rule == "semantic.definition-cycle"},
        )


class StructuralCase(PackageFixtures, unittest.TestCase):
    def test_module_lead_cardinality(self) -> None:
        package = self.make(
            {
                "demo.h.md": "Root.\n",
                "missing/api.h.md": "No declaration.\n",
                "multiple/one.h.md": '+++\n"module lead" = true\n+++\nOne.\n',
                "multiple/two.h.md": '+++\n"module lead" = true\n+++\nTwo.\n',
            },
            modules=("missing", "multiple"),
            defaults=False,
        )
        findings = [finding for finding in self.findings(package) if finding.rule == "semantic.one-module-lead"]
        self.assertIn("missing", {finding.path for finding in findings})
        self.assertIn("multiple", {finding.path for finding in findings})

    def test_missing_same_named_source_join(self) -> None:
        package = self.make(
            {
                "model/model.h.md": "## Structure\n```\n  thing    meaning\n```\n",
                "grammar/grammar.h.md": "## Structure\n```\n  thing    syntax\n```\n",
                "source/source.h.md": "## Structure\n```\n  thing    [model.thing]\n```\n",
            },
            modules=("model", "grammar", "source"),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.join", 1)
        self.assertIn("grammar.thing", next(finding.detail for finding in findings if finding.rule == "semantic.join"))

    def test_complete_same_named_source_join_is_valid(self) -> None:
        package = self.make(
            {
                "model/model.h.md": "## Structure\n```\n  thing    meaning\n```\n",
                "grammar/grammar.h.md": "## Structure\n```\n  thing    syntax\n```\n",
                "source/source.h.md": "## Structure\n```\n  thing    [model.thing] and [grammar.thing]\n```\n",
            },
            modules=("model", "grammar", "source"),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])


if __name__ == "__main__":
    unittest.main()
