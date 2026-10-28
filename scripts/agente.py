#!/usr/bin/env python3
"""Agente che osserva la classifica Tripadvisor dei primi 100 ristoranti di Catania.

Uso:  python3 scripts/agente.py add FILE.json CITTA [AAAA-MM-GG]   (CITTA = catania, roma, milano, ...)
  FILE.json = lista di {"rank": 1, "name": "...", "reviews": 1479, "avg": 4.8}
  Salva lo snapshot del giorno, riaddestra il modello su tutti i giorni raccolti
  e riscrive agente/modello.json e agente/rapporto.md.

Cosa impara (solo libreria standard):
 1. Test diretto dell'ipotesi: se un locale porta piu' recensioni nuove di quello
    che gli sta davanti, lo supera? (per differenza di recensioni nuove: 0,1,2,3,4,5+)
 2. Quale fattore spiega meglio l'ordine: punteggio, totale recensioni, recensioni
    recenti (7 giorni), recensioni dell'ultimo giorno.
 3. Un modello a coppie (regressione logistica) che parte dall'ipotesi 'contano le
    recensioni recenti' ma si corregge con i dati (regolarizzazione verso l'ipotesi
    che si indebolisce al crescere dei dati).
 4. Stima di quante recensioni da 5 stelle servono ai Cutilisci per superare chi sta davanti.
"""
import glob, json, math, os, sys
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, 'agente')
SNAP = os.path.join(DIR, 'snapshots')
TARGET = 'cutilisci'
FEATS = ['log_totale', 'punteggio', 'recensioni_7gg', 'recensioni_ultimo_giorno']
PRIOR = [0.0, 0.0, 1.0, 0.5]   # ipotesi di partenza: contano le recensioni recenti, non il punteggio
PRIOR_STRENGTH = 200.0          # peso dell'ipotesi, in 'coppie equivalenti'
DAYS_GOAL = 7
CITIES = {'catania': 187888, 'roma': 187791, 'milano': 187849, 'napoli': 187785, 'torino': 187855,
          'firenze': 187895, 'bologna': 187801, 'palermo': 187890, 'genova': 187823, 'venezia': 187870}
MIN_ROWS = {'catania': 80}   # le altre citta' si leggono fino a 60


def today_rome():
    return (datetime.now(timezone.utc) + timedelta(hours=1)).date().isoformat()


def load_snaps(city):
    out = []
    for f in sorted(glob.glob(os.path.join(SNAP, city, '*.json'))):
        d = os.path.basename(f)[:-5]
        rows = json.load(open(f))
        out.append((d, {r['name']: r for r in rows}))
    return out


def gap(d0, d1):
    return (date.fromisoformat(d1) - date.fromisoformat(d0)).days


def build_states(snaps):
    """Per ogni snapshot e locale: rank, totale, punteggio, nuove nell'ultimo intervallo, nuove negli ultimi 7 giorni."""
    states = []
    hist = {}  # name -> lista (data, nuove)
    prev = None
    for d, rows in snaps:
        st = {}
        for name, r in rows.items():
            new = 0
            if prev is not None and name in prev[1] and gap(prev[0], d) <= 2:
                new = max(0, r['reviews'] - prev[1][name]['reviews'])
            hist.setdefault(name, []).append((d, new))
            w7 = sum(n for dd, n in hist[name] if 0 <= gap(dd, d) < 7)
            st[name] = dict(rank=r['rank'], n=r['reviews'], avg=r['avg'], new=new, w7=w7)
        states.append((d, st))
        prev = (d, rows)
    return states


def feat(s):
    return [math.log(max(1, s['n'])), s['avg'], s['w7'], s['new']]


def pair_samples(st, maxdist=8):
    """Coppie (A sopra B) dello stesso giorno entro maxdist posizioni."""
    names = sorted(st, key=lambda k: st[k]['rank'])
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:i + 1 + maxdist]:
            out.append((feat(st[a]), feat(st[b])))
    return out


def standardizer(samples):
    cols = list(zip(*[x for a, b in samples for x in (a, b)]))
    mu = [sum(c) / len(c) for c in cols]
    sd = [max(1e-9, (sum((v - m) ** 2 for v in c) / len(c)) ** 0.5) for c, m in zip(cols, mu)]
    return mu, sd


def fit(samples, mu, sd, iters=150, lr=0.5):
    """Regressione logistica sulle differenze (sopra - sotto) standardizzate, con prior."""
    X = [[(a[k] - b[k]) / sd[k] for k in range(4)] for a, b in samples]
    n = len(X)
    w = list(PRIOR)
    lam = PRIOR_STRENGTH / max(1, n)
    for _ in range(iters):
        g = [0.0] * 4
        for x in X:
            z = sum(w[k] * x[k] for k in range(4))
            p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            for k in range(4):
                g[k] += (p - 1) * x[k]
        for k in range(4):
            w[k] -= lr * (g[k] / n + 2 * lam * (w[k] - PRIOR[k]))
    return w


def accuracy(samples, w, sd):
    if not samples:
        return None
    ok = 0
    for a, b in samples:
        z = sum(w[k] * (a[k] - b[k]) / sd[k] for k in range(4))
        ok += z > 0
    return ok / len(samples)


def single_accuracy(samples, k):
    if not samples:
        return None
    ok = tot = 0
    for a, b in samples:
        if a[k] == b[k]:
            continue
        tot += 1
        ok += a[k] > b[k]
    return ok / tot if tot else None


def swap_test(pooled):
    """Se il locale sotto porta piu' recensioni nuove di quello sopra, lo supera?"""
    buckets = {}
    pairs = [p for states in pooled for p in zip(states, states[1:])]
    for (d0, s0), (d1, s1) in pairs:
        if gap(d0, d1) > 2:
            continue
        names = sorted((k for k in s0 if k in s1), key=lambda k: s0[k]['rank'])
        for i, a in enumerate(names):
            for b in names[i + 1:i + 4]:
                delta = s1[b]['new'] - s1[a]['new']
                key = '<=0' if delta <= 0 else ('5+' if delta >= 5 else str(delta))
                swapped = s1[b]['rank'] < s1[a]['rank']
                c = buckets.setdefault(key, [0, 0])
                c[0] += 1
                c[1] += swapped
    order = ['<=0', '1', '2', '3', '4', '5+']
    return [dict(delta=k, coppie=buckets[k][0], sorpassi=buckets[k][1],
                 quota=round(buckets[k][1] / buckets[k][0], 3)) for k in order if k in buckets]


def estimate(st, w, mu, sd):
    """Quante recensioni da 5 stelle servono ai Cutilisci per superare il locale davanti."""
    me = next((k for k in st if TARGET in k.lower()), None)
    if not me or st[me]['rank'] <= 1:
        return None
    ahead = next(k for k in st if st[k]['rank'] == st[me]['rank'] - 1)
    def score(s):
        f = feat(s)
        return sum(w[k] * f[k] / sd[k] for k in range(4))
    base = dict(st[me])
    target = score(st[ahead])
    for x in range(0, 501):
        n = base['n'] + x
        avg = (base['avg'] * base['n'] + 5 * x) / n
        s = dict(base, n=n, avg=avg, w7=base['w7'] + x, new=base['new'])
        if score(s) > target:
            return dict(davanti=ahead, posizione_davanti=st[ahead]['rank'], posizione_tua=st[me]['rank'],
                        recensioni_5_stelle=x, ipotesi='tutte le recensioni arrivano entro 7 giorni')
    return dict(davanti=ahead, posizione_davanti=st[ahead]['rank'], posizione_tua=st[me]['rank'],
                recensioni_5_stelle=None, ipotesi='non raggiungibile entro 500 recensioni')


def run():
    per_city = {c: build_states(load_snaps(c)) for c in CITIES}
    per_city = {c: st for c, st in per_city.items() if st}
    days = sorted({d for st in per_city.values() for d, _ in st})
    n_days = len(days)
    res = dict(giorni=n_days, ultimo=days[-1] if days else None, obiettivo_giorni=DAYS_GOAL,
               citta={c: len(st) for c, st in per_city.items()})
    prev_model = {}
    try:
        prev_model = json.load(open(os.path.join(DIR, 'modello.json')))
    except Exception:
        pass
    history = prev_model.get('storia', [])
    if n_days >= 3:
        all_states = [(c, d, st) for c, sts in per_city.items() for d, st in sts[1:]]
        all_samples = [x for c, d, st in all_states for x in pair_samples(st)]
        mu, sd = standardizer(all_samples)
        w = fit(all_samples, mu, sd)
        res['pesi'] = dict(zip(FEATS, [round(x, 3) for x in w]))
        res['accuratezza_in_campione'] = round(accuracy(all_samples, w, sd), 3)
        res['singoli_fattori'] = {f: (None if single_accuracy(all_samples, k) is None else round(single_accuracy(all_samples, k), 3))
                                  for k, f in enumerate(FEATS)}
        # per citta': il modello comune funziona ovunque?
        res['per_citta'] = {}
        for c, sts in per_city.items():
            sm = [x for d, st in sts[1:] for x in pair_samples(st)]
            res['per_citta'][c] = dict(accuratezza=None if not sm else round(accuracy(sm, w, sd), 3),
                                       recensioni_7gg=single_accuracy(sm, 2) and round(single_accuracy(sm, 2), 3),
                                       punteggio=single_accuracy(sm, 1) and round(single_accuracy(sm, 1), 3))
        if n_days >= 4:
            last = days[-1]
            train = [x for c, sts in per_city.items() for d, st in sts[1:] if d != last for x in pair_samples(st)]
            test = [x for c, sts in per_city.items() for d, st in sts if d == last for x in pair_samples(st)]
            if train and test:
                mu2, sd2 = standardizer(train)
                w2 = fit(train, mu2, sd2)
                history = [h for h in history if h['data'] != last]
                history.append(dict(data=last, accuratezza_fuori_campione=round(accuracy(test, w2, sd2), 3)))
        if 'catania' in per_city:
            res['stima'] = estimate(per_city['catania'][-1][1], w, mu, sd)
        res['test_ipotesi'] = swap_test(list(per_city.values()))
    res['storia'] = history
    json.dump(res, open(os.path.join(DIR, 'modello.json'), 'w'), ensure_ascii=False, indent=1)
    open(os.path.join(DIR, 'rapporto.md'), 'w').write(report(res))
    return res


def report(r):
    L = ['# Agente classifica Tripadvisor – Catania', '',
         f"Giorni osservati: **{r['giorni']} / {r['obiettivo_giorni']}** · ultimo dato: {r['ultimo']} · citta': {', '.join(r['citta'])}", '']
    if 'pesi' not in r:
        L += ['Servono almeno 3 giorni di dati per iniziare ad addestrare il modello.', '']
        return '\n'.join(L)
    if r['giorni'] < 7:
        L += ['> Pochi giorni di dati: i risultati sotto sono solo indicativi.', '']
    L += ['## Cosa pesa di piu\' (pesi del modello, scala confrontabile)', '',
          '| Fattore | Peso |', '|---|---|'] + [f'| {k} | {v} |' for k, v in r['pesi'].items()]
    L += ['', 'Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.', '']
    L += ['## Quanto spiega l\'ordine ogni fattore da solo (coppie vicine in classifica)', '',
          '| Fattore | Accuratezza |', '|---|---|'] + [f'| {k} | {v} |' for k, v in r['singoli_fattori'].items()]
    L += ['', f"Modello completo, sui dati gia' visti: **{r['accuratezza_in_campione']}**", '']
    if r['storia']:
        last = r['storia'][-5:]
        L += ['## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)', '',
              '| Data | Accuratezza |', '|---|---|'] + [f"| {h['data']} | {h['accuratezza_fuori_campione']} |" for h in last] + ['']
    if r.get('per_citta'):
        L += ['## Per citta\' (il modello comune vale ovunque?)', '', '| Citta\' | Modello | Solo recensioni 7gg | Solo punteggio |', '|---|---|---|---|']
        L += [f"| {c} | {v['accuratezza']} | {v['recensioni_7gg']} | {v['punteggio']} |" for c, v in r['per_citta'].items()]
        L += ['']
    L += ['## Test dell\'ipotesi: chi porta piu\' recensioni nuove del locale sopra lo supera?', '',
          '| Recensioni nuove in piu\' | Coppie | Sorpassi | Quota |', '|---|---|---|---|']
    L += [f"| {t['delta']} | {t['coppie']} | {t['sorpassi']} | {t['quota']} |" for t in r['test_ipotesi']]
    L += ['', 'Se l\'ipotesi e\' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.', '']
    e = r.get('stima')
    if e:
        L += ['## Stima per i Cutilisci', '']
        if e['recensioni_5_stelle'] is None:
            L += [f"Oggi sei {e['posizione_tua']}°; davanti c'e' {e['davanti']} ({e['posizione_davanti']}°). Con il modello attuale: {e['ipotesi']}."]
        else:
            L += [f"Oggi sei {e['posizione_tua']}°; davanti c'e' {e['davanti']} ({e['posizione_davanti']}°). "
                  f"Servono circa **{e['recensioni_5_stelle']}** recensioni da 5 stelle per superarlo ({e['ipotesi']})."]
        L += ['']
    if r['giorni'] >= r['obiettivo_giorni']:
        L += ['## Verdetto finale', '',
              f"Dopo {r['giorni']} giorni: confronta la tabella dei sorpassi e i pesi sopra. "
              'Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l\'ipotesi va scartata.', '']
    return '\n'.join(L)


def add(path, city, day):
    if city not in CITIES:
        sys.exit(f'Citta sconosciuta: {city}. Valide: {", ".join(CITIES)}')
    rows = json.load(open(path))
    rows = sorted((r for r in rows if r.get('rank') and r['rank'] <= 100), key=lambda r: r['rank'])
    clean = [dict(rank=int(r['rank']), name=r['name'].strip(), reviews=int(r['reviews']), avg=float(r['avg'])) for r in rows]
    need = MIN_ROWS.get(city, 50)
    if len(clean) < need:
        sys.exit(f'{city}: solo {len(clean)} locali (servono almeno {need}), snapshot non salvato.')
    os.makedirs(os.path.join(SNAP, city), exist_ok=True)
    json.dump(clean, open(os.path.join(SNAP, city, f'{day}.json'), 'w'), ensure_ascii=False)
    print(f'Snapshot {city} {day} salvato ({len(clean)} locali).')


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'add':
        add(sys.argv[2], sys.argv[3].lower(), sys.argv[4] if len(sys.argv) > 4 else today_rome())
    elif len(sys.argv) >= 2 and sys.argv[1] == 'run':
        os.makedirs(DIR, exist_ok=True)
        run()
        print('Modello aggiornato.')
    else:
        print(__doc__)
