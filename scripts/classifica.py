#!/usr/bin/env python3
"""Classifica Tripadvisor dei ristoranti e delle pizzerie di Catania, letta con Apify (Tripadvisor Scraper).

Ogni giorno aggiunge a storico.csv la riga dei Cutilisci presa da data.json (nessuna chiamata).
Una volta a settimana legge le prime posizioni delle due classifiche (solo fino a poco sotto i Cutilisci),
le aggiunge allo storico e stima quanto pesano le recensioni: il risultato va in classifica.json,
che la pagina usa per dire quante recensioni servono per arrivare a una certa posizione.
Solo libreria standard di Python."""
import csv, json, math, os, random, sys, time
import urllib.request, urllib.error
from datetime import datetime, timedelta

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
EVERY_DAYS = int(os.environ.get('EVERY_DAYS') or 1)   # classifica generale: ogni giorno
PIZZA_EVERY_DAYS = int(os.environ.get('PIZZA_EVERY_DAYS') or 7)  # lista pizzerie: una volta a settimana
OBS_DAYS = 28      # giorni di osservazione prima di usare le recensioni recenti nelle stime
WINDOW = 30        # le recensioni 'recenti' sono quelle degli ultimi 30 giorni
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


def features(p, use_recent):
    f = [math.log1p(p['reviews']), p['avg'] or 0]
    if use_recent:
        f.insert(0, math.log1p(p['per_year']))
    return f


LEARN_DAYS = 120   # l'apprendimento usa gli ultimi 120 giorni (la classifica cambia nel tempo)


def snapshots(hist, today=None):
    """Storico per giorno: {data: {id: riga}} solo per le righe con posizione (lette dalla classifica)."""
    days = {}
    for r in hist:
        if r.get('rank') and r.get('reviews'):
            days.setdefault(r['date'], {})[r['id']] = r
    if today:
        keep = (today - timedelta(days=LEARN_DAYS + WINDOW + 15)).isoformat()
        days = {d: v for d, v in days.items() if d >= keep}
    return dict(sorted(days.items()))


def recent_rate(days, loc, day):
    """Recensioni nuove all'anno, misurate sugli ultimi ~30 giorni (almeno 7) prima di 'day'."""
    now = days.get(day, {}).get(loc)
    if not now:
        return None
    d0 = datetime.fromisoformat(day).date()
    best = None
    for gap in sorted(range(7, WINDOW + 16), key=lambda g: abs(g - WINDOW)):  # dal giorno piu' vicino a 30
        then = days.get((d0 - timedelta(days=gap)).isoformat(), {}).get(loc)
        if then:
            best = (gap, then)
            break
    if not best:
        return None
    return max(0, int(now['reviews']) - int(best[1]['reviews'])) / best[0] * 365


def day_rows(days, day, use_recent):
    out = []
    for loc, r in days[day].items():
        p = {'reviews': int(r['reviews']), 'avg': float(r['avg'] or 0)}
        if use_recent:
            p['per_year'] = recent_rate(days, loc, day)
            if p['per_year'] is None:
                continue
        out.append((features(p, use_recent), int(r['rank'])))
    return out


def fit_days(sets, names):
    """Regressione logistica sulle coppie di ogni giorno osservato (chi sta sopra deve avere
    punteggio piu' alto); pesi >= 0. 'sets' e' una lista di giorni, ognuno [(feature, posizione)]."""
    X = [f for day in sets for f, _ in day]
    if len(X) < 3:
        return None
    k = len(names)
    mu = [sum(x[j] for x in X) / len(X) for j in range(k)]
    sd = [math.sqrt(sum((x[j] - mu[j]) ** 2 for x in X) / len(X)) or 1 for j in range(k)]
    diffs = []
    for day in sets:
        Z = [([(f[j] - mu[j]) / sd[j] for j in range(k)], r) for f, r in day]
        diffs += [[a[j] - b[j] for j in range(k)] for a, ra in Z for b, rb in Z if ra < rb]
    if len(diffs) > 6000:  # basta un campione: tiene veloce il calcolo
        diffs = random.Random(1).sample(diffs, 6000)
    if not diffs:
        return None
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
    model = {'kind': 'order', 'features': names, 'mu': mu, 'sd': sd, 'w': [round(x, 5) for x in w], 'n': len(X)}
    model['accuracy'] = accuracy(model, sets)
    return model


def accuracy(model, sets):
    """Quota di coppie di locali che il modello mette nell'ordine giusto."""
    k = len(model['w'])
    ok = tot = 0
    for day in sets:
        sc = [(sum(model['w'][j] * (f[j] - model['mu'][j]) / model['sd'][j] for j in range(k)), r) for f, r in day]
        for a, ra in sc:
            for b, rb in sc:
                if ra < rb:
                    tot += 1
                    ok += a > b
    return round(ok / tot, 4) if tot else None


def learn(hist, today):
    """L'osservatore: confronta ogni giorno la classifica con le recensioni recenti di ogni locale.
    Usa le recensioni recenti nelle stime solo dopo OBS_DAYS giorni e solo se, sull'ultima settimana
    (non usata per imparare), prevede la classifica meglio del modello senza."""
    all_days = snapshots(hist)
    if not all_days:
        return None, {'days': 0}
    first = datetime.fromisoformat(next(iter(all_days))).date()
    observed = (today - first).days + 1
    days = snapshots(hist, today)
    since = (today - timedelta(days=LEARN_DAYS)).isoformat()
    rec_days = [d for d in days if d >= since and len(day_rows(days, d, True)) >= 10]
    info = {'days': observed, 'needed': OBS_DAYS, 'snapshots': len(days), 'recent_days': len(rec_days), 'active': False}
    if observed < OBS_DAYS or len(rec_days) < 10:
        return None, info
    test, train = rec_days[-7:], rec_days[:-7]
    names_r, names_b = ['recenti', 'totale', 'voto'], ['totale', 'voto']
    m_r = fit_days([day_rows(days, d, True) for d in train], names_r)
    m_b = fit_days([day_rows(days, d, False) for d in train], names_b)
    if not m_r or not m_b:
        return None, info
    test_rows = [day_rows(days, d, True) for d in test]
    acc_r = accuracy(m_r, test_rows)
    acc_b = accuracy(m_b, [[(f[1:], r) for f, r in day] for day in test_rows])  # stessi locali, senza recenti
    info.update({'test_recent': acc_r, 'test_base': acc_b})
    if acc_r is None or acc_b is None or acc_r < acc_b + 0.01:
        return None, info
    info['active'] = True
    model = fit_days([day_rows(days, d, True) for d in rec_days], names_r)
    model['recent_window'] = WINDOW
    return model, info


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

    # 2) Ogni giorno la classifica generale, una volta a settimana la lista delle pizzerie
    old = load_json(OUT)
    last = None if old.get('error') else old.get('date')
    if not force and last and (today - datetime.fromisoformat(last).date()).days < EVERY_DAYS:
        print(f'Classifica gia\' letta oggi ({last}). Nessuna chiamata.')
        return 0
    if not token:
        print('Classifica: manca il segreto APIFY_TOKEN. Nessuna chiamata.')
        return 0
    pdate = old.get('pizza_date')
    read_pizza = force or not old.get('pizzerie') or not pdate or \
        (today - datetime.fromisoformat(pdate).date()).days >= PIZZA_EVERY_DAYS
    try:
        gen = [parse_item(x) for x in scrape(token, LISTS['g'], TOP['g'])]
        piz = [parse_item(x) for x in scrape(token, LISTS['p'], TOP['p'])] if read_pizza else []
    except Exception as e:
        print('ERRORE:', e)
        return 1
    if not read_pizza:
        # Pizzerie gia' note: la loro posizione la ricavo dalla classifica generale di oggi
        ids = set(old.get('pizzerie') or [])
        piz = [p for p in gen if p['id'] in ids]
        pdate = old.get('pizza_date')
    else:
        pdate = today.isoformat()
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

    # 3) Storico di oggi, poi ritmo di nuove recensioni (ultimi 30 giorni) e apprendimento
    sel = sorted(places.values(), key=lambda p: p['rank'])
    done = {r['id'] for r in hist if r['date'] == today.isoformat() and r.get('rank')}
    rows = [dict(p, date=today.isoformat(), pizza_total=None) for p in sel if str(p['id']) not in done]
    append_hist(rows)
    hist += [{k: '' if r.get(k) is None else str(r[k]) for k in HIST_COLS} for r in rows]
    days = snapshots(hist, today)
    for p in sel:
        r = recent_rate(days, str(p['id']), today.isoformat())
        p['per_year'] = round(r, 1) if r is not None else None
        p['per_year_src'] = 'storico' if r is not None else None

    model, info = learn(hist, today)
    if model:
        # Locali senza storico sufficiente: uso il ritmo mediano, per non escluderli
        known = sorted(p['per_year'] for p in sel if p['per_year'] is not None)
        for p in sel:
            if p['per_year'] is None and known:
                p['per_year'], p['per_year_src'] = known[len(known) // 2], 'mediana'
    else:
        model = fit_raw(sel) or fit_days([[(features(p, False), p['rank']) for p in sel]], ['totale', 'voto'])
    mine = places[me]
    out = {
        'date': today.isoformat(), 'updatedAt': now.isoformat(timespec='seconds'), 'source': 'apify',
        'me': me, 'pizza_source': 'api' if pz else None,
        'rank_total': mine['rank_total'], 'pizza_total': None,
        'model': model, 'learning': info, 'places': sel,
        'pizzerie': sorted(p['id'] for p in pz), 'pizza_date': pdate,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    q = (model or {}).get('r2', (model or {}).get('accuracy'))
    print(f"OK: Cutilisci n. {mine['rank']} (pizzerie: {mine['pizza_rank']}), {len(sel)} locali letti, "
          f"modello {(model or {}).get('kind')} qualita' {q}, punteggio Tripadvisor: {'si' if mine['raw'] is not None else 'no'}")
    print(f"Osservazione: {info.get('days')} giorni su {OBS_DAYS}, recensioni recenti nelle stime: "
          f"{'si' if info.get('active') else 'non ancora'} (prova sull'ultima settimana: con {info.get('test_recent')}, "
          f"senza {info.get('test_base')})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
