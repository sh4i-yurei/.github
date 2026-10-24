import re
import unittest
from pathlib import Path

from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / ".github" / "ISSUE_TEMPLATE"
YAML_READER = YAML(typ="safe")


def read_file(path):
    assert path.is_file(), f"required template is missing: {path.relative_to(ROOT)}"
    return path.read_text()


def read_yaml(path):
    return YAML_READER.load(read_file(path))


def prompts(form):
    return {item["attributes"]["label"]: item for item in form["body"]}


class DefaultTemplatesTest(unittest.TestCase):
    def test_four_forms_and_no_blank_issue(self):
        self.assertEqual(
            {path.name for path in FORMS.glob("*")},
            {"config.yml", "bug.yml", "feature.yml", "chore.yml", "docs.yml"},
        )
        self.assertEqual(read_yaml(FORMS / "config.yml")["blank_issues_enabled"], False)
        self.assertEqual(
            {
                read_yaml(path)["name"]
                for path in FORMS.glob("*.yml")
                if path.name != "config.yml"
            },
            {"Bug", "Feature", "Chore", "Docs"},
        )

    def test_each_form_sets_one_correct_label(self):
        for name, label in {
            "bug": "type:fix",
            "feature": "type:feature",
            "chore": "type:chore",
            "docs": "type:docs",
        }.items():
            with self.subTest(name=name):
                self.assertEqual(read_yaml(FORMS / f"{name}.yml")["labels"], [label])

    def test_bug_collects_reproducible_evidence(self):
        fields = prompts(read_yaml(FORMS / "bug.yml"))
        self.assertEqual(
            set(fields),
            {
                "What happened",
                "What I expected",
                "How to reproduce",
                "Where",
                "Done when",
            },
        )
        self.assertIn(
            "real error or output", fields["What happened"]["attributes"]["description"]
        )
        self.assertIn("commit", fields["Where"]["attributes"]["description"])
        self.assertIn(
            "project or environment", fields["Where"]["attributes"]["description"]
        )
        self.assertTrue(fields["What happened"]["validations"]["required"])
        self.assertTrue(fields["Done when"]["validations"]["required"])

    def test_planned_work_has_project_step_reason_change_and_check(self):
        for name in ("feature", "chore", "docs"):
            with self.subTest(name=name):
                fields = prompts(read_yaml(FORMS / f"{name}.yml"))
                self.assertEqual(
                    set(fields),
                    {"Project, step, and reason", "What changes", "Done when"},
                )
                self.assertIn(
                    "project",
                    fields["Project, step, and reason"]["attributes"]["description"],
                )
                self.assertIn(
                    "step",
                    fields["Project, step, and reason"]["attributes"]["description"],
                )
                self.assertIn(
                    "why",
                    fields["Project, step, and reason"]["attributes"]["description"],
                )
                self.assertTrue(fields["Done when"]["validations"]["required"])

    def test_pull_request_template_keeps_every_section(self):
        template = read_file(ROOT / ".github" / "pull_request_template.md")
        self.assertIn("Closes #", template)
        self.assertIn("intent statement", template)
        self.assertEqual(
            re.findall(r"^## (.+)$", template, re.MULTILINE),
            ["Summary", "How it was checked", "Risk", "Rollback"],
        )

    def test_public_text_is_generic_and_readme_states_boundary(self):
        files = [
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and not {".git", "__pycache__"}.intersection(path.relative_to(ROOT).parts)
        ]
        forbidden = (
            r"(?i)\b("
            + "|".join(("an" + "sible", "play" + "book", "ro" + "le", "mach" + "ine"))
            + r")\b"
        )
        for path in files:
            with self.subTest(path=path):
                self.assertNotRegex(read_file(path), forbidden)
        readme = (ROOT / "README.md").read_text().lower()
        self.assertIn("default issue forms", readme)
        self.assertIn("private repository", readme)
        self.assertIn("estate", readme)

    def test_ci_checks_branches_and_pull_requests(self):
        workflow = read_yaml(ROOT / ".github" / "workflows" / "validate.yml")
        self.assertIn("push", workflow["on"])
        self.assertIn("pull_request", workflow["on"])
        if isinstance(workflow["on"], dict):
            self.assertNotIn("branches", workflow["on"].get("push") or {})


if __name__ == "__main__":
    unittest.main()
