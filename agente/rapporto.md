# Agente classifica Tripadvisor – Catania

Giorni osservati: **3 / 7** · ultimo dato: 2026-10-30 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

> Pochi giorni di dati: i risultati sotto sono solo indicativi.

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.094 |
| punteggio | 0.192 |
| recensioni_7gg | 0.309 |
| recensioni_ultimo_giorno | -0.191 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.51 |
| punteggio | 0.556 |
| recensioni_7gg | 0.534 |
| recensioni_ultimo_giorno | 0.534 |

Modello completo, sui dati gia' visti: **0.559**

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.567 | 0.593 | 0.554 |
| roma | 0.527 | 0.488 | 0.561 |
| milano | 0.581 | 0.554 | 0.551 |
| napoli | 0.562 | 0.608 | 0.544 |
| torino | 0.561 | 0.571 | 0.574 |
| firenze | 0.537 | 0.559 | 0.509 |
| bologna | 0.564 | 0.474 | 0.578 |
| palermo | 0.553 | 0.469 | 0.558 |
| genova | 0.58 | 0.622 | 0.605 |
| venezia | 0.551 | 0.522 | 0.528 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 3439 | 52 | 0.015 |
| 1 | 170 | 7 | 0.041 |
| 2 | 56 | 4 | 0.071 |
| 3 | 22 | 0 | 0.0 |
| 4 | 10 | 0 | 0.0 |
| 5+ | 5 | 0 | 0.0 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 58°; davanti c'e' Ciauru i Mari (57°). Servono circa **1** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).
