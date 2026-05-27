"""
Modulo per il plotting e la verifica visiva dei percorsi generati.
Integra la libreria Matplotlib per mappare graficamente le coordinate della sede
e dei punti di consegna, permettendo all'utente una valutazione immediata
dell'effettiva ottimizzazione del percorso prima della stampa finale del percorso per i 
volontari.
"""
import matplotlib.pyplot as plt
from ClassIndirizzo import GestoreIndirizzi
from logistica import OttimizzatorePercorsi


def crea_figura_giri(giri, sede_lat=45.637, sede_lon=13.791):
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    colori = ["blue", "red", "green", "orange", "purple", "brown", "darkcyan"]

    ax.scatter(sede_lon, sede_lat, color='black', marker='*', s=200, label='Partenza', zorder=5)
    distanza_complessiva = 0

    for i, giro in enumerate(giri):
        if not giro:
            continue

        ottimizzatore = OttimizzatorePercorsi(sede_lat=sede_lat, sede_lon=sede_lon)
        dist_km = ottimizzatore.calcola_lunghezza_giro(giro)
        distanza_complessiva += dist_km

        colore = colori[i % len(colori)]
        lats = [p.lat for p in giro]
        lons = [p.lon for p in giro]
        etichetta = f'Gruppo {i+1}: {len(giro)} nodi ({round(dist_km, 2)})'

        ax.scatter(lons, lats, color=colore, label=etichetta, s=60, zorder=4)
        px = [sede_lon] + lons + [sede_lon]
        py = [sede_lat] + lats + [sede_lat]
        ax.plot(px, py, color=colore, linestyle='--', alpha=0.7, zorder=3)

    ax.set_title(f"Percorsi Divisi ({round(distanza_complessiva, 2)})")
    ax.legend(loc='best', fontsize='small')
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.set_xlabel('Longitudine')
    ax.set_ylabel('Latitudine')
    return fig


def visualizza_grafico():
    print("Avvio visualizzazione distribuzione...")
    n_mezzi = 2

    print(f"Caricamento indirizzi...")
    gi = GestoreIndirizzi()
    gi.carica_json()
    
    if not gi.vault:
        print("Nessun indirizzo trovato nel JSON")
        return

    sede_lat = 45.637
    sede_lon = 13.791
    ottimizzatore = OttimizzatorePercorsi(sede_lat=sede_lat, sede_lon=sede_lon)

    punti_validi = [p for p in gi.vault if p.lat and p.lon and p.in_whitelist]
    
    if not punti_validi:
        print("Nessun punto valido")
        return
    
    print(f"Generazione giri ottimizzati...")
    giri = ottimizzatore.genera_giri(gi.vault, n_mezzi)
    
    fig = crea_figura_giri(giri, sede_lat=sede_lat, sede_lon=sede_lon)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualizza_grafico()