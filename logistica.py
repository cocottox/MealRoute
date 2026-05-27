# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:04:22 2026
@author: Matteo Senn
"""
"""
Cuore algoritmico del sistema per la risoluzione del Vehicle Routing Problem (VRP).
Implementa logiche di clustering spaziale basate su ordinamento polare per dividere
equamente le consegne tra i mezzi e applica una combinazione degli algoritmi
Nearest Neighbor e 2-Opt (ancorato alla sede) per l'ottimizzazione del percorso.
"""
import math

class OttimizzatorePercorsi:
    def __init__(self, sede_lat=45.650, sede_lon=13.781): 
        """Punto di partenza predefinito"""
        self.sede = {"lat": sede_lat, "lon": sede_lon}

    def calcola_distanza(self, lat1, lon1, lat2, lon2):
        """Calcolo euclideo per distanze cittadine"""
        return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

    def calcola_lunghezza_giro(self, percorso):
        """Calcola la distanza totale del percorso includendo A/R dalla sede attuale"""
        if not percorso: return 0
        
        distanza = self.calcola_distanza(self.sede["lat"], self.sede["lon"], percorso[0].lat, percorso[0].lon)
        for i in range(len(percorso) - 1):
            distanza += self.calcola_distanza(percorso[i].lat, percorso[i].lon, percorso[i+1].lat, percorso[i+1].lon)
        distanza += self.calcola_distanza(percorso[-1].lat, percorso[-1].lon, self.sede["lat"], self.sede["lon"])
        return distanza

    def ordina_percorso(self, punti):
        """
        Inizializza il percorso con Nearest Neighbor partendo dalla sede
        e lo rifinisce usando l'algoritmo 2-Opt per minimizzare i chilometri totali.
        """
        if not punti: return []
        percorso = []
        rimanenti = punti.copy()
        curr_lat, curr_lon = self.sede["lat"], self.sede["lon"]
        
        while rimanenti:
            vicino = min(rimanenti, key=lambda p: self.calcola_distanza(curr_lat, curr_lon, p.lat, p.lon))
            percorso.append(vicino)
            curr_lat, curr_lon = vicino.lat, vicino.lon
            rimanenti.remove(vicino)

        migliorato = True
        while migliorato:
            migliorato = False
            for i in range(len(percorso)):
                for j in range(i + 1, len(percorso)):
                    nuovo_percorso = percorso[:i] + percorso[i:j+1][::-1] + percorso[j+1:]
                    if self.calcola_lunghezza_giro(nuovo_percorso) < self.calcola_lunghezza_giro(percorso):
                        percorso = nuovo_percorso
                        migliorato = True
        return percorso

    def genera_giri(self, lista_indirizzi, n_mezzi=2, progress_callback=None):
        """
        Divide i nodi spazialmente senza incroci usando l'ordinamento polare,
        esplorando tutte le rotazioni con una tolleranza dinamica del 40-60%.
        """
        validi = [p for p in lista_indirizzi if p.lat and p.lon and p.in_whitelist]
        n_totale = len(validi)
        if n_totale < 2:
            if progress_callback:
                progress_callback(1, 1, "Percorso generato rapidamente")
            return [self.ordina_percorso(validi)]

        b_lat = sum(p.lat for p in validi) / n_totale
        b_lon = sum(p.lon for p in validi) / n_totale

        validi_ordinati = sorted(validi, key=lambda p: math.atan2(p.lat - b_lat, p.lon - b_lon))
        
        k_min = max(1, int(n_totale * 0.45))
        k_max = min(n_totale, int(n_totale * 0.55) + 1)

        miglior_dist_totale = float('inf')
        migliori_giri = []

        total_steps = max(1, n_totale * max(1, k_max - k_min))
        step = 0
        if progress_callback:
            progress_callback(0, total_steps, "Avvio ottimizzazione rotte...")

        for r in range(n_totale):
            lista_ruotata = validi_ordinati[r:] + validi_ordinati[:r]
            
            for mid in range(k_min, k_max):
                g1, g2 = lista_ruotata[:mid], lista_ruotata[mid:]
                
                p1, p2 = self.ordina_percorso(g1), self.ordina_percorso(g2)
                dist_attuale = self.calcola_lunghezza_giro(p1) + self.calcola_lunghezza_giro(p2)
                
                if dist_attuale < miglior_dist_totale:
                    miglior_dist_totale = dist_attuale
                    migliori_giri = [p1, p2]

                step += 1
                if progress_callback and step % 5 == 0:
                    progress_callback(step, total_steps, f"Ottimizzazione: rotazione {r+1}/{n_totale}, split {mid-k_min+1}/{max(1, k_max-k_min)}")

        if progress_callback:
            progress_callback(total_steps, total_steps, "Ottimizzazione completata")

        return migliori_giri