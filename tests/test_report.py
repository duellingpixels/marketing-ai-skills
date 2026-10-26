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

    def test_margin_table_shows_cost_inputs_percentage_and_definitions(self):
        report=self.report()
        report['products'][0].update(unit_cost='15.00',other_unit_cost='2.00',cost_basis_confirmed=True)
        text=render_markdown(report)
        self.assertIn('| Unit cost | Other unit costs | Unit Margin | Unit Margin/Sale Price (%) |',text)
        self.assertIn('| 20.00 | 15.00 | 2.00 | 3.00 | 15.00% |',text)
        self.assertIn('Unit Margin = planned selling price − unit cost − other unit costs.',text)
        self.assertIn('Unit Margin/Sale Price (%) = Unit Margin ÷ planned selling price × 100.',text)
        self.assertIn('All prices and costs are per unit in AUD.',text)
        self.assertNotIn('Contribution per unit',text)
        self.assertNotIn('Contribution %',text)

    def test_missing_costs_are_distinct_from_known_zero_cost(self):
        report=self.report()
        report['products'][0].update(unit_cost=None,other_unit_cost='0.00',
                                    contribution_per_unit=None,contribution_percent=None)
        text=render_markdown(report)
        self.assertIn('| 20.00 | Not supplied | 0.00 | Not calculated | Not calculated |',text)

    def test_zero_price_has_no_percentage(self):
        report=self.report()
        report['products'][0].update(planned_price='0.00',unit_cost='2.00',other_unit_cost='0.00',
                                    contribution_per_unit='-2.00',contribution_percent=None)
        text=render_markdown(report)
        self.assertIn('| 0.00 | 2.00 | 0.00 | -2.00 | Not calculated |',text)
