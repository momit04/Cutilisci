# Agente classifica Tripadvisor – Catania

Giorni osservati: **10 / 7** · ultimo dato: 2026-11-06 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.107 |
| punteggio | 0.239 |
| recensioni_7gg | 0.136 |
| recensioni_ultimo_giorno | 0.018 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.511 |
| punteggio | 0.554 |
| recensioni_7gg | 0.543 |
| recensioni_ultimo_giorno | 0.539 |

Modello completo, sui dati gia' visti: **0.569**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-11-02 | 0.562 |
| 2026-11-03 | 0.567 |
| 2026-11-04 | 0.571 |
| 2026-11-05 | 0.573 |
| 2026-11-06 | 0.572 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.575 | 0.54 | 0.555 |
| roma | 0.549 | 0.533 | 0.559 |
| milano | 0.589 | 0.556 | 0.55 |
| napoli | 0.567 | 0.587 | 0.539 |
| torino | 0.565 | 0.529 | 0.566 |
| firenze | 0.562 | 0.564 | 0.518 |
| bologna | 0.566 | 0.497 | 0.576 |
| palermo | 0.558 | 0.517 | 0.551 |
| genova | 0.588 | 0.572 | 0.599 |
| venezia | 0.564 | 0.535 | 0.527 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 14545 | 390 | 0.027 |
| 1 | 1335 | 43 | 0.032 |
| 2 | 434 | 21 | 0.048 |
| 3 | 139 | 7 | 0.05 |
| 4 | 97 | 3 | 0.031 |
| 5+ | 85 | 3 | 0.035 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 58°; davanti c'e' Ciauru i Mari (57°). Servono circa **9** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 10 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
