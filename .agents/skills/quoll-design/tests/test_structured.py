from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import textwrap
import unittest


TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR.parent / "scripts"))

from quollcheck import (  # noqa: E402
    Decision,
    FileRecord,
    Finding,
    content_hash,
    extract_refs,
    hash_directory,
    load_package,
    parse_locator,
    parse_selector,
    structured_findings,
    validate_structured,
)


PID = "pkg:quoll/example.com/demo"
VALID_HASH = "1220" + "0" * 64
VALID_COMMIT = "a" * 40
VALID_DEV = f"{PID}@v0.0.0-20240102030405-abcdef123456"


class PackageFixtures:
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def current(
        self,
        *,
        dependencies: list[str] | None = None,
        lock: str = "dependencies = []\n",
        modules: str = 'modules = ["mod"]\n',
    ) -> None:
        dependency_text = ", ".join(repr(item).replace("'", '"') for item in (dependencies or []))
        self.write(
            "package.quoll.toml",
            f'id = "{PID}"\nedition = "0.4.0"\ndescription = "Demo."\n'
            f"dependencies = [{dependency_text}]\n",
        )
        self.write("modules.quoll.toml", modules)
        self.write("package.lock.quoll.toml", lock)
        self.write("mod/mod.h.md", "A module.\n")


class PackageCase(PackageFixtures, unittest.TestCase):
    def test_valid_current_package_and_relationships(self) -> None:
        self.current()
        self.write(
            "mod/mod.private.h.md",
            '+++\nincludes = ["other"]\n"module lead" = true\n+++\nPrivate.\n',
        )
        self.write("mod/mod.body.md", '+++\nimplements = ["mod.item"]\n+++\nBody.\n')
        self.write("mod/mod.decisions.md", "**D1. First**\n*Stated by* [mod.item]\n")
        package = load_package(self.root)
        self.assertEqual([], [str(finding) for finding in package.findings])
        self.assertEqual(["", "mod"], [module.path for module in package.modules])
        module = package.module_map["mod"]
        self.assertEqual("mod/mod.h.md", module.header.path)
        self.assertEqual("mod/mod.private.h.md", module.private_header.path)
        self.assertEqual("mod/mod.body.md", module.body.path)
        self.assertEqual("D1", module.decisions.decisions[0].id)
        self.assertTrue(module.decisions.decisions[0].active)
        self.assertEqual("mod", module.header.module)
        self.assertEqual([], validate_structured(package))

    def test_legacy_baseline_is_not_accepted(self) -> None:
        self.write(
            "package.md",
            "---\nname: legacy\nmodules:\n  - alpha\n---\n# Legacy\n\nSee [old.item].\n",
        )
        self.write("alpha/alpha.h.md", "Legacy header.\n")
        package = load_package(self.root, baseline=True)
        self.assertIn("manifest.required", {finding.rule for finding in package.findings})
        self.assertIn("source.placement", {finding.rule for finding in package.findings})

    def test_baseline_flag_does_not_change_current_v04_rules(self) -> None:
        self.write("package.md", "---\nname: old\n---\n")
        package = load_package(self.root, baseline=True)
        self.assertIn("manifest.required", {finding.rule for finding in package.findings})

    def test_unlisted_module_source_is_discovered_and_diagnosed(self) -> None:
        self.current(modules="modules = []\n")
        (self.root / "mod/mod.h.md").unlink()
        self.write("orphan/orphan.h.md", "A [missing].\n")
        package = load_package(self.root)
        source = next(source for source in package.files if source.kind == "header")
        self.assertEqual(["orphan/orphan.h.md"], [source.path])
        self.assertEqual("orphan", source.module)
        self.assertEqual(["missing"], source.references)
        self.assertEqual(["source.placement"], [finding.rule for finding in package.findings])

    def test_malformed_toml_becomes_findings(self) -> None:
        for filename in (
            "package.quoll.toml",
            "modules.quoll.toml",
            "package.lock.quoll.toml",
        ):
            with self.subTest(filename=filename):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    for other in (
                        "package.quoll.toml",
                        "modules.quoll.toml",
                        "package.lock.quoll.toml",
                    ):
                        text = "id = [" if other == filename else (
                            'id = "pkg:quoll/example.com/x"\nedition = "0.4.0"\n'
                            'description = "x"\ndependencies = []\n'
                            if other == "package.quoll.toml"
                            else "modules = []\n" if other == "modules.quoll.toml" else "dependencies = []\n"
                        )
                        (root / other).write_text(text, encoding="utf-8")
                    package = load_package(root)
                    self.assertIn("toml.syntax", {finding.rule for finding in package.findings})

    def test_required_files_and_exact_schemas(self) -> None:
        package = load_package(self.root)
        self.assertEqual(
            {"manifest.required", "modules.required", "lock.required"},
            {finding.rule for finding in package.findings},
        )
        self.write(
            "package.quoll.toml",
            f'id = "{PID}"\nedition = 4\ndescription = "Demo"\n'
            'dependencies = "none"\nextra = true\n',
        )
        self.write("modules.quoll.toml", 'modules = ["../escape"]\nother = []\n')
        self.write("package.lock.quoll.toml", "dependencies = {}\nother = []\n")
        rules = {finding.rule for finding in load_package(self.root).findings}
        self.assertIn("manifest.keys", rules)
        self.assertIn("manifest.type", rules)
        self.assertIn("modules.path", rules)
        self.assertIn("modules.keys", rules)
        self.assertIn("lock.type", rules)
        self.assertIn("lock.keys", rules)

    def test_same_major_duplicates_and_distinct_majors(self) -> None:
        self.current(dependencies=[f"{PID}@v1.0.0", f"{PID}@v1.2.0"])
        findings = load_package(self.root).findings
        self.assertEqual(["manifest.duplicate"], [finding.rule for finding in findings])
        self.current(dependencies=[f"{PID}@v1.0.0", f"{PID}@v2.0.0"])
        self.assertEqual([], load_package(self.root).findings)

    def test_front_schema_and_view_and_decision_parsing(self) -> None:
        self.current()
        self.write(
            "mod/mod.body.md",
            textwrap.dedent(
                """\
                +++
                implements = ["api.run"]
                [aliases]
                old = "pkg:quoll/example.com/old@v1.2.3"
                +++
                Body.

                ## Structure

                ```
                  impl [api.run]:
                  ensures:
                    first    joined
                             statement
                    second   next statement
                  open:
                    third    independent
                ```
                """
            ),
        )
        self.write(
            "mod/mod.decisions.md",
            "# Decisions\n\n**D1. Original**\n*Stated by* [first]\n*Superseded by* [D2]\n\n"
            "**D2. Replacement**\n*Stated by* [second]\n",
        )
        package = load_package(self.root)
        self.assertEqual([], [str(finding) for finding in package.findings])
        body = package.module_map["mod"].body
        self.assertEqual(["api.run"], body.front["implements"])
        first = body.items[0]
        self.assertEqual("first", first.name)
        self.assertEqual("joined statement", first.statements)
        self.assertEqual("ensures", first.direction)
        self.assertEqual("api.run", first.impl)
        self.assertEqual(13, first.line)
        self.assertEqual("open", body.items[2].direction)
        self.assertIsNone(body.items[2].impl)
        decisions = package.module_map["mod"].decisions.decisions
        self.assertEqual(["D1", "D2"], [decision.id for decision in decisions])
        self.assertEqual(["Original", "Replacement"], [decision.title for decision in decisions])
        self.assertEqual([3, 7], [decision.line for decision in decisions])
        self.assertEqual([5, 8], [decision.end_line for decision in decisions])
        self.assertEqual("[first]", decisions[0].fields["Stated by"])
        self.assertFalse(decisions[0].active)
        self.assertEqual("D2", decisions[0].successor)
        self.assertTrue(decisions[1].active)
        self.assertIsNone(decisions[1].successor)

    def test_view_ignores_tab_opening_lines(self) -> None:
        self.current()
        self.write(
            "mod/mod.h.md",
            "## Structure\n\n```\n  first    one\n  \tbad    ignored\n  second   two\n```\n",
        )
        source = load_package(self.root).module_map["mod"].header
        self.assertEqual(["first", "second"], [item.name for item in source.items])
        self.assertEqual([4, 6], [item.line for item in source.items])

    def test_tilde_view_items_references_and_lines(self) -> None:
        self.current()
        self.write(
            "mod/mod.h.md",
            "Lead [before].\n## Structure\n~~~quoll\n  first    [inside]\n~~~\nAfter [after].\n",
        )
        source = load_package(self.root).module_map["mod"].header
        self.assertEqual(["first"], [item.name for item in source.items])
        self.assertEqual(4, source.items[0].line)
        self.assertEqual(["before", "inside", "after"], source.references)
        self.assertEqual(
            [("before", 1), ("inside", 4), ("after", 6)],
            extract_refs(source, with_lines=True),
        )

    def test_longer_literal_fence_ignores_shorter_internal_fence(self) -> None:
        text = "````text\n```\n[inside]\n````\n[outside]\n"
        self.assertEqual(["outside"], extract_refs(text))
        self.assertEqual([("outside", 5)], extract_refs(text, with_lines=True))

    def test_block_command_checks_tilde_views_and_longer_fences(self) -> None:
        self.write(
            "broken.h.md",
            "## Structure\n~~~quoll\n  broken statement\n  wide    " + "x" * 100 + "\n~~~\n",
        )
        script = TEST_DIR.parent / "scripts" / "check_blocks.py"
        result = subprocess.run(
            [sys.executable, "-I", str(script), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertIn("no two spaces after the name", result.stdout)
        self.assertIn("columns", result.stdout)
        self.assertIn("problems: 2", result.stdout)

        (self.root / "broken.h.md").write_text(
            "## Structure\n~~~~quoll\n  first    valid\n~~~  not a closing fence\n  second   also valid\n~~~~\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "-I", str(script), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertIn("problems: 0", result.stdout)

    def test_malformed_front_matter_is_safe(self) -> None:
        self.current()
        self.write("mod/mod.h.md", "+++\nincludes = [\n+++\nText [still.visible].\n")
        package = load_package(self.root)
        self.assertIn("front.toml", {finding.rule for finding in package.findings})
        self.assertIn("still.visible", package.module_map["mod"].header.references)

    def test_reference_masking_and_physical_lines(self) -> None:
        text = (
            "Before [one] and `[code]`.\n\n"
            "```text\n[literal]\n```\n"
            "## Structure\n```\n  impl [target]:\n    item    [two] `or [code]`\n```\n"
            "After [three].\n"
        )
        self.assertEqual(["one", "target", "two", "three"], extract_refs(text))
        self.assertEqual(
            [("one", 1), ("target", 8), ("two", 9), ("three", 11)],
            extract_refs(text, with_lines=True),
        )
        self.assertEqual(["x"], extract_refs("Plain [x].\n- [x] literal task\n"))
        self.assertEqual(
            ["real.item"],
            extract_refs("A [label](https://example.com) and [real.item]."),
        )

    def test_real_language_structured_files(self) -> None:
        repository = TEST_DIR.parents[3]
        self.assertEqual([], [str(finding) for finding in structured_findings(repository / "language")])


class SelectorCase(unittest.TestCase):
    def test_every_selector_family(self) -> None:
        cases = {
            f"{PID}@v1": ("partial", 1, None, None),
            f"{PID}@v1.2": ("partial", 1, 2, None),
            f"{PID}@v1.2.3": ("stable", 1, 2, 3),
            f"{PID}@v1.2.3-alpha.1": ("prerelease", 1, 2, 3),
            f"{PID}@v0.0.0-20240102030405-abcdef123456": ("development", 0, 0, 0),
            f"{PID}@v1.2.3-pre.0.20240102030405-abcdef123456": ("development", 1, 2, 3),
            f"{PID}@v1.2.4-0.20240102030405-abcdef123456": ("development", 1, 2, 4),
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                selector = parse_selector(raw)
                self.assertEqual(expected, (selector.kind, selector.major, selector.minor, selector.patch))
                self.assertEqual(PID, selector.unversioned_id)
        self.assertEqual("20240102030405", parse_selector(VALID_DEV).timestamp)
        self.assertEqual("abcdef123456", parse_selector(VALID_DEV).revision)

    def test_malformed_selectors(self) -> None:
        values = [
            "quoll/example.com/demo@v1.2.3",
            "pkg:quoll/demo@v1.2.3",
            "pkg:quoll/example.com/Demo@v1.2.3",
            f"{PID}@1.2.3",
            f"{PID}@v1.2",
            f"{PID}@v1.2.3.4",
            f"{PID}@v01.2.3",
            f"{PID}@v1.2.3-alpha.01",
            f"{PID}@v0.0.0-20241302030405-abcdef123456",
            f"{PID}@v0.0.0-20240102250405-abcdef123456",
            f"{PID}@v0.0.0-20240102030405-ABCDEF123456",
            f"{PID}@v1.2.3-pre.0.20240102030405-abcdef12345",
            f"{PID}@v1.2.4-0.20240102030405-abcdef1234567",
        ]
        # v1.2 is a valid partial; use a genuinely malformed partial in its place.
        values[4] = f"{PID}@v1.2.x"
        for raw in values:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_selector(raw)

    def test_pseudo_version_timestamp_and_revision_shape_boundaries(self) -> None:
        families = (
            "v0.0.0-{stamp}-abcdef123456",
            "v1.2.3-pre.0.{stamp}-abcdef123456",
            "v1.2.4-0.{stamp}-abcdef123456",
        )
        timestamps = (
            "20240102030",
            "2024010203040",
            "202401020304051",
            "2024010203040512",
            "notnumeric",
            "2024010203040x",
            "",
        )
        for family in families:
            for timestamp in timestamps:
                raw = f"{PID}@{family.format(stamp=timestamp)}"
                with self.subTest(raw=raw), self.assertRaises(ValueError):
                    parse_selector(raw)
            for revision in ("abcdef12345", "abcdef1234567", "ABCDEF123456", "ghijkl123456", "", "abcdef.123456"):
                version = family.format(stamp="20240102030405")[:-12] + revision
                raw = f"{PID}@{version}"
                with self.subTest(raw=raw), self.assertRaises(ValueError):
                    parse_selector(raw)


class LockCase(PackageFixtures, unittest.TestCase):
    def lock_entry(self, selector: str, locator: str, tag: str | None = None) -> str:
        tag_line = f'tag = "{tag}"\n' if tag is not None else ""
        return (
            "[[dependencies]]\n"
            f'id = "{selector}"\nhash = "{VALID_HASH}"\n'
            "[[dependencies.sources]]\n"
            f'locator = "{locator}"\ncommit = "{VALID_COMMIT}"\n{tag_line}'
        )

    def test_root_nested_and_development_sources(self) -> None:
        entries = [
            self.lock_entry(f"{PID}@v1.2.3", "github.com/acme/repo@v1.2.3", "v1.2.3"),
            self.lock_entry(
                "pkg:quoll/example.com/nested@v2.0.0-rc.1",
                "https://github.com/acme/repo.git/lib/nested@v2.0.0-rc.1",
                "lib/nested/v2.0.0-rc.1",
            ),
            self.lock_entry(VALID_DEV, "http://github.com/acme/demo@abcdef123456"),
        ]
        self.current(lock="".join(entries))
        self.assertEqual([], [str(finding) for finding in load_package(self.root).findings])
        shorthand = parse_locator("github.com/acme/repo/lib/demo@main")
        self.assertEqual("github.com/acme/repo", shorthand.repository)
        self.assertEqual("lib/demo", shorthand.package_path)
        self.assertEqual("main", shorthand.request)
        explicit = parse_locator("https://example.org/a/repo.git/nested/p@v1.0.0")
        self.assertEqual("https://example.org/a/repo.git", explicit.repository)
        self.assertEqual("nested/p", explicit.package_path)
        rooted = parse_locator("https://example.org/repo.git/pkg@v1.0.0")
        self.assertEqual("https://example.org/repo.git", rooted.repository)
        self.assertEqual("pkg", rooted.package_path)

    def test_lock_hash_commit_sources_and_tags(self) -> None:
        bad_hash = "1220" + "A" * 64
        bad_commit = "a" * 39
        self.current(
            lock=(
                "[[dependencies]]\n"
                f'id = "{PID}@v1.2.3"\nhash = "{bad_hash}"\n'
                "[[dependencies.sources]]\n"
                f'locator = "github.com/acme/repo@v1"\ncommit = "{bad_commit}"\ntag = "wrong"\n'
            )
        )
        rules = {finding.rule for finding in load_package(self.root).findings}
        self.assertTrue({"lock.hash", "lock.commit", "lock.tag"} <= rules)
        self.current(lock=self.lock_entry(f"{PID}@v1", "github.com/acme/repo@v1", "v1"))
        self.assertIn("lock.selector", {finding.rule for finding in load_package(self.root).findings})
        self.current(lock=f'[[dependencies]]\nid = "{PID}@v1.2.3"\nhash = "{VALID_HASH}"\nsources = []\n')
        self.assertIn("lock.sources", {finding.rule for finding in load_package(self.root).findings})
        self.current(lock=self.lock_entry(VALID_DEV, "github.com/acme/repo@abcdef123456", "v0.0.0"))
        self.assertIn("lock.tag", {finding.rule for finding in load_package(self.root).findings})

    def test_invalid_locators(self) -> None:
        for locator in (
            "gitlab.com/acme/repo@v1.0.0",
            "github.com/acme/repo",
            "ftp://github.com/acme/repo@v1.0.0",
            "github.com/acme/repo/../demo@v1.0.0",
            "github.com/acme/repo@",
        ):
            with self.subTest(locator=locator):
                with self.assertRaises(ValueError):
                    parse_locator(locator)


class HashCase(unittest.TestCase):
    def test_fixed_independent_hash_vector_and_filename_regression(self) -> None:
        record = FileRecord("a.txt", b"hello\n")
        self.assertEqual(
            "1220c542ecfa5e23acccadeb4188670608c3b6e16f3c0adc2911d49c936e84197ac9",
            content_hash([record]),
        )
        # An omitted filename would instead hash only the bare inner digest.
        inner = hashlib.sha256(b"hello\n").hexdigest().encode("ascii")
        omitted = "1220" + hashlib.sha256(inner).hexdigest()
        self.assertNotEqual(omitted, content_hash([record]))

    def test_same_content_different_names_and_sorting(self) -> None:
        first = FileRecord("b.txt", b"same")
        second = FileRecord("a.txt", b"same")
        self.assertNotEqual(content_hash([first]), content_hash([second]))
        self.assertEqual(content_hash([first, second]), content_hash([second, first]))

    def test_raw_crlf_bytes_are_not_normalized(self) -> None:
        crlf = FileRecord("a.txt", b"one\r\ntwo\r\n")
        lf = FileRecord("a.txt", b"one\ntwo\n")
        expected_row = hashlib.sha256(b"one\r\ntwo\r\n").hexdigest().encode() + b"  a.txt\n"
        self.assertEqual("1220" + hashlib.sha256(expected_row).hexdigest(), content_hash([crlf]))
        self.assertNotEqual(content_hash([crlf]), content_hash([lf]))

    def test_simulated_mode_and_path_failures(self) -> None:
        bad_modes = [0o100755, 0o120777, 0o040755, 0o160000, 0o104755]
        for mode in bad_modes:
            with self.subTest(mode=oct(mode)), self.assertRaises(ValueError):
                content_hash([FileRecord("a", b"x", mode)])
        bad_paths = [
            "/absolute", "./a", "a/../b", "a//b", "a\\b", "a:b", "a?.txt",
            "dir./a", "dir /a", "CON", "con.txt", "nested/LPT1.md", "bad\nname",
        ]
        for path in bad_paths:
            with self.subTest(path=path), self.assertRaises(ValueError):
                content_hash([FileRecord(path, b"x")])
        with self.assertRaisesRegex(ValueError, "collision"):
            content_hash([FileRecord("Readme", b"x"), FileRecord("readme", b"y")])

    def test_directory_adaptation_dot_exclusion_and_real_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.txt").write_bytes(b"a")
            (root / ".hidden").write_bytes(b"hidden")
            (root / ".git").mkdir()
            (root / ".git" / "config").write_bytes(b"hidden")
            (root / "sub").mkdir()
            (root / "sub" / "b.txt").write_bytes(b"b")
            expected = content_hash([
                FileRecord("a.txt", b"a"),
                FileRecord("sub/b.txt", b"b"),
            ])
            self.assertEqual(expected, hash_directory(root))
            (root / "run").write_bytes(b"x")
            (root / "run").chmod(0o755)
            with self.assertRaisesRegex(ValueError, "executable"):
                hash_directory(root)
            (root / "run").unlink()
            if hasattr(os, "symlink"):
                (root / "link").symlink_to(root / "a.txt")
                with self.assertRaisesRegex(ValueError, "symlink"):
                    hash_directory(root)


class FindingCase(unittest.TestCase):
    def test_comparison_key_ignores_line_and_format_is_one_line(self) -> None:
        first = Finding("rule", "error", "a.md", "item", "detail", 2)
        second = Finding("rule", "error", "a.md", "item", "detail", 99)
        self.assertEqual(first, second)
        self.assertEqual(first.key, second.key)
        rendered = str(first)
        self.assertNotIn("\n", rendered)
        self.assertIn("a.md:2", rendered)
        self.assertIn("rule", rendered)


if __name__ == "__main__":
    unittest.main()
