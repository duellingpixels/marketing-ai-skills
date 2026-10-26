import unittest
from datetime import date
from decimal import Decimal as D
from marketing_ai_skills.black_friday.imports import Product, Offer, InputError
from marketing_ai_skills.black_friday.checks import audit
from marketing_ai_skills.black_friday.report import render_markdown


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.products = {'A': Product('A','Tea',D('20'),True,30,True)}
        self.offers = [Offer('A',D('20'),'AUD',10,D('10'),D('2'),True)]
        self.today = date(2026,11,2)
        self.evidence = {'as_of':'2026-11-02','merchant':[{'sku':'A','status':'approved'}],
                         'analytics':{'period_start':'2026-10-26','period_end':'2026-11-01',
                                      'purchase_events':5,'purchase_revenue':'100'},
                         'pages':[{'sku':'A','url':'https://example.com/tea','http_status':200,
                                   'observed_price':'20','currency':'AUD'}]}

    def run_audit(self, **kwargs):
        args = dict(products=self.products, offers=self.offers, platform='woocommerce',
                    currency='AUD', as_of=self.today, evidence=self.evidence)
        args.update(kwargs)
        return audit(**args)

    def codes(self, result):
        return {f['code'] for f in result['findings']}

    def test_missing_product_blocks_promotion(self):
        self.assertIn('product_missing', self.codes(self.run_audit(products={})))

    def test_unpublished_product_blocks_promotion(self):
        self.products['A'] = Product('A','Tea',D('20'),False,30,True)
        self.assertIn('not_published', self.codes(self.run_audit()))

    def test_zero_stock_blocks_promotion(self):
        self.products['A'] = Product('A','Tea',D('20'),True,0,False)
        self.assertIn('no_stock', self.codes(self.run_audit()))

    def test_unknown_stock_is_not_a_stockout(self):
        self.products['A'] = Product('A','Tea',D('20'),True)
        codes = self.codes(self.run_audit())
        self.assertIn('stock_unknown', codes)
        self.assertNotIn('no_stock', codes)

    def test_stock_shortfall_uses_supplied_demand(self):
        self.assertIn('stock_shortfall', self.codes(self.run_audit(stock={'A':3})))

    def test_low_stock_threshold_is_configurable(self):
        self.assertIn('low_stock', self.codes(self.run_audit(stock={'A':15},low_stock=20)))
        self.assertNotIn('low_stock', self.codes(self.run_audit(stock={'A':15},low_stock=10)))

    def test_prelaunch_price_difference_is_review(self):
        self.offers = [Offer('A',D('15'),'AUD')]
        finding = next(f for f in self.run_audit()['findings'] if f['code']=='price_difference')
        self.assertEqual(finding['priority'], 'review')

    def test_margin_calculation_is_exact(self):
        result = self.run_audit()
        self.assertEqual(result['products'][0]['contribution_per_unit'],'8.00')
        self.assertEqual(result['products'][0]['contribution_percent'],'40.00')

    def test_unconfirmed_cost_basis_does_not_calculate(self):
        self.offers = [Offer('A',D('20'),'AUD',unit_cost=D('10'))]
        result = self.run_audit()
        self.assertIsNone(result['products'][0]['contribution_per_unit'])
        self.assertIn('costs_unknown', self.codes(result))

    def test_negative_contribution_is_flagged(self):
        self.offers = [Offer('A',D('5'),'AUD',unit_cost=D('10'),other_unit_cost=D('0'),cost_basis_confirmed=True)]
        self.assertIn('negative_contribution', self.codes(self.run_audit()))

    def test_disapproval_is_blocker(self):
        self.evidence['merchant'][0]['status']='disapproved'
        finding = next(f for f in self.run_audit()['findings'] if f['code']=='merchant_disapproved')
        self.assertEqual(finding['priority'],'blocker')

    def test_missing_evidence_remains_unknown(self):
        codes = self.codes(self.run_audit(evidence=None))
        self.assertTrue({'merchant_unknown','tracking_unknown','page_unknown'} <= codes)

    def test_stale_evidence_not_used_as_current(self):
        self.evidence['as_of']='2026-10-01'
        self.evidence['analytics']['period_start']='2026-09-24'
        self.evidence['analytics']['period_end']='2026-09-30'
        codes=self.codes(self.run_audit())
        self.assertIn('evidence_stale',codes)
        self.assertIn('merchant_unknown',codes)

    def test_future_evidence_rejected(self):
        self.evidence['as_of']='2026-11-03'
        with self.assertRaises(InputError):
            self.run_audit()

    def test_invalid_evidence_values_rejected(self):
        for value in [-1, True, 2.5, 'five']:
            with self.subTest(value=value):
                self.evidence['analytics']['purchase_events']=value
                with self.assertRaises(InputError):
                    self.run_audit()

    def test_zero_purchases_cannot_validate_tracking(self):
        self.evidence['analytics']['purchase_events']=0
        self.assertIn('no_purchase_events',self.codes(self.run_audit()))

    def test_recorded_purchases_do_not_claim_tracking_correctness(self):
        result = self.run_audit()
        self.assertIn('tracking_validation',self.codes(result))
        self.assertIn('not a checkout test', render_markdown(result).lower())

    def test_page_error_and_currency_mismatch(self):
        self.evidence['pages'][0]['http_status']=404
        self.evidence['pages'][0]['currency']='USD'
        codes=self.codes(self.run_audit())
        self.assertIn('page_error',codes)
        self.assertIn('page_currency',codes)

    def test_incomplete_page_evidence_does_not_pass(self):
        self.evidence['pages']=[{'sku':'A','url':'https://example.com/tea','http_status':200}]
        self.assertIn('page_price_unknown',self.codes(self.run_audit()))

    def test_every_finding_has_evidence_and_action(self):
        result=self.run_audit(evidence=None)
        self.assertTrue(result['findings'])
        for finding in result['findings']:
            self.assertTrue(finding['evidence'])
            self.assertTrue(finding['action'])
        self.assertNotEqual(result['summary'], 'ready')

    def test_reject_bad_evidence_structure(self):
        for value in [[], {'as_of':'2026-11-02','merchant':'yes'},
                      {'as_of':'2026-11-02','pages':[{'sku':'A','url':'javascript:alert(1)','http_status':200}]},
                      {'as_of':'2026-11-02','merchant':[{'sku':'A','status':'approved'},{'sku':'A','status':'disapproved'}]}]:
            with self.subTest(value=value):
                with self.assertRaises(InputError):
                    self.run_audit(evidence=value)

    def test_backorder_needs_fulfilment_review(self):
        self.products['A']=Product('A','Tea',D('20'),True,30,None,True)
        self.assertIn('backorder_review',self.codes(self.run_audit()))
