"""Render plain findings; escape source text instead of treating it as Markdown."""
from html import escape


def safe(value):
    text = escape(str(value), quote=False).replace('\r',' ').replace('\n',' ')
    for char in ('\\','`','*','_','[',']','|','#'):
        text = text.replace(char, '\\'+char)
    return text


def render_markdown(report):
    counts = report['counts']
    product_names = {p['sku']: p.get('name') or 'Name unavailable' for p in report['products']}
    lines = ['# Black Friday readiness: actions to review', '',
             f'Platform: **{safe(report["platform"])}** · Report date: **{report["as_of"]}** · Currency: **{safe(report["currency"])}**',
             '',report['summary'],'',
             f'**{counts["blocker"]} blockers · {counts["review"]} review items · {counts["unknown"]} checks needing evidence**',
             '', 'Finding counts are individual checks, not numbers of affected products. Unknown checks may be inapplicable; record why when reviewing them.',
             '', '## Sources', '']
    lines.extend(f'- {safe(key)}: {safe(value)}' for key,value in report['sources'].items())
    lines += ['', '## Promoted products', '',
              f'All prices and costs are per unit in {safe(report["currency"])}.', '',
              '**Unit Margin = planned selling price − unit cost − other unit costs.**', '',
              '**Value = Unit Margin ÷ planned selling price × 100.** This column shows the margin as a percentage of the selling price.', '',
              'Unit cost is the cost of the product. Other unit costs are the additional selling costs you supplied, such as payment fees or packaging. '
              'Unit Margin is what remains after those listed costs; business overheads and any costs you have not supplied still need covering.', '',
              'Not supplied means a cost is missing. Not calculated means costs are missing or their currency and tax basis have not been confirmed comparable. '
              'Value is also not calculated when the selling price is zero. A known zero cost is shown as 0.00.', '',
              '| Product name | SKU | Planned selling price | Unit cost | Other unit costs | Unit Margin | Value | Available units |',
              '|---|---|---:|---:|---:|---:|---:|---:|']
    for p in report['products']:
        unit_cost = p.get('unit_cost')
        other_cost = p.get('other_unit_cost')
        margin = p['contribution_per_unit']
        percent = p['contribution_percent']
        values = [product_names[p['sku']], p['sku'], p['planned_price'],
                  unit_cost if unit_cost is not None else 'Not supplied',
                  other_cost if other_cost is not None else 'Not supplied',
                  margin if margin is not None else 'Not calculated',
                  percent + '%' if percent is not None else 'Not calculated',
                  p['stock'] if p['stock'] is not None else 'Unverified']
        lines.append('| '+' | '.join(safe(v) for v in values)+' |')
    for priority,title in [('blocker','Resolve before promotion'),('review','Review before launch'),('unknown','Checks still needing evidence')]:
        lines += ['',f'## {title}','']
        matching = [f for f in report['findings'] if f['priority']==priority]
        if not matching:
            lines.append('No findings in this category from the supplied inputs.')
        for finding in matching:
            sku = (f' — {safe(product_names.get(finding["sku"], "Name unavailable"))} [{safe(finding["sku"])}]'
                   if finding['sku'] else '')
            lines += [f'### {safe(finding["title"])}{sku}', '',
                      f'**Evidence:** {safe(finding["evidence"])}','',f'**Action:** {safe(finding["action"])}','']
    lines += ['', '## Limits and assumptions', '']
    lines.extend('- '+safe(item) for item in report['assumptions'])
    return '\n'.join(lines)+'\n'
