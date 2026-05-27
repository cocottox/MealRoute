"""
Created on Mon Mar 23 10:15:00 2026

@author: Matteo Senn
"""
"""
Modulo per la gestione dell'anagrafica e della persistenza dei dati.
Definisce la struttura dati 'indirizzo' tramite dataclass e implementa
la classe 'GestoreIndirizzi' per il caricamento, il salvataggio su file JSON,
l'aggiunta (con controllo di ridondanza) e la manipolazione dei contatti.
"""

from dataclasses import dataclass, asdict
from typing import List
import json
import os

@dataclass
class indirizzo:
    via: str
    nome: str
    cognome: str
    in_whitelist: bool
    note: str = ""
    lat: float = None
    lon: float = None

class GestoreIndirizzi:
    
    def __init__(self):
        self.vault: List[indirizzo] = []
        
    def carica_json(self, nome_file="indirizzi.json"):
        if os.path.exists(nome_file) and os.path.getsize(nome_file) > 0: 
            try:
                with open(nome_file, "r", encoding="utf-8") as f: 
                    dati_caricati = json.load(f)
                    self.vault = [indirizzo(**d) for d in dati_caricati]
                print(f"Dati caricati con successo ({len(self.vault)} indirizzi)")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Errore nella decodifica del file: {e}")
                self.vault = [] 
        else:
            
            print("File non trovato o vuoto. Inizializzazione vault vuoto.")
            self.vault = []
    
    def aggiungi_indirizzo(self, via: str, nome: str, cognome: str, in_whitelist: bool, note: str=""):
        
        nuovo_utente = indirizzo(via, nome, cognome, in_whitelist, note)
        for i,a in enumerate(self.vault): 
            if a.nome.lower() == nome.lower() and a.cognome.lower() == cognome.lower():
                del self.vault[i]   
                print("Elemento ridondante... eliminato")
        self.vault.append(nuovo_utente) 
        print(f"L'indirizzo {nome} {cognome} è stato aggiunto alla lista.")
        self.salva_json() 
        
        
    def salva_json(self, nome_file="indirizzi.json"):
        dati = [asdict(addr) for addr in self.vault]            
        with open(nome_file, "w", encoding="utf-8") as f:       
            json.dump(dati, f, indent=4, ensure_ascii=False)    
        print(f"Dati salvati con successo in {nome_file}")
    
    def insert_indirizzo(self):
        
        self.carica_json("indirizzi.json")
        
        while True:
            nome_input = input("Inserisci nome: ")
            cognome_input = input("Inserisci cognome: ")
            via_input = input("Inserisci via: ")
            
            val = input("Inserisci 'si' per whitelist, premi Invio per No: ")
            in_whitelist_input = val.lower() == "si" 
            
            self.aggiungi_indirizzo(
                nome=nome_input,
                cognome=cognome_input,
                via=via_input,
                in_whitelist=in_whitelist_input
            )
            
            fine = input("Vuoi aggiungerne un altro? (y/n): ")
            if fine.lower() == "n":
                print("Uscita in corso...")
                break
    
    def cerca_indirizzo(self):
        
        nome_cerca = input("Inserisci nome da cercare:")
        cognome_cerca = input("inserisci cognome da cercare:")
        
        self.carica_json("indirizzi.json")
        
        for i, a in enumerate(self.vault):
            if a.nome.lower() == nome_cerca.lower() and a.cognome.lower() == cognome_cerca.lower():
                print(f"{nome_cerca}-{cognome_cerca} | trovato nell'indice <{i+1}>")
                print(self.vault[i])
                
    def elimina_indirizzo(self, nome: str, cognome: str):
        original_len = len(self.vault)
        self.vault = [a for a in self.vault if not (a.nome.lower() == nome.lower() and a.cognome.lower() == cognome.lower())]
        
        if len(self.vault) < original_len:
            print(f"L'indirizzo di {nome} {cognome} è stato eliminato.")
            self.salva_json()
            return True
        else:
            print("Indirizzo non trovato.")
            return False