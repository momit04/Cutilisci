# Agente classifica Tripadvisor – Catania

Giorni osservati: **14 / 7** · ultimo dato: 2026-11-10 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.104 |
| punteggio | 0.248 |
| recensioni_7gg | 0.154 |
| recensioni_ultimo_giorno | 0.016 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.51 |
| punteggio | 0.554 |
| recensioni_7gg | 0.543 |
| recensioni_ultimo_giorno | 0.543 |

Modello completo, sui dati gia' visti: **0.571**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-11-06 | 0.572 |
| 2026-11-07 | 0.577 |
| 2026-11-08 | 0.579 |
| 2026-11-09 | 0.575 |
| 2026-11-10 | 0.565 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.579 | 0.543 | 0.557 |
| roma | 0.554 | 0.541 | 0.558 |
| milano | 0.588 | 0.551 | 0.552 |
| napoli | 0.564 | 0.575 | 0.533 |
| torino | 0.571 | 0.517 | 0.566 |
| firenze | 0.561 | 0.563 | 0.519 |
| bologna | 0.571 | 0.508 | 0.575 |
| palermo | 0.562 | 0.522 | 0.553 |
| genova | 0.592 | 0.57 | 0.596 |
| venezia | 0.56 | 0.535 | 0.526 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 20897 | 547 | 0.026 |
| 1 | 1992 | 68 | 0.034 |
| 2 | 650 | 29 | 0.045 |
| 3 | 231 | 15 | 0.065 |
| 4 | 131 | 4 | 0.031 |
| 5+ | 132 | 4 | 0.03 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 57°; davanti c'e' Ciauru i Mari (56°). Servono circa **10** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 14 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
