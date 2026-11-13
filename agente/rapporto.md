# Agente classifica Tripadvisor – Catania

Giorni osservati: **17 / 7** · ultimo dato: 2026-11-13 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.105 |
| punteggio | 0.254 |
| recensioni_7gg | 0.167 |
| recensioni_ultimo_giorno | 0.006 |

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
| 2026-11-09 | 0.575 |
| 2026-11-10 | 0.565 |
| 2026-11-11 | 0.57 |
| 2026-11-12 | 0.565 |
| 2026-11-13 | 0.568 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.579 | 0.547 | 0.559 |
| roma | 0.558 | 0.543 | 0.557 |
| milano | 0.582 | 0.548 | 0.552 |
| napoli | 0.559 | 0.57 | 0.528 |
| torino | 0.566 | 0.51 | 0.565 |
| firenze | 0.566 | 0.563 | 0.518 |
| bologna | 0.573 | 0.513 | 0.578 |
| palermo | 0.561 | 0.526 | 0.554 |
| genova | 0.591 | 0.57 | 0.596 |
| venezia | 0.559 | 0.537 | 0.527 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 25809 | 702 | 0.027 |
| 1 | 2444 | 85 | 0.035 |
| 2 | 762 | 35 | 0.046 |
| 3 | 261 | 15 | 0.057 |
| 4 | 141 | 4 | 0.028 |
| 5+ | 151 | 6 | 0.04 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 55°; davanti c'e' Scalia Comida Mexicana (54°). Servono circa **13** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).

## Verdetto finale

Dopo 17 giorni: confronta la tabella dei sorpassi e i pesi sopra. Se la quota di sorpassi non cresce con la differenza di recensioni nuove, l'ipotesi va scartata.
