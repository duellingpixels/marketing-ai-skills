import unittest
from marketing_ai_skills.black_friday.report import render_markdown


class ReportTests(unittest.TestCase):
    def report(self, name='Ceramic cup blue'):
        return dict(platform='woocommerce',as_of='2026-11-02',currency='AUD',
                    summary='Action list',counts={'blocker':1,'review':0,'unknown':0},sources={},
                    products=[dict(sku='CUP-BLU',name=name,planned_price='20.00',stock=0,
                                   contribution_per_unit='3.00',contribution_percent='15.00')],
                    findings=[dict(priority='blocker',sku='CUP-BLU',title='No available stock',
                                   evidence='0 units',action='Review availability')],assumptions=[])

    def test_product_name_and_sku_appear_in_table_and_finding(self):
        text=render_markdown(self.report())
        self.assertIn('| Product name | SKU |',text)
        self.assertIn('| Ceramic cup blue | CUP-BLU | 20.00 |',text)
        self.assertIn('### No available stock — Ceramic cup blue [CUP-BLU]',text)

    def test_missing_name_keeps_sku_and_explains_name_is_unavailable(self):
        for name in [None,'']:
            with self.subTest(name=name):
                text=render_markdown(self.report(name))
                self.assertIn('| Name unavailable | CUP-BLU |',text)
                self.assertIn('Name unavailable [CUP-BLU]',text)

    def test_product_names_are_escaped_in_table_and_headings(self):
        text=render_markdown(self.report('<b>Blue</b> | *Cup*\nName'))
        self.assertNotIn('<b>',text)
        self.assertIn('&lt;b&gt;Blue&lt;/b&gt; \\| \\*Cup\\* Name',text)
