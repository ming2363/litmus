import unittest

from harbor.catalog import Catalog, load_pairs
from harbor.constraint import parse_constraint
from harbor.formatting import format_component
from harbor.selection import Dependency, resolve
from harbor.version import compare, parse_version, sort_versions


class TestPublic(unittest.TestCase):
    def test_numeric_order(self):
        self.assertLess(compare("1.9.0", "1.10.0"), 0)
        self.assertLess(compare("1.2.0", "1.2.3"), 0)
        self.assertEqual(compare("2.0.0", "2.0.0"), 0)

    def test_build_metadata_ignored(self):
        self.assertEqual(compare("1.2.3+build.1", "1.2.3+build.2"), 0)
        self.assertEqual(compare("1.2.3+001", "1.2.3"), 0)

    def test_prerelease_identifiers(self):
        self.assertLess(compare("1.0.0-alpha", "1.0.0-alpha.1"), 0)
        self.assertLess(compare("1.0.0-alpha.1", "1.0.0-alpha.beta"), 0)
        self.assertLess(compare("1.0.0-alpha.beta", "1.0.0-beta"), 0)
        self.assertLess(compare("1.0.0-beta", "1.0.0-beta.2"), 0)
        self.assertLess(compare("1.0.0-beta.2", "1.0.0-beta.11"), 0)
        self.assertLess(compare("1.0.0-beta.11", "1.0.0-rc.1"), 0)

    def test_lower_core_before_higher_prerelease(self):
        self.assertLess(compare("1.9.0", "1.10.0-rc.1"), 0)

    def test_sort_plain_versions(self):
        ordered = sort_versions(["1.10.0", "1.2.0", "1.9.0", "1.2.0+b1"])
        self.assertEqual(ordered, ["1.2.0", "1.2.0+b1", "1.9.0", "1.10.0"])

    def test_reject_invalid(self):
        for raw in ("", "1.2", "01.2.3", "1.2.3-", "1.2.3-01", "1.2.03", "v1.2.3"):
            with self.assertRaises(ValueError) as caught:
                parse_version(raw)
            self.assertIn(raw, str(caught.exception))

    def test_constraint_and_catalog_plain(self):
        rule = parse_constraint(">= 1.2.0")
        self.assertTrue(rule.matches("1.2.0"))
        self.assertTrue(rule.matches("1.10.0"))
        self.assertFalse(rule.matches("1.1.9"))
        catalog = load_pairs([("gate", "1.2.0"), ("gate", "1.10.0"), ("gate", "1.9.0")])
        self.assertEqual(catalog.latest("gate"), "1.10.0")
        self.assertEqual(catalog.satisfying("gate", "<1.10.0"), ["1.2.0", "1.9.0"])

    def test_resolve_plain_latest(self):
        catalog = load_pairs([("gate", "1.2.0"), ("gate", "1.4.0"), ("gate", "1.3.0")])
        picked = resolve(catalog, [Dependency("gate", ">=1.3.0")])
        self.assertEqual(picked, {"gate": "1.4.0"})

    def test_format_release_line(self):
        catalog = Catalog()
        catalog.add("gate", "1.2.0+build.7")
        text = format_component(catalog, "gate")
        self.assertIn("1.2.0", text)
        self.assertIn("rel", text)

    def test_release_vs_prerelease(self):
        self.assertLess(compare("1.10.0-rc.1", "1.10.0"), 0)
        self.assertGreater(compare("1.0.0", "1.0.0-alpha"), 0)
        self.assertLess(compare("2.0.0-rc.1+build.4", "2.0.0+build.9"), 0)
