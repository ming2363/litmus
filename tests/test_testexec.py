import tempfile
import unittest
from pathlib import Path

from litmus.testexec import CompileError, TestTimeoutError, compile_project, run_tests


class TestTestexec(unittest.TestCase):
    def test_python_runner_pass_fail_timeout_and_shadowing_immunity(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "tests").mkdir()
            # 故意在工作目录放置同名 json.py，验证 -I 启动不会遮蔽标准库
            (proj / "json.py").write_text("raise RuntimeError('shadowed!')\n", encoding="utf-8")
            (proj / "calc.py").write_text(
                "def add(a, b):\n    return a + b\n",
                encoding="utf-8",
            )
            (proj / "tests" / "test_calc.py").write_text(
                "import time\n"
                "import unittest\n"
                "from calc import add\n\n"
                "class TestCalc(unittest.TestCase):\n"
                "    def test_pass(self):\n"
                "        print('noisy stdout should not break json')\n"
                "        self.assertEqual(add(1, 2), 3)\n"
                "    def test_fail(self):\n"
                "        self.assertEqual(add(1, 2), 9)\n"
                "    def test_slow(self):\n"
                "        try:\n"
                "            time.sleep(2.0)\n"
                "        except Exception:\n"
                "            pass\n"
                "        time.sleep(2.0)\n",
                encoding="utf-8",
            )

            compile_project("python", proj)
            outcomes = run_tests(
                "python",
                proj,
                test_ids=[
                    "tests.test_calc.TestCalc.test_pass",
                    "tests.test_calc.TestCalc.test_fail",
                    "tests.test_calc.TestCalc.test_slow",
                ],
                timeouts={"tests.test_calc.TestCalc.test_slow": 0.2},
            )
            self.assertEqual(outcomes["tests.test_calc.TestCalc.test_pass"].status, "pass")
            self.assertEqual(outcomes["tests.test_calc.TestCalc.test_fail"].status, "fail")
            self.assertEqual(outcomes["tests.test_calc.TestCalc.test_slow"].status, "timeout")

    def test_python_compile_error_and_overall_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "bad.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
            with self.assertRaises(CompileError):
                run_tests("python", proj)

        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "test_hang.py").write_text(
                "import time, unittest\n"
                "class TestHang(unittest.TestCase):\n"
                "    def test_hang(self):\n"
                "        time.sleep(5.0)\n",
                encoding="utf-8",
            )
            with self.assertRaises(TestTimeoutError):
                run_tests("python", proj, overall_timeout=0.4)

    def test_java_runner_pass_fail_timeout_and_compile_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "Calc.java").write_text(
                "public class Calc {\n"
                "    public static int add(int a, int b) { return a + b; }\n"
                "}\n",
                encoding="utf-8",
            )
            # 故意放入伪造运行器文件，验证运行器不会被工作目录替换
            (proj / "JavaRunner.java").write_text(
                "public class JavaRunner { public static void main(String[] a) {} }\n",
                encoding="utf-8",
            )
            (proj / "CalcTest.java").write_text(
                "public class CalcTest {\n"
                "    public void testPass() {\n"
                "        System.out.println(\"stdout noise\");\n"
                "        if (Calc.add(2, 3) != 5) throw new AssertionError(\"bad\");\n"
                "    }\n"
                "    public void testFail() {\n"
                "        throw new AssertionError(\"expected failure\");\n"
                "    }\n"
                "    public void testSlow() throws Exception {\n"
                "        Thread.sleep(3000);\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            compile_project("java", proj)
            outcomes = run_tests(
                "java",
                proj,
                test_ids=["CalcTest#testPass", "CalcTest#testFail", "CalcTest#testSlow"],
                timeouts={"CalcTest#testSlow": 0.2},
            )
            self.assertEqual(outcomes["CalcTest#testPass"].status, "pass")
            self.assertEqual(outcomes["CalcTest#testFail"].status, "fail")
            self.assertEqual(outcomes["CalcTest#testSlow"].status, "timeout")

        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "Broken.java").write_text("public class Broken { int x = ; }\n", encoding="utf-8")
            with self.assertRaises(CompileError):
                run_tests("java", proj)


if __name__ == "__main__":
    unittest.main()
