# Agente classifica Tripadvisor – Catania

Giorni osservati: **11 / 7** · ultimo dato: 2026-11-07 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.106 |
| punteggio | 0.241 |
| recensioni_7gg | 0.14 |
| recensioni_ultimo_giorno | 0.018 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.51 |
| punteggio | 0.554 |
| recensioni_7gg | 0.543 |
| recensioni_ultimo_giorno | 0.54 |

Modello completo, sui dati gia' visti: **0.569**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-11-03 | 0.567 |
| 2026-11-04 | 0.571 |
| 2026-11-05 | 0.573 |
| 2026-11-06 | 0.572 |
| 2026-11-07 | 0.577 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.577 | 0.539 | 0.556 |
| roma | 0.551 | 0.536 | 0.559 |
| milano | 0.589 | 0.556 | 0.551 |
| napoli | 0.563 | 0.584 | 0.538 |
| torino | 0.567 | 0.525 | 0.565 |
| firenze | 0.561 | 0.563 | 0.518 |
| bologna | 0.567 | 0.499 | 0.575 |
| palermo | 0.557 | 0.521 | 0.551 |
| genova | 0.589 | 0.57 | 0.598 |
| venezia | 0.562 | 0.534 | 0.526 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 16167 | 441 | 0.027 |
| 1 | 1487 | 50 | 0.034 |
| 2 | 472 | 22 | 0.047 |
| 3 | 159 | 7 | 0.044 |
| 4 | 105 | 3 | 0.029 |
| 5+ | 93 | 3 | 0.032 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 57°; davanti c'e' Ciauru i Mari (56°). Servono circa **10** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 11 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
