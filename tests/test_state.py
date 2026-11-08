import multiprocessing
import re
import tempfile
import unittest
from pathlib import Path

from litmus.state import (
    create_run,
    has_active_run,
    load_active_state,
    load_state,
    parse_iso,
    save_state,
    state_lock,
)


def _concurrent_worker(root_str: str, run_dir_str: str, worker_id: int, iterations: int) -> None:
    root = Path(root_str)
    run_dir = Path(run_dir_str)
    for idx in range(iterations):
        with state_lock(root):
            state = load_state(run_dir)
            key = "t-{}-{}".format(worker_id, idx)
            state["results"][key] = {
                "status": "pass",
                "reasons": [],
                "merge_veto": False,
                "elapsed_s": 1.0,
                "seq": len(state["results"]) + 1,
                "submitted_at": "2026-11-08T10:00:00+08:00",
                "extra": {},
            }
            save_state(run_dir, state)


class TestState(unittest.TestCase):
    def test_create_load_save_and_active_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir, state = create_run("quick", "abc1234", ["bug-py-01", "read-py-01"], root=root)
            self.assertRegex(state["run_dir"], r"^\d{8}-\d{6}-[0-9a-f]{4}$")
            self.assertRegex(state["marker"], r"^LITMUS-RUN-[0-9a-f]{6}$")
            self.assertEqual(state["status"], "active")
            self.assertEqual(has_active_run(root), state["run_dir"])

            loaded_pair = load_active_state(root)
            self.assertIsNotNone(loaded_pair)
            loaded_dir, loaded_state = loaded_pair
            self.assertEqual(loaded_dir, run_dir)
            self.assertEqual(loaded_state["head"], "abc1234")

            loaded_state["status"] = "done"
            save_state(run_dir, loaded_state)
            self.assertIsNone(has_active_run(root))

    def test_parse_iso_supports_z_suffix_on_py39(self):
        dt = parse_iso("2026-11-08T12:30:45Z")
        self.assertIsNotNone(dt.tzinfo)
        dt2 = parse_iso("2026-11-08T20:30:45+08:00")
        self.assertEqual(dt.timestamp(), dt2.timestamp())

    def test_concurrent_processes_do_not_corrupt_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir, _ = create_run("full", "deadbeef", [], root=root)
            ctx = multiprocessing.get_context("spawn")
            p1 = ctx.Process(target=_concurrent_worker, args=(str(root), str(run_dir), 1, 20))
            p2 = ctx.Process(target=_concurrent_worker, args=(str(root), str(run_dir), 2, 20))
            p1.start()
            p2.start()
            p1.join(timeout=30)
            p2.join(timeout=30)
            self.assertEqual(p1.exitcode, 0)
            self.assertEqual(p2.exitcode, 0)

            final_state = load_state(run_dir)
            self.assertEqual(len(final_state["results"]), 40)


if __name__ == "__main__":
    unittest.main()
