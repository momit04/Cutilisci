# Agente classifica Tripadvisor – Catania

Giorni osservati: **19 / 7** · ultimo dato: 2026-11-15 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.105 |
| punteggio | 0.255 |
| recensioni_7gg | 0.168 |
| recensioni_ultimo_giorno | 0.003 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.51 |
| punteggio | 0.554 |
| recensioni_7gg | 0.543 |
| recensioni_ultimo_giorno | 0.544 |

Modello completo, sui dati gia' visti: **0.57**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-11-11 | 0.57 |
| 2026-11-12 | 0.565 |
| 2026-11-13 | 0.568 |
| 2026-11-14 | 0.565 |
| 2026-11-15 | 0.566 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.578 | 0.55 | 0.559 |
| roma | 0.561 | 0.543 | 0.558 |
| milano | 0.581 | 0.547 | 0.553 |
| napoli | 0.56 | 0.57 | 0.527 |
| torino | 0.564 | 0.509 | 0.563 |
| firenze | 0.565 | 0.563 | 0.517 |
| bologna | 0.574 | 0.511 | 0.581 |
| palermo | 0.561 | 0.526 | 0.554 |
| genova | 0.592 | 0.569 | 0.596 |
| venezia | 0.56 | 0.537 | 0.527 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 29027 | 774 | 0.027 |
| 1 | 2768 | 94 | 0.034 |
| 2 | 843 | 37 | 0.044 |
| 3 | 297 | 16 | 0.054 |
| 4 | 156 | 6 | 0.038 |
| 5+ | 170 | 6 | 0.035 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 55°; davanti c'e' Scalia Comida Mexicana (54°). Servono circa **13** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 19 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
