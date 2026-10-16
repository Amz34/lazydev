import unittest
from lazydev.analyzer import analyze_source
from lazydev.detector import RedundancyDetector
from lazydev.pruner import prune_whitespace_and_blank_lines, simplify_code, strip_inline_comments


class TestAnalyzer(unittest.TestCase):
    def test_basic_metrics(self):
        code = '''
def hello(name):
    # Say hello
    if name:
        return f"Hello, {name}!"
    return "Hello, World!"
'''
        res = analyze_source(code)
        self.assertEqual(res["functions"], 1)
        self.assertEqual(res["classes"], 0)
        self.assertEqual(res["cyclomatic_complexity"], 2)
        self.assertGreater(res["sloc"], 0)

    def test_unused_variables(self):
        code = '''
def calculate():
    unused_var = 42
    result = 100
    return result
'''
        res = analyze_source(code)
        self.assertIn("unused_var", res["unused_variables"])
        self.assertNotIn("result", res["unused_variables"])


class TestDetector(unittest.TestCase):
    def test_singleton_detection(self):
        code = '''
class AppConfig:
    _instance = None
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AppConfig()
        return cls._instance
'''
        det = RedundancyDetector(code)
        findings = det.run()
        patterns = [f["pattern"] for f in findings]
        self.assertIn("singleton", patterns)

    def test_swallowed_exception(self):
        code = '''
try:
    int("invalid")
except Exception:
    pass
'''
        det = RedundancyDetector(code)
        findings = det.run()
        patterns = [f["pattern"] for f in findings]
        self.assertIn("swallowed_exception", patterns)

    def test_trivial_passthrough(self):
        code = '''
def helper(x):
    return x * 2

def proxy(x):
    return helper(x)
'''
        det = RedundancyDetector(code)
        findings = det.run()
        patterns = [f["pattern"] for f in findings]
        self.assertIn("trivial_passthrough", patterns)


class TestPruner(unittest.TestCase):
    def test_prune_whitespace(self):
        text = "line 1   \n\n\n\nline 2"
        pruned = prune_whitespace_and_blank_lines(text, max_consecutive_blanks=1)
        self.assertEqual(pruned, "line 1\n\nline 2")

    def test_strip_comments(self):
        code = "# Temporary comment\na = 1\n# Another comment\nb = 2\n"
        pruned = strip_inline_comments(code)
        self.assertEqual(pruned, "a = 1\nb = 2\n")

    def test_simplify_code(self):
        code = "# Header comment\n\n\nx = 10   \n\n\n# Inline note\ny = 20\n"
        res = simplify_code(code)
        self.assertIn("x = 10", res)
        self.assertIn("y = 20", res)
        self.assertNotIn("# Inline note", res)


if __name__ == "__main__":
    unittest.main()
