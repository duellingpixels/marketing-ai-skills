"""Read product exports without guessing missing data or modifying the source."""
import csv
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


class InputError(ValueError):
    """An input cannot be safely interpreted. Explain the correction to the user."""


def money(value, field, optional=False):
    if str(value).strip() == '' and optional:
        return None
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise InputError(f'{field}: use a plain non-negative number, such as 19.95.') from exc
    if not number.is_finite() or number < 0 or number > Decimal('1000000000000'):
        raise InputError(f'{field}: amount must be finite and between 0 and 1000000000000.')
    if number != number.quantize(Decimal('0.01')):
        raise InputError(f'{field}: this release supports monetary values to two decimal places. Confirm a suitable value before rerunning.')
    return number


def integer(value, field, optional=False, negative=False):
    if str(value).strip() == '' and optional:
        return None
    text = str(value).strip()
    if len(text) > 19 or not re.fullmatch(r'-?[0-9]+', text):
        raise InputError(f'{field}: use a whole number.')
    result = int(text)
    if not negative and result < 0:
        raise InputError(f'{field}: cannot be negative.')
    return result


def boolean(value, field):
    text = str(value).strip().lower()
    if not text:
        return None
    if text in ('true', '1', 'yes'):
        return True
    if text in ('false', '0', 'no'):
        return False
    raise InputError(f'{field}: use true/false, yes/no or 1/0.')


def read_csv(path, required=()):
    try:
        with Path(path).open(encoding='utf-8-sig', newline='') as source:
            reader = csv.DictReader(source, strict=True)
            headers = reader.fieldnames
            if not headers or any(not h.strip() for h in headers):
                raise InputError(f'{Path(path).name}: missing column headers.')
            if len(set(headers)) != len(headers):
                raise InputError(f'{Path(path).name}: duplicate column headers.')
            if any(key not in headers for key in required):
                raise InputError(f'{Path(path).name}: required columns: {", ".join(required)}.')
            rows = []
            for index, row in enumerate(reader, 2):
                if None in row or any(value is None for value in row.values()):
                    raise InputError(f'{Path(path).name}: row {index} has the wrong number of columns.')
                if any(value.strip() for value in row.values()):
                    rows.append({key: value.strip() for key, value in row.items()})
    except (OSError, UnicodeError, csv.Error) as exc:
        raise InputError(f'Cannot read CSV {Path(path).name}: {exc}') from exc
    if not rows:
        raise InputError(f'{Path(path).name}: no data rows.')
    return rows


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: Decimal | None
    published: bool | None
    stock: int | None = None
    in_stock: bool | None = None
    backorder: bool = False


@dataclass(frozen=True)
class Offer:
    sku: str
    planned_price: Decimal
    currency: str
    expected_units: int | None = None
    unit_cost: Decimal | None = None
    other_unit_cost: Decimal | None = None
    cost_basis_confirmed: bool | None = None


def add_unique(target, sku, value):
    if sku in target:
        raise InputError(f'Duplicate SKU {sku!r}: assign unique variant SKUs before checking.')
    target[sku] = value


def pick(row, *keys):
    return next((row[k] for k in keys if k in row), '')


def woo_visibility(row):
    value = row.get('Published', '')
    if value == '1':
        return True
    if value in ('0', '-1', '2'):
        return False
    if value:
        raise InputError(f'Published: unsupported value {value!r}. Use a core WooCommerce export.')
    return None


def load_products(path, platform):
    products = {}
    if platform == 'woocommerce':
        rows = read_csv(path, ('SKU', 'Name', 'Regular price'))
        parents = {}
        for row in rows:
            if row.get('ID'):
                parents['id:' + row['ID']] = row
            if row.get('SKU'):
                if row['SKU'] in parents:
                    raise InputError(f'Duplicate SKU {row["SKU"]!r}.')
                parents[row['SKU']] = row
        for row in rows:
            product_type = row.get('Type', 'simple').split(',')[0].strip()
            if not row['SKU'] or product_type in ('variable', 'grouped', 'external'):
                continue
            sku = row['SKU']
            published = woo_visibility(row)
            if product_type == 'variation':
                parent = parents.get(row.get('Parent'))
                parent_visibility = woo_visibility(parent) if parent else None
                if parent_visibility is False or published is False:
                    published = False
                elif parent_visibility is not True:
                    published = None
            regular = money(row['Regular price'], f'{sku} regular price', optional=True)
            sale = money(row.get('Sale price', ''), f'{sku} sale price', optional=True)
            scheduled = bool(row.get('Date sale price starts') or row.get('Date sale price ends'))
            price = None if scheduled and sale is not None else (sale if sale is not None else regular)
            stock_value = row.get('Stock', '')
            stock = None if stock_value.lower() == 'parent' else integer(stock_value, f'{sku} stock', optional=True, negative=True)
            backorder = row.get('In stock?', '').lower() == 'backorder'
            in_stock = None if backorder else boolean(row.get('In stock?', ''), f'{sku} in stock')
            add_unique(products, sku, Product(sku, row['Name'], price, published, stock, in_stock, backorder))
    elif platform == 'shopify':
        rows = read_csv(path)
        headers = rows[0]
        for aliases in [('SKU', 'Variant SKU'), ('Price', 'Variant Price'), ('URL handle', 'Handle')]:
            if not any(key in headers for key in aliases):
                raise InputError(f'Shopify product column missing: {" or ".join(aliases)}.')
        metadata = {}
        for row in rows:
            handle = pick(row, 'URL handle', 'Handle')
            if not handle:
                raise InputError('Shopify URL handle/Handle is missing on a product row.')
            parent = metadata.setdefault(handle, {})
            for key in ('Title', 'Published on online store', 'Published', 'Status'):
                if row.get(key):
                    if key in parent and parent[key] != row[key]:
                        raise InputError(f'Conflicting {key} values for Shopify handle {handle!r}.')
                    parent[key] = row[key]
        for row in rows:
            sku = pick(row, 'SKU', 'Variant SKU')
            if not sku:  # image-only rows and unkeyed variants cannot be matched to campaign SKUs
                continue
            parent = metadata[pick(row, 'URL handle', 'Handle')]
            visible = boolean(pick(parent, 'Published on online store', 'Published'), f'{sku} published')
            status = parent.get('Status', '').lower()
            if status and status not in ('active', 'draft', 'archived', 'unlisted'):
                raise InputError(f'{sku}: unsupported Shopify Status {status!r}.')
            published = False if visible is False or status in ('draft', 'archived') else (
                True if visible is True and status == 'active' else None)
            price = money(pick(row, 'Price', 'Variant Price'), f'{sku} price', optional=True)
            add_unique(products, sku, Product(sku, parent.get('Title', ''), price, published))
    else:
        raise InputError('Platform must be woocommerce or shopify.')
    if not products:
        raise InputError('No purchasable products with SKUs found. Export variants with unique SKUs.')
    return products


def load_offers(path, currency):
    offers = {}
    for row in read_csv(path, ('sku', 'planned_price', 'currency')):
        sku = row['sku']
        if not sku:
            raise InputError('Every offer requires a non-empty sku.')
        if row['currency'] != currency:
            raise InputError(f'{sku}: offer currency {row["currency"]!r} differs from report currency {currency}.')
        offer = Offer(sku, money(row['planned_price'], f'{sku} planned price'), currency,
                      integer(row.get('expected_units', ''), f'{sku} expected units', optional=True),
                      money(row.get('unit_cost', ''), f'{sku} unit cost', optional=True),
                      money(row.get('other_unit_cost', ''), f'{sku} other unit cost', optional=True),
                      boolean(row.get('cost_basis_confirmed', ''), f'{sku} cost basis confirmed'))
        add_unique(offers, sku, offer)
    return list(offers.values())


def load_stock(path):
    stock = {}
    for row in read_csv(path, ('sku', 'available_quantity')):
        if not row['sku']:
            raise InputError('Every stock row requires a non-empty sku.')
        add_unique(stock, row['sku'], integer(row['available_quantity'], 'available_quantity', negative=True))
    return stock
