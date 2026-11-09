import json
import tempfile
import unittest
from pathlib import Path

from litmus.tasks import (
    TaskValidationError,
    get_task_order,
    load_all_tasks,
    load_manifest,
    load_task,
)


def _create_sample_task(
    root: Path,
    task_id: str,
    grader: str = "tests",
    lang: str = "python",
    extra_fields=None,
) -> None:
    tdir = root / "tasks" / task_id
    (tdir / "repo").mkdir(parents=True, exist_ok=True)
    (tdir / "prompt.md").write_bytes(("# {}\n题面\n".format(task_id)).encode("utf-8"))
    meta = {
        "id": task_id,
        "dimension": "bug",
        "lang": lang,
        "difficulty": "easy",
        "title": "示例题",
        "ref_minutes": 5,
        "grader": grader,
    }
    if grader == "tests":
        meta["allowed_paths"] = ["src/*.py"]
    if grader in ("tool_call", "read_code", "review"):
        meta["answer_file"] = "answer.json" if grader != "review" else "review.json"
    if extra_fields:
        meta.update(extra_fields)
    (tdir / "task.json").write_bytes((json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


class TestTasks(unittest.TestCase):
    def test_load_all_tasks_success_and_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_sample_task(root, "bug-py-01", grader="tests", lang="python")
            _create_sample_task(root, "tool-none-01", grader="tool_call", lang="none")
            (root / "tasks" / "manifest.json").write_bytes((json.dumps({"version": 1, "order": ["bug-py-01", "tool-none-01"], "quick": ["tool-none-01"]})).encode("utf-8"))
            manifest, tasks = load_all_tasks(root)
            self.assertEqual(manifest.order, ("bug-py-01", "tool-none-01"))
            self.assertEqual(manifest.quick, ("tool-none-01",))
            self.assertEqual(get_task_order("full", manifest), ["bug-py-01", "tool-none-01"])
            self.assertEqual(get_task_order("quick", manifest), ["tool-none-01"])
            self.assertEqual(tasks["tool-none-01"].answer_file, "answer.json")

    def test_validation_rejects_duplicates_subset_mismatch_and_dir_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_sample_task(root, "bug-py-01")

            # 1) 重复题号
            (root / "tasks" / "manifest.json").write_text(
                json.dumps({"version": 1, "order": ["bug-py-01", "bug-py-01"], "quick": []}),
                encoding="utf-8",
            )
            with self.assertRaises(TaskValidationError):
                load_manifest(root)

            # 2) quick 不是 order 子集
            (root / "tasks" / "manifest.json").write_text(
                json.dumps({"version": 1, "order": ["bug-py-01"], "quick": ["missing-01"]}),
                encoding="utf-8",
            )
            with self.assertRaises(TaskValidationError):
                load_manifest(root)

            # 3) 存在未在 manifest 中的多余目录
            _create_sample_task(root, "orphan-py-02")
            (root / "tasks" / "manifest.json").write_text(
                json.dumps({"version": 1, "order": ["bug-py-01"], "quick": ["bug-py-01"]}),
                encoding="utf-8",
            )
            with self.assertRaises(TaskValidationError):
                load_all_tasks(root)

    def test_task_json_field_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_sample_task(root, "bad-01", extra_fields={"id": "other-id"})
            with self.assertRaises(TaskValidationError):
                load_task("bad-01", root)

            _create_sample_task(root, "bad-02", extra_fields={"grader": "unknown"})
            with self.assertRaises(TaskValidationError):
                load_task("bad-02", root)

            _create_sample_task(root, "bad-03", grader="tests", extra_fields={"allowed_paths": []})
            with self.assertRaises(TaskValidationError):
                load_task("bad-03", root)


if __name__ == "__main__":
    unittest.main()
