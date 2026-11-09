# Agente classifica Tripadvisor – Catania

Giorni osservati: **13 / 7** · ultimo dato: 2026-11-09 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.105 |
| punteggio | 0.246 |
| recensioni_7gg | 0.149 |
| recensioni_ultimo_giorno | 0.018 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.51 |
| punteggio | 0.554 |
| recensioni_7gg | 0.543 |
| recensioni_ultimo_giorno | 0.542 |

Modello completo, sui dati gia' visti: **0.571**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-11-05 | 0.573 |
| 2026-11-06 | 0.572 |
| 2026-11-07 | 0.577 |
| 2026-11-08 | 0.579 |
| 2026-11-09 | 0.575 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.578 | 0.543 | 0.557 |
| roma | 0.555 | 0.54 | 0.558 |
| milano | 0.589 | 0.553 | 0.552 |
| napoli | 0.564 | 0.58 | 0.534 |
| torino | 0.573 | 0.521 | 0.565 |
| firenze | 0.561 | 0.562 | 0.519 |
| bologna | 0.57 | 0.505 | 0.575 |
| palermo | 0.563 | 0.522 | 0.553 |
| genova | 0.591 | 0.569 | 0.597 |
| venezia | 0.56 | 0.535 | 0.527 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 19334 | 527 | 0.027 |
| 1 | 1817 | 61 | 0.034 |
| 2 | 591 | 26 | 0.044 |
| 3 | 209 | 14 | 0.067 |
| 4 | 114 | 3 | 0.026 |
| 5+ | 117 | 3 | 0.026 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 57°; davanti c'e' Ciauru i Mari (56°). Servono circa **10** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 13 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
