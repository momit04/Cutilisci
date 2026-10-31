# Agente classifica Tripadvisor – Catania

Giorni osservati: **4 / 7** · ultimo dato: 2026-10-31 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

> Pochi giorni di dati: i risultati sotto sono solo indicativi.

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.1 |
| punteggio | 0.208 |
| recensioni_7gg | 0.16 |
| recensioni_ultimo_giorno | -0.041 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.511 |
| punteggio | 0.555 |
| recensioni_7gg | 0.541 |
| recensioni_ultimo_giorno | 0.535 |

Modello completo, sui dati gia' visti: **0.561**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-10-31 | 0.555 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.566 | 0.581 | 0.554 |
| roma | 0.537 | 0.514 | 0.561 |
| milano | 0.583 | 0.558 | 0.551 |
| napoli | 0.564 | 0.599 | 0.543 |
| torino | 0.562 | 0.571 | 0.573 |
| firenze | 0.541 | 0.567 | 0.513 |
| bologna | 0.564 | 0.477 | 0.579 |
| palermo | 0.56 | 0.487 | 0.556 |
| genova | 0.582 | 0.553 | 0.602 |
| venezia | 0.548 | 0.531 | 0.525 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 5022 | 96 | 0.019 |
| 1 | 321 | 10 | 0.031 |
| 2 | 134 | 7 | 0.052 |
| 3 | 40 | 2 | 0.05 |
| 4 | 26 | 2 | 0.077 |
| 5+ | 13 | 0 | 0.0 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 58°; davanti c'e' Ciauru i Mari (57°). Servono circa **3** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).
