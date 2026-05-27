# MealRoute
**Read this in other languages** [English](README.md)

MealRoute è un'applicazione desktop open-source sviluppata in Python e concepita per supportare i volontari nella pianificazione e nell'ottimizzazione logistica della consegna dei pasti a domicilio.
Il software nasce con l'obiettivo di ridurre i chilometri percorsi, azzerare le sovrapposizioni tra i mezzi e automatizzare un processo che spesso viene gestito manualmente, restituendo tempo prezioso a chi si dedica agli altri.

## Funzionalità Chiave
* **Gestione Anagrafica Intuitiva**: Un sistema di database locale basato su file JSON per salvare contatti, note di consegna e gestire una whitelist dinamica per selezionare rapidamente chi includere nel giro del giorno.
* **Geocodifica Locale e Leggera**: Per evitare i costi di API esterne o il peso computazionale di file OSM (.pbf) completi, il sistema interroga un database geospaziale locale (DataAddress.json) per associare istantaneamente latitudine e longitudine a ogni civico.
* **Algoritmo di Routing Avanzato (VRP)**: I punti di consegna vengono distribuiti equamente tra i mezzi tramite un ordinamento polare calcolato rispetto al baricentro geografico, evitando che i veicoli si incrocino.
Ogni sotto-percorso viene ottimizzato sequenzialmente utilizzando l'approccio Nearest Neighbor combinato con un motore di rifinitura 2-Opt rigidamente ancorato al punto di partenza.
* **Interfaccia Grafica (GUI)**: Sviluppata in Tkinter, offre funzionalità di autocompletamento delle vie in tempo reale, tabelle interattive (Treeview) e barre di progresso durante l'elaborazione.
* **Visualizzazione dei Percorsi**: Integrazione nativa di un canvas Matplotlib che mappa graficamente i giri generati per colore una volta stilate le liste, permettendo ai volontari una verifica visiva immediata senza doversi "fidare alla cieca" dell'algoritmo.

## **Giri a confronto**
| Giri Reali |  Giri Ottimizzati  |
|:--------:|:--------:|
|![real data graph](<confronti/18-05-2026(non ottimizzato).png>)|![optimized by program](confronti/18-05-2026(ottimizzato).png)|
|![real data graph](<confronti/16-05-2026(non ottimizzato).png>)|![optimized by program](confronti/16-05-2026(ottimizzato).png)|


## Stack Tecnico
* **Linguaggio**: Python 3.x
* **Interfaccia Utente**: Tkinter / TTK
* **Algoritmi e Logica**: Math (Ordinamento Polare, Nearest Neighbor, 2-Opt TSP)
* **Data Visualization**: Matplotlib
* **Data Storage**: JSON / Dataclasses

## Contributi e Filosofia
Questo software è stato sviluppato non per sostituire l'esperienza dei volontari, ma per porsi come uno strumento di supporto decisionale. Se vuoi contribuire a ottimizzare gli algoritmi di routing, migliorare la UI o adattare il database locale ad altri comuni, le Pull Request sono le benvenute!

## Come Installare e avviare il programma
Segui questi passaggi per configurare il progetto in locale sulla tua macchina.
### 1. Prerequisiti
Assicurati di avere installato sul tuo computer:
* **Python 3.8 o superiore** ([Scarica Python qui](https://www.python.org/downloads/))
* **Git** (opzionale, per clonare la repository)

### 2. Installazione Guidata
Apri il tuo terminale (o Prompt dei Comandi) ed esegui i seguenti comandi:
####  Passo 1: Clona la repository (oppure scarica il file ZIP)
```bash
git clone [https://github.com/cocottox/MealRoute-TS.git](https://github.com/cocottox/MealRoute.git)
cd MealRoute
```
####  Passo 2: Crea l'ambiente virtuale
* ##### Su Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```
* ##### Su MacOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
####  Passo 3: Installa le dipendenze necessarie
```bash
pip install -r requirements.txt
```
##### Struttura dei File Richiesti
Per funzionare correttamente, l'applicazione ha bisogno di due file di dati nella stessa cartella dei file .py. Assicurati che siano presenti:
* *DataAddress.json* (Il database locale con tutti gli indirizzi della città)
* *indirizzi.json* (La tua rubrica, viene creata automaticamente al primo avvio se mancante)
####  Passo 4: Avvio dell'applicazione
Una volta completata l'installazione, puoi lanciare l'applicazione semplicemente eseguendo il file principale:
```bash
python main.py
```
