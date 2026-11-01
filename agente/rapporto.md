# Agente classifica Tripadvisor – Catania

Giorni osservati: **5 / 7** · ultimo dato: 2026-11-01 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

> Pochi giorni di dati: i risultati sotto sono solo indicativi.

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.105 |
| punteggio | 0.218 |
| recensioni_7gg | 0.139 |
| recensioni_ultimo_giorno | -0.018 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.511 |
| punteggio | 0.555 |
| recensioni_7gg | 0.543 |
| recensioni_ultimo_giorno | 0.539 |

Modello completo, sui dati gia' visti: **0.562**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-10-31 | 0.555 |
| 2026-11-01 | 0.557 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.567 | 0.567 | 0.554 |
| roma | 0.543 | 0.531 | 0.558 |
| milano | 0.58 | 0.558 | 0.55 |
| napoli | 0.564 | 0.592 | 0.543 |
| torino | 0.561 | 0.571 | 0.572 |
| firenze | 0.542 | 0.565 | 0.516 |
| bologna | 0.571 | 0.489 | 0.579 |
| palermo | 0.562 | 0.492 | 0.554 |
| genova | 0.578 | 0.573 | 0.601 |
| venezia | 0.549 | 0.529 | 0.523 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 6594 | 116 | 0.018 |
| 1 | 492 | 14 | 0.028 |
| 2 | 191 | 8 | 0.042 |
| 3 | 54 | 2 | 0.037 |
| 4 | 42 | 2 | 0.048 |
| 5+ | 34 | 0 | 0.0 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 58°; davanti c'e' Ciauru i Mari (57°). Servono circa **6** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).
