# Agente classifica

Ogni giorno alle 6:43 (ora italiana) un'attività pianificata legge i primi 100 ristoranti di Catania
(lista Tripadvisor ordinata per Pertinenza), salva lo snapshot in `snapshots/AAAA-MM-GG.json`
e lancia `python3 scripts/agente.py add FILE.json`, che riaddestra il modello.

- `rapporto.md`: risultati leggibili (pesi, test dell'ipotesi, stima per i Cutilisci)
- `modello.json`: gli stessi dati in formato macchina
- Si addestra per 30 giorni; il rapporto finale compare quando gli snapshot sono 30.

Limiti: Tripadvisor non pubblica la formula. Dalla lista si vede solo il numero di recensioni nuove
(differenza del totale tra un giorno e l'altro), non le stelle di ognuna.
