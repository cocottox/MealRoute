# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 13:02:07 2026

@author: Matteo Senn
"""
"""
Modulo dell'interfaccia grafica utente (GUI) basato sulla libreria Tkinter.
Gestisce l'interazione interattiva con l'utente, inclusi l'autocompletamento
delle vie in tempo reale, la visualizzazione della rubrica tramite tabelle (Treeview)
e l'integrazione del canvas grafico per i percorsi ottimizzati.
"""
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from ClassIndirizzo import GestoreIndirizzi
from logistica import OttimizzatorePercorsi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from visualization import crea_figura_giri

class AppIndirizzi:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gestore Giro Pasti")
        self.root.geometry("450x400")
        self.root.protocol("WM_DELETE_WINDOW", self.chiudi_app)
        self.gi = GestoreIndirizzi()
        self.gi.carica_json()
        self.db_triest = []
        self.carica_database_triest()
        self.crea_widget()

    def chiudi_app(self):
        try:
            self.root.quit()
        finally:
            self.root.destroy()

    def crea_widget(self):
        """Funzione di gestione dell'interfaccia tk"""
        self.campi_config = [
            ("nome", "Nome:"),
            ("cognome", "Cognome:"),
            ("via", "Via:"),
            ("whitelist", "Nel giro ?:"),
            ("note","Note (Richieste ecc..):")
        ]
        
        self.entries = {}
        self.whitelist_var = tk.BooleanVar(value=False)
        for i, (chiave, testo) in enumerate(self.campi_config):
            row = i if i < 3 else i + 1
            tk.Label(self.root, text=testo).grid(row=row, column=0, columnspan=1, pady=5)
            if chiave == "whitelist":
                cb = tk.Checkbutton(self.root, text="(Spunta -> si)", variable=self.whitelist_var, onvalue=True, offvalue=False)
                cb.grid(row=row, column=2, columnspan=3, pady=5, sticky="w")
                self.entries[chiave] = cb
            else:
                entry = tk.Entry(self.root)
                entry.grid(row=row, column=1, columnspan=3, pady=5, ipadx=50)
                if chiave == "via":
                    entry.bind("<KeyRelease>", self.aggiorna_suggerimenti_via)
                self.entries[chiave] = entry

        tk.Label(self.root, text="Suggerimenti Via:").grid(row=3, column=0, sticky="nw", padx=(0, 5))
        self.via_suggerimenti = tk.Listbox(self.root, height=5, exportselection=False)
        self.via_suggerimenti.grid(row=3, column=1, columnspan=3, pady=(0, 5), padx=5, sticky="ew")
        self.via_suggerimenti.bind("<<ListboxSelect>>", self.seleziona_suggerimento_via)
        self.via_suggerimenti.grid_remove()

        riga_attuale = 6
        
        #SALVA
        self.btn_salva = tk.Button(self.root, text="Salva", command=self.salva_e_verifica, bg="#7cfc00")
        self.btn_salva.grid(row=riga_attuale, column=0, columnspan=1, pady=5,padx=15,ipadx=30)
        #CERCA
        self.btn_cerca = tk.Button(self.root, text="Cerca", command=self.azione_cerca, bg="#ffbf00")
        self.btn_cerca.grid(row=riga_attuale, column=1, columnspan=1, pady=5,padx=15, ipadx=30)
        #ELIMINA
        self.btn_elimina = tk.Button(self.root, text="Elimina", command=self.azione_elimina, bg="#ff0000")
        self.btn_elimina.grid(row=riga_attuale, column=3, columnspan=1, pady=5,padx=15,ipadx=30)
        riga_attuale += 1
        #MOSTRA LISTA
        self.btn_mostra = tk.Button(self.root, text="Visualizza Lista", command=self.apri_rubrica, bg="#9932cc")
        self.btn_mostra.grid(row=riga_attuale, column=0, columnspan=1, pady=5, ipadx=15)
        #VERIFICA
        self.btn_verifica = tk.Button(self.root, text="Verifica Indirizzi", command=self.controlla_database_locale, bg="#00b7eb")
        self.btn_verifica.grid(row=riga_attuale, column=1, columnspan=2, pady=5,padx=15,ipadx=15)
        #GENERA
        self.btn_calcola = tk.Button(self.root, text="Genera Percorsi", command=self.apri_finestra_giri, bg="#ffd54f")
        self.btn_calcola.grid(row=riga_attuale + 1, column=3, pady=10, padx=5, ipadx=10)

        self.status = tk.Label(self.root, text="", fg="blue")
        self.status.grid(row=riga_attuale + 2, column=0, columnspan=4, sticky="w", padx=10)

        self.root.grid_columnconfigure(1, weight=1)
        
        self.lista_focus = [self.entries[chiave] for chiave, _ in self.campi_config]
        
        #COLLEGAMENTO FRECCE
        for widget in self.lista_focus:
            widget.bind("<Down>", self.muovi_focus)
            widget.bind("<Return>", self.muovi_focus)
            widget.bind("<Up>", self.muovi_focus_indietro)
            
        if self.lista_focus:
            self.lista_focus[0].focus_set()
        
    def muovi_focus(self, event):
        
        current_widget = event.widget
        try:
            index = self.lista_focus.index(current_widget)
            next_widget = self.lista_focus[index + 1]
            next_widget.focus_set()
        except IndexError:
            
            self.azione_aggiungi()
        return "break"
    
    def muovi_focus_indietro(self, event):
        
        current_widget = event.widget
        index = self.lista_focus.index(current_widget)
        if index > 0:
            prev_widget = self.lista_focus[index - 1]
            prev_widget.focus_set()
        return "break"

    def azione_aggiungi(self):
    
        nome = self.entries["nome"].get()
        cognome = self.entries["cognome"].get()
        via = self.entries["via"].get()
        whitelist = bool(self.whitelist_var.get())

        if nome and cognome and via:
            self.gi.aggiungi_indirizzo(via, nome, cognome, whitelist)
            messagebox.showinfo("Successo", f"Salvato: {nome} {cognome}")
            self.pulisci_campi()
        else:
            messagebox.showwarning("Errore", "I primi tre campi sono obbligatori!")

    def azione_cerca(self):
        
        n_cerca = self.entries["nome"].get().lower()
        c_cerca = self.entries["cognome"].get().lower()

        if not n_cerca or not c_cerca:
            messagebox.showwarning("Ricerca", "Inserisci Nome e Cognome per cercare.")
            return

        trovato = False
        for i, a in enumerate(self.gi.vault):
            if a.nome.lower() == n_cerca and a.cognome.lower() == c_cerca:
                 
                self.entries["via"].delete(0, tk.END)
                self.entries["via"].insert(0, a.via)
                self.whitelist_var.set(a.in_whitelist)
                
                self.status.config(text=f"Trovato in posizione {i+1}", fg="blue")
                messagebox.showinfo("Risultato", f"Trovato!\nVia: {a.via}\nWhitelist: {a.in_whitelist}")
                trovato = True
                break
        
        if not trovato:
            messagebox.showwarning("Ricerca", "Nessun risultato trovato.")
            
    def pulisci_campi(self):
        """Svuota tutte le entry e rimette il cursore sul campo Nome"""
        for chiave, widget in self.entries.items():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
        self.whitelist_var.set(False)
        if hasattr(self, 'via_suggerimenti'):
            self.via_suggerimenti.grid_remove()
        
        if "nome" in self.entries:
            self.entries["nome"].focus_set()

    def aggiorna_suggerimenti_via(self, event=None):
        termine = self.entries["via"].get().lower().strip()
        suggestions = []
        seen_vie = set()
        self.via_suggerimenti.delete(0, tk.END)

        def match_via(termine, via_testo):
            parts = [p for p in termine.split() if p]
            via_testo = via_testo.lower()
            return all(part in via_testo for part in parts)

        if termine and self.db_triest:
            for via_testo in self.db_triest:
                via_testo_lower = via_testo.lower()
                if match_via(termine, via_testo_lower) and via_testo_lower not in seen_vie:
                    seen_vie.add(via_testo_lower)
                    suggestions.append(via_testo)

        if suggestions:
            for via in suggestions[:15]:
                self.via_suggerimenti.insert(tk.END, via)
            self.via_suggerimenti.grid()
        else:
            self.via_suggerimenti.grid_remove()

    def seleziona_suggerimento_via(self, event):
        selezione = self.via_suggerimenti.curselection()
        if not selezione:
            return
        via_scelta = self.via_suggerimenti.get(selezione[0])
        self.entries["via"].delete(0, tk.END)
        self.entries["via"].insert(0, via_scelta)
        self.via_suggerimenti.grid_remove()

    def carica_database_triest(self):
        self.db_triest = []
        file_path = os.path.join(os.path.dirname(__file__), "DataAddress.json")
        if not os.path.exists(file_path):
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                db_osm = json.load(f)
            seen = set()
            for elemento in db_osm:
                if elemento.get('categoria') in ['indirizzo', 'edificio']:
                    via = str(elemento.get('via', '')).strip()
                    civico = str(elemento.get('civico', '')).strip()
                    if not via:
                        continue
                    indirizzo = f"{via} {civico}".strip()
                    lower = indirizzo.lower()
                    if lower not in seen:
                        seen.add(lower)
                        self.db_triest.append(indirizzo)
        except Exception:
            self.db_triest = []

    def azione_elimina(self):

        nome = self.entries["nome"].get()
        cognome = self.entries["cognome"].get()

        if not nome or not cognome:
            messagebox.showwarning("Attenzione", "Inserisci Nome e Cognome per eliminare l'indirizzo.")
            return

        conferma = messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare {nome} {cognome}?")
        
        if conferma:
            successo = self.gi.elimina_indirizzo(nome, cognome)
            if successo:
                self.pulisci_campi()
                messagebox.showinfo("Eliminato", "Indirizzo rimosso con successo.")
                
                if hasattr(self, 'finestra_rubrica') and self.finestra_rubrica.winfo_exists():
                    for item in self.tree_rubrica.get_children():
                        self.tree_rubrica.delete(item)
                    for p in self.gi.vault:
                        wl_testo = "Sì" if p.in_whitelist else "No"
                        nota_testo = getattr(p, 'note', '') 
                        self.tree_rubrica.insert("", tk.END, values=(p.nome, p.cognome, p.via, wl_testo, nota_testo))
            else:
                messagebox.showerror("Errore", "Impossibile trovare l'indirizzo da eliminare.")
                
    def apri_rubrica(self):
        """Funzione di gestione della rubrica(da sistemare in futuro)"""
        top = tk.Toplevel(self.root)
        top.title("Rubrica Indirizzi")
        top.geometry("660x520")
        top.resizable(True, True)

        search_frame = tk.LabelFrame(top, text="Ricerca Indirizzi", padx=10, pady=10)
        search_frame.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(search_frame, text="Nome e Cognome:").grid(row=0, column=0, sticky="w")
        search_nome_completo_var = tk.StringVar()
        entry_nome_completo_search = tk.Entry(search_frame, textvariable=search_nome_completo_var)
        entry_nome_completo_search.grid(row=0, column=1, columnspan=4, sticky="ew", padx=(5, 15))

        btn_filtra = tk.Button(search_frame, text="Filtra", command=lambda: filtra_rubrica(), bg="#ffbf00")
        btn_filtra.grid(row=0, column=5, padx=(0, 5), ipadx=10)
        btn_azzera = tk.Button(search_frame, text="Azzera", command=lambda: reset_rubrica(), bg="#d3d3d3")
        btn_azzera.grid(row=0, column=6, ipadx=10)

        tk.Label(search_frame, text="Suggerimenti:").grid(row=1, column=0, columnspan=7, sticky="w", pady=(10, 0))

        suggerimenti_frame = tk.Frame(search_frame)
        suggerimenti_frame.grid(row=2, column=0, columnspan=7, sticky="nsew")

        lista_suggerimenti = tk.Listbox(suggerimenti_frame, height=6, exportselection=False)
        lista_suggerimenti.pack(side="left", fill="both", expand=True)
        sugg_scroll = tk.Scrollbar(suggerimenti_frame, orient=tk.VERTICAL, command=lista_suggerimenti.yview)
        sugg_scroll.pack(side="left", fill="y")
        lista_suggerimenti.config(yscrollcommand=sugg_scroll.set)

        search_frame.grid_columnconfigure(1, weight=1)

        colonne = ("nome", "cognome", "via", "whitelist", "note")
        tree = ttk.Treeview(top, columns=colonne, show='headings')
        
        tree.heading("nome", text="Nome")
        tree.heading("cognome", text="Cognome")
        tree.heading("via", text="Indirizzo")
        tree.heading("whitelist", text="Whitelist")
        tree.heading("note", text="Note")
        
        tree.column("nome", width=120)
        tree.column("cognome", width=120)
        tree.column("via", width=200)
        tree.column("whitelist", width=80, anchor="center")
        tree.column("note", width=140)

        def matches_nome_cognome(termine, nome_cognome):
            if not termine:
                return True
            termine = termine.lower().strip()
            tokens = [t for t in termine.split() if t]
            if not tokens:
                return True
            nome_cognome = nome_cognome.lower()
            return all(token in nome_cognome for token in tokens)

        def popola_tree(nome_cognome_filtro=None):
            tree.delete(*tree.get_children())
            for p in self.gi.vault:
                nome_cognome = f"{p.nome} {p.cognome}"
                if nome_cognome_filtro and not matches_nome_cognome(nome_cognome_filtro, nome_cognome):
                    continue
                wl_testo = "☑" if p.in_whitelist else "☐"
                nota_testo = getattr(p, 'note', '')
                tree.insert("", tk.END, values=(p.nome, p.cognome, p.via, wl_testo, nota_testo))

        def aggiorna_suggerimenti(event=None):
            termine = search_nome_completo_var.get().strip()
            lista_suggerimenti.delete(0, tk.END)
            if not termine:
                return
            for p in self.gi.vault:
                nome_cognome = f"{p.nome} {p.cognome}"
                if termine and not matches_nome_cognome(termine, nome_cognome):
                    continue
                lista_suggerimenti.insert(tk.END, f"{p.nome} {p.cognome} - {p.via}")

        def filtra_rubrica():
            termine = search_nome_completo_var.get().strip()
            if not termine:
                messagebox.showwarning("Ricerca", "Inserisci Nome o Cognome per filtrare.")
                return
            popola_tree(termine)
            aggiorna_suggerimenti()
        def reset_rubrica():
            search_nome_completo_var.set("")
            lista_suggerimenti.delete(0, tk.END)
            popola_tree()

        def on_suggerimento_select(event):
            selezione = lista_suggerimenti.curselection()
            if not selezione:
                return
            testo = lista_suggerimenti.get(selezione[0])
            nome_cognome, _, _ = testo.partition(" - ")
            if not nome_cognome:
                return
            search_nome_completo_var.set(nome_cognome)
            filtra_rubrica()

        entry_nome_completo_search.bind("<KeyRelease>", aggiorna_suggerimenti)
        lista_suggerimenti.bind("<<ListboxSelect>>", on_suggerimento_select)

        popola_tree()

        button_frame = tk.Frame(top)
        button_frame.pack(fill="x", padx=10, pady=(5, 0))

        btn_close = tk.Button(button_frame, text="Chiudi", command=top.destroy, bg="#d3d3d3")
        btn_close.pack(side="right")

        tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar = ttk.Scrollbar(top, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        def toggle_whitelist_selected():
            selezioni = tree.selection()
            if not selezioni:
                return
            item = selezioni[0]
            valori = list(tree.item(item, "values"))
            if not valori:
                return
            corrente = valori[3] == "☑"
            nuovi = "☐" if corrente else "☑"
            valori[3] = nuovi
            tree.item(item, values=tuple(valori))

            nome, cognome = valori[0], valori[1]
            for p in self.gi.vault:
                if p.nome == nome and p.cognome == cognome:
                    p.in_whitelist = not corrente
                    self.gi.salva_json()
                    break

        def seleziona_elemento(event):
            item = tree.identify_row(event.y)
            if not item:
                return
            col = tree.identify_column(event.x)
            if col == "#4":
                toggle_whitelist_selected()
                return

            valori = tree.item(item, "values")
            if not valori:
                return

            self.pulisci_campi()
            self.entries["nome"].insert(0, valori[0])
            self.entries["cognome"].insert(0, valori[1])
            self.entries["via"].insert(0, valori[2])
            self.whitelist_var.set(valori[3] == "☑")

            if len(valori) > 4:
                self.entries["note"].delete(0, tk.END)
                self.entries["note"].insert(0, valori[4])

            top.destroy()

        tree.bind("<Double-1>", seleziona_elemento)

        self.finestra_rubrica = top
        self.tree_rubrica = tree

        
        
    def crea_tabella_giro(self, container, titolo, colore, lista_punti):
        
        frame_settore = tk.LabelFrame(container, text=titolo, font=("Arial", 12, "bold"), fg=colore, padx=10, pady=10)
        frame_settore.pack(fill="x", padx=15, pady=10)

        if not lista_punti:
            tk.Label(frame_settore, text="Nessun indirizzo assegnato a questo mezzo", fg="grey").pack()
            return

        cols = ("pos", "nome", "via", "note")
        tree = ttk.Treeview(frame_settore, columns=cols, show='headings', height=min(len(lista_punti), 6))
        
        tree.heading("pos", text="#")
        tree.heading("nome", text="Nominativo")
        tree.heading("via", text="Indirizzo")
        tree.heading("note", text="Note")
        
        tree.column("pos", width=40, anchor="center")
        tree.column("nome", width=150)
        tree.column("via", width=300)
        tree.column("note", width=150)
        
        for i, p in enumerate(lista_punti, 1):
            nota = getattr(p, 'note', '')
            tree.insert("", tk.END, values=(i, f"{p.nome} {p.cognome}", p.via, nota))
        
        tree.pack(fill="x")
        
    def mostra_barra_progresso_tabella(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=(10, 0), padx=10)

        label = tk.Label(frame, text="Preparazione liste indirizzi...", anchor="w")
        label.pack(fill="x")

        bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", maximum=100)
        bar.pack(fill="x", pady=5)

        return label, bar

    def aggiorna_barra_progresso(self, label, bar, value, maximum, testo=None):
        bar.configure(maximum=maximum, value=value)
        if testo:
            label.configure(text=testo)
        else:
            label.configure(text=f"Elaborazione {value}/{maximum}")
        bar.update_idletasks()
        label.update_idletasks()

    def apri_finestra_giri(self):
        """Funzione di apertura finestra con giri esposti(da aggiungere esportazione a Excel o PDF)"""
        n_mezzi = 2

        ottimizzatore = OttimizzatorePercorsi(45.637, 13.791)

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Generazione Percorsi")
        progress_window.geometry("520x160")
        progress_window.resizable(False, False)

        progress_label, progress_bar = self.mostra_barra_progresso_tabella(progress_window)
        
        def progress_callback(step, total, message=""):
            testo = message if message else f"Ottimizzazione {step}/{total}"
            self.aggiorna_barra_progresso(progress_label, progress_bar, step, total, testo)

        tutti_i_giri = ottimizzatore.genera_giri(self.gi.vault, n_mezzi, progress_callback=progress_callback)
        self.aggiorna_barra_progresso(progress_label, progress_bar, 1, 1, "Ottimizzazione completata")

        progress_window.after(300, progress_window.destroy)

        graph_window = tk.Toplevel(self.root)
        graph_window.title("Grafico Percorsi")
        graph_window.geometry("780x500")
        graph_window.resizable(True, True)

        plot_frame = tk.Frame(graph_window)
        plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        fig = crea_figura_giri(tutti_i_giri, sede_lat=45.637, sede_lon=13.791)
        plot_canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        plot_canvas.draw()
        plot_widget = plot_canvas.get_tk_widget()
        plot_widget.pack(fill="both", expand=True)

        list_window = tk.Toplevel(self.root)
        list_window.title("Liste Indirizzi per Mezzo")
        list_window.geometry("760x620")
        list_window.resizable(True, True)

        list_frame = tk.LabelFrame(list_window, text="Liste indirizzi per mezzo", padx=8, pady=8)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        colori = ["blue", "red", "green", "orange", "purple", "brown", "darkcyan"]

        for i, giro in enumerate(tutti_i_giri):
            colore_titolo = colori[i % len(colori)]
            self.crea_tabella_giro(scrollable_frame, f"GIRO {i+1}", colore_titolo, giro)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def controlla_database_locale(self):
        """Metodo che incrocia indirizzi.json con DataAddress.json"""
        if not os.path.exists('DataAddress.json'):
            messagebox.showerror("Errore", "File DataAddress.json non trovato!")
            return

        with open('DataAddress.json', 'r', encoding='utf-8') as f:
            db_osm = json.load(f)

        trovati = 0
        mancanti = []
        
        for persona in self.gi.vault:
            input_pulito = persona.via.lower().strip().replace(",", "")
            
            match_trovato = False
            for elemento in db_osm:
                if elemento.get('categoria') in ['indirizzo', 'edificio']:
                    via_db = str(elemento.get('via', '')).lower().strip()
                    civico_db = str(elemento.get('civico', '')).lower().strip()
                    confronto_db = f"{via_db} {civico_db}".strip()

                    if input_pulito == confronto_db:
                        persona.lat = elemento.get('lat')
                        persona.lon = elemento.get('lon')
                        match_trovato = True
                        trovati += 1
                        break
            
            if not match_trovato:
                mancanti.append(persona.via)

        self.gi.salva_json()
        
        msg = f" Aggiornamento completato!\nIndirizzi con coordinate: {trovati}"
        if mancanti:
            msg += "\n\n Non trovati nel database:\n" + "\n".join(mancanti[:5])
            if len(mancanti) > 5: msg += "\n..."
        
        messagebox.showinfo("Esito Verifica", msg)

    def salva_e_verifica(self):
        dati = {}
        for chiave, _ in self.campi_config:
            if chiave == "whitelist":
                dati[chiave] = self.whitelist_var.get()
            else:
                dati[chiave] = self.entries[chiave].get().strip()
        
        if not dati['nome'] or not dati['cognome']:
            messagebox.showwarning("Attenzione", "I campi Nome e Cognome sono obbligatori!")
            return
        if not dati['via']:
            messagebox.showwarning("Attenzione", "Il campo Via è obbligatorio!")
            return
            
        is_white = bool(dati['whitelist'])
        
        self.controlla_database_locale()

        self.gi.aggiungi_indirizzo(
            nome=dati['nome'], 
            cognome=dati['cognome'], 
            via=dati['via'], 
            in_whitelist=is_white,
            note=dati.get('note', '')
        )
        
        self.pulisci_campi()
        messagebox.showinfo("Successo", "Contatto salvato e coordinate verificate!")