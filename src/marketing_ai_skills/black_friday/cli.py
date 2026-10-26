"""Generate local action reports from exports. Exit 0 is not a readiness pass."""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from .checks import audit
from .evidence import iso_date
from .imports import InputError, load_products, load_offers, load_stock
from .report import render_markdown


def reject_constant(value):
    raise InputError(f'Invalid JSON numeric constant: {value}.')


def unique_json_keys(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise InputError(f'Duplicate JSON key {key!r}.')
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='Find sale preparation issues from WooCommerce or Shopify exports. No network calls or store changes.')
    parser.add_argument('--platform',choices=['woocommerce','shopify'],required=True)
    parser.add_argument('--products',type=Path,required=True)
    parser.add_argument('--offers',type=Path,required=True)
    parser.add_argument('--stock',type=Path)
    parser.add_argument('--evidence',type=Path)
    parser.add_argument('--currency',required=True,help='Single report currency, such as AUD.')
    parser.add_argument('--as-of',required=True,help='Report date: YYYY-MM-DD.')
    parser.add_argument('--exported-on',help='Date of the oldest product/stock snapshot used: YYYY-MM-DD.')
    parser.add_argument('--campaign-start',required=True)
    parser.add_argument('--campaign-end',required=True)
    parser.add_argument('--low-stock',type=int,default=10)
    parser.add_argument('--max-evidence-age-days',type=int,default=7)
    parser.add_argument('--output-dir',type=Path,required=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code
    created = []
    try:
        if not re.fullmatch('[A-Z]{3}',args.currency):
            raise InputError('Currency must be three uppercase letters, such as AUD.')
        as_of = iso_date(args.as_of,'as-of')
        start = iso_date(args.campaign_start,'campaign-start')
        end = iso_date(args.campaign_end,'campaign-end')
        if start > end:
            raise InputError('Campaign start must be on or before campaign end.')
        exported = iso_date(args.exported_on,'exported-on') if args.exported_on else None
        if exported and exported > as_of:
            raise InputError('Product/stock export date cannot be after the report date.')
        targets = [args.output_dir/'report.json',args.output_dir/'report.md']
        if any(path.exists() or path.is_symlink() for path in targets):
            raise InputError('Output report already exists. Choose a new output directory to preserve previous reports.')
        products = load_products(args.products,args.platform)
        offers = load_offers(args.offers,args.currency)
        stock = load_stock(args.stock) if args.stock else None
        evidence = None
        if args.evidence:
            with args.evidence.open(encoding='utf-8-sig') as source:
                evidence = json.load(source,parse_constant=reject_constant,object_pairs_hook=unique_json_keys)
        report = audit(products,offers,args.platform,args.currency,as_of,stock,evidence,
                       args.low_stock,args.max_evidence_age_days)
        report['campaign'] = dict(start=start.isoformat(),end=end.isoformat())
        report['exported_on'] = exported.isoformat() if exported else None
        report['sources'] = {key:getattr(args,key).name for key in ('products','offers','stock','evidence') if getattr(args,key)}
        if exported is None or (as_of-exported).days > args.max_evidence_age_days:
            report['findings'].append(dict(priority='unknown',code='export_stale' if exported else 'export_date_unknown',
                sku=None,title='Verify the product and stock snapshot dates',
                evidence=f'Oldest supplied snapshot date: {exported.isoformat() if exported else "not supplied"}.',
                action='Use fresh exports and supply --exported-on for the oldest snapshot used.'))
            report['counts']['unknown'] += 1
        report['assumptions'].append(f'Campaign dates {start.isoformat()} to {end.isoformat()}; check scheduling in the store timezone.')
        json_text = json.dumps(report,indent=2,ensure_ascii=False)+'\n'
        markdown = render_markdown(report)
        args.output_dir.mkdir(parents=True,exist_ok=True)
        for path,content in zip(targets,(json_text,markdown)):
            with path.open('x',encoding='utf-8') as output:
                created.append(path)
                output.write(content)
        print(f'Report generated: {args.output_dir / "report.md"}')
        print('This is an action list, not confirmation that the store is ready.')
        return 0
    except (InputError,OSError,UnicodeError,json.JSONDecodeError) as exc:
        for path in created:
            path.unlink(missing_ok=True)
        print(f'Input error: {exc}',file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
