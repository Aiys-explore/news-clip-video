#!/usr/bin/env python3
"""Check the editorial plan before rendering; factual corroboration is separate."""
import argparse
import datetime as dt
import json
from pathlib import Path

ROUTES = {
    'brief': [('news','support','context'), ('news','support','context','next')],
    'event_intro': [('news','why_now','significance','reaction','watch')],
    'chronology': [('origin','development','outcome')],
    'reverse_chronology': [('outcome','prior','origin')],
    'hourglass': [('news','turn','origin','development','return')],
    'explainer': [('question','mechanism','takeaway')],
    'case_feature': [('case','nut_graf','context','return')],
    'data_check': [('claim','baseline','comparison','finding')],
}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def day(value):
    return dt.date.fromisoformat(value)


def shown(b, asset, marker):
    return any(marker in text for text in (b.get('headline',''), b.get('detail',''),
                                           b.get('caption',''), asset.get('credit','')))


def validate(m):
    """Raise ValueError for a malformed plan; return editorial metadata."""
    ed = m['editorial']
    route, ledger = ed['structure'], ed['facts']
    need(route in ROUTES, f'Unknown story structure: {route}')
    need(ed['question'].strip() and ledger, 'Give a viewer question and fact ledger')
    as_of = day(ed['as_of'])
    for k,f in ledger.items():
        need(all(f.get(field, '').strip() for field in ('text','source','locator')), f'{k}: fact lacks text, source or locator')
        need(f['source'].startswith(('https://','http://')), f'{k}: use a source URL')
        need(day(f['available_on']) <= as_of, f'{k}: source was not available as of {as_of}')
        need(f['kind'] in {'fact','statement','plan','inference'}, f'{k}: unknown fact kind')
        if f['kind'] in {'statement','plan'}:
            need(bool(f.get('attribution')), f'{k}: attribute statement or plan')

    group, dated = [], []
    for n,b in enumerate(m['beats'], 1):
        role, ids, visual = b['role'], b['fact_ids'], b['visual_role']
        if not group or role != group[-1]:
            group.append(role)
        need(isinstance(ids,list) and ids and all(k in ledger for k in ids), f'Beat {n}: missing or unknown fact IDs')
        need(visual in {'direct','archive','illustration','document'}, f'Beat {n}: unknown visual role')
        asset = m['assets'][b['asset']] if 'asset' in b else {}
        need(visual not in {'direct','archive'} or asset, f'Beat {n}: factual footage requires asset')
        if asset:
            need(bool(b.get('visual_date')), f'Beat {n}: add date or known date range for asset')
            need(shown(b,asset,b['visual_date']), f'Beat {n}: put the footage date/range on screen')
        if role == 'reaction':
            mode = b.get('quote_mode')
            need(mode in {'direct','paraphrase'}, f'Beat {n}: specify whether reaction was quoted or paraphrased')
            need(any(ledger[k]['kind']=='statement' and (mode=='paraphrase' or ledger[k].get('original_quote')) for k in ids),
                 f'Beat {n}: provide sourced statement with attribution and original wording if quoted')
        if role in {'watch','next'}:
            need(any(ledger[k]['kind'] in {'plan','inference'} for k in ids),
                 f'Beat {n}: distinguish the stated plan or editorial watchpoint from fact')

        ordered = ((route == 'chronology' and role in {'origin','development','outcome'}) or
                   (route == 'reverse_chronology' and role in {'origin','prior','outcome'}) or
                   (route == 'hourglass' and role in {'origin','development','return'}))
        if ordered or route == 'hourglass' and role in {'news','turn'}:
            when = day(b['event_date'])
            need(when <= as_of, f'Beat {n}: narrated event postdates the editorial cutoff')
            if ordered and (not dated or dated[-1] != (when,role)):
                dated.append((when,role))
            if (route == 'reverse_chronology' or role=='turn'):
                need(shown(b,asset,b.get('event_date_label',b['event_date'])), f'Beat {n}: display the date of the time shift')
    need(tuple(group) in ROUTES[route], f'{route}: expected {ROUTES[route]}, received {group}')
    if dated:
        dates = [x[0] for x in dated]
        descending = route=='reverse_chronology'
        need(len(dates) >= 3 and all((a>b if descending else a<b) for a,b in zip(dates,dates[1:])),
             f'{route}: show at least three strictly {"descending" if descending else "ascending"} milestones')
    if route == 'hourglass':
        first = next(b for b in m['beats'] if b['role']=='news')
        turn = next(b for b in m['beats'] if b['role']=='turn')
        need(day(turn['event_date']) == dated[0][0] and day(first['event_date']) == dated[-1][0],
             'hourglass: label the date rewound to; date the return to the opening event')
    if route == 'explainer':
        need(sum(b['role']=='mechanism' for b in m['beats']) >= 2, 'explainer: use at least two distinct mechanism beats')
    return ed


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args()
    try:
        m=json.loads(args.manifest.read_text(encoding='utf-8'))
        ed=validate(m)
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        parser.exit(1, f'Editorial preflight failed: {exc}\n')
    print(f"PASS: {ed['structure']} | {len(m['beats'])} beats | as of {ed['as_of']}")


if __name__ == '__main__':
    main()
