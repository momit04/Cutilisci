#!/usr/bin/env python3
"""Classifica Tripadvisor dei ristoranti e delle pizzerie di Catania (API Terra).

Ogni giorno aggiunge a storico.csv la riga dei Cutilisci presa da data.json (nessuna chiamata in piu').
Una volta a settimana legge posizione e recensioni dei locali sopra (e poco sotto) ai Cutilisci,
li aggiunge allo storico e stima come Tripadvisor ordina la classifica: il risultato va in classifica.json,
che la pagina usa per dire quante recensioni servono per arrivare a una certa posizione.
Solo libreria standard di Python."""
import csv, json, math, os, random, sys, time
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fetch import call, parse_rankings, now_rome

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data.json')
OUT = os.path.join(ROOT, 'classifica.json')
HIST = os.path.join(ROOT, 'storico.csv')
HIST_COLS = ['date', 'id', 'name', 'rank', 'rank_total', 'pizza_rank', 'pizza_total', 'reviews', 'avg']

GEO = int(os.environ.get('GEO_ID') or 187888)              # Catania
EVERY_DAYS = int(os.environ.get('EVERY_DAYS') or 7)         # ogni quanti giorni rileggere i concorrenti
MARGIN = int(os.environ.get('MARGIN') or 5)                 # quante posizioni sotto ai Cutilisci seguire
# Riquadro in cui cercare i ristoranti di Catania (sud-ovest, nord-est)
BBOX = [float(v) for v in (os.environ.get('BBOX') or '37.45,15.00,37.56,15.13').split(',')]
MIN_RATING = os.environ.get('DISCOVERY_MIN_RATING') or '4'
MAX_DISCOVERY = int(os.environ.get('MAX_DISCOVERY') or 1000)
REDISCOVER_DAYS = 30

billed = 0  # entita' fatturate da Tripadvisor in questa esecuzione (stima)


def api(method, path, key, params=None, body=None):
    q = dict(params or {})
    q.setdefault('version', '1')
    url = path + '?' + urlencode(q, doseq=True)
    for wait in (2, 4, 8, 16, None):
        status, text, _ = call(method, url, key, body)
        if status != 429 or wait is None:
            break
        time.sleep(wait)
    data = None
    if text:
        try:
            data = json.loads(text)
        except ValueError:
            pass
    return status, data, text


def items(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ('data', 'content', 'results', 'locations', 'items'):
            if isinstance(data.get(k), list):
                return data[k]
    return []


def total_pages(data):
    if not isinstance(data, dict):
        return None
    p = data.get('pagination') or data.get('metadata') or {}
    return p.get('total_pages')


def discover(key):
    """Ristoranti nel riquadro di Catania (catalogo, non limitato dalla allowlist), con il numero di recensioni.
    Ordinati dal piu' recensito: chi sta in alto in classifica di solito ne ha tante."""
    global billed
    found, with_cat = {}, True
    for tile in tiles():
        with_cat = search_tile(key, tile, found, with_cat)
    print(f'Trovati {len(found)} ristoranti nel riquadro di Catania')
    return sorted(found, key=lambda i: -found[i])


def tiles():
    """Tripadvisor accetta riquadri di massimo 50 km2: divido BBOX in pezzi da circa 40."""
    sw_lat, sw_lon, ne_lat, ne_lon = BBOX
    km_lat = (ne_lat - sw_lat) * 111.0
    km_lon = (ne_lon - sw_lon) * 111.0 * math.cos(math.radians((sw_lat + ne_lat) / 2))
    n_lat, n_lon = max(1, math.ceil(km_lat / 6.3)), max(1, math.ceil(km_lon / 6.3))
    dl, dn = (ne_lat - sw_lat) / n_lat, (ne_lon - sw_lon) / n_lon
    return [(round(sw_lat + a * dl, 5), round(sw_lon + b * dn, 5), round(sw_lat + (a + 1) * dl, 5),
             round(sw_lon + (b + 1) * dn, 5)) for a in range(n_lat) for b in range(n_lon)]


def search_tile(key, tile, found, with_cat):
    global billed
    sw_lat, sw_lon, ne_lat, ne_lon = tile
    base = {'sw_lat': sw_lat, 'sw_lon': sw_lon, 'ne_lat': ne_lat, 'ne_lon': ne_lon, 'size': 20}
    if MIN_RATING:
        base['min_rating'] = MIN_RATING
    page = 1
    while len(found) < MAX_DISCOVERY:
        time.sleep(0.5)  # la ricerca ha un limite di richieste piu' basso
        q = dict(base, page=page)
        if with_cat:
            q['category'] = 'RESTAURANT'
        status, data, text = api('GET', '/catalog/locations/nearby', key, q)
        if status == 400 and with_cat and page == 1:
            with_cat = False  # categoria non accettata: filtro dopo, dai dettagli
            continue
        if status != 200:
            raise RuntimeError(f'Ricerca dei ristoranti: Tripadvisor ha risposto {status}: {text[:300]}')
        got = items(data)
        billed += len(got)
        for x in got:
            loc = x.get('location') or x if isinstance(x, dict) else {}
            if loc.get('id') is not None:
                found[int(loc['id'])] = int((loc.get('overall_rating') or {}).get('count') or 0)
        tp = total_pages(data)
        if not got or (tp is not None and page >= tp):
            break
        page += 1
    return with_cat


allowed = None  # locali gia' nella allowlist (letta una volta, la lettura non e' fatturata)


def allow(key, ids):
    global allowed
    if allowed is None:
        allowed = set()
        page = 0
        while page < 50:
            s, data, _ = api('GET', '/allowlist', key, {'page': page, 'version': 'v1'})
            got = items(data) if s == 200 else []
            if s == 200 and isinstance(data, dict) and not got:
                got = data.get('allowlist') or []
            allowed |= {int(x if not isinstance(x, dict) else x.get('id') or x.get('location_id') or 0) for x in got}
            if len(got) < 1000:
                break
            page += 1
    ids = [i for i in ids if i not in allowed]
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        s, _, t = api('POST', '/allowlist', key, body={'operation_type': 'APPEND', 'allowlist': chunk})
        if s >= 300:
            print(f'Allowlist: risposta {s} {t[:200]}')
        else:
            allowed |= set(chunk)
        time.sleep(1)


def details(key, ids):
    global billed
    out = {}
    for i in range(0, len(ids), 20):
        chunk = ids[i:i + 20]
        status, data, text = api('GET', '/locations', key, {'id': ','.join(map(str, chunk))})
        if status != 200:
            raise RuntimeError(f'Dettagli dei ristoranti: Tripadvisor ha risposto {status}: {text[:300]}')
        for d in items(data):
            out[int(d['id'])] = d
        billed += len(items(data))
    return out


def text_of(v):
    return json.dumps(v, ensure_ascii=False).lower() if v else ''


def is_pizza_ranking(r):
    return 'pizz' in text_of(r) or str(r.get('category_id')) in ('31', 'c31')


def pick_rank(rankings, pizza):
    rs = [r for r in rankings if is_pizza_ranking(r) == pizza]
    rs = [r for r in rs if r.get('geo_id') == GEO] or ([] if pizza else rs)
    if not rs:
        return None
    return max(rs, key=lambda r: r.get('total') or 0)


def parse_place(d):
    names = d.get('names') or []
    name = next((n['value'] for n in names if n.get('primary')), names[0]['value'] if names else str(d.get('id')))
    br = (d.get('traveler_ratings') or {}).get('breakdowns') or []
    by = {int(b.get('rating', 0)): int(b.get('count', 0) or 0) for b in br}
    n = sum(by.values())
    rankings = parse_rankings(d)
    gen, piz = pick_rank(rankings, False), pick_rank(rankings, True)
    cuisine = text_of(d.get('categories')) + text_of(d.get('attributes')) + text_of(d.get('cuisines'))
    url = ((d.get('urls') or {}).get('tripadvisor') or {}).get('main')
    return {
        'id': int(d['id']), 'name': name, 'url': url,
        'rank': gen and gen['rank'], 'rank_total': gen and gen.get('total'),
        'pizza_rank': piz and piz['rank'], 'pizza_total': piz and piz.get('total'),
        'pizza': bool(piz) or 'pizz' in cuisine,
        'reviews': n, 'avg': round(sum(k * v for k, v in by.items()) / n, 4) if n else None,
        'status': (d.get('status') or {}).get('value'),
    }


def review_date(r):
    for k, v in r.items():
        if 'publish' in k and isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00')[:19]).date()
            except ValueError:
                pass
    return None


def per_year_from_reviews(key, loc, today):
    """Recensioni dell'ultimo anno, dalle 20 piu' recenti (una sola chiamata, stima)."""
    global billed
    cutoff = today - timedelta(days=365)
    status, data, text = api('GET', f'/locations/{loc}/reviews', key, {
        'published_after_ts': cutoff.isoformat(), 'sort_by': 'MOST_RECENT', 'size': 20, 'page': 1})
    if status in (401, 403):
        raise PermissionError(text[:200])
    if status != 200:
        return None
    billed += 1
    got = items(data)
    dates = sorted((x for x in (review_date(r) for r in got if isinstance(r, dict)) if x), reverse=True)
    pag = data.get('pagination') or {} if isinstance(data, dict) else {}
    count = pag.get('total_elements', len(dates))
    if len(dates) >= 3 and (len(dates) >= 20 or len(dates) >= count):
        # L'API puo' dare solo le ultime N recensioni: se il ritmo delle ultime ricevute
        # dice molto di piu' del totale, il totale e' tagliato e uso il ritmo.
        rate = len(dates) / max((today - dates[-1]).days, 7) * 365
        return round(max(count, rate) if rate > count * 1.3 else count, 1)
    return float(count)


def read_hist():
    try:
        with open(HIST, encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def append_hist(rows):
    new = not os.path.exists(HIST)
    with open(HIST, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=HIST_COLS)
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
    return {'features': names, 'mu': mu, 'sd': sd, 'w': [round(x, 5) for x in w],
            'accuracy': round(ok / len(diffs), 4) if diffs else None, 'pairs': len(diffs), 'n': len(pl)}


def load_json(path):
    try:
        return json.load(open(path, encoding='utf-8'))
    except Exception:
        return {}


def main():
    key = os.environ.get('TRIPADVISOR_API_KEY', '').strip()
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
        rk = d.get('rankings') or []
        gen, piz = pick_rank(rk, False), pick_rank(rk, True)
        row = {'date': d['date'], 'id': me, 'name': d.get('name'), 'reviews': n,
               'avg': round(sum(v * s for v, s in zip(c, (5, 4, 3, 2, 1))) / n, 4) if n else None,
               'rank': gen and gen['rank'], 'rank_total': gen and gen.get('total'),
               'pizza_rank': piz and piz['rank'], 'pizza_total': piz and piz.get('total')}
        append_hist([row])
        hist.append({k: str(v) if v is not None else '' for k, v in row.items()})
        print('Storico: aggiunta la riga di oggi dei Cutilisci')

    # 2) Una volta a settimana: i concorrenti
    old = load_json(OUT)
    if old.get('error') and not force:
        print('Classifica sospesa:', old['error'], 'Nessuna chiamata.')
        return 0
    last = old.get('date')
    if not force and last and (today - datetime.fromisoformat(last).date()).days < EVERY_DAYS:
        print(f'Classifica letta il {last}: la rileggo tra {EVERY_DAYS} giorni. Nessuna chiamata.')
        return 0
    if not key:
        print('ERRORE: manca il segreto TRIPADVISOR_API_KEY')
        return 1

    tracked = old.get('tracked') or []
    disc_at = old.get('discoveredAt')
    places = {}

    def read(ids):
        ids = [i for i in ids if i not in places]
        allow(key, ids)
        got = details(key, ids)
        if me in got:
            d = got[me]
            print('Campi del locale:', ', '.join(sorted(d.keys())))
            print('Posizioni trovate:', json.dumps(parse_rankings(d), ensure_ascii=False))
        places.update({i: parse_place(x) for i, x in got.items()})

    def limit():
        return ((places.get(me) or {}).get('rank') or 85) + MARGIN

    def missing():
        seen = {p['rank'] for p in places.values() if p['rank']}
        return [r for r in range(1, limit() + 1) if r not in seen]

    def search():
        # Leggo i dettagli a gruppi, dal piu' recensito, e mi fermo appena ho tutte le posizioni che servono
        # (alcune posizioni possono essere di locali fuori dalla ricerca, es. voto sotto 4: le lascio perdere)
        cand = discover(key)
        idle = 0
        for i in range(0, len(cand), 40):
            before = len(missing())
            if before <= max(2, limit() // 20) or idle >= 2:
                break
            read(cand[i:i + 40])
            idle = idle + 1 if len(missing()) >= before else 0
        print(f'Letti i dettagli di {len(places)} locali; posizioni ancora mancanti: {len(missing())}')

    try:
        read([me])
        if me in places and not places[me]['rank']:
            # Senza posizione dei Cutilisci non ha senso cercare i concorrenti: mi fermo e non spendo nulla
            msg = ("L'API Tripadvisor non fornisce la posizione in classifica con questa chiave "
                   "(manca il campo rankings): classifica non disponibile.")
            print(msg)
            with open(OUT, 'w', encoding='utf-8') as f:
                json.dump({'date': today.isoformat(), 'updatedAt': now.isoformat(timespec='seconds'),
                           'error': msg}, f, ensure_ascii=False, indent=1)
                f.write('\n')
            return 0
        read([i for i in tracked if i != me])
        if not tracked:
            search()
            disc_at = today.isoformat()
        else:
            # Se nella fascia mancano posizioni (qualcuno nuovo e' salito), ricerco (max 1 volta al mese)
            stale = not disc_at or (today - datetime.fromisoformat(disc_at).date()).days >= REDISCOVER_DAYS
            if len(missing()) > 2 and stale:
                print(f'Mancano {len(missing())} posizioni nella fascia seguita: cerco di nuovo i ristoranti')
                search()
                disc_at = today.isoformat()
        lim = limit()
        plim = ((places.get(me) or {}).get('pizza_rank') or 0) + MARGIN
        keep = {i for i, p in places.items() if i == me or (p['rank'] and p['rank'] <= lim)
                or (p['pizza_rank'] and p['pizza_rank'] <= plim)}
    except RuntimeError as e:
        print('ERRORE:', e)
        return 1
    if me not in places:
        print('ERRORE: Tripadvisor non ha restituito i dati dei Cutilisci')
        return 1

    # 3) Ritmo di nuove recensioni (recensioni all'anno): dallo storico se basta, altrimenti dalle ultime recensioni
    prev = {p['id']: p for p in old.get('places') or []}
    reviews_ok = True
    sel = sorted((places[i] for i in keep), key=lambda p: (p['rank'] or 10 ** 6))
    for p in sel:
        h = per_year_from_hist(hist, p['id'], p['reviews'], today)
        if h is not None:
            p['per_year'], p['per_year_src'] = h, 'storico'
            continue
        q = prev.get(p['id']) or {}
        if q.get('per_year_src') == 'recensioni' and q.get('per_year_date') and \
                (today - datetime.fromisoformat(q['per_year_date']).date()).days < 30:
            p.update({k: q[k] for k in ('per_year', 'per_year_src', 'per_year_date')})
            continue
        if reviews_ok:
            try:
                p['per_year'] = per_year_from_reviews(key, p['id'], today)
                p['per_year_src'], p['per_year_date'] = 'recensioni', today.isoformat()
            except PermissionError as e:
                print('Recensioni recenti non disponibili con questa chiave:', e)
                reviews_ok = False
        p.setdefault('per_year', None)

    # Classifica pizzerie: se l'API non la da', la ricavo dall'ordine generale dei locali che fanno pizza
    pizza_src = 'api' if any(p['pizza_rank'] for p in sel) else 'stima'
    if pizza_src == 'stima':
        places[me]['pizza'] = True  # i Cutilisci sono una pizzeria
        pz = sorted((p for p in sel if p['pizza'] and p['rank']), key=lambda p: p['rank'])
        if len(pz) < 5:
            pizza_src = None  # Tripadvisor non dice chi fa pizza: niente classifica pizzerie
            pz = []
        for n, p in enumerate(pz, 1):
            p['pizza_rank'] = n

    done = {r['id'] for r in hist if r['date'] == today.isoformat()}
    append_hist([dict(p, date=today.isoformat()) for p in sel if str(p['id']) not in done])
    model = fit(sel)
    mine = places[me]
    out = {
        'date': today.isoformat(), 'updatedAt': now.isoformat(timespec='seconds'),
        'me': me, 'geo_id': GEO, 'pizza_source': pizza_src,
        'rank_total': mine['rank_total'], 'pizza_total': mine['pizza_total'],
        'model': model, 'places': sel,
        'tracked': sorted(keep), 'discoveredAt': disc_at, 'billed_last_run': billed,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f"OK: Cutilisci n. {mine['rank']} di {mine['rank_total']} (pizzerie: {mine['pizza_rank']}), "
          f"{len(sel)} locali seguiti, modello corretto sul {round(((model or {}).get('accuracy') or 0) * 100)}% delle coppie, "
          f"~{billed} entita' fatturate")
    return 0


if __name__ == '__main__':
    sys.exit(main())
