# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:46:57 2026

@author: Matteo Senn
"""
"""
Modulo dedicato alla geocodifica locale degli indirizzi.
Interroga in modo efficiente un database geospaziale locale (DataAddress.json)
per associare latitudine e longitudine a ciascuna via registrata, evitando
la dipendenza da API esterne a pagamento o pesanti file OSM completi.
Una lista come DataAddress è facilmente ottenibile scaricando una mappa da OpenStreetMap e
ritagliandola con un file GEOjson e in seguito estrarre tutti gli indirizzi con osmium.
"""
import json
import os
from ClassIndirizzo import GestoreIndirizzi

class GestoreCoordinate:
    
    def __init__(self, database_path='DataAddress.json'):
        self.gi = GestoreIndirizzi()
        self.gi.carica_json()
        self.database_path = database_path
    
    def _carica_db_locale(self):
        
        if os.path.exists(self.database_path):
            with open(self.database_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def latlon_indirizzi(self):
        
        db_osm = self._carica_db_locale()
        
        if not db_osm:
            print(f"Errore: {self.database_path} non trovato o vuoto.")
            return

        for persona in self.gi.vault:
            input_utente = persona.via.lower().strip()
            
            print(f"Ricerca locale per: {persona.via}...")
            trovato = False
            
            for elemento in db_osm:
                if elemento.get('categoria') in ['indirizzo', 'edificio']:
                    via_db = elemento.get('via', '').lower().strip()
                    civico_db = str(elemento.get('civico', '')).lower().strip()
                    
                    indirizzo_db_completo = f"{via_db} {civico_db}".strip()
                    
                    if input_utente == indirizzo_db_completo:
                        persona.lat = elemento.get('lat')
                        persona.lon = elemento.get('lon')
                        print(f"Trovato: {persona.lat}, {persona.lon}")
                        trovato = True
                        break
            
            if not trovato:
                print(f"Nessuna corrispondenza in DataAddress.json per: {persona.via}")
        
        self.gi.salva_json()