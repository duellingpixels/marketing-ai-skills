"""Validate user-recorded observations; this is not an API connector."""
from datetime import date
from urllib.parse import urlsplit
from .imports import InputError, money


def iso_date(value, field):
    if not isinstance(value, str):
        raise InputError(f'{field}: expected an ISO date (YYYY-MM-DD).')
    try:
        if len(value) != 10:
            raise ValueError
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f'{field}: expected an ISO date (YYYY-MM-DD).') from exc


def count(value, field):
    if type(value) is not int or value < 0:
        raise InputError(f'{field}: expected a non-negative integer.')
    return value


def validate_evidence(evidence, as_of):
    if not isinstance(evidence, dict):
        raise InputError('Evidence must be a JSON object.')
    observed = iso_date(evidence.get('as_of'), 'evidence.as_of')
    if observed > as_of:
        raise InputError('Evidence date is after the report date.')
    for key in ('merchant', 'pages'):
        values = evidence.get(key, [])
        if not isinstance(values, list):
            raise InputError(f'evidence.{key}: expected a list.')
        seen = set()
        for row in values:
            if not isinstance(row, dict) or not isinstance(row.get('sku'), str) or not row['sku'].strip():
                raise InputError(f'evidence.{key}: every row requires a non-empty string sku.')
            if row['sku'] in seen:
                raise InputError(f'evidence.{key}: duplicate SKU {row["sku"]!r}.')
            seen.add(row['sku'])
            if key == 'merchant':
                if row.get('status') not in ('approved', 'disapproved', 'pending'):
                    raise InputError('Merchant status must be approved, disapproved or pending.')
                if 'issue' in row and not isinstance(row['issue'], str):
                    raise InputError('Merchant issue must be text.')
            else:
                url = row.get('url')
                try:
                    parsed = urlsplit(url) if isinstance(url, str) else None
                    valid_url = parsed and parsed.scheme in ('http','https') and parsed.hostname and not parsed.username and not parsed.password
                    if parsed:
                        parsed.port
                except ValueError:
                    valid_url = False
                if not valid_url or any(ord(c) < 32 for c in url):
                    raise InputError('Page evidence requires an HTTP(S) URL without credentials.')
                status = row.get('http_status')
                if type(status) is not int or not 100 <= status <= 599:
                    raise InputError('Page http_status must be an integer from 100 to 599.')
                if row.get('observed_price') is not None:
                    money(row['observed_price'], 'page observed_price')
                if 'currency' in row and (not isinstance(row['currency'], str) or len(row['currency']) != 3 or not row['currency'].isascii() or not row['currency'].isupper() or not row['currency'].isalpha()):
                    raise InputError('Page currency must be three uppercase letters.')
    if 'analytics' in evidence:
        analytics = evidence['analytics']
        if not isinstance(analytics, dict):
            raise InputError('evidence.analytics: expected an object.')
        start = iso_date(analytics.get('period_start'), 'analytics.period_start')
        end = iso_date(analytics.get('period_end'), 'analytics.period_end')
        if start > end or end > observed:
            raise InputError('Analytics period must end on or before the evidence date and start on or before its end.')
        count(analytics.get('purchase_events'), 'analytics.purchase_events')
        money(analytics.get('purchase_revenue'), 'analytics.purchase_revenue')
    return observed
