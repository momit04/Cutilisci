# Agente classifica Tripadvisor – Catania

Giorni osservati: **6 / 7** · ultimo dato: 2026-11-02 · citta': catania, roma, milano, napoli, torino, firenze, bologna, palermo, genova, venezia

> Pochi giorni di dati: i risultati sotto sono solo indicativi.

## Cosa pesa di piu' (pesi del modello, scala confrontabile)

| Fattore | Peso |
|---|---|
| log_totale | 0.106 |
| punteggio | 0.224 |
| recensioni_7gg | 0.125 |
| recensioni_ultimo_giorno | 0.008 |

Partenza: contano le recensioni recenti, non il punteggio. Se i dati dicono altro, il peso cambia.

## Quanto spiega l'ordine ogni fattore da solo (coppie vicine in classifica)

| Fattore | Accuratezza |
|---|---|
| log_totale | 0.512 |
| punteggio | 0.554 |
| recensioni_7gg | 0.545 |
| recensioni_ultimo_giorno | 0.54 |

Modello completo, sui dati gia' visti: **0.565**

## Previsione su dati nuovi (addestro fino a ieri, provo su oggi)

| Data | Accuratezza |
|---|---|
| 2026-10-31 | 0.555 |
| 2026-11-01 | 0.557 |
| 2026-11-02 | 0.562 |

## Per citta' (il modello comune vale ovunque?)

| Citta' | Modello | Solo recensioni 7gg | Solo punteggio |
|---|---|---|---|
| catania | 0.568 | 0.556 | 0.554 |
| roma | 0.545 | 0.537 | 0.557 |
| milano | 0.578 | 0.554 | 0.549 |
| napoli | 0.57 | 0.589 | 0.542 |
| torino | 0.563 | 0.565 | 0.572 |
| firenze | 0.55 | 0.571 | 0.517 |
| bologna | 0.578 | 0.492 | 0.579 |
| palermo | 0.559 | 0.501 | 0.554 |
| genova | 0.581 | 0.584 | 0.6 |
| venezia | 0.555 | 0.531 | 0.522 |

## Test dell'ipotesi: chi porta piu' recensioni nuove del locale sopra lo supera?

| Recensioni nuove in piu' | Coppie | Sorpassi | Quota |
|---|---|---|---|
| <=0 | 8161 | 116 | 0.014 |
| 1 | 671 | 14 | 0.021 |
| 2 | 246 | 8 | 0.033 |
| 3 | 75 | 2 | 0.027 |
| 4 | 44 | 2 | 0.045 |
| 5+ | 55 | 0 | 0.0 |

Se l'ipotesi e' giusta, la quota di sorpassi sale con la differenza e diventa alta intorno a 4-5.

## Stima per i Cutilisci

Oggi sei 58°; davanti c'e' Ciauru i Mari (57°). Servono circa **6** recensioni da 5 stelle per superarlo (tutte le recensioni arrivano entro 7 giorni).
