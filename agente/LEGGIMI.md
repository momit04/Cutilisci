# Agente classifica

Ogni giorno alle 6:43 (ora italiana) un'attivita' pianificata legge la lista Pertinenza di 10 citta' (Catania top 100, le altre top 60)
(lista Tripadvisor ordinata per Pertinenza), salva uno snapshot per citta' in `snapshots/CITTA/AAAA-MM-GG.json`
e poi lancia `python3 scripts/agente.py run`, che riaddestra il modello su tutte le citta'.

- `rapporto.md`: risultati leggibili (pesi, test dell'ipotesi, stima per i Cutilisci)
- `modello.json`: gli stessi dati in formato macchina
- Si addestra per 7 giorni; il rapporto finale compare quando gli snapshot sono 7.

Limiti: Tripadvisor non pubblica la formula. Dalla lista si vede solo il numero di recensioni nuove
(differenza del totale tra un giorno e l'altro), non le stelle di ognuna.
