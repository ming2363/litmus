"""py_runner 的项目路径排序：项目包不能被已安装的同名第三方包遮蔽，也不能遮蔽标准库。"""

import os
import unittest

from litmus.runners.py_runner import project_path_order


class TestProjectPathOrder(unittest.TestCase):
    def test_project_goes_before_site_packages(self):
        stdlib = os.path.join(os.sep, "py", "lib", "python3.14")
        site = os.path.join(stdlib, "site-packages")
        aeosa = os.path.join(site, "aeosa")
        project = os.path.join(os.sep, "work", "repo")
        paths = [stdlib + ".zip", stdlib, os.path.join(stdlib, "lib-dynload"), site, aeosa]
        order = project_path_order(paths, project, [site])
        self.assertEqual(order.index(project), 3)
        # 标准库仍在项目之前
        self.assertLess(order.index(stdlib), order.index(project))
        self.assertLess(order.index(project), order.index(site))

    def test_dist_packages_detected_without_site_dirs(self):
        project = os.path.join(os.sep, "work", "repo")
        dist = os.path.join(os.sep, "usr", "lib", "python3", "dist-packages")
        order = project_path_order(["/usr/lib/python3.9", dist], project, [])
        self.assertEqual(order, ["/usr/lib/python3.9", project, dist])

    def test_no_site_dir_appends_and_dedups(self):
        project = os.path.join(os.sep, "work", "repo")
        order = project_path_order(["/usr/lib/python3.9", project], project, [])
        self.assertEqual(order, ["/usr/lib/python3.9", project])


if __name__ == "__main__":
    unittest.main()
