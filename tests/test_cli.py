import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from marketing_ai_skills.black_friday.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.products=self.root/'products.csv'
        self.offers=self.root/'offers.csv'
        self.offers.write_text('sku,planned_price,currency\nA,10,AUD\n')
        self.products.write_text('SKU,Name,Published,Regular price,Stock\nA,Tea,1,10,20\n')
        self.args=['--platform','woocommerce','--products',str(self.products),'--offers',str(self.offers),
                   '--currency','AUD','--as-of','2026-11-02','--campaign-start','2026-11-27',
                   '--campaign-end','2026-11-30','--output-dir',str(self.root/'output')]

    def run_cli(self, extra=None):
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return main(self.args+(extra or []))

    def test_cli_writes_both_reports(self):
        self.assertEqual(self.run_cli(),0)
        report=json.loads((self.root/'output'/'report.json').read_text())
        self.assertEqual(report['products'][0]['sku'],'A')
        self.assertEqual(report['sources']['products'],'products.csv')
        self.assertIn('campaign',report)
        self.assertTrue((self.root/'output'/'report.md').is_file())

    def test_existing_output_is_not_overwritten(self):
        self.assertEqual(self.run_cli(),0)
        path=self.root/'output'/'report.md'
        path.write_text('keep this')
        self.assertEqual(self.run_cli(),2)
        self.assertEqual(path.read_text(),'keep this')

    def test_invalid_evidence_is_actionable_error(self):
        p=self.root/'bad.json'
        p.write_text('not JSON')
        self.assertEqual(self.run_cli(['--evidence',str(p)]),2)

    def test_nan_in_json_is_rejected(self):
        p=self.root/'bad.json'
        p.write_text('{"as_of":"2026-11-02","value":NaN}')
        self.assertEqual(self.run_cli(['--evidence',str(p)]),2)

    def test_shopify_cli_works(self):
        self.products.write_text('URL handle,Title,SKU,Price,Status,Published on online store\ntea,Tea,A,10,active,true\n')
        self.args[1]='shopify'
        stock=self.root/'stock.csv'
        stock.write_text('sku,available_quantity\nA,12\n')
        self.assertEqual(self.run_cli(['--stock',str(stock)]),0)
        report=json.loads((self.root/'output'/'report.json').read_text())
        self.assertEqual(report['products'][0]['stock'],12)

    def test_bad_date_is_error(self):
        self.assertEqual(self.run_cli(['--as-of','tomorrow']),2)

    def test_negative_option_is_error(self):
        self.assertEqual(self.run_cli(['--low-stock','-1']),2)

    def test_campaign_dates_must_be_ordered(self):
        self.assertEqual(self.run_cli(['--campaign-end','2026-11-01']),2)

    def test_future_product_export_is_error(self):
        self.assertEqual(self.run_cli(['--exported-on','2026-11-03']),2)

    def test_stale_export_is_flagged(self):
        self.assertEqual(self.run_cli(['--exported-on','2026-10-01']),0)
        report=json.loads((self.root/'output'/'report.json').read_text())
        self.assertIn('export_stale',{f['code'] for f in report['findings']})

    def test_missing_files_fail_without_report(self):
        self.products.unlink()
        self.assertEqual(self.run_cli(),2)
        self.assertFalse((self.root/'output'/'report.md').exists())

    def test_documented_example_fixtures_run_on_both_platforms(self):
        examples=Path(__file__).resolve().parents[1]/'examples'/'black-friday'
        for platform,filename in [('woocommerce','woocommerce-products.csv'),('shopify','shopify-products.csv'),('shopify','shopify-products-legacy.csv')]:
            with self.subTest(filename=filename):
                args=['--platform',platform,'--products',str(examples/filename),
                      '--offers',str(examples/'offers.csv'),'--evidence',str(examples/'evidence.json'),
                      '--currency','AUD','--as-of','2026-11-02','--exported-on','2026-11-02',
                      '--campaign-start','2026-11-27','--campaign-end','2026-11-30',
                      '--output-dir',str(self.root/filename)]
                if platform=='shopify':
                    args+=['--stock',str(examples/'stock.csv')]
                with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main(args),0)
                report=json.loads((self.root/filename/'report.json').read_text())
                self.assertEqual(report['products'][0]['contribution_per_unit'],'3.00')
                self.assertEqual(report['products'][1]['contribution_per_unit'],'-1.00')
                self.assertTrue({'not_published','no_stock','merchant_disapproved','product_missing'} <= {f['code'] for f in report['findings']})
