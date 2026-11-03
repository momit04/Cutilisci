# Agente classifica Tripadvisor – Catania

Giorni osservati: **7 / 7** · ultimo dato: 2026-11-03 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.106 |
| punteggio | 0.228 |
| recensioni_7gg | 0.13 |
| recensioni_ultimo_giorno | 0.008 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.511 |
| punteggio | 0.554 |
| recensioni_7gg | 0.545 |
| recensioni_ultimo_giorno | 0.538 |

Modello completo, sui dati gia' visti: **0.566**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-10-31 | 0.555 |
| 2026-11-01 | 0.557 |
| 2026-11-02 | 0.562 |
| 2026-11-03 | 0.567 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.571 | 0.546 | 0.554 |
| roma | 0.548 | 0.537 | 0.555 |
| milano | 0.579 | 0.558 | 0.548 |
| napoli | 0.568 | 0.591 | 0.542 |
| torino | 0.567 | 0.553 | 0.569 |
| firenze | 0.55 | 0.57 | 0.517 |
| bologna | 0.572 | 0.491 | 0.578 |
| palermo | 0.556 | 0.505 | 0.552 |
| genova | 0.587 | 0.58 | 0.601 |
| venezia | 0.558 | 0.534 | 0.523 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 9677 | 215 | 0.022 |
| 1 | 863 | 24 | 0.028 |
| 2 | 315 | 14 | 0.044 |
| 3 | 104 | 6 | 0.058 |
| 4 | 59 | 2 | 0.034 |
| 5+ | 70 | 3 | 0.043 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 59°; davanti c'e' Canni & Pisci - Meat & Fish (58°). Servono circa **6** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 7 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
