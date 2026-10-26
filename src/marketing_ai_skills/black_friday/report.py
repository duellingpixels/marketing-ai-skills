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
    lines += ['', '## Promoted products', '', '| Product name | SKU | Planned price | Available units | Contribution per unit | Contribution % |',
              '|---|---|---:|---:|---:|---:|']
    for p in report['products']:
        values=[product_names[p['sku']],p['sku'],p['planned_price'],p['stock'],p['contribution_per_unit'],p['contribution_percent']]
        lines.append('| '+' | '.join(safe(v) if v is not None else 'Unverified' for v in values)+' |')
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
