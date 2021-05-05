import unittest
import json

from wb_parser.parser import WBParser


class ParsingCategoriesTestCase(unittest.TestCase):
    def setUp(self):
        with open("fixtures/test_wb_parser.json") as f:
            self._categories_cnt = json.load(f)

    def test_parse_categories(self):
        for cat in self._categories_cnt.items():
            page_url = f"https://www.wildberries.ru{cat[0]}"
            self.assertEqual(
                cat[1], len(WBParser(page_url).parse_categories()), msg=page_url
            )
