#!/usr/bin/env python3
"""Legge i voti da Tripadvisor (API Terra) e salva data.json.
Fa al massimo UNA chiamata al giorno: se data.json e' gia' di oggi (ora italiana), non fa nulla.
Solo libreria standard di Python."""
import json, os, sys, re, urllib.request, urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo

API = os.environ.get('TA_API_BASE', 'https://terra.tripadvisor.com/api')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data.json')
TZ = ZoneInfo('Europe/Rome')


def now_rome():
    return datetime.now(TZ)


def call(method, path, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {'X-API-Key': key, 'accept': 'application/json'}
    if data:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode('utf-8', 'ignore'), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'ignore'), dict(e.headers)


def show_limits(headers):
    rl = {k: v for k, v in headers.items() if re.search(r'limit|quota|remaining|reset|retry', k, re.I)}
    if rl:
        print('Tripadvisor indica:', rl)


def fetch(key, loc):
    status, text, hdr = call('GET', f'/locations/{loc}', key)
    show_limits(hdr)
    if status in (403, 404):
        # Il locale potrebbe non essere nella allowlist del tuo account: lo aggiungo (non toglie nulla)
        s2, t2, _ = call('POST', '/allowlist', key, {'operation_type': 'APPEND', 'allowlist': [int(loc)]})
        print(f'Provo ad aggiungere il locale alla allowlist -> {s2} {t2[:200]}')
        status, text, hdr = call('GET', f'/locations/{loc}', key)
        show_limits(hdr)
    if status != 200:
        hint = ' (chiave non valida, limitata a un IP, o non abilitata a questo locale)' if status in (401, 403) else ''
        raise RuntimeError(f'Tripadvisor ha risposto {status}{hint}: {text[:300]}')
    d = json.loads(text)
    br = (d.get('traveler_ratings') or {}).get('breakdowns')
    if not br:
        raise RuntimeError('Risposta senza traveler_ratings.breakdowns')
    by = {int(b.get('rating', 0)): int(b.get('count', 0) or 0) for b in br}
    counts = [by.get(k, 0) for k in (5, 4, 3, 2, 1)]
    names = d.get('names') or []
    name = next((n['value'] for n in names if n.get('primary')), names[0]['value'] if names else None)
    return {'name': name, 'counts': counts, 'total': sum(counts)}


def main():
    key = os.environ.get('TRIPADVISOR_API_KEY', '').strip()
    loc = (os.environ.get('LOCATION_ID') or '1739002').strip()
    event = os.environ.get('EVENT', '')
    force = os.environ.get('FORCE', '').lower() == 'true'
    now = now_rome()
    today = now.date().isoformat()

    if not force:
        if event == 'schedule' and (now.hour, now.minute) < (7, 0):
            print(f'Sono le {now:%H:%M} in Italia: aspetto le 7:00. Nessuna chiamata.')
            return 0
        try:
            old = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            old = {}
        if old.get('date') == today:
            print(f'Dati gia\' aggiornati oggi ({today}). Nessuna chiamata a Tripadvisor.')
            return 0

    if not key:
        print('ERRORE: manca il segreto TRIPADVISOR_API_KEY (Settings -> Secrets and variables -> Actions)')
        return 1
    try:
        data = fetch(key, loc)
    except Exception as e:
        print('ERRORE:', e)
        return 1  # data.json resta com'era: nessun dato sovrascritto
    data.update({'date': today, 'updatedAt': now.isoformat(timespec='seconds')})
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('OK:', data['name'], '->', data['total'], 'recensioni', data['counts'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
