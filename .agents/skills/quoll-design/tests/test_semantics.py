from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import textwrap
import tomllib
import unittest


TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR.parent / "scripts"))

from quollcheck import (  # noqa: E402
    Finding,
    Package,
    check_package,
    decision_lifetime_findings,
    dependent_site_evidence,
    load_package,
    prose_findings,
    public_reading,
    semantic_findings,
)


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
        edition: str = "0.6.0",
    ) -> Package:
        root = root or self.root
        dependency_text = ", ".join(f'"{dependency}"' for dependency in (dependencies or []))
        self.write(
            "package.quoll.toml",
            f'id = "{pid}"\nedition = "{edition}"\ndescription = "Demo."\ndependencies = [{dependency_text}]\n',
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
            f"{name}.h.md": '+++\n[exposes]\ndefault = "default"\n+++\n## Structure\n```\n  open    public\n```\n',
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

    def test_named_interface_cannot_collide_with_sibling_module(self) -> None:
        package = self.make(
            {
                "api.h.md": "## Structure\n```\n  facade    public\n```\n",
                "api/api.h.md": "## Structure\n```\n  internal    private implementation face\n```\n",
            },
            modules=("api",),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.unique-names", 1)
        self.assertEqual("api.h.md", findings[0].path)

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
        package = self.make({"mod/mod.h.md": "An [external.default.open].\n"})
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


class ExposureCase(PackageFixtures, unittest.TestCase):
    def natural_package(self, *, name: str = "demo", root: Path | None = None) -> Package:
        return self.make(
            {
                f"{name}.h.md": """\
                    +++
                    [exposes]
                    "model.kernel" = "model.kernel"
                    short = "model.kernel"
                    +++
                    Root declarations.
                    """,
                "model/model.h.md": "Model.\n",
                "model/kernel.h.md": "## Structure\n```\n  uses    relation\n```\n",
            },
            modules=("model",),
            root=root,
            pid=f"pkg:quoll/example.com/{name}",
        )

    @staticmethod
    def scoped_text(text: str, exposures: tuple[str, ...]) -> str:
        """Materialize only the exposure declarations present in a reading's scope."""

        kept: list[str] = []
        in_front = False
        front_closed = False
        in_exposes = False
        for line in text.splitlines(keepends=True):
            stripped = line.strip()
            if stripped == "+++" and not front_closed:
                in_front = not in_front
                front_closed = not in_front
                in_exposes = False
                kept.append(line)
                continue
            if in_front and stripped.startswith("["):
                in_exposes = stripped == "[exposes]"
            if in_front and in_exposes and "=" in line:
                try:
                    assignment = tomllib.loads(line)
                except tomllib.TOMLDecodeError:
                    assignment = {}
                if assignment and not set(assignment) & set(exposures):
                    continue
            kept.append(line)
        return "".join(kept)

    def rebuild_reading(
        self,
        package: Package,
        reading,
        *dependencies: Package,
    ) -> tuple[Package, dict[str, Package]]:
        package_ids = dict.fromkeys(
            [unit.package_id for unit in reading.units]
            + [module.package_id for module in reading.modules]
        )
        rebuilt: dict[str, Package] = {}
        for pid in package_ids:
            temporary = tempfile.TemporaryDirectory()
            self.extra_temporaries.append(temporary)
            units = [unit for unit in reading.units if unit.package_id == pid]
            files = {
                unit.path: self.scoped_text(unit.text, unit.exposures)
                for unit in units
            }
            modules = tuple(
                module.path
                for module in reading.modules
                if module.package_id == pid
            )
            declarations = reading.dependencies if pid == package.id else (units[0].dependencies if units else ())
            rebuilt[pid] = self.make(
                files,
                dependencies=list(declarations),
                modules=modules,
                defaults=False,
                root=Path(temporary.name),
                pid=pid,
                edition=units[0].edition if units else "0.6.0",
            )
        return rebuilt[package.id], rebuilt

    def assert_reading_rebuilds(
        self,
        package: Package,
        reading,
        *dependencies: Package,
        expected: dict[str, list[Finding]] | None = None,
    ) -> Package:
        rebuilt, packages = self.rebuild_reading(package, reading, *dependencies)
        for pid, current in packages.items():
            declared = {selector.id for selector in current.dependencies}
            supplied = [
                candidate
                for candidate in packages.values()
                if candidate.id in declared and candidate is not current
            ]
            findings = self.findings(current, *supplied)
            expected_findings = (expected or {}).get(pid, [])
            self.assertEqual(
                sorted(finding.key for finding in expected_findings),
                [finding.key for finding in findings],
                f"{pid}: {[str(finding) for finding in findings]}",
            )
        return rebuilt

    def test_natural_shortened_and_multiple_exposures_preserve_identity(self) -> None:
        package = self.natural_package()
        self.write(
            "inspect.private.h.md",
            "Resolve [model.kernel.uses], [demo.short.uses], and [demo.model.kernel.uses].\n",
        )
        package = load_package(self.root)
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        self.assertEqual(
            ("demo.h.md", "model/kernel.h.md"),
            public_reading(package).paths,
        )

    def test_dependency_paths_follow_only_the_same_public_exposures(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        dependency = self.natural_package(name="external", root=Path(temporary.name))
        package = self.make(
            {
                "mod/mod.h.md": "Resolve [external.model.kernel.uses], [external.short.uses], and [external.model.kernel].\n",
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package, dependency)])

    def test_intermediate_reexport_is_public_only_through_root_chain(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        dependency = self.make(
            {
                "external.h.md": '+++\n[exposes]\npublic = "branch.api"\n+++\nRoot.\n',
                "branch/branch.h.md": '+++\n[exposes]\napi = "deep.api"\n+++\nBranch.\n',
                "branch/deep/api.h.md": "## Structure\n```\n  run    contract\n```\n",
            },
            modules=("branch", "branch/deep"),
            root=Path(temporary.name),
            pid="pkg:quoll/example.com/external",
        )
        package = self.make(
            {"mod/mod.h.md": "Public [external.public.run]; private [external.branch.api].\n"},
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        findings = self.findings(package, dependency)
        self.assert_rule(findings, "semantic.resolved", 1)
        self.assertEqual("external.branch.api", findings[0].subject)
        self.assertEqual(
            ("branch/branch.h.md", "branch/deep/api.h.md", "external.h.md"),
            public_reading(dependency).paths,
        )

    def test_malformed_exposure_declarations_are_diagnosed_at_front_matter(self) -> None:
        cases = (
            ('exposes = "api"\n', "front.type"),
            ('[exposes]\napi = 1\n', "front.type"),
            ('[exposes]\n"bad..path" = "default"\n', "front.exposure"),
            ('[exposes]\napi = "[default]"\n', "front.exposure"),
            ('[exposes]\napi.extra = "default"\n', "front.type"),
        )
        for front, rule in cases:
            with self.subTest(front=front):
                package = self.make({"demo.h.md": f"+++\n{front}+++\nRoot.\n"}, modules=())
                self.assert_rule(package.findings, rule, 1)
        package = self.make(
            {
                "demo.h.md": '+++\n[aliases]\nbad = "default"\n[exposes]\nbad = 1\n+++\nRoot.\n',
            },
            modules=(),
        )
        finding = next(finding for finding in package.findings if finding.rule == "front.type")
        self.assertEqual(5, finding.line)
        package = self.make(
            {"demo.h.md": "+++\nexposes = { bad = 1 }\n+++\nRoot.\n"},
            modules=(),
        )
        finding = next(finding for finding in package.findings if finding.rule == "front.type")
        self.assertEqual(2, finding.line)
        package = self.make(
            {
                "demo.h.md": "+++\n[exposes.sub]\nsub = 1\n+++\nRoot.\n",
            },
            modules=(),
        )
        finding = next(finding for finding in package.findings if finding.rule == "front.type")
        self.assertEqual("sub", finding.subject)
        self.assertEqual(2, finding.line)
        for header, written in (
            ("[exposes] # public surface", r"'bad..path'"),
            ('["exposes"]', r'"bad..path"'),
            ("[ exposes ] # decoded basic key", '"bad' + chr(92) + 'u002e' + chr(92) + 'u002epath"'),
        ):
            with self.subTest(header=header, written=written):
                package = self.make(
                    {
                        "demo.h.md": (
                            f"+++\n[aliases]\nunused = \"default\"\n{header}\n"
                            f"{written} = \"default\"\n+++\nRoot.\n"
                        ),
                    },
                    modules=(),
                )
                finding = next(
                    finding
                    for finding in package.findings
                    if finding.rule == "front.exposure"
                )
                self.assertEqual("bad..path", finding.subject)
                self.assertEqual(5, finding.line)
        package = self.make(
            {
                "demo.body.md": '+++\nexposes = {}\n+++\nBody.\n',
                "demo.decisions.md": '+++\nexposes = {}\n+++\n',
            },
            modules=(),
        )
        self.assert_rule(package.findings, "front.keys", 2)

    def test_nonunique_exposures_fail_but_structural_and_public_names_stay_distinct(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\nsame = "api"\n+++\nRoot.\n',
                "other.private.h.md": '+++\n[exposes]\nsame = "api"\n+++\nOther.\n',
                "api.h.md": "API.\n",
            },
            modules=(),
        )
        self.assert_rule(self.findings(package), "semantic.exposure-unique", 1)

        (self.root / "other.private.h.md").unlink()
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\napi = "other"\n+++\nRoot.\n',
                "api.h.md": "API.\n",
                "other.h.md": "Other.\n",
                "inspect.private.h.md": "Local [api]; public [demo.api].\n",
            },
            modules=(),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_exposure_cycles_terminate_and_report_each_participant(self) -> None:
        package = self.make(
            {
                "a/a.h.md": '+++\n[exposes]\nloop = "b.loop"\n+++\nA.\n',
                "b/b.h.md": '+++\n[exposes]\nloop = "a.loop"\n+++\nB.\n',
            },
            modules=("a", "b"),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.exposure-cycle", 2)
        self.assertEqual(
            {"a/a.h.md", "b/b.h.md"},
            {finding.path for finding in findings if finding.rule == "semantic.exposure-cycle"},
        )

    def test_exposure_rejects_out_of_sight_and_wrong_kind_targets(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\nhidden = "a.secret"\nmodule = "mod"\nitem = "mod.api.open"\n+++\nRoot.\n',
                "a/secret.private.h.md": "Secret.\n",
                "mod/mod.h.md": '+++\n[exposes]\nimplementation = "hidden"\n+++\nModule.\n',
                "mod/api.h.md": "## Structure\n```\n  open    public\n```\n",
                "mod/mod.body.md": "## Flow\n```\n  hidden    implementation\n```\n",
            },
            modules=("a", "mod"),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.exposure-target", 4)
        self.assertEqual(
            {"demo.h.md", "mod/mod.h.md"},
            {finding.path for finding in findings if finding.rule == "semantic.exposure-target"},
        )

    def test_inclusion_composes_items_without_publishing_included_interface(self) -> None:
        dependency = self.dependency(
            "external",
            {
                "external.h.md": '+++\n[exposes]\napi = "api"\n+++\nRoot.\n',
                "api.h.md": '+++\nincludes = ["secret"]\n+++\nAPI.\n',
                "secret.private.h.md": "## Structure\n```\n  hidden    composed\n```\n",
            },
        )
        package = self.make(
            {
                "mod/mod.h.md": "Included [external.api.hidden]; not published [external.secret] or [external.hidden].\n",
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        findings = self.findings(package, dependency)
        self.assert_rule(findings, "semantic.resolved", 2)
        self.assertEqual(
            {"external.secret", "external.hidden"},
            {finding.subject for finding in findings},
        )

    def test_recursive_closure_and_reader_collection_need_only_public_units(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\na = "a"\nb = "b"\n+++\nRoot.\n',
                "a.h.md": "## Structure\n```\n  first    [b.run]\n```\n",
                "b.h.md": "## Structure\n```\n  run    [c.hidden]\n```\n",
                "c.private.h.md": "## Structure\n```\n  hidden    recursive\n```\n",
            },
            modules=(),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.public-closure", 1)
        self.assertEqual("c.hidden", findings[0].subject)

        self.write(
            "demo.h.md",
            '+++\n[exposes]\na = "a"\nb = "b"\nc = "c"\n+++\nRoot.\n',
        )
        package = load_package(self.root)
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        reading = public_reading(package)
        self.assertEqual(("a.h.md", "b.h.md", "c.private.h.md", "demo.h.md"), reading.paths)
        self.assertEqual(reading, public_reading(package))

        self.assert_reading_rebuilds(package, reading)

    def test_foreign_interface_alias_preserves_dependency_public_bounds(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        dependency = self.make(
            {
                "external.h.md": '+++\n[exposes]\napi = "mod.named"\n+++\nRoot.\n',
                "mod/mod.h.md": "## Structure\n```\n  open    private default item\n```\n",
                "mod/named.h.md": "## Structure\n```\n  run    public\n```\n",
                "mod/secret.private.h.md": "Private.\n",
                "mod/deep/deep.h.md": "Nested.\n",
            },
            modules=("mod", "mod/deep"),
            root=Path(temporary.name),
            pid="pkg:quoll/example.com/external",
        )
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    [aliases]
                    m = "external.api"
                    +++
                    Public [m.run]; private [m.default], [m.secret], [m.deep.default], and [external.mod.default].
                    """
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        findings = self.findings(package, dependency)
        self.assert_rule(findings, "semantic.resolved", 4)
        self.assertEqual(
            {"m.default", "m.secret", "m.deep.default", "external.mod.default"},
            {finding.subject for finding in findings},
        )
        self.assertNotIn("semantic.alias-target", {finding.rule for finding in findings})

    def test_composed_exposure_collision_is_rejected_without_a_reference(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\na = "m.x"\n"a.x" = "m.one"\n+++\nRoot.\n',
                "m/m.h.md": '+++\n[exposes]\nx = "two"\n+++\nModule.\n',
                "m/one.h.md": "One.\n",
                "m/two.h.md": "## Structure\n```\n  x    composed item\n```\n",
            },
            modules=("m",),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.exposure-unique", 2)
        self.assertTrue(
            all("composed exposure path a.x" in finding.detail for finding in findings)
        )

    def test_interface_item_collision_is_rejected_without_a_reference(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\na = "api"\n"a.x" = "other"\n+++\nRoot.\n',
                "api.h.md": '+++\nincludes = ["composed"]\n+++\nAPI.\n',
                "composed.private.h.md": "## Structure\n```\n  x    composed item\n```\n",
                "other.h.md": "Other.\n",
                "inspect.private.h.md": '+++\n[aliases]\nitem = "api.x"\n+++\nAn item remains terminal at [item.more].\n',
            },
            modules=(),
        )
        findings = self.findings(package)
        collisions = [
            finding
            for finding in findings
            if finding.rule == "semantic.exposure-unique"
            and "composed exposure path a.x" in finding.detail
        ]
        self.assertEqual(2, len(collisions), [str(finding) for finding in findings])
        self.assert_rule(findings, "semantic.reference-form", 1)
        self.assertEqual(
            "item.more",
            next(
                finding.subject
                for finding in findings
                if finding.rule == "semantic.reference-form"
            ),
        )

    def test_default_interface_items_collide_under_shortened_exposure_aliases(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\nx = "m.default"\n"x.path" = "other"\n+++\nRoot.\n',
                "m/m.h.md": '+++\nincludes = ["composed"]\n+++\nModule.\n',
                "m/composed.private.h.md": "## Structure\n```\n  path    included default item\n```\n",
                "other.h.md": "Other.\n",
                "inspect.private.h.md": "Structural [m.default.path] remains forbidden.\n",
            },
            modules=("m",),
        )
        findings = self.findings(package)
        collisions = [
            finding
            for finding in findings
            if finding.rule == "semantic.exposure-unique"
            and "composed exposure path x.path" in finding.detail
        ]
        self.assertEqual(2, len(collisions), [str(finding) for finding in findings])
        self.assert_rule(findings, "semantic.reference-form", 1)
        self.assertEqual(
            "m.default.path",
            next(
                finding.subject
                for finding in findings
                if finding.rule == "semantic.reference-form"
            ),
        )

    def test_unrelated_modules_may_reuse_exposure_and_item_suffixes(self) -> None:
        package = self.make(
            {
                "one/one.h.md": '+++\n[exposes]\na = "api"\n+++\nOne.\n',
                "one/api.h.md": "## Structure\n```\n  x    first module item\n```\n",
                "two/two.h.md": '+++\n[exposes]\n"a.x" = "other"\n+++\nTwo.\n',
                "two/other.h.md": "Second module interface.\n",
            },
            modules=("one", "two"),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_public_closure_accepts_dependency_package_and_public_target(self) -> None:
        dependency = self.dependency("external")
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\napi = "api"\n+++\nRoot.\n',
                "api.h.md": "Whole [external].\n## Structure\n```\n  open    [external.default.open]\n```\n",
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package, dependency)])
        self.assertEqual(
            ("pkg:quoll/example.com/external@v1.0.0",),
            public_reading(package, (dependency,)).dependencies,
        )

    def test_whole_file_and_empty_inclusion_closure_rebuild(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\napi = "api"\nhelper = "helper"\n+++\nDeclaration holder [helper.hidden].\n',
                "api.h.md": '+++\nincludes = ["empty"]\n+++\nExposed-item lead [helper.hidden].\n## Structure\n```\n  open      public\n  sibling   [helper.hidden]\n```\n',
                "empty.private.h.md": "Included empty lead [helper.hidden].\n",
                "helper.h.md": "## Structure\n```\n  hidden    public target\n```\n",
            },
            modules=(),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        reading = public_reading(package)
        self.assertEqual(
            ("api.h.md", "demo.h.md", "empty.private.h.md", "helper.h.md"),
            reading.paths,
        )
        self.assert_reading_rebuilds(package, reading)

    def test_declaration_and_same_file_references_require_exposure(self) -> None:
        package = self.make(
            {
                "demo.h.md": """\
                    +++
                    [exposes]
                    a = "a"
                    +++
                    Declaration-only [helper.hidden] and same-file [purpose].
                    ## Structure
                    ```
                      purpose    private declaration-holder item
                    ```
                    """,
                "a.h.md": "Exposed interface.\n",
                "helper.h.md": "## Structure\n```\n  hidden    cross-file target\n```\n",
            },
            modules=(),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.public-closure", 2)
        closures = [
            finding for finding in findings if finding.rule == "semantic.public-closure"
        ]
        self.assertEqual(
            {("demo.h.md", "helper.hidden"), ("demo.h.md", "purpose")},
            {(closure.path, closure.subject) for closure in closures},
        )
        self.assertEqual(("a.h.md", "demo.h.md"), public_reading(package).paths)

        self.write(
            "demo.h.md",
            """\
            +++
            [exposes]
            default = "default"
            a = "a"
            helper = "helper"
            +++
            Declaration-only [helper.hidden] and same-file [purpose].
            ## Structure
            ```
              purpose    private declaration-holder item
            ```
            """,
        )
        package = load_package(self.root)
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        reading = public_reading(package)
        self.assertEqual(("a.h.md", "demo.h.md", "helper.h.md"), reading.paths)
        self.assert_reading_rebuilds(package, reading)

    def test_supplied_dependency_findings_are_not_discarded(self) -> None:
        dependency = self.dependency(
            "external",
            {
                "external.h.md": '+++\n[exposes]\ndefault = "default"\n+++\n## Structure\n```\n  open    [missing]\n```\n',
            },
        )
        package = self.make({"mod/mod.h.md": "Local only.\n"})
        findings = self.findings(package, dependency)
        self.assert_rule(findings, "semantic.resolved", 1)
        finding = next(finding for finding in findings if finding.rule == "semantic.resolved")
        self.assertEqual(("external.h.md", "missing"), (finding.path, finding.subject))

    def test_identical_foreign_findings_keep_package_owners(self) -> None:
        first = self.dependency("first", {"api.h.md": "A [missing].\n"})
        second = self.dependency("second", {"api.h.md": "A [missing].\n"})
        package = self.make(
            {"mod/mod.h.md": "Local only.\n"},
            dependencies=[
                "pkg:quoll/example.com/first@v1.0.0",
                "pkg:quoll/example.com/second@v1.0.0",
            ],
        )
        findings = self.findings(package, first, second)
        unresolved = [finding for finding in findings if finding.rule == "semantic.resolved"]
        self.assertEqual(2, len(unresolved), [str(finding) for finding in findings])
        self.assertEqual({first.id, second.id}, {finding.package_id for finding in unresolved})
        self.assertEqual({"api.h.md"}, {finding.path for finding in unresolved})
        for finding in unresolved:
            self.assertIn(finding.package_id, str(finding))

    def test_baseline_filter_preserves_other_package_identical_finding(self) -> None:
        first = self.dependency("first", {"api.h.md": "A [missing].\n"})
        second = self.dependency("second", {"api.h.md": "A [missing].\n"})
        valid_second = self.dependency("second")
        dependencies = [
            "pkg:quoll/example.com/first@v1.0.0",
            "pkg:quoll/example.com/second@v1.0.0",
        ]
        package = self.make({"mod/mod.h.md": "Local only.\n"}, dependencies=dependencies)
        baseline_root = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(baseline_root)
        baseline = self.make(
            {"mod/mod.h.md": "Local only.\n"},
            dependencies=dependencies,
            root=Path(baseline_root.name),
        )
        findings = check_package(
            package,
            baseline,
            (first, second),
            baseline_dependency_packages=(first, valid_second),
        )
        self.assertEqual(1, len(findings), [str(finding) for finding in findings])
        self.assertEqual(second.id, findings[0].package_id)
        self.assertEqual("semantic.resolved", findings[0].rule)

    def test_foreign_reexport_units_keep_owner_identity_and_rebuild(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        dependency = self.make(
            {
                "external.h.md": '+++\n[exposes]\napi = "api"\n+++\nRoot.\n',
                "api.h.md": "## Structure\n```\n  run    foreign\n```\n",
            },
            modules=(),
            root=Path(temporary.name),
            pid="pkg:quoll/example.com/external",
        )
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\nreexported = "external.api"\nlocal = "api"\n+++\nHolder [external.api.run].\n',
                "api.h.md": "## Structure\n```\n  run    local\n```\n",
            },
            modules=(),
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package, dependency)])
        reading = public_reading(package, (dependency,))
        self.assertEqual(2, reading.paths.count("api.h.md"))
        self.assertEqual(len(reading.units), len(set(reading.identities)))
        self.assertEqual(len(reading.units), len({unit.locator for unit in reading.units}))
        self.assertEqual(reading, public_reading(package, (dependency,)))
        self.assert_reading_rebuilds(package, reading, dependency)

    def test_foreign_closure_excludes_unrelated_public_interfaces(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        dependency = self.make(
            {
                "external.h.md": '+++\n[exposes]\napi = "api"\nhelper = "helper"\nunrelated = "unrelated"\nother = "other"\n+++\nRoot.\n',
                "api.h.md": "## Structure\n```\n  run    [helper.run]\n```\n",
                "helper.h.md": "## Structure\n```\n  run    required transitive contract\n```\n",
                "unrelated.h.md": "## Structure\n```\n  entry    [other.run]\n```\n",
                "other.h.md": "## Structure\n```\n  run    unrelated transitive contract\n```\n",
            },
            modules=(),
            root=Path(temporary.name),
            pid="pkg:quoll/example.com/external",
        )
        for mode in ("reexport", "reference", "inclusion"):
            with self.subTest(mode=mode):
                current_root = tempfile.TemporaryDirectory()
                self.extra_temporaries.append(current_root)
                files = {
                    "demo.h.md": '+++\n[exposes]\nselected = "external.api"\n+++\nRoot.\n',
                }
                if mode != "reexport":
                    files["demo.h.md"] = '+++\n[exposes]\nselected = "local"\n+++\nRoot.\n'
                    files["local.h.md"] = (
                        '+++\nincludes = ["external.api"]\n+++\nLocal.\n'
                        if mode == "inclusion"
                        else "## Structure\n```\n  open    [external.api.run]\n```\n"
                    )
                package = self.make(
                    files,
                    modules=(),
                    root=Path(current_root.name),
                    dependencies=["pkg:quoll/example.com/external@v1.0.0"],
                )
                self.assertEqual(
                    [],
                    [str(finding) for finding in self.findings(package, dependency)],
                )
                reading = public_reading(package, (dependency,))
                foreign_paths = {
                    unit.path
                    for unit in reading.units
                    if unit.package_id == dependency.id
                }
                self.assertEqual({"api.h.md", "external.h.md", "helper.h.md"}, foreign_paths)
                foreign_root = next(
                    unit
                    for unit in reading.units
                    if unit.package_id == dependency.id and unit.path == "external.h.md"
                )
                self.assertEqual(("api", "helper"), foreign_root.exposures)
                self.assertNotIn("unrelated.h.md", reading.paths)
                self.assertNotIn("other.h.md", reading.paths)
                self.assert_reading_rebuilds(package, reading, dependency)

    def test_transitive_foreign_reexport_and_inclusion_rebuild_complete_readings(self) -> None:
        for mode in ("reexport", "inclusion"):
            with self.subTest(mode=mode):
                roots = []
                for _name in ("a", "b", "c"):
                    temporary = tempfile.TemporaryDirectory()
                    self.extra_temporaries.append(temporary)
                    roots.append(Path(temporary.name))
                a_root, b_root, c_root = roots
                c = self.make(
                    {
                        "c.h.md": '+++\n[exposes]\napi = "api"\n+++\nC root.\n',
                        "api.h.md": "## Structure\n```\n  run    C contract\n```\n",
                    },
                    modules=(),
                    root=c_root,
                    pid="pkg:quoll/example.com/c",
                )
                b_files = {
                    "b.h.md": '+++\n[exposes]\napi = "c.api"\n+++\nB root.\n',
                }
                if mode == "inclusion":
                    b_files = {
                        "b.h.md": '+++\n[exposes]\nlocal = "local"\n+++\nB root.\n',
                        "local.h.md": '+++\nincludes = ["c.api"]\n+++\nB inclusion.\n',
                    }
                b = self.make(
                    b_files,
                    modules=(),
                    root=b_root,
                    pid="pkg:quoll/example.com/b",
                    dependencies=["pkg:quoll/example.com/c@v1.0.0"],
                )
                b_path = "api" if mode == "reexport" else "local"
                a = self.make(
                    {
                        "a.h.md": '+++\n[exposes]\nlocal = "api"\n+++\nA root.\n',
                        "api.h.md": f"## Structure\n```\n  open    [b.{b_path}.run]\n```\n",
                    },
                    modules=(),
                    root=a_root,
                    pid="pkg:quoll/example.com/a",
                    dependencies=[
                        "pkg:quoll/example.com/b@v1.0.0",
                        "pkg:quoll/example.com/c@v1.0.0",
                    ],
                )
                self.assertEqual(
                    [], [str(finding) for finding in self.findings(a, b, c)]
                )
                reading = public_reading(a, (b, c))
                expected_paths = {
                    a.id: {"a.h.md", "api.h.md"},
                    b.id: {"b.h.md"} | ({"local.h.md"} if mode == "inclusion" else set()),
                    c.id: {"c.h.md", "api.h.md"},
                }
                for pid, paths in expected_paths.items():
                    self.assertEqual(
                        paths,
                        {unit.path for unit in reading.units if unit.package_id == pid},
                    )
                self.assertEqual(
                    ("local",),
                    next(unit.exposures for unit in reading.units if unit.identity == f"{a.id}:source:a.h.md"),
                )
                self.assertEqual(
                    (b_path,),
                    next(unit.exposures for unit in reading.units if unit.identity == f"{b.id}:source:b.h.md"),
                )
                self.assertEqual(
                    ("api",),
                    next(unit.exposures for unit in reading.units if unit.identity == f"{c.id}:source:c.h.md"),
                )
                self.assert_reading_rebuilds(a, reading, b, c)

    def test_foreign_rebuild_asserts_findings_outside_resolution_allowlist(self) -> None:
        dependency = self.dependency(
            "external",
            {
                "external.h.md": '+++\n[exposes]\napi = "api"\n+++\nRoot.\n',
                "api.h.md": "## Structure\n```\n  duplicate    first\n  duplicate    second\n```\n",
            },
        )
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\nselected = "external.api"\n+++\nRoot.\n',
            },
            modules=(),
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        reading = public_reading(package, (dependency,))
        with self.assertRaises(AssertionError) as caught:
            self.assert_reading_rebuilds(package, reading, dependency)
        self.assertIn("semantic.unique-names", str(caught.exception))

    def test_root_default_can_hold_interface_exposure_without_becoming_public(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        dependency = self.make(
            {"std.h.md": '+++\n[exposes]\nfs = "fs.default"\n+++\nStandard library.\n'},
            modules=("fs",),
            root=Path(temporary.name),
            pid="pkg:quoll/example.com/std",
        )
        reading = public_reading(dependency)
        self.assertEqual(("fs/fs.h.md", "std.h.md"), reading.paths)
        self.assertEqual(("fs",), tuple(module.path for module in reading.modules))
        rebuilt_std = self.assert_reading_rebuilds(dependency, reading)
        package = self.make(
            {"mod/mod.h.md": "Public [std.fs]; not recursive [std.fs.default] or [std.default].\n"},
            dependencies=["pkg:quoll/example.com/std@v1.0.0"],
        )
        findings = self.findings(package, rebuilt_std)
        self.assert_rule(findings, "semantic.resolved", 2)
        self.assertEqual({"std.fs.default", "std.default"}, {finding.subject for finding in findings})

    def test_default_interface_alias_coexists_with_private_module_and_unexposed_root(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        dependency = self.make(
            {
                "std.h.md": """\
                    +++
                    [exposes]
                    fs = "fs.default"
                    copy = "std.fs"
                    +++
                    The unexposed root default holds only exposure declarations.
                    """,
                "std.body.md": "Local [fs] and [fs.path]; public [std.fs] and [std.fs.path].\n",
                "fs/fs.h.md": "The carrying module is identified without exposing descendants.\n## Structure\n```\n  path    public file-system path\n```\n",
            },
            modules=("fs",),
            root=Path(temporary.name),
            pid="pkg:quoll/example.com/std",
        )
        self.assertEqual([], [str(finding) for finding in self.findings(dependency)])
        reading = public_reading(dependency)
        self.assertEqual(("fs/fs.h.md", "std.h.md"), reading.paths)
        rebuilt_std = self.assert_reading_rebuilds(dependency, reading)
        package = self.make(
            {
                "mod/mod.h.md": '+++\nincludes = ["std.fs"]\n+++\nPublic [std.fs.path]; not structural [std.fs.default] or [std.default].\n',
            },
            dependencies=["pkg:quoll/example.com/std@v1.0.0"],
        )
        findings = self.findings(package, rebuilt_std)
        self.assert_rule(findings, "semantic.resolved", 2)
        self.assertEqual({"std.fs.default", "std.default"}, {finding.subject for finding in findings})
        self.assertNotIn("semantic.exposure-unique", {finding.rule for finding in findings})
        self.assertNotIn("semantic.ambiguous", {finding.rule for finding in findings})

    def test_same_spelled_module_does_not_hide_an_unrelated_exposure_target(self) -> None:
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\nfs = "other"\n+++\nRoot.\n',
                "fs/fs.h.md": "Private structural module.\n",
                "other.h.md": "Unrelated exposed interface.\n",
                "inspect.private.h.md": "The local [fs] module and public [demo.fs] interface are distinct.\n",
            },
            modules=("fs",),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])


    def test_public_reading_preserves_each_front_and_rebuilds_without_author_roots(self) -> None:
        fronts = {
            "omitted": "",
            "empty": "+++\nprelude = []\n[use]\n\"helper\" = [\"uses\"]\n+++\n",
            "selective": "+++\nprelude = [\"module\"]\n+++\n",
            "use": "+++\nprelude = []\n[use]\n\"helper\" = [\"run\"]\n+++\n",
        }
        statements = {
            "omitted": "[uses]",
            "empty": "[uses]",
            "selective": "[module] and [helper.uses]",
            "use": "[run]",
        }
        for mode, front in fronts.items():
            with self.subTest(mode=mode):
                package = self.make({
                    "demo.h.md": '+++\n[exposes]\napi = "api"\nhelper = "helper.default"\n+++\nRoot.\n',
                    "api.h.md": front + f"Public {statements[mode]}.\n## Structure\n```\n  open    contract\n```\n",
                    "helper/helper.h.md": "## Structure\n```\n  run    target\n  uses   package-owned target\n```\n",
                }, modules=("helper",))
                self.assertEqual([], [str(finding) for finding in self.findings(package)])
                reading = public_reading(package)
                for unit in reading.units:
                    self.assertEqual("0.6.0", unit.edition)
                    self.assertEqual((package.root / unit.path).read_text(encoding="utf-8"), unit.text)
                api_unit = next(unit for unit in reading.units if unit.path == "api.h.md")
                self.assertEqual(front, api_unit.text[: len(front)])
                self.assert_reading_rebuilds(package, reading)

        self.make({"demo.h.md": "Old public input.\n"}, modules=(), edition="0.5.0")
        with self.assertRaisesRegex(ValueError, "0.6.0"):
            public_reading(load_package(self.root))


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

    def test_item_to_own_interface_edges_do_not_form_interface_cycles(self) -> None:
        package = self.make(
            {
                "demo.h.md": "## Structure\n```\n  root item    [root item]\n```\n",
                "api.h.md": "## Structure\n```\n  choice    meaning\n  choose    [choice]\n```\n",
                "mod/mod.h.md": "## Structure\n```\n  local    meaning\n  use    [local]\n```\n",
            }
        )
        findings = self.findings(package)
        self.assertNotIn("semantic.interface-cycle", {finding.rule for finding in findings})
        self.assertNotIn("semantic.includes-cycle", {finding.rule for finding in findings})

    def test_interface_self_inclusion_cycle_is_detected(self) -> None:
        package = self.make({
            "mod/mod.h.md": '+++\nincludes = ["default"]\n+++\nModule.\n',
        })
        self.assert_rule(self.findings(package), "semantic.includes-cycle", 1)

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
            "external.h.md": '+++\nincludes = ["one", "two"]\n[exposes]\ndefault = "default"\n+++\nPublic.\n',
            "one.h.md": "## Structure\n```\n  thing    one\n```\n",
            "two.h.md": "## Structure\n```\n  thing    two\n```\n",
        })
        package = self.make(
            {"mod/mod.h.md": "An [external.default.thing].\n"},
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

    def test_recursive_public_closure_reports_exposed_and_included_sources(self) -> None:
        package = self.make({
            "demo.h.md": '+++\n[exposes]\napi = "api"\n+++\nRoot declarations.\n',
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
            {
                "demo.h.md": '+++\n[exposes]\napi = "api"\n+++\nRoot.\n',
                "api.h.md": "## Structure\n```\n  open    [external.default.open]\n```\n",
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package, dependency)])
    def test_dependency_included_item_satisfies_public_closure(self) -> None:
        dependency = self.dependency("external", {
            "external.h.md": '+++\nincludes = ["secret"]\n[exposes]\ndefault = "default"\n+++\nPublic.\n',
            "secret.private.h.md": "## Structure\n```\n  hidden    exposed by inclusion\n```\n",
        })
        package = self.make(
            {"api.h.md": "## Structure\n```\n  open    [external.default.hidden]\n```\n"},
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
            "external.h.md": '+++\n[exposes]\ndefault = "default"\napi = "api"\n+++\nPublic.\n## Structure\n```\n  open    public\n```\n',
            "api.h.md": "## Structure\n```\n  run    contract\n```\n",
        })
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    [aliases]
                    dep = "pkg:quoll/example.com/external@v1.0.0"
                    api = "dep.api"
                    open = "dep.default.open"
                    +++
                    Land on [dep], [dep.default], [dep.api], [dep.api.run], [dep.default.open], [api.run], and [open].
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
                    open = "dep.default.open"
                    bad = "open.more"
                    +++
                    Invalid [dep.default.open.more] and [open.more].
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

    def test_interface_alias_cannot_use_forbidden_body_item_fallback(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                +++
                [aliases]
                bad = "hidden"
                +++
                Module.
                """,
            "mod/mod.body.md": """\
                +++
                [aliases]
                implementation = "hidden"
                +++
                ## Flow
                ```
                  hidden    implementation
                ```
                """,
            "mod/mod.decisions.md": """\
                +++
                [aliases]
                implementation = "hidden"
                +++
                **D-1. Body item alias**
                *Stated by* [implementation]
                """,
        })
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.alias-target", 1)
        finding = next(finding for finding in findings if finding.rule == "semantic.alias-target")
        self.assertEqual("mod/mod.h.md", finding.path)
        self.assertEqual("bad", finding.subject)

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

    def test_same_package_module_interface_and_item_aliases_in_body_and_decisions(self) -> None:
        package = self.make(
            {
                "demo.body.md": """\
                    +++
                    prelude = []
                    [aliases]
                    model_alias = "model"
                    kernel = "model.kernel"
                    uses = "model.kernel.uses"
                    short = "uses"
                    +++
                    Resolve [model_alias.kernel.uses], [kernel.uses], [uses], and [short].
                    """,
                "demo.decisions.md": """\
                    +++
                    prelude = []
                    [aliases]
                    uses = "model.kernel.uses"
                    +++
                    **D-1. Local alias**
                    *Stated by* [uses]
                    """,
                "model/model.h.md": "Model.\n",
                "model/kernel.h.md": "## Structure\n```\n  uses    relation\n```\n",
            },
            modules=("model",),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_decision_front_matter_accepts_only_aliases(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  thing    meaning\n```\n",
            "mod/mod.decisions.md": """\
                +++
                includes = ["default"]
                [aliases]
                thing = "default.thing"
                +++
                **D-1. Decision alias**
                *Stated by* [thing]
                """,
        })
        self.assert_rule(package.findings, "front.keys", 1)
        self.assertNotIn("semantic.alias-target", {finding.rule for finding in self.findings(package)})

    def test_aliases_remain_file_local(self) -> None:
        package = self.make(
            {
                "a/a.h.md": '+++\n[aliases]\nthing = "default.local"\n+++\nA [thing].\n## Structure\n```\n  local    meaning\n```\n',
                "b/b.h.md": "B [thing].\n",
            },
            modules=("a", "b"),
        )
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.resolved", 1)
        self.assertEqual("b/b.h.md", next(finding.path for finding in findings if finding.rule == "semantic.resolved"))

    def test_same_package_item_alias_is_terminal(self) -> None:
        package = self.make(
            {
                "mod/mod.h.md": """\
                    +++
                    [aliases]
                    uses = "api.uses"
                    +++
                    Invalid [uses.more].
                    """,
                "mod/api.h.md": "## Structure\n```\n  uses    relation\n```\n",
            },
        )
        self.assert_rule(self.findings(package), "semantic.reference-form", 1)

    def test_alias_cycle_reports_participants_but_not_an_acyclic_prefix(self) -> None:
        package = self.make({
            "mod/mod.body.md": """\
                +++
                [aliases]
                prefix = "a.api"
                a = "b.api"
                b = "c.api"
                c = "b.api"
                +++
                Body.
                """
        })
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.alias-cycle", 2)
        self.assertEqual(
            {"b", "c"},
            {finding.subject for finding in findings if finding.rule == "semantic.alias-cycle"},
        )

    def test_alias_collision_with_visible_dependency(self) -> None:
        package = self.make(
            {
                "mod/mod.body.md": '+++\n[aliases]\nexternal = "pkg:quoll/example.com/external@v1.0.0"\n+++\nBody.\n',
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        self.assert_rule(self.findings(package), "semantic.alias-unique", 1)

    def test_public_closure_uses_alias_target_identity(self) -> None:
        dependency = self.dependency("external")
        package = self.make(
            {
                "demo.h.md": '+++\n[exposes]\napi = "api"\n+++\nRoot.\n',
                "api.h.md": """\
                    +++
                    [aliases]
                    open = "external.default.open"
                    hidden = "mod.internal.escape"
                    +++
                    Public [open] but private [hidden].
                    """,
                "mod/mod.h.md": "Module.\n",
                "mod/internal.h.md": "## Structure\n```\n  escape    hidden\n```\n",
            },
            dependencies=["pkg:quoll/example.com/external@v1.0.0"],
        )
        findings = self.findings(package, dependency)
        self.assert_rule(findings, "semantic.public-closure", 1)
        self.assertEqual("hidden", next(finding.subject for finding in findings if finding.rule == "semantic.public-closure"))

    def workspace(self, decisions: str) -> Package:
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.write("workspace.decisions.md", decisions)
        self.make(
            {
                "member.h.md": '+++\n[exposes]\ndefault = "default"\napi = "api"\n+++\n## Structure\n```\n  open    public\n```\n',
                "api.h.md": "## Structure\n```\n  run    public\n  public surface    public\n```\n",
                "secret.private.h.md": "## Structure\n```\n  hidden    private\n```\n",
                "internal/internal.h.md": "## Structure\n```\n  hidden    internal\n```\n",
            },
            modules=("internal",),
            root=self.root / "member",
            pid="pkg:quoll/example.com/member",
        )
        return load_package(self.root)

    def test_workspace_decision_aliases_use_member_public_roots(self) -> None:
        package = self.workspace("""\
            +++
            [aliases]
            member_alias = "member"
            open = "member.default.open"
            api = "member.api"
            by_id = "pkg:quoll/example.com/member.api.run"
            by_id_multiword = "pkg:quoll/example.com/member.api.public surface"
            +++
            **W-1. Public member aliases**
            *Because* [member_alias.api.run], [open], [api.run], [by_id], and [by_id_multiword] are public.
            """)
        self.assertEqual([], [str(finding) for finding in package.findings if finding.rule == "front.alias"])
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_workspace_decision_aliases_do_not_add_member_sight(self) -> None:
        package = self.workspace("""\
            +++
            [aliases]
            internal = "member.internal.hidden"
            private = "member.secret.hidden"
            +++
            **W-1. Bounded member sight**
            *Because* [member.internal.hidden] and [member.secret.hidden] are not public roots.
            """)
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.alias-target", 2)
        self.assert_rule(findings, "semantic.resolved", 2)

    def test_workspace_alias_collides_with_member_name(self) -> None:
        package = self.workspace("""\
            +++
            [aliases]
            member = "member.default.open"
            +++
            **W-1. Member collision**
            *Because* The local spelling collides.
            """)
        self.assert_rule(self.findings(package), "semantic.alias-unique", 1)

    def test_workspace_interface_alias_keeps_member_public_bounds(self) -> None:
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.write(
            "workspace.decisions.md",
            """\
            +++
            [aliases]
            m = "member.api"
            +++
            **W-1. Exposed member interface**
            *Because* [m.run] is public while [m.default], [m.secret], and [m.deep.default] are bounded.
            """,
        )
        self.make(
            {
                "member.h.md": '+++\n[exposes]\napi = "mod.named"\n+++\nMember.\n',
                "mod/mod.h.md": "Module.\n",
                "mod/named.h.md": "## Structure\n```\n  run    public\n```\n",
                "mod/secret.private.h.md": "Private.\n",
                "mod/deep/deep.h.md": "Nested.\n",
            },
            modules=("mod", "mod/deep"),
            root=self.root / "member",
            pid="pkg:quoll/example.com/member",
        )
        findings = self.findings(load_package(self.root))
        self.assert_rule(findings, "semantic.resolved", 3)
        self.assertEqual(
            {"m.default", "m.secret", "m.deep.default"},
            {finding.subject for finding in findings},
        )
        self.assertNotIn("semantic.alias-target", {finding.rule for finding in findings})

    def test_workspace_discovery_prunes_only_declared_member_roots(self) -> None:
        self.write(
            "workspace.quoll.toml",
            'packages = ["packages/member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.make(
            {"member.h.md": "Member.\n"},
            modules=(),
            root=self.root / "packages/member",
            pid="pkg:quoll/example.com/member",
        )
        self.write("packages/other/other.h.md", "A [missing].\n")
        package = load_package(self.root)
        placements = [finding for finding in package.findings if finding.rule == "source.placement"]
        self.assertEqual(["packages/other/other.h.md"], [finding.path for finding in placements])
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.resolved", 1)
        self.assertEqual(
            "packages/other/other.h.md",
            next(finding.path for finding in findings if finding.rule == "semantic.resolved"),
        )

    def test_current_and_baseline_keep_the_same_undeclared_sibling_package(self) -> None:
        current_root = self.root / "current"
        baseline_root = self.root / "baseline"
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
            current_root,
        )
        self.make(
            {"member.h.md": "Member.\n"},
            modules=(),
            root=current_root / "member",
            pid="pkg:quoll/example.com/member",
        )
        self.make(
            {"other.h.md": "Undeclared sibling.\n"},
            modules=(),
            root=current_root / "other",
            pid="pkg:quoll/example.com/other",
        )
        shutil.copytree(current_root, baseline_root)
        current = load_package(current_root)
        baseline = load_package(baseline_root, baseline=True)
        current_places = [finding.path for finding in current.findings if finding.rule == "source.placement"]
        baseline_places = [finding.path for finding in baseline.findings if finding.rule == "source.placement"]
        self.assertEqual(["other/other.h.md"], current_places)
        self.assertEqual(current_places, baseline_places)
        self.assertNotIn("member/member.h.md", current_places + baseline_places)


class EditionPreludeCase(PackageFixtures, unittest.TestCase):
    def test_default_empty_selective_inflection_and_capitalization(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                +++
                [aliases]
                m = "module"
                +++
                Edition [module], inflected [module]s, and explicit [m].
                ## Structure
                ```
                  module    package-owned but reserved by the included prelude
                ```
                """,
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        evidence = dependent_site_evidence(package)
        self.assertTrue(evidence.complete, evidence.limits)
        module_targets = {site.target for site in evidence.sites if site.reference == "module"}
        self.assertEqual({"edition:0.6.0:model.kernel.module"}, module_targets)
        self.assertEqual(
            {"edition:0.6.0:model.kernel.module"},
            {site.target for site in evidence.sites if site.reference == "m"},
        )

        package = self.make({
            "mod/mod.h.md": """\
                +++
                prelude = ["uses"]
                +++
                Local [module], edition [uses], and a [module](https://example.com) link.
                ## Structure
                ```
                  module    package-owned meaning
                ```
                """,
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        evidence = dependent_site_evidence(package)
        self.assertTrue(any(
            site.reference == "module" and site.target.endswith(":mod:mod:module")
            for site in evidence.sites
        ))
        self.assertIn("edition:0.6.0:model.kernel.uses", {site.target for site in evidence.sites})

        package = self.make({
            "mod/mod.h.md": """\
                +++
                prelude = []
                +++
                Both [module] and [uses] are package-owned; `[module]` and [module](https://example.com) are literal or links.
                ## Structure
                ```
                  module    local
                  uses      local
                ```
                """,
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        package = self.make({"mod/mod.h.md": "Capitalized [Module] is not an edition alias.\n"})
        self.assert_rule(self.findings(package), "semantic.resolved", 1)

    def test_prelude_stated_by_needs_no_language_dependency(self) -> None:
        package = self.make({
            "mod/mod.decisions.md": "**D-1. Edition item**\n*Stated by* [module].\n",
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_unknown_duplicate_and_malformed_prelude_fail(self) -> None:
        cases = (
            ('prelude = true\n', "front.type"),
            ('prelude = "uses"\n', "front.type"),
            ('prelude = [1]\n', "front.type"),
            ('prelude = ["unknown"]\n', "front.prelude"),
            ('prelude = ["uses", "uses"]\n', "front.prelude"),
        )
        for declaration, rule in cases:
            with self.subTest(declaration=declaration):
                package = self.make({"mod/mod.h.md": f"+++\n{declaration}+++\nModule.\n"})
                self.assert_rule(package.findings, rule, 1)

    def test_same_and_distinct_target_collisions_and_excluded_rename(self) -> None:
        declarations = (
            '[aliases]\nuses = "model.kernel.uses"\n',
            '[aliases]\nuses = "default.local"\n',
            '[use]\n"model.kernel" = ["uses"]\n',
        )
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                package = self.make({
                    "mod/mod.h.md": f"+++\n{declaration}+++\nModule.\n## Structure\n```\n  local    target\n```\n",
                    "model/model.h.md": "Model.\n",
                    "model/kernel.h.md": "## Structure\n```\n  uses    relation\n```\n",
                }, modules=("mod", "model"))
                self.assert_rule(self.findings(package), "semantic.alias-unique", 1)

        package = self.make({
            "mod/mod.h.md": '+++\nprelude = []\n[aliases]\nuses = "model.kernel.uses"\n+++\nRenamed [uses].\n',
            "model/model.h.md": "Model.\n",
            "model/kernel.h.md": "## Structure\n```\n  uses    relation\n```\n",
        }, modules=("mod", "model"))
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_non_language_lookalikes_never_capture_prelude_targets(self) -> None:
        package = self.make({
            "model/model.h.md": "Consumer-owned model module.\n",
            "model/kernel.h.md": "## Structure\n```\n  module    consumer lookalike\n```\n",
            "model/graph.h.md": "## Structure\n```\n  package    consumer lookalike\n```\n",
            "other/other.h.md": "Fixed [module] and [package] references.\n",
        }, modules=("model", "other"))
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        evidence = dependent_site_evidence(package)
        self.assertEqual(
            {"edition:0.6.0:model.kernel.module", "edition:0.6.0:model.graph.package"},
            {site.target for site in evidence.sites if site.path == "other/other.h.md"},
        )

    def test_edition_references_add_no_public_or_uses_edge_but_keep_definition_cycles(self) -> None:
        package = self.make({
            "language.h.md": '+++\n[exposes]\nother = "other.default"\n+++\nRoot.\n',
            "language.body.md": """\
                ## Rules
                ```
                  other alone    [module] providing [other.default] [uses] no [interface]
                ```
                """,
            "model/model.h.md": "Model.\n",
            "model/kernel.h.md": "## Structure\n```\n  module    edition item\n  uses      relation\n  interface contract\n```\n",
            "other/other.h.md": "## Structure\n```\n  open    [module]\n```\n",
        }, modules=("model", "other"), pid="pkg:quoll/rete-labs.ru/quoll/language")
        findings = self.findings(package)
        self.assertNotIn("semantic.public-closure", {finding.rule for finding in findings})
        self.assertNotIn("semantic.uses", {finding.rule for finding in findings})
        self.assertNotIn("model/kernel.h.md", public_reading(package).paths)

        package = self.make({
            "model/model.h.md": "Model.\n",
            "model/kernel.h.md": "## Structure\n```\n  module    [other.open]\n```\n",
            "other/other.h.md": "## Structure\n```\n  open    [module]\n```\n",
        }, modules=("model", "other"), pid="pkg:quoll/rete-labs.ru/quoll/language")
        self.assert_rule(self.findings(package), "semantic.definition-cycle", 2)

    def test_old_current_and_baseline_editions_are_rejected_without_old_semantics(self) -> None:
        self.make({
            "model/model.h.md": "Model.\n",
            "model/kernel.h.md": "## Structure\n```\n  module    item\n  decision  item\n```\n",
            "model/model.decisions.md": "**D-1. Old spelling**\n*Stated by* module and decision.\n",
        }, modules=("model",), edition="0.5.0")
        baseline = load_package(self.root, baseline=True)
        self.assert_rule(baseline.findings, "manifest.edition", 1)
        self.assertEqual([], baseline.files)
        current = load_package(self.root)
        self.assert_rule(current.findings, "manifest.edition", 1)
        self.assertEqual([], current.files)
    def test_unavailable_dependency_sites_relations_and_exposures_limit_evidence(self) -> None:
        package = self.make({
            "demo.h.md": '+++\n[exposes]\nselected = "external.api"\n+++\nRoot.\n',
            "mod/mod.h.md": '+++\nincludes = ["external.api"]\n+++\nA [external.api.run].\n',
        }, dependencies=["pkg:quoll/example.com/external@v1.0.0"])
        evidence = dependent_site_evidence(package)
        self.assertFalse(evidence.complete)
        limits = "\n".join(evidence.limits)
        self.assertIn("unavailable dependency surface", limits)
        self.assertIn("mod/mod.h.md:external.api.run", limits)
        self.assertIn("includes", limits)
        self.assertIn("exposes", limits)

    def test_malformed_front_binding_limits_evidence_without_a_reference(self) -> None:
        package = self.make({
            "mod/mod.h.md": '+++\n[use]\n"mod.api" = ["run"\n+++\nModule.\n',
        })
        self.assertIn("front.toml", {finding.rule for finding in package.findings})
        evidence = dependent_site_evidence(package)
        self.assertFalse(evidence.complete)
        self.assertIn("malformed or absent front bindings", "\n".join(evidence.limits))


class UseAliasCase(PackageFixtures, unittest.TestCase):
    def test_derived_names_and_every_relation_consumer(self) -> None:
        package = self.make({
            "mod/mod.h.md": "Module.\n",
            "mod/api.h.md": """\
                ## Structure
                ```
                  run              contract
                  public surface   contract
                  Capitalized      contract
                ```
                """,
            "consumer/consumer.h.md": """\
                +++
                includes = ["api"]
                [use]
                "mod" = ["api"]
                [exposes]
                selected = "api"
                +++
                Included [api.run].
                """,
            "inspect/inspect.h.md": """\
                +++
                [use]
                "mod.api" = ["run", "public surface", "Capitalized"]
                +++
                Prose [run], [public surface], and [Capitalized].
                """,
            "consumer/consumer.body.md": """\
                +++
                implements = ["api"]
                [use]
                "mod" = ["api"]
                +++
                ## Flow
                ```
                  impl [api]:
                    run    implementation
                ```
                """,
            "decide/decide.h.md": "Decision module.\n",
            "decide/decide.decisions.md": """\
                +++
                [use]
                "mod.api" = ["run"]
                +++
                **C-1. Derived decision reference**
                *Stated by* [run]
                """,
        }, modules=("mod", "consumer", "decide", "inspect"))
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        evidence = dependent_site_evidence(package)
        self.assertTrue(
            {"includes", "implements", "impl", "exposes", "decision"}
            <= {site.context for site in evidence.sites}
        )

    def test_alias_resolved_prefix_no_prefix_alias_and_terminal_rejection(self) -> None:
        package = self.make({
            "mod/mod.h.md": "Module.\n",
            "mod/api.h.md": "## Structure\n```\n  run    contract\n```\n",
            "consumer/consumer.h.md": """\
                +++
                [aliases]
                m = "mod"
                bad = "run.more"
                [use]
                "m.api" = ["run"]
                +++
                Derived [run], missing prefix alias [api], and invalid [run.more].
                """,
        }, modules=("mod", "consumer"))
        findings = self.findings(package)
        self.assert_rule(findings, "semantic.resolved", 1)
        self.assert_rule(findings, "semantic.reference-form", 1)
        self.assert_rule(findings, "semantic.alias-target", 1)

    def test_malformed_empty_and_duplicate_use_declarations_fail(self) -> None:
        cases = (
            ('use = "mod.api"\n', "front.type"),
            ('[use]\nmod.api = ["run"]\n', "front.type"),
            ('[use]\n"" = ["run"]\n', "front.use"),
            ('[use]\n"mod.api" = [""]\n', "front.use"),
            ('[use]\n"mod.api" = ["pkg:quoll/example.com/x"]\n', "front.use"),
            ('[use]\n"mod.api" = ["run", "run"]\n', "front.use"),
        )
        for declaration, rule in cases:
            with self.subTest(declaration=declaration):
                package = self.make({"mod/mod.h.md": f"+++\n{declaration}+++\nModule.\n"})
                self.assert_rule(package.findings, rule, 1)

    def test_cross_group_and_rename_collisions_are_order_independent(self) -> None:
        declarations = (
            '[use]\n"mod.api" = ["run", "other.run"]\n',
            '[aliases]\nrun = "mod.api.run"\n[use]\n"mod.api" = ["run"]\n',
            '[use]\n"mod.api" = ["run"]\n[aliases]\nrun = "mod.api.run"\n',
        )
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                package = self.make({
                    "mod/mod.h.md": "Module.\n",
                    "mod/api.h.md": "## Structure\n```\n  run    contract\n```\n",
                    "mod/other.h.md": "## Structure\n```\n  run    contract\n```\n",
                    "consumer/consumer.h.md": f"+++\n{declaration}+++\nConsumer.\n",
                }, modules=("mod", "consumer"))
                self.assert_rule(self.findings(package), "semantic.alias-unique", 1)

    def test_use_cycles_and_sight_are_not_exempted(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                +++
                [aliases]
                a = "run"
                [use]
                "a" = ["run"]
                +++
                Module.
                """,
        })
        self.assert_rule(self.findings(package), "semantic.alias-cycle", 2)
        package = self.make({
            "a/secret.private.h.md": "## Structure\n```\n  hidden    private\n```\n",
            "b/b.h.md": '+++\n[use]\n"a.secret" = ["hidden"]\n+++\nB.\n',
        }, modules=("a", "b"))
        self.assert_rule(self.findings(package), "semantic.alias-target", 1)


    def test_grouped_use_is_current_and_old_baselines_are_rejected(self) -> None:
        files = {
            "mod/mod.h.md": "Module.\n",
            "mod/api.h.md": "## Structure\n```\n  run    contract\n```\n",
            "consumer/consumer.h.md": '+++\n[use]\n"mod.api" = ["run"]\n+++\nCurrent [run].\n',
        }
        current = self.make(files, modules=("mod", "consumer"))
        self.assertEqual([], [str(finding) for finding in self.findings(current)])

        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        self.make(
            files,
            modules=("mod", "consumer"),
            root=Path(temporary.name),
            edition="0.5.0",
        )
        baseline = load_package(temporary.name, baseline=True)
        self.assert_rule(baseline.findings, "manifest.edition", 1)
        self.assertEqual([], baseline.files)

    def test_workspace_use_and_resolved_dependent_site_evidence(self) -> None:
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.write(
            "workspace.decisions.md",
            '+++\n[use]\n"member.api" = ["run"]\n+++\n**W-1. Derived member reference**\n*Because* [run] and [module] resolve publicly.\n',
        )
        self.make({
            "member.h.md": '+++\n[exposes]\napi = "api"\n+++\nMember.\n',
            "api.h.md": "## Structure\n```\n  run    public\n```\n",
        }, modules=(), root=self.root / "member", pid="pkg:quoll/example.com/member")
        workspace = load_package(self.root)
        self.assertEqual([], [str(finding) for finding in self.findings(workspace)])
        evidence = dependent_site_evidence(workspace)
        site = next(
            site
            for site in evidence.sites
            if site.path == "workspace.decisions.md" and site.reference == "run"
        )
        self.assertEqual("run", site.reference)
        self.assertIn("pkg:quoll/example.com/member:item:", site.target)
        self.assertIn(
            "edition:0.6.0:model.kernel.module",
            {site.target for site in evidence.sites if site.reference == "module"},
        )

        self.write(
            "workspace.decisions.md",
            '+++\nprelude = []\n+++\n**W-1. Disabled edition prelude**\n*Because* [member.api.run] stays ordinary while [module] has no local target.\n',
        )
        self.assert_rule(self.findings(load_package(self.root)), "semantic.resolved", 1)


class WorkspacePreludeCase(PackageFixtures, unittest.TestCase):
    def workspace(self, front: str, decision: str, *, member_edition: str = "0.6.0") -> Package:
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.write("workspace.decisions.md", front + decision)
        self.make({
            "member.h.md": '+++\n[exposes]\ndefault = "default"\napi = "api"\n+++\nMember.\n',
            "api.h.md": "## Structure\n```\n  run     public\n  module  public\n```\n",
        }, modules=(), root=self.root / "member", pid="pkg:quoll/example.com/member", edition=member_edition)
        return load_package(self.root)

    def test_workspace_omitted_empty_and_selective_prelude(self) -> None:
        package = self.workspace("", "**W-1. Omitted**\n*Because* [module] is fixed.\n")
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        evidence = dependent_site_evidence(package)
        self.assertIn(
            "edition:0.6.0:model.kernel.module",
            {site.target for site in evidence.sites if site.reference == "module"},
        )

        for selected in ([], ["uses"]):
            with self.subTest(selected=selected):
                front = (
                    "+++\n"
                    + "prelude = [" + ", ".join(f'\"{name}\"' for name in selected) + "]\n"
                    + '[aliases]\nmodule = "member"\n+++\n'
                )
                package = self.workspace(front, "**W-1. Selected**\n*Because* [module.api.run] is public.\n")
                self.assertEqual([], [str(finding) for finding in self.findings(package)])
                if selected:
                    self.write(
                        "workspace.decisions.md",
                        front + "**W-2. Fixed uses**\n*Because* [uses] is fixed.\n",
                    )
                    self.assertEqual([], [str(finding) for finding in self.findings(load_package(self.root))])

    def test_workspace_prelude_collision_and_invalid_entries(self) -> None:
        package = self.workspace(
            '+++\n[aliases]\nmodule = "member"\n+++\n',
            "**W-1. Reserved**\n*Because* The included spelling cannot be shadowed.\n",
        )
        self.assert_rule(self.findings(package), "semantic.alias-unique", 1)
        package = self.workspace(
            '+++\n[use]\n"member.api" = ["module"]\n+++\n',
            "**W-1. Derived reserved**\n*Because* The derived spelling cannot shadow either.\n",
        )
        self.assert_rule(self.findings(package), "semantic.alias-unique", 1)

        for declaration, rule in (
            ('prelude = true\n', "front.type"),
            ('prelude = ["unknown"]\n', "front.prelude"),
            ('prelude = ["uses", "uses"]\n', "front.prelude"),
        ):
            with self.subTest(declaration=declaration):
                package = self.workspace(f"+++\n{declaration}+++\n", "**W-1. Invalid**\n")
                self.assert_rule(package.findings, rule, 1)

    def test_member_edition_is_mandatory_and_not_inherited(self) -> None:
        package = self.workspace("", "**W-1. Workspace edition**\n*Because* [module] is fixed.\n", member_edition="0.5.0")
        self.assertEqual("0.6.0", package.edition)
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        member = package.workspace_members[0]
        self.assert_rule(member.findings, "manifest.edition", 1)
        self.assertEqual([], member.files)


class RelatedWorkspaceCase(PackageFixtures, unittest.TestCase):
    def write_ancestor(self, edition: str | None) -> Path:
        ancestor = self.root / "ancestor"
        edition_line = f'edition = "{edition}"\n' if edition is not None else ""
        self.write(
            "workspace.quoll.toml",
            f'packages = ["member"]\n{edition_line}description = "Ancestor workspace."\n',
            ancestor,
        )
        self.write(
            "workspace.decisions.md",
            "+++\nunknown = true\n+++\n**W-1. Front must not be parsed without authority.**\n",
            ancestor,
        )
        return ancestor

    def test_nonmember_ignores_invalid_ancestor_workspace_edition(self) -> None:
        for edition in (None, "0.5.0"):
            with self.subTest(edition=edition):
                ancestor = self.write_ancestor(edition)
                package = self.make(root=ancestor / "nonmember")
                self.assertEqual("0.6.0", package.edition)
                self.assertEqual([], package.related_decisions)
                self.assertNotIn("workspace.edition", {finding.rule for finding in package.findings})
                self.assertNotIn("front.keys", {finding.rule for finding in package.findings})
                self.assertEqual([], [str(finding) for finding in self.findings(package)])

    def test_member_requires_valid_ancestor_before_decision_front_parsing(self) -> None:
        for edition in (None, "0.5.0"):
            with self.subTest(edition=edition):
                ancestor = self.write_ancestor(edition)
                package = self.make(root=ancestor / "member")
                self.assertEqual("0.6.0", package.edition)
                self.assertEqual([], package.related_decisions)
                self.assert_rule(package.findings, "workspace.edition", 1)
                self.assertNotIn("front.keys", {finding.rule for finding in package.findings})


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

    def test_stated_by_accepts_exactly_the_seven_bracketed_prelude_items(self) -> None:
        package = self.make(
            {
                "model/model.h.md": "Model.\n",
                "model/kernel.h.md": (
                    "## Structure\n```\n"
                    "  module     one\n  interface  one\n  item       one\n"
                    "  decision   one\n  uses       relation\n```\n"
                ),
                "model/graph.h.md": "## Structure\n```\n  workspace  one\n  package    one\n```\n",
                "model/model.decisions.md": (
                    "**D-1. Prelude items**\n"
                    "*Stated by* [workspace], [package], [module], [interface], [item], [decision] and [uses].\n"
                ),
            },
            modules=("model",),
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

        self.write(
            "model/model.decisions.md",
            "**D-1. Not a core word**\n*Stated by* module and uses.\n",
        )
        findings = self.findings(load_package(self.root))
        self.assert_rule(findings, "semantic.stated-by-form", 1)
        self.assertNotIn("semantic.stated-by-target", {finding.rule for finding in findings})

    def test_bracketed_prelude_items_resolve_to_edition_items_across_modules(self) -> None:
        package = self.make(
            {
                "model/model.h.md": "Model.\n",
                "model/kernel.h.md": "## Structure\n```\n  module  contains no local lookalike\n```\n",
                "model/graph.h.md": "## Structure\n```\n  package  edition meaning\n```\n",
                "other/other.h.md": "## Structure\n```\n  module  local lookalike\n  package  local lookalike\n```\n",
                "other/other.decisions.md": (
                    "**D-1. Edition items**\n*Stated by* [package] and [module].\n"
                ),
            },
            modules=("model", "other"),
            pid="pkg:quoll/rete-labs.ru/quoll/language",
        )
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        negative = next(
            finding
            for finding in prose_findings(package, review=True)
            if finding.rule == "prose.negative-definition" and finding.path == "model/kernel.h.md"
        )
        self.assertIn("D-1", negative.detail)

    def test_bare_core_word_and_bare_multiword_are_rejected_in_stated_by(self) -> None:
        for stated_by in ("decision", "full interface"):
            with self.subTest(stated_by=stated_by):
                package = self.make({
                    "mod/mod.decisions.md": f"**D-1. Required target**\n*Stated by* {stated_by}\n",
                })
                findings = self.findings(package)
                self.assert_rule(findings, "semantic.stated-by-form", 1)

    def test_every_stated_by_reference_lands_on_an_item(self) -> None:
        package = self.make({
            "mod/mod.decisions.md": """\
                **D-1. Decision target**
                *Stated by* [D-1]
                """,
        })
        self.assert_rule(self.findings(package), "semantic.stated-by-target", 1)

    def test_structure_item_may_use_a_later_item(self) -> None:
        package = self.make({
            "mod/mod.h.md": """\
                ## Structure
                ```
                  entry    [failure]
                  failure  definition
                ```
                """,
        })
        findings = self.findings(package)
        self.assertEqual([], [str(finding) for finding in findings])
        self.assertNotIn("semantic.definition-order", {finding.rule for finding in findings})

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


class PointerStubLifetimeCase(PackageFixtures, unittest.TestCase):
    def baseline(self, files: dict[str, str]) -> Package:
        temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(temporary)
        return self.make(files, root=Path(temporary.name))

    def test_nested_copied_baseline_preserves_modules_decisions_and_lifetime(self) -> None:
        original_temporary = tempfile.TemporaryDirectory()
        working_temporary = tempfile.TemporaryDirectory()
        current_temporary = tempfile.TemporaryDirectory()
        self.extra_temporaries.extend((original_temporary, working_temporary, current_temporary))
        files = {
            "mod/mod.h.md": "## Structure\n```\n  run    meaning\n```\n",
            "mod/mod.decisions.md": "**D-1. Kept**\n*Stated by* [run]\n*Because* History persists.\n",
        }
        original = self.make(files, root=Path(original_temporary.name))
        self.assertIn("mod", original.module_map)
        nested = Path(working_temporary.name) / "copies/working/baseline"
        nested.parent.mkdir(parents=True)
        shutil.copytree(original.root, nested)
        shutil.copytree(original.root, nested / "language")
        self.write(
            "workspace.quoll.toml",
            'packages = ["mod"]\nedition = "0.6.0"\ndescription = "Not a member package root."\n',
            nested,
        )
        baseline = load_package(nested, baseline=True)
        self.assertIn("mod", baseline.module_map)
        self.assertEqual(["D-1"], [decision.id for decision in baseline.module_map["mod"].decisions.decisions])
        self.assertNotIn("source.placement", {finding.rule for finding in baseline.findings})
        current = self.make(files, root=Path(current_temporary.name))
        self.assertEqual([], [str(finding) for finding in decision_lifetime_findings(current, baseline, review=True)])

    def test_full_entry_to_pointer_stub_is_valid_but_changed_successor_is_not(self) -> None:
        header = "## Structure\n```\n  run    meaning\n```\n"
        old_decisions = (
            "**D-1. Old choice**\n"
            "*Stated by* [missing]\n"
            "*Because* Withdrawn historical prose.\n"
            "*Superseded by* D-2\n\n"
            "**D-2. Current choice**\n"
            "*Stated by* [run]\n"
            "*Rejected* The old choice.\n"
        )
        new_decisions = (
            "**D-1.** *Superseded by* D-2\n\n"
            "**D-2. Current choice**\n"
            "*Stated by* [run]\n"
            "*Rejected* The old choice.\n"
        )
        baseline = self.baseline({"mod/mod.h.md": header, "mod/mod.decisions.md": old_decisions})
        current = self.make({"mod/mod.h.md": header, "mod/mod.decisions.md": new_decisions})
        self.assertEqual([], [str(finding) for finding in self.findings(current)])
        self.assertEqual(
            [],
            [str(finding) for finding in decision_lifetime_findings(current, baseline, review=True)],
        )

        self.write(
            "mod/mod.decisions.md",
            new_decisions.replace("D-2. Current choice", "D-2. Changed choice"),
        )
        changed = load_package(self.root)
        findings = decision_lifetime_findings(changed, baseline, review=True)
        self.assert_rule(findings, "lifetime.in-place-replacement", 1)
        finding = next(finding for finding in findings if finding.rule == "lifetime.in-place-replacement")
        self.assertEqual("D-2", finding.subject)
        self.assertEqual("review", finding.severity)

    def test_inactive_pointer_migrates_when_its_successor_is_superseded(self) -> None:
        header = "## Structure\n```\n  run    meaning\n```\n"
        baseline = self.baseline({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": (
                "**D-1.** *Superseded by* D-2\n\n"
                "**D-2. Former active choice**\n*Stated by* [run]\n"
            ),
        })
        current = self.make({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": (
                "**D-1.** *Superseded by* D-3\n\n"
                "**D-2.** *Superseded by* D-3\n\n"
                "**D-3. Current choice**\n*Stated by* [run]\n"
            ),
        })
        self.assertEqual(
            [],
            [
                str(finding)
                for finding in decision_lifetime_findings(current, baseline, review=True)
            ],
        )

    def test_inactive_pointer_cannot_retarget_while_former_successor_is_active(self) -> None:
        header = "## Structure\n```\n  run    meaning\n```\n"
        baseline = self.baseline({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": (
                "**D-1.** *Superseded by* D-2\n\n"
                "**D-2. Still active**\n*Stated by* [run]\n\n"
                "**D-3. Unrelated active choice**\n*Stated by* [run]\n"
            ),
        })
        current = self.make({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": (
                "**D-1.** *Superseded by* D-3\n\n"
                "**D-2. Still active**\n*Stated by* [run]\n\n"
                "**D-3. Unrelated active choice**\n*Stated by* [run]\n"
            ),
        })
        findings = decision_lifetime_findings(current, baseline, review=True)
        self.assert_rule(findings, "lifetime.successor-changed", 1)
        self.assertEqual("D-1", findings[0].subject)
        self.assertEqual(1, len(findings), [str(finding) for finding in findings])

    def test_dependent_pointer_migration_still_requires_a_fresh_successor(self) -> None:
        header = "## Structure\n```\n  run    meaning\n```\n"
        baseline = self.baseline({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": (
                "**D-1.** *Superseded by* D-2\n\n"
                "**D-2.** *Superseded by* D-3\n\n"
                "**D-3. Already committed**\n*Stated by* [run]\n"
            ),
        })
        current = self.make({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": (
                "**D-1.** *Superseded by* D-3\n\n"
                "**D-2.** *Superseded by* D-3\n\n"
                "**D-3. Already committed**\n*Stated by* [run]\n"
            ),
        })
        findings = decision_lifetime_findings(current, baseline, review=True)
        self.assert_rule(findings, "lifetime.successor-stale", 1)
        self.assertEqual("D-1", findings[0].subject)
        self.assertEqual(1, len(findings), [str(finding) for finding in findings])

    def test_pointer_only_move_resolves_in_declared_parent_workspace(self) -> None:
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.write(
            "workspace.decisions.md",
            "**WS-3. Moved choice**\n*Formerly* D-1\n*Because* The choice moved.\n",
        )
        package = self.make(
            {
                "mod/mod.h.md": "## Structure\n```\n  run  meaning\n```\n",
                "mod/mod.decisions.md": "**D-1.** *Superseded by* WS-3\n",
            },
            root=self.root / "member",
            pid="pkg:quoll/example.com/member",
        )
        self.assertEqual([], [str(finding) for finding in decision_lifetime_findings(package)])
        self.assertEqual([], [str(finding) for finding in self.findings(package)])

        self.write(
            "mod/mod.decisions.md",
            "**D-1. Full historical entry**\n*Stated by* [run]\n*Superseded by* WS-3\n",
            root=package.root,
        )
        full_entry = load_package(package.root)
        self.assert_rule(
            decision_lifetime_findings(full_entry),
            "lifetime.successor-missing",
            1,
        )

    def test_cross_module_pointer_chains_check_cycles_and_unique_ids(self) -> None:
        files = {
            "two/two.h.md": "## Structure\n```\n  run  meaning\n```\n",
            "one/one.decisions.md": "**D-1.** *Superseded by* D-2\n",
            "two/two.decisions.md": "**D-2. Current**\n*Stated by* [run]\n",
        }
        package = self.make(files, modules=("one", "two"))
        self.assertEqual([], [str(finding) for finding in decision_lifetime_findings(package)])

        self.write(
            "two/two.decisions.md",
            "**D-2.** *Superseded by* D-1\n",
        )
        cyclic = load_package(self.root)
        findings = decision_lifetime_findings(cyclic)
        self.assert_rule(findings, "lifetime.successor-cycle", 2)
        self.assertNotIn("lifetime.successor-missing", {finding.rule for finding in findings})

    def test_cross_module_dependent_migration_remains_guarded(self) -> None:
        baseline_root = tempfile.TemporaryDirectory()
        self.extra_temporaries.append(baseline_root)
        old_files = {
            "two/two.h.md": "## Structure\n```\n  run  meaning\n```\n",
            "one/one.decisions.md": "**D-1.** *Superseded by* D-2\n",
            "two/two.decisions.md": (
                "**D-2.** *Superseded by* D-3\n\n"
                "**D-3. Former endpoint**\n*Stated by* [run]\n"
            ),
        }
        baseline = self.make(
            old_files,
            modules=("one", "two"),
            root=Path(baseline_root.name),
        )
        current = self.make(
            {
                "two/two.h.md": old_files["two/two.h.md"],
                "one/one.decisions.md": "**D-1.** *Superseded by* D-4\n",
                "two/two.decisions.md": (
                    "**D-2.** *Superseded by* D-4\n\n"
                    "**D-3.** *Superseded by* D-4\n\n"
                    "**D-4. Active endpoint**\n*Stated by* [run]\n"
                ),
            },
            modules=("one", "two"),
        )
        self.assertEqual(
            [],
            [str(finding) for finding in decision_lifetime_findings(current, baseline, review=True)],
        )

        arbitrary_baseline = self.make(
            {
                "two/two.h.md": old_files["two/two.h.md"],
                "one/one.decisions.md": "**D-1.** *Superseded by* D-2\n",
                "two/two.decisions.md": (
                    "**D-2. Still active**\n*Stated by* [run]\n\n"
                    "**D-4. Unrelated active choice**\n*Stated by* [run]\n"
                ),
            },
            modules=("one", "two"),
            root=Path(baseline_root.name),
        )
        self.write(
            "two/two.decisions.md",
            (
                "**D-2. Still active**\n*Stated by* [run]\n\n"
                "**D-4. Unrelated active choice**\n*Stated by* [run]\n"
            ),
        )
        arbitrary = load_package(self.root)
        findings = decision_lifetime_findings(arbitrary, arbitrary_baseline, review=True)
        self.assert_rule(findings, "lifetime.successor-changed", 1)
        self.assertEqual("D-1", findings[0].subject)

    def test_twelve_one_line_stub_migrations_keep_ids_but_true_withdrawal_is_reported(self) -> None:
        old_entries: list[str] = []
        new_entries: list[str] = []
        for number in range(1, 13):
            successor = 100 + number
            old_entries.extend((
                (
                    f"**D-{number}. Old choice**\n"
                    "*Stated by* [missing]\n"
                    f"*Superseded by* D-{successor}"
                ),
                f"**D-{successor}. Current choice**\n*Stated by* [run]",
            ))
            new_entries.extend((
                f"**D-{number}.** *Superseded by* D-{successor}",
                f"**D-{successor}. Current choice**\n*Stated by* [run]",
            ))
        header = "## Structure\n```\n  run    meaning\n```\n"
        baseline = self.baseline({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": (
                "\n\n".join(old_entries)
                + "\n\n**D-99. Actually withdrawn**\n*Stated by* [run]\n"
            ),
        })
        current = self.make({
            "mod/mod.h.md": header,
            "mod/mod.decisions.md": "\n\n".join(new_entries) + "\n",
        })
        decisions = current.module_map["mod"].decisions.decisions
        self.assertEqual(12, len([decision for decision in decisions if not decision.active and decision.id != "D-99"]))
        findings = decision_lifetime_findings(current, baseline, review=True)
        self.assert_rule(findings, "lifetime.withdrawn", 1)
        self.assertEqual("D-99", findings[0].subject)
        self.assertEqual(1, len(findings), [str(finding) for finding in findings])

    def test_titleless_stubs_still_check_missing_cycles_and_duplicate_ids(self) -> None:
        package = self.make({
            "mod/mod.h.md": "## Structure\n```\n  run    meaning\n```\n",
            "mod/mod.decisions.md": (
                "**D-1.**\n*Superseded by* D-2\n\n"
                "**D-2.**\n*Superseded by* D-1\n\n"
                "**D-3.**\n*Superseded by* D-99\n\n"
                "**D-4.**\n*Superseded by* D-5\n\n"
                "**D-4.**\n*Superseded by* D-5\n\n"
                "**D-5. Current**\n*Stated by* [run]\n"
            ),
        })
        self.assertEqual([], [str(finding) for finding in self.findings(package)])
        findings = decision_lifetime_findings(package)
        self.assert_rule(findings, "lifetime.successor-missing", 1)
        self.assert_rule(findings, "lifetime.successor-cycle", 2)
        self.assert_rule(findings, "lifetime.duplicate-id", 1)
        self.assertNotIn("lifetime.successor-stale", {finding.rule for finding in findings})

    def test_titleless_stub_successor_must_be_fresh(self) -> None:
        files = {
            "mod/mod.h.md": "## Structure\n```\n  run    meaning\n```\n",
            "mod/mod.decisions.md": "**D-2. Current**\n*Stated by* [run]\n",
        }
        baseline = self.baseline(files)
        current = self.make({
            **files,
            "mod/mod.decisions.md": (
                "**D-1.**\n*Superseded by* D-2\n\n"
                "**D-2. Current**\n*Stated by* [run]\n"
            ),
        })
        findings = decision_lifetime_findings(current, baseline)
        self.assert_rule(findings, "lifetime.successor-stale", 1)
        self.assertEqual("D-1", next(finding for finding in findings if finding.rule == "lifetime.successor-stale").subject)


class ProseCase(PackageFixtures, unittest.TestCase):
    def test_language_reviews_all_seven_former_core_words_as_ordinary_bare_words(self) -> None:
        package = self.make(
            {
                "language.h.md": (
                    "A workspace package module interface item decision uses.\n"
                    "## Structure\n```\n"
                    "  workspace    one\n  package      one\n  module       one\n"
                    "  interface    one\n  item         one\n  decision     one\n  uses         relation\n"
                    "```\n"
                ),
            },
            modules=(),
            pid="pkg:quoll/example.com/language",
        )
        findings = [
            finding
            for finding in prose_findings(package, review=True)
            if finding.rule == "prose.bare-word"
        ]
        self.assertEqual(
            ["decision", "interface", "item", "module", "package", "uses", "workspace"],
            [finding.subject for finding in findings],
            [str(finding) for finding in findings],
        )

    def test_workspace_decisions_scan_member_public_item_vocabulary(self) -> None:
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.write(
            "workspace.decisions.md",
            "**W-1. Member vocabulary**\n*Because* The public surface may run a module.\n",
        )
        self.make(
            {
                "member.h.md": '+++\n[exposes]\ndefault = "default"\napi = "api"\n+++\n## Structure\n```\n  run    public\n  module    core word\n```\n',
                "api.h.md": "## Structure\n```\n  public surface    public\n```\n",
            },
            modules=(),
            root=self.root / "member",
            pid="pkg:quoll/example.com/member",
        )
        findings = prose_findings(load_package(self.root), review=True)
        compounds = [finding for finding in findings if finding.rule == "prose.bare-compound"]
        words = [finding for finding in findings if finding.rule == "prose.bare-word"]
        self.assertEqual(["public surface"], [finding.subject for finding in compounds])
        self.assertEqual(["member.api.public surface"], [finding.detail.split("write [", 1)[1].split("]", 1)[0] for finding in compounds])
        self.assertEqual(["module", "run"], [finding.subject for finding in words])
        self.assertEqual(
            ["member.default.module", "member.default.run"],
            [finding.detail.split("write [", 1)[1].split("]", 1)[0] for finding in words],
        )
        self.assertTrue(all(finding.path == "workspace.decisions.md" for finding in findings))

    def test_workspace_vocabulary_follows_nested_exposures_to_default_items(self) -> None:
        self.write(
            "workspace.quoll.toml",
            'packages = ["member"]\nedition = "0.6.0"\ndescription = "Workspace."\n',
        )
        self.write(
            "workspace.decisions.md",
            "**W-1. Nested vocabulary**\n*Because* The nested_single and nested compound are public.\n",
        )
        self.make(
            {
                "member.h.md": '+++\n[exposes]\napi = "branch.api"\n+++\nMember.\n',
                "branch/branch.h.md": '+++\n[exposes]\napi = "deep.default"\n+++\nBranch.\n',
                "branch/deep/deep.h.md": "## Structure\n```\n  nested_single    public\n  nested compound    public\n```\n",
            },
            modules=("branch", "branch/deep"),
            root=self.root / "member",
            pid="pkg:quoll/example.com/member",
        )
        findings = [
            finding
            for finding in prose_findings(load_package(self.root), review=True)
            if finding.path == "workspace.decisions.md"
        ]
        compounds = [finding for finding in findings if finding.rule == "prose.bare-compound"]
        words = [finding for finding in findings if finding.rule == "prose.bare-word"]
        self.assertEqual(["nested compound"], [finding.subject for finding in compounds])
        self.assertEqual(["nested_single"], [finding.subject for finding in words])
        self.assertIn("[member.api.nested compound]", compounds[0].detail)
        self.assertIn("[member.api.nested_single]", words[0].detail)

    def test_abstract_compounds_do_not_create_reverse_dependency_suggestions(self) -> None:
        package = self.make(
            {
                "demo.body.md": (
                    "## Rules\n```\n"
                    "  model alone    [model.module] providing [model.default] [model.uses] no [model.interface]\n"
                    "```\n"
                ),
                "model/model.h.md": (
                    "A content hash identifies content, while a public surface describes visibility.\n"
                    "## Structure\n```\n"
                    "  item    meaning\n"
                    "  module    unit\n"
                    "  uses    consumption\n"
                    "  interface    contract\n"
                    "```\n"
                ),
                "model/model.decisions.md": (
                    "**M-1. Abstract concepts**\n"
                    "*Stated by* [item]\n"
                    "*Because* A content hash and a public surface remain abstract here.\n"
                ),
                "layout/layout.h.md": (
                    "## Structure\n```\n"
                    "  content hash    syntax identity\n"
                    "```\n"
                ),
                "source/source.h.md": (
                    "## Structure\n```\n"
                    "  public surface    source identity\n"
                    "```\n"
                ),
            },
            modules=("model", "layout", "source"),
        )
        findings = [
            finding
            for finding in prose_findings(package)
            if finding.rule == "prose.bare-compound" and finding.path.startswith("model/")
        ]
        self.assertEqual([], [str(finding) for finding in findings])

    def test_genuine_local_bare_compound_is_still_an_error(self) -> None:
        package = self.make({
            "mod/mod.h.md": (
                "A content hash identifies content.\n"
                "## Structure\n```\n  content hash    identity\n```\n"
            ),
        })
        findings = [finding for finding in prose_findings(package) if finding.rule == "prose.bare-compound"]
        self.assertEqual(1, len(findings), [str(finding) for finding in findings])
        self.assertEqual("mod/mod.h.md", findings[0].path)
        self.assertIn("[content hash]", findings[0].detail)

    def test_foreign_bare_compound_uses_an_allowed_qualified_direction(self) -> None:
        package = self.make(
            {
                "model/model.h.md": (
                    "## Structure\n```\n  content hash    identity\n  item    meaning\n```\n"
                ),
                "layout/layout.h.md": (
                    "A content hash identifies syntax.\n"
                    "## Structure\n```\n  model use    [model.item]\n```\n"
                ),
            },
            modules=("model", "layout"),
        )
        findings = [
            finding
            for finding in prose_findings(package)
            if finding.rule == "prose.bare-compound" and finding.path == "layout/layout.h.md"
        ]
        self.assertEqual(1, len(findings), [str(finding) for finding in findings])
        self.assertIn("[model.content hash]", findings[0].detail)


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
