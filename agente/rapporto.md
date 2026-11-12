# Agente classifica Tripadvisor – Catania

Giorni osservati: **16 / 7** · ultimo dato: 2026-11-12 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.105 |
| punteggio | 0.252 |
| recensioni_7gg | 0.164 |
| recensioni_ultimo_giorno | 0.009 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.51 |
| punteggio | 0.554 |
| recensioni_7gg | 0.543 |
| recensioni_ultimo_giorno | 0.542 |

Modello completo, sui dati gia' visti: **0.57**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-11-08 | 0.579 |
| 2026-11-09 | 0.575 |
| 2026-11-10 | 0.565 |
| 2026-11-11 | 0.57 |
| 2026-11-12 | 0.565 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.58 | 0.546 | 0.558 |
| roma | 0.556 | 0.542 | 0.557 |
| milano | 0.584 | 0.549 | 0.552 |
| napoli | 0.561 | 0.571 | 0.53 |
| torino | 0.568 | 0.512 | 0.566 |
| firenze | 0.563 | 0.563 | 0.519 |
| bologna | 0.573 | 0.513 | 0.577 |
| palermo | 0.56 | 0.525 | 0.554 |
| genova | 0.591 | 0.571 | 0.596 |
| venezia | 0.56 | 0.537 | 0.526 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 24134 | 653 | 0.027 |
| 1 | 2319 | 83 | 0.036 |
| 2 | 736 | 35 | 0.048 |
| 3 | 250 | 15 | 0.06 |
| 4 | 138 | 4 | 0.029 |
| 5+ | 143 | 6 | 0.042 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 55°; davanti c'e' Scalia Comida Mexicana (54°). Servono circa **12** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 16 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
