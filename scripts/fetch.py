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


def parse_rankings(d):
    """Posizioni in classifica del locale, in forma compatta.
    Cerco ovunque nella risposta gli oggetti con un campo 'rank' (il nome del contenitore puo' cambiare)."""
    found = []

    def walk(v):
        if isinstance(v, dict):
            for k in ('rank', 'ranking', 'position', 'rank_position'):
                x = v.get(k)
                if isinstance(x, int) or (isinstance(x, str) and re.fullmatch(r'\d[\d.,]*', x.strip())):
                    found.append(dict(v, rank=int(re.sub(r'\D', '', str(x)))))
                    break
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk({k: v for k, v in d.items() if k not in ('reviews',)})
    out = []
    for r in found:
        tot = r.get('total', r.get('ranking_out_of', r.get('out_of', r.get('total_count'))))
        if isinstance(tot, str) and re.fullmatch(r'\d[\d.,]*', tot.strip()):
            tot = int(re.sub(r'\D', '', tot))
        r = dict(r, total=tot)
        out.append({k: r.get(k) for k in ('rank', 'total', 'category', 'category_id', 'geo', 'geo_id', 'display_text',
                                          'ranking_string', 'geo_location_name')
                    if r.get(k) is not None})
    return out


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
    return {'name': name, 'counts': counts, 'total': sum(counts), 'rankings': parse_rankings(d),
            'rank_raw': raw_rank_award(d)}


def raw_rank_award(d):
    """Copia grezza (ridotta) di tutto cio' che nella risposta riguarda classifica o premi:
    serve a scoprire come l'API Terra chiama questi campi. Nessun dato inventato, solo cio' che arriva."""
    hits = []

    def walk(v, path):
        if len(hits) >= 20:
            return
        if isinstance(v, dict):
            for k, x in v.items():
                p = f'{path}.{k}' if path else k
                if re.search(r'rank|award|position|popular', k, re.I):
                    s = json.dumps(x, ensure_ascii=False)
                    hits.append({'campo': p, 'valore': json.loads(s) if len(s) <= 800 else s[:800] + '…'})
                else:
                    walk(x, p)
        elif isinstance(v, list):
            for i, x in enumerate(v[:30]):
                walk(x, f'{path}[{i}]')
    walk({k: v for k, v in d.items() if k not in ('reviews', 'photos', 'descriptions')}, '')
    return {'campi_principali': sorted(d.keys()), 'trovati': hits}


CONTENT_API = os.environ.get('TA_CONTENT_API_BASE', 'https://api.content.tripadvisor.com/api/v1')


def fetch_content(key, loc):
    """API Content ufficiale: /location/{id}/details restituisce ranking_data e awards."""
    url = f"{CONTENT_API}/location/{loc}/details?key={key}&language=it&currency=EUR"
    req = urllib.request.Request(url, headers={'accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode('utf-8', 'ignore'))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode('utf-8', 'ignore')[:200]}")
    out = {}
    rd = d.get('ranking_data') or {}
    if rd.get('ranking'):
        out['ranking_api'] = {
            'pos': int(str(rd.get('ranking')).replace('.', '').replace(',', '')),
            'totale': int(str(rd.get('ranking_out_of') or 0).replace('.', '').replace(',', '')) or None,
            'testo': rd.get('ranking_string'),
            'geo': rd.get('geo_location_name'),
        }
    aw = d.get('awards') or []
    out['awards'] = [{'tipo': a.get('award_type'), 'anno': a.get('year'), 'nome': a.get('display_name')} for a in aw]
    for k in ('rating', 'num_reviews'):
        if d.get(k) is not None:
            out['content_' + k] = d.get(k)
    print('API Content:', out.get('ranking_api'), '| premi:', len(out['awards']))
    return out


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
    # Classifica e premi dall'API Content ufficiale (facoltativa: serve il segreto TRIPADVISOR_CONTENT_KEY).
    # Una sola chiamata al giorno, nessuna visita alla pagina del locale.
    ckey = os.environ.get('TRIPADVISOR_CONTENT_KEY', '').strip()
    if ckey:
        try:
            data.update(fetch_content(ckey, loc))
        except Exception as e:
            print('Classifica API Content non disponibile:', e)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('OK:', data['name'], '->', data['total'], 'recensioni', data['counts'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
