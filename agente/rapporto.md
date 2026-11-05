# Agente classifica Tripadvisor – Catania

Giorni osservati: **9 / 7** · ultimo dato: 2026-11-05 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.107 |
| punteggio | 0.236 |
| recensioni_7gg | 0.134 |
| recensioni_ultimo_giorno | 0.015 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.511 |
| punteggio | 0.554 |
| recensioni_7gg | 0.544 |
| recensioni_ultimo_giorno | 0.537 |

Modello completo, sui dati gia' visti: **0.568**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-11-01 | 0.557 |
| 2026-11-02 | 0.562 |
| 2026-11-03 | 0.567 |
| 2026-11-04 | 0.571 |
| 2026-11-05 | 0.573 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.574 | 0.541 | 0.555 |
| roma | 0.546 | 0.533 | 0.558 |
| milano | 0.587 | 0.559 | 0.549 |
| napoli | 0.57 | 0.591 | 0.541 |
| torino | 0.566 | 0.535 | 0.567 |
| firenze | 0.557 | 0.566 | 0.518 |
| bologna | 0.566 | 0.493 | 0.576 |
| palermo | 0.557 | 0.516 | 0.551 |
| genova | 0.588 | 0.577 | 0.599 |
| venezia | 0.569 | 0.535 | 0.526 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 12916 | 348 | 0.027 |
| 1 | 1173 | 33 | 0.028 |
| 2 | 396 | 18 | 0.045 |
| 3 | 129 | 7 | 0.054 |
| 4 | 87 | 2 | 0.023 |
| 5+ | 83 | 3 | 0.036 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 58°; davanti c'e' Ciauru i Mari (57°). Servono circa **10** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 9 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
