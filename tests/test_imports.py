import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from marketing_ai_skills.black_friday.imports import InputError, load_products, load_offers, load_stock


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'input.csv'

    def write(self, rows):
        with self.path.open('w', newline='', encoding='utf-8-sig') as f:
            csv.writer(f).writerows(rows)
        return self.path

    def test_woo_sale_and_zero_stock(self):
        self.write([['Type','SKU','Name','Published','Regular price','Sale price','Stock','In stock?'],
                    ['simple','A','Tea','1','20.10','18.10','0','0']])
        p = load_products(self.path, 'woocommerce')['A']
        self.assertEqual(p.price, Decimal('18.10'))
        self.assertEqual(p.stock, 0)
        self.assertFalse(p.in_stock)
        self.assertTrue(p.published)

    def test_woo_child_of_unpublished_parent(self):
        self.write([['ID','Type','SKU','Name','Published','Parent','Regular price'],
                    ['1','variable','P','Shirt','-1','',''],
                    ['2','variation','BLUE','Blue','1','id:1','30']])
        products = load_products(self.path, 'woocommerce')
        self.assertNotIn('P', products)
        self.assertFalse(products['BLUE'].published)

    def test_woo_unresolved_parent_leaves_visibility_unknown(self):
        self.write([['Type','SKU','Name','Published','Parent','Regular price'],
                    ['variation','BLUE','Blue','1','id:9','30']])
        self.assertIsNone(load_products(self.path, 'woocommerce')['BLUE'].published)

    def test_woo_scheduled_sale_does_not_guess_current_price(self):
        self.write([['Type','SKU','Name','Published','Regular price','Sale price','Date sale price starts'],
                    ['simple','A','Tea','1','20','15','2026-11-27']])
        self.assertIsNone(load_products(self.path, 'woocommerce')['A'].price)

    def test_shopify_legacy_variants_inherit_product_metadata(self):
        self.write([['Handle','Title','Variant SKU','Variant Price','Published','Status','Variant Inventory Qty'],
                    ['shirt','Shirt','RED','20','TRUE','active','12'],
                    ['shirt','','BLUE','25','','','4'],
                    ['shirt','','','','','','']])
        p = load_products(self.path, 'shopify')
        self.assertEqual(set(p), {'RED','BLUE'})
        self.assertEqual(p['BLUE'].name, 'Shirt')
        self.assertTrue(p['BLUE'].published)
        self.assertIsNone(p['BLUE'].stock)

    def test_shopify_current_headers(self):
        self.write([['URL handle','Title','SKU','Price','Published on online store','Status'],
                    ['tea','Tea','A','19.95','true','draft']])
        p = load_products(self.path, 'shopify')['A']
        self.assertEqual(p.price, Decimal('19.95'))
        self.assertFalse(p.published)

    def test_missing_visibility_is_unknown(self):
        self.write([['Handle','Title','Variant SKU','Variant Price'],['tea','Tea','A','10']])
        self.assertIsNone(load_products(self.path, 'shopify')['A'].published)

    def test_duplicate_sku_is_rejected(self):
        self.write([['SKU','Name','Regular price'], ['A','Tea','2'], ['A','Coffee','3']])
        with self.assertRaisesRegex(InputError, 'Duplicate SKU'):
            load_products(self.path, 'woocommerce')

    def test_invalid_price_is_rejected(self):
        for value in ['NaN','Infinity','-1','AUD 20']:
            with self.subTest(value=value):
                self.write([['SKU','Name','Regular price'],['A','Tea',value]])
                with self.assertRaises(InputError):
                    load_products(self.path, 'woocommerce')

    def test_bad_stock_is_rejected(self):
        self.write([['SKU','Name','Regular price','Stock'],['A','Tea','10','1.5']])
        with self.assertRaises(InputError):
            load_products(self.path, 'woocommerce')

    def test_offers_require_unique_skus_and_currency(self):
        self.write([['sku','planned_price','currency'],['A','15.50','AUD']])
        self.assertEqual(load_offers(self.path, 'AUD')[0].planned_price, Decimal('15.50'))
        with self.assertRaisesRegex(InputError, 'currency'):
            load_offers(self.path, 'USD')
        self.write([['sku','planned_price','currency'],['A','15','AUD'],['A','14','AUD']])
        with self.assertRaisesRegex(InputError, 'Duplicate SKU'):
            load_offers(self.path, 'AUD')

    def test_empty_or_malformed_csv_is_rejected(self):
        for content in ['', 'sku,planned_price,currency\n',
                        'sku,sku,planned_price,currency\nA,A,10,AUD\n',
                        'sku,planned_price,currency\nA,10,AUD,extra\n',
                        'sku,planned_price,currency\nA,10\n']:
            with self.subTest(content=content):
                self.path.write_text(content)
                with self.assertRaises(InputError):
                    load_offers(self.path, 'AUD')

    def test_stock_override_keeps_zero_and_negative_availability(self):
        self.write([['sku','available_quantity'],['A','0'],['B','-2']])
        self.assertEqual(load_stock(self.path), {'A':0, 'B':-2})

    def test_offers_validate_demand(self):
        self.write([['sku','planned_price','currency','expected_units'],['A','10','AUD','-1']])
        with self.assertRaises(InputError):
            load_offers(self.path, 'AUD')

    def test_different_platform_headers_fail_clearly(self):
        self.write([['sku','planned_price','currency'],['A','10','AUD']])
        with self.assertRaisesRegex(InputError, 'column'):
            load_products(self.path, 'shopify')

    def test_malformed_negative_quantity_has_actionable_error(self):
        self.write([['sku','available_quantity'],['A','--1']])
        with self.assertRaises(InputError):
            load_stock(self.path)

    def test_excessively_long_quantity_has_actionable_error(self):
        self.write([['sku','available_quantity'],['A','9'*5000]])
        with self.assertRaises(InputError):
            load_stock(self.path)

    def test_woo_parent_stock_is_unknown_not_invalid(self):
        self.write([['ID','Type','SKU','Name','Published','Parent','Regular price','Stock'],
                    ['1','variable','P','Shirt','1','','','20'],
                    ['2','variation','BLUE','Blue','1','id:1','30','parent']])
        self.assertIsNone(load_products(self.path,'woocommerce')['BLUE'].stock)

    def test_woo_backorder_is_explicit(self):
        self.write([['Type','SKU','Name','Published','Regular price','Stock','In stock?'],
                    ['simple','A','Tea','1','20','0','backorder']])
        p=load_products(self.path,'woocommerce')['A']
        self.assertTrue(p.backorder)
        self.assertIsNone(p.in_stock)

    def test_woo_type_flags_do_not_bypass_parent_visibility(self):
        self.write([['ID','Type','SKU','Name','Published','Parent','Regular price'],
                    ['1','variable','P','Shirt','-1','',''],
                    ['2','variation, virtual','BLUE','Blue','1','id:1','30']])
        self.assertFalse(load_products(self.path,'woocommerce')['BLUE'].published)

    def test_unsupported_monetary_precision_is_rejected(self):
        for value in ['0.001','0.000000000000000000000000000001','1e-1000000']:
            with self.subTest(value=value):
                self.write([['sku','planned_price','currency'],['A',value,'AUD']])
                with self.assertRaisesRegex(InputError,'decimal places'):
                    load_offers(self.path,'AUD')

    def test_money_accepts_harmless_trailing_zeros(self):
        self.write([['sku','planned_price','currency'],['A','10.0000','AUD']])
        self.assertEqual(load_offers(self.path,'AUD')[0].planned_price,Decimal('10'))
