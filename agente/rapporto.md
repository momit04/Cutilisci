# Agente classifica Tripadvisor – Catania

Giorni osservati: **8 / 7** · ultimo dato: 2026-11-04 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.107 |
| punteggio | 0.232 |
| recensioni_7gg | 0.132 |
| recensioni_ultimo_giorno | 0.01 |

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
| 2026-10-31 | 0.555 |
| 2026-11-01 | 0.557 |
| 2026-11-02 | 0.562 |
| 2026-11-03 | 0.567 |
| 2026-11-04 | 0.571 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.573 | 0.542 | 0.555 |
| roma | 0.546 | 0.535 | 0.558 |
| milano | 0.586 | 0.561 | 0.549 |
| napoli | 0.567 | 0.591 | 0.543 |
| torino | 0.566 | 0.542 | 0.568 |
| firenze | 0.554 | 0.567 | 0.517 |
| bologna | 0.572 | 0.491 | 0.577 |
| palermo | 0.556 | 0.511 | 0.551 |
| genova | 0.592 | 0.578 | 0.6 |
| venezia | 0.566 | 0.536 | 0.525 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 11290 | 274 | 0.024 |
| 1 | 1026 | 29 | 0.028 |
| 2 | 356 | 18 | 0.051 |
| 3 | 121 | 7 | 0.058 |
| 4 | 72 | 2 | 0.028 |
| 5+ | 74 | 3 | 0.041 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 58°; davanti c'e' Ciauru i Mari (57°). Servono circa **9** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 8 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
