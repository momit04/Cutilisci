#!/usr/bin/env python3
"""Classifica Tripadvisor dei ristoranti e delle pizzerie di Catania, letta con Apify (Tripadvisor Scraper).

Ogni giorno aggiunge a storico.csv la riga dei Cutilisci presa da data.json (nessuna chiamata).
Una volta a settimana legge le prime posizioni delle due classifiche (solo fino a poco sotto i Cutilisci),
le aggiunge allo storico e stima quanto pesano le recensioni: il risultato va in classifica.json,
che la pagina usa per dire quante recensioni servono per arrivare a una certa posizione.
Solo libreria standard di Python."""
import csv, json, math, os, random, sys, time
import urllib.request, urllib.error
from datetime import datetime

from fetch import now_rome

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data.json')
OUT = os.path.join(ROOT, 'classifica.json')
HIST = os.path.join(ROOT, 'storico.csv')
HIST_COLS = ['date', 'id', 'name', 'rank', 'rank_total', 'pizza_rank', 'pizza_total', 'reviews', 'avg', 'raw']

LISTS = {
    'g': os.environ.get('URL_RISTORANTI') or 'https://www.tripadvisor.it/Restaurants-g187888-Catania_Province_of_Catania_Sicily.html',
    'p': os.environ.get('URL_PIZZERIE') or 'https://www.tripadvisor.it/Restaurants-g187888-c31-Catania_Province_of_Catania_Sicily.html',
}
# Tripadvisor mostra prima i locali 'in evidenza': per coprire le prime 60 posizioni ne leggo di piu'
TOP = {'g': int(os.environ.get('POSIZIONI') or 150), 'p': int(os.environ.get('POSIZIONI_PIZZERIE') or 60)}
EVERY_DAYS = int(os.environ.get('EVERY_DAYS') or 7)   # una volta a settimana
ACTOR = os.environ.get('APIFY_ACTOR') or 'maxcopell~tripadvisor'
APIFY = os.environ.get('APIFY_API_BASE') or 'https://api.apify.com/v2'


def apify(method, path, token, body=None, timeout=60):
    url = APIFY + path + ('&' if '?' in path else '?') + 'token=' + token
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode('utf-8', 'ignore') or 'null')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'ignore')[:300]


def scrape(token, url, top):
    """Avvia lo scraper su una pagina di classifica, aspetta la fine e restituisce i locali."""
    s, run = apify('POST', f'/acts/{ACTOR}/runs', token, {
        'startUrls': [{'url': url}], 'maxItemsPerQuery': top, 'includeRestaurants': True,
        'includeHotels': False, 'includeAttractions': False, 'includeVacationRentals': False,
        'includeTags': False, 'includeNearbyResults': False, 'language': 'it', 'currency': 'EUR'})
    if s >= 300:
        raise RuntimeError(f'Apify non ha avviato lo scraper ({s}): {run}')
    run = run['data']
    t0 = time.time()
    while run.get('status') in ('READY', 'RUNNING'):
        if time.time() - t0 > 1500:
            raise RuntimeError('Apify: lo scraper non ha finito in 25 minuti')
        time.sleep(15)
        s, r = apify('GET', f"/actor-runs/{run['id']}", token)
        if s == 200:
            run = r['data']
    if run.get('status') != 'SUCCEEDED':
        raise RuntimeError(f"Apify: lo scraper e' finito con stato {run.get('status')}")
    s, rows = apify('GET', f"/datasets/{run['defaultDatasetId']}/items?clean=true&format=json", token, timeout=120)
    if s != 200 or not isinstance(rows, list):
        raise RuntimeError(f'Apify: non riesco a leggere i risultati ({s})')
    return rows


def num(v):
    try:
        return int(str(v).replace('.', '').replace(',', '').strip())
    except (TypeError, ValueError):
        return None


def parse_item(x):
    h = x.get('ratingHistogram') or {}
    counts = {k: num(h.get(f'count{k}')) or 0 for k in range(1, 6)}
    n = sum(counts.values()) or num(x.get('numberOfReviews')) or 0
    avg = sum(k * v for k, v in counts.items()) / sum(counts.values()) if sum(counts.values()) else x.get('rating')
    raw = x.get('rawRanking')
    return {
        'id': num(x.get('locationId') or x.get('id')), 'name': x.get('name'), 'url': x.get('webUrl') or x.get('url'),
        'rank': num(x.get('rankingPosition')), 'rank_total': num(x.get('rankingDenominator')),
        'reviews': n, 'avg': round(avg, 4) if avg else None,
        'raw': float(raw) if isinstance(raw, (int, float)) else None,
    }


def read_hist():
    try:
        with open(HIST, encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def append_hist(rows):
    new = not os.path.exists(HIST)
    if not new:
        with open(HIST, encoding='utf-8', newline='') as f:
            r = csv.DictReader(f)
            if r.fieldnames != HIST_COLS:  # storico con colonne vecchie: lo riscrivo con quelle nuove
                old = list(r)
                with open(HIST, 'w', encoding='utf-8', newline='') as g:
                    w = csv.DictWriter(g, fieldnames=HIST_COLS, extrasaction='ignore')
                    w.writeheader()
                    w.writerows(old)
    with open(HIST, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=HIST_COLS, extrasaction='ignore')
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: ('' if r.get(k) is None else r.get(k)) for k in HIST_COLS})


def per_year_from_hist(hist, loc, reviews, today):
    """Ritmo di nuove recensioni dallo storico, se copre almeno 4 settimane (fino a un anno)."""
    rows = [r for r in hist if r['id'] == str(loc) and r['reviews']]
    old = [r for r in rows if 28 <= (today - datetime.fromisoformat(r['date']).date()).days <= 400]
    if not old:
        return None
    first = min(old, key=lambda r: r['date'])
    days = (today - datetime.fromisoformat(first['date']).date()).days
    return round(max(0, reviews - int(first['reviews'])) / days * 365, 1)


def features(p, use_recent):
    f = [math.log1p(p['reviews']), p['avg'] or 0]
    if use_recent:
        f.insert(0, math.log1p(p['per_year']))
    return f


def fit_raw(places):
    """Se Tripadvisor fornisce il punteggio interno (rawRanking), imparo come cambia con
    recensioni recenti, totale e voto (minimi quadrati, pesi >= 0): le distanze sono quelle vere."""
    pl = [p for p in places if p.get('raw') is not None and p.get('reviews')]
    if len(pl) < 10:
        return None
    use_recent = all(p.get('per_year') is not None for p in pl)
    names = (['recenti'] if use_recent else []) + ['totale', 'voto']
    X = [features(p, use_recent) for p in pl]
    y = [p['raw'] for p in pl]
    k = len(names)
    mu = [sum(x[j] for x in X) / len(X) for j in range(k)]
    sd = [math.sqrt(sum((x[j] - mu[j]) ** 2 for x in X) / len(X)) or 1 for j in range(k)]
    Z = [[(x[j] - mu[j]) / sd[j] for j in range(k)] for x in X]
    ym = sum(y) / len(y)
    active = list(range(k))
    while True:
        # equazioni normali sulle colonne attive (eliminazione di Gauss)
        A = [[sum(z[i] * z[j] for z in Z) for j in active] + [sum(z[i] * (yy - ym) for z, yy in zip(Z, y))]
             for i in active]
        n = len(active)
        for c in range(n):
            piv = max(range(c, n), key=lambda r: abs(A[r][c]))
            A[c], A[piv] = A[piv], A[c]
            if abs(A[c][c]) < 1e-12:
                A[c][c] = 1e-12
            for r in range(n):
                if r != c:
                    f = A[r][c] / A[c][c]
                    A[r] = [A[r][j] - f * A[c][j] for j in range(n + 1)]
        sol = {active[i]: A[i][n] / A[i][i] for i in range(n)}
        neg = [j for j, v in sol.items() if v < 0]
        if not neg or len(active) == 1:
            break
        active = [j for j in active if j not in neg]
    w = [max(0.0, sol.get(j, 0.0)) for j in range(k)]
    pred = [ym + sum(w[j] * z[j] for j in range(k)) for z in Z]
    ss = sum((a - b) ** 2 for a, b in zip(y, pred))
    st = sum((a - ym) ** 2 for a in y) or 1
    return {'kind': 'raw', 'features': names, 'mu': mu, 'sd': sd, 'w': [round(x, 6) for x in w],
            'b': ym, 'r2': round(1 - ss / st, 4), 'n': len(pl)}


def fit(places):
    """Impara dai dati quanto pesano recensioni recenti, numero totale e voto medio.
    Regressione logistica sulle coppie (chi sta sopra deve avere punteggio piu' alto); pesi >= 0."""
    pl = [p for p in places if p.get('rank') and p.get('reviews')]
    if len(pl) < 3:
        return None
    use_recent = all(p.get('per_year') is not None for p in pl)
    names = (['recenti'] if use_recent else []) + ['totale', 'voto']
    X = [features(p, use_recent) for p in pl]
    k = len(names)
    mu = [sum(x[j] for x in X) / len(X) for j in range(k)]
    sd = [math.sqrt(sum((x[j] - mu[j]) ** 2 for x in X) / len(X)) or 1 for j in range(k)]
    Z = [[(x[j] - mu[j]) / sd[j] for j in range(k)] for x in X]
    pairs = [(Z[a], Z[b]) for a in range(len(pl)) for b in range(len(pl)) if pl[a]['rank'] < pl[b]['rank']]
    if len(pairs) > 6000:  # basta un campione: tiene veloce il calcolo
        pairs = random.Random(1).sample(pairs, 6000)
    diffs = [[a[j] - b[j] for j in range(k)] for a, b in pairs]
    w = [1.0] * k
    lam, lr = 0.01, 0.5
    for _ in range(1500):
        g = [lam * wj for wj in w]
        for d in diffs:
            m = sum(w[j] * d[j] for j in range(k))
            s = -1 / (1 + math.exp(min(m, 50)))
            for j in range(k):
                g[j] += s * d[j] / len(diffs)
        w = [max(0.0, w[j] - lr * g[j]) for j in range(k)]
    ok = sum(1 for d in diffs if sum(w[j] * d[j] for j in range(k)) > 0)
    return {'kind': 'order', 'features': names, 'mu': mu, 'sd': sd, 'w': [round(x, 5) for x in w],
            'accuracy': round(ok / len(diffs), 4) if diffs else None, 'pairs': len(diffs), 'n': len(pl)}


def load_json(path):
    try:
        return json.load(open(path, encoding='utf-8'))
    except Exception:
        return {}


def main():
    token = os.environ.get('APIFY_TOKEN', '').strip()
    me = int((os.environ.get('LOCATION_ID') or '1739002').strip())
    force = os.environ.get('FORCE_CLASSIFICA', '').lower() == 'true'
    now = now_rome()
    today = now.date()
    hist = read_hist()

    # 1) Ogni giorno: riga dei Cutilisci dallo stesso data.json di oggi (0 chiamate)
    d = load_json(DATA)
    if d.get('date') == today.isoformat() and not any(r['date'] == d['date'] and r['id'] == str(me) for r in hist):
        c = d.get('counts') or [0] * 5
        n = sum(c)
        row = {'date': d['date'], 'id': me, 'name': d.get('name'), 'reviews': n,
               'avg': round(sum(v * s for v, s in zip(c, (5, 4, 3, 2, 1))) / n, 4) if n else None}
        append_hist([row])
        hist.append({k: '' if row.get(k) is None else str(row[k]) for k in HIST_COLS})
        print('Storico: aggiunta la riga di oggi dei Cutilisci')

    # 2) Una volta a settimana: le classifiche
    old = load_json(OUT)
    last = None if old.get('error') else old.get('date')
    if not force and last and (today - datetime.fromisoformat(last).date()).days < EVERY_DAYS:
        print(f'Classifica letta il {last}: la rileggo tra {EVERY_DAYS} giorni. Nessuna chiamata.')
        return 0
    if not token:
        print('Classifica: manca il segreto APIFY_TOKEN. Nessuna chiamata.')
        return 0
    try:
        gen = [parse_item(x) for x in scrape(token, LISTS['g'], TOP['g'])]
        piz = [parse_item(x) for x in scrape(token, LISTS['p'], TOP['p'])]
    except Exception as e:
        print('ERRORE:', e)
        return 1
    mine = next((p for p in gen + piz if p['id'] == me), None)
    if not mine:
        print(f"ERRORE: i Cutilisci non sono tra i locali letti: aumenta POSIZIONI")
        return 1
    # Solo i locali della stessa classifica dei Cutilisci (fuori Catania la classifica e' un'altra)
    tot = mine['rank_total']
    same = lambda p: p['id'] and p['rank'] and (not tot or p['rank_total'] == tot)
    gen, piz = [p for p in gen if same(p)], [p for p in piz if same(p)]
    places = {p['id']: p for p in gen}
    # Posizione tra le pizzerie: ordine della classifica generale tra i locali della lista pizzerie
    pz = sorted(piz, key=lambda p: p['rank'])
    for i, p in enumerate(pz, 1):
        q = places.setdefault(p['id'], p)
        q['pizza_rank'] = i
    for p in places.values():
        p.setdefault('pizza_rank', None)
        p['pizza'] = p['pizza_rank'] is not None
    places.setdefault(me, mine)
    gaps = [r for r in range(1, mine['rank']) if r not in {p['rank'] for p in places.values()}]
    if gaps:
        print(f'Posizioni sopra ai Cutilisci non lette: {gaps}')

    # 3) Ritmo di nuove recensioni: dallo storico (servono almeno 4 settimane)
    sel = sorted(places.values(), key=lambda p: p['rank'])
    for p in sel:
        p['per_year'] = per_year_from_hist(hist, p['id'], p['reviews'], today)
        p['per_year_src'] = 'storico' if p['per_year'] is not None else None
    done = {r['id'] for r in hist if r['date'] == today.isoformat() and r.get('rank')}
    append_hist([dict(p, date=today.isoformat(), pizza_total=None) for p in sel if str(p['id']) not in done])

    model = fit_raw(sel) or fit(sel)
    mine = places[me]
    out = {
        'date': today.isoformat(), 'updatedAt': now.isoformat(timespec='seconds'), 'source': 'apify',
        'me': me, 'pizza_source': 'api' if pz else None,
        'rank_total': mine['rank_total'], 'pizza_total': None,
        'model': model, 'places': sel,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    q = (model or {}).get('r2', (model or {}).get('accuracy'))
    print(f"OK: Cutilisci n. {mine['rank']} (pizzerie: {mine['pizza_rank']}), {len(sel)} locali letti, "
          f"modello {(model or {}).get('kind')} qualita' {q}, punteggio Tripadvisor: {'si' if mine['raw'] is not None else 'no'}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
