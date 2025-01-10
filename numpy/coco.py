from io import BytesIO
import re
import sqlite3
import sys
from tkinter import Image
import requests

from collections import deque
from datetime import datetime

from PyQt5.QtCore import QUrl,QByteArray
from PyQt5.QtGui import   QIcon,  QPixmap,  QKeySequence 
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QProgressBar, QComboBox,
    QFileDialog, QTabWidget, QShortcut, QMenu, QAction
)

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocked_domains):
        super().__init__()
        self.blocked_domains = blocked_domains

    def interceptRequest(self, info):
        blocked_domains = [
            "ads", 
            "tracking", 
            "doubleclick", 
            "adservice", 
            "googlesyndication",
            "googler.com",
            "facebook.com",
            "flashtalking.com",
            "serving-sys.com",
            "openx.net",
            "adroll.com",
            "rubiconproject.com",
            "t.co",
            "criteo.com",
            "amazon-adsystem.com",
        ]
        
        # Vérifier si l'URL contient un domaine de publicité à bloquer
        url = info.requestUrl().toString()
        if any(domain in url for domain in blocked_domains):
            info.block(True)  # Bloque la requête

        # Bloquer les fenêtres popups JavaScript
        if "popup" in url or "advert" in url:
            info.block(True)  # Bloque les popups JavaScript

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySurf")
        self.setGeometry(100, 100, 1024, 768)

        # Composants du navigateur
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # Choix du moteur de recherche
        self.search_engine_selector = QComboBox()
        self.search_engine_selector.addItems([
            "Google", "Bing", "DuckDuckGo", "Yahoo"
        ])
        self.search_engine_selector.currentIndexChanged.connect(self.change_search_engine)

        self.current_search_engine = "https://www.google.com/search?q="

        # Boutons de navigation
        self.back_button = QPushButton("<")
        self.back_button.clicked.connect(self.navigate_back)
        self.back_button.setToolTip("Revenir à la page précédente.")

        self.forward_button = QPushButton(">")
        self.forward_button.clicked.connect(self.navigate_forward)
        self.forward_button.setToolTip("Aller à la page suivante.")

        self.refresh_button = QPushButton("⟳")
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh_button.setToolTip("Rafraîchir la page actuelle.")

        self.home_button = QPushButton("🏠")
        self.home_button.clicked.connect(self.navigate_home)
        self.home_button.setToolTip("Aller à la page d'accueil.")

        self.favorites_button = QPushButton("⭐")
        self.favorites_button.clicked.connect(self.save_to_favorites)
        self.favorites_button.setToolTip("Ajouter la page actuelle aux favoris.")

        self.dark_mode_button = QPushButton("🌙")
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.dark_mode_button.setToolTip("Activer/désactiver le mode sombre.")

        # Nouveau bouton de recherche
        self.search_button = QPushButton("🔍 Rechercher")
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setToolTip("Lancer une recherche sur le web.")

        # Nouveau bouton pour ouvrir un nouvel onglet
        self.new_tab_button = QPushButton("+ Onglet")
        self.new_tab_button.clicked.connect(self.open_new_tab)
        self.new_tab_button.setToolTip("Ouvrir un nouvel onglet.")

        # Nouveau bouton pour télécharger un fichier
        self.download_button = QPushButton("Télécharger")
        self.download_button.clicked.connect(self.download_file)
        self.download_button.setToolTip("Télécharger le fichier de la page.")
        
        # Nouveau bouton pour afficher les informations de la page
        self.page_info_button = QPushButton("ℹ️ Infos")
        self.page_info_button.clicked.connect(self.show_page_info)
        self.page_info_button.setToolTip("Afficher les informations de la page.")

        # Add a button to show the functionalities
        self.button_Fonctionnalites = QPushButton("Fonctionnalités")
        self.button_Fonctionnalites.clicked.connect(self.show_functionality_menu)
        self.button_Fonctionnalites.setToolTip("Afficher les fonctionnalités du navigateur.")

        

        # Barre de progression
        self.progress_bar = QProgressBar()

        # Layout de la barre de navigation
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addWidget(self.favorites_button)
        nav_layout.addWidget(self.dark_mode_button)
        nav_layout.addWidget(self.search_engine_selector)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.search_button)  # Ajouter le bouton de recherche
        nav_layout.addWidget(self.page_info_button)
        nav_layout.addWidget(self.new_tab_button)  # Ajouter le bouton de nouvel onglet
        # Ajouter le bouton au layout de la barre de navigation
        nav_layout.addWidget(self.button_Fonctionnalites)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addLayout(nav_layout)  # Barre de navigation
        main_layout.addWidget(self.tab_widget)  # Onglets
        #main_layout.addWidget(self.progress_bar)  # Barre de progression

        # Conteneur central
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Liste de l'historique et des favoris
        self.history = []
        self.favorites = []

        # Liste pour stocker les onglets fermés
        self.closed_tabs = []
                
        # Initialisation de la deque pour les favoris
        self.file = deque(maxlen=10)  # Limite de taille de 10 éléments

        self.pile = [] 

        # Initialisation des favoris SQLite
        self.init_favorites_db()



        # Raccourci pour ouvrir un nouvel onglet
        self.new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.new_tab_shortcut.activated.connect(self.open_new_tab)

        # Raccourci pour fermer un onglet
        self.close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_tab_shortcut.activated.connect(self.close_current_tab)

        # Raccourci pour rouvrir l'onglet fermé
        self.reopen_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        self.reopen_tab_shortcut.activated.connect(self.reopen_last_closed_tab)

        # Raccourci pour rafraîchir la page
        self.refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.refresh_shortcut.activated.connect(self.refresh)

        self.onglet_name = "Nouvel Onglet"
        self.onglet_Favoris = "Favoris"
        self.onglet_Historique = "Historique"
        # Ajouter un premier onglet
        self.open_new_tab()

        # Signaux et slots
        # self.tab_widget.currentChanged.connect(self.update_url_bar)

    def init_favorites_db(self):  
        # Spécifier le nom de la base de données (ici "navigateur.db")
        self.db_connection = sqlite3.connect('navigateur.db')
        self.db_cursor = self.db_connection.cursor()

        # Créer la table de l'historique si elle n'existe pas
        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            date_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.db_connection.commit()
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                date_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db_connection.commit()
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS openpages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT UNIQUE NOT NULL
            )
        """)
        self.db_connection.commit()


        self.load_favorites_from_db()
        self.load_history_from_db()

    def load_favorites_from_db(self):
        """Charge les favoris depuis la base de données."""
        self.favorites = []
        self.db_cursor.execute("SELECT url, title,date_visited FROM favorites ORDER BY date_visited DESC")
        for row in self.db_cursor.fetchall():
            self.favorites.append({"url": row[0], "title": row[1], "date_visited": row[2]})

    def load_history_from_db(self):
        """Charge les favoris depuis la base de données."""
        self.history = []
        self.db_cursor.execute("SELECT url, date_visited FROM history")
        for row in self.db_cursor.fetchall():
            self.history.append({"url": row[0], "title": row[1]})

    def navigate_to_url(self, url, current_browser):
        """Navigue vers l'URL de la barre d'adresse."""
        if current_browser:
            # Cas 1 : Si l'URL commence par http:// ou https://, on la charge directement.
            if url.startswith("http://") or url.startswith("https://"):
                self.load_url(url, current_browser)
    
            # Cas 2 : Si l'URL commence par www., on ajoute http:// au début.
            elif url.startswith("www."):
                url = "http://" + url
                self.load_url(url, current_browser)
            
            # Cas 3 : Si l'URL est un domaine valide sans protocole (ex: youtube.com).
            elif self.is_valid_domain(url):  # Vérifie si c'est un domaine valide
                url = "http://" + url
                self.load_url(url, current_browser)
            
            # Cas 4 : Sinon, c'est probablement une recherche, on utilise le moteur de recherche.
            else:
                search_url = f"{self.current_search_engine}{url}"
                url = search_url
                self.load_url(search_url, current_browser)
            
            self.url_bar.setText(url)

    def load_url(self, url, current_browser):
        """Charge l'URL dans le navigateur."""
        #print(f"Chargement de l'URL: {url}")  # Log pour vérifier l'URL avant le chargement
        current_browser.load(QUrl(url))
    
    def is_valid_domain(self, url):
        """Vérifie si l'URL est un domaine valide sans le protocole (ex: youtube.com)."""
        return re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,10}$', url) is not None

    def close_current_tab(self):
        """Fermer l'onglet actuel et sauvegarder les informations."""
        current_index = self.tab_widget.currentIndex()
        if current_index != -1: 
            browser = self.tab_widget.widget(current_index)
            if isinstance(browser, QWebEngineView):
                # Obtenir l'URL de la page active
                url = browser.url().toString() 
                # Obtenir le titre de l'onglet
                title = self.tab_widget.tabText(current_index)
                
                # Sauvegarder dans la base de données et ajouter à la file
                try:
                    self.db_cursor.execute("INSERT INTO openpages (title, url) VALUES (?, ?)", (title, url))
                    self.db_connection.commit()
                except sqlite3.IntegrityError:
                    print(f"L'URL {url} existe déjà dans la base de données.")
                
                # Sauvegarder dans la base de données
                self.pile.append({"url": url, "title": title}) 

                
                # Fermer l'onglet
                self.tab_widget.removeTab(current_index)

    def reopen_last_closed_tab(self):
        """Réouvrir le dernier onglet fermé depuis la file."""
        if self.pile:
            first_value = self.pile.pop()  # Retirer et retourner l'élément du dessus

            # Extraire l'URL et le titre du dictionnaire
            url = first_value["url"]
            title = first_value["title"]

            self.open_new_tab()
            current_browser = self.tab_widget.currentWidget()
            
            # Navigue vers l'URL dans l'onglet actuel
            if isinstance(current_browser, QWebEngineView):
                # current_browser.setUrl(QUrl(url))
                self.navigate_to_url(url,current_browser) 
                self.history.append(url)  # Ajoute l'URL à l'historique

                # Ajouter l'URL à l'historique dans la base de données
                self.add_to_history(url)
                
                # Mettre à jour le titre une fois la page chargée
                current_browser.titleChanged.connect(self.update_tab_title)
        else:
            try:  
                self.db_cursor.execute("SELECT COUNT(*) FROM openpages")    
                count = self.db_cursor.fetchone()[0]  # Récupérer la valeur réelle du comptage
                
                # Limiter à 10 éléments si le nombre total d'éléments est supérieur à 10
                limit = min(count, 10)

                # Charger les derniers 
                self.db_cursor.execute(f"SELECT url, title FROM openpages ORDER BY id DESC LIMIT {limit}")
                for row in self.db_cursor.fetchall():
                    self.pile.append({"url": row[0], "title": row[1]})
                
                self.pile.reverse()
                self.reopen_last_closed_tab()
            except sqlite3.IntegrityError:
                print(f"****")

    def show_functionality_menu(self):
        """Affiche un menu avec des fonctionnalités."""
        menu = QMenu(self)
        
        # Créer les actions du menu
        show_favorites_action = QAction("Afficher les favoris", self)
        show_favorites_action.triggered.connect(self.show_favorites)
        show_favorites_action.setToolTip("Afficher la liste des favoris.")

        show_history_action = QAction("Afficher l'historique", self)
        show_history_action.triggered.connect(self.show_history)
        show_history_action.setToolTip("Afficher l'historique des pages.")
        
        enable_adblock_action = QAction("Activer AdBlock", self)
        enable_adblock_action.triggered.connect(self.enable_ad_blocker)
        enable_adblock_action.setToolTip("Activer le bloqueur de publicités.")
        
        disable_adblock_action = QAction("Désactiver AdBlock", self)
        disable_adblock_action.triggered.connect(self.disable_ad_blocker)
        enable_adblock_action.setToolTip("Désactiver le bloqueur de publicités.")

        full_screen_button = QAction("⛶ Activer/désactiver", self)
        full_screen_button.triggered.connect(self.toggle_full_screen)
        full_screen_button.setToolTip("Activer/désactiver le mode plein écran.")

        screenshot_button = QAction("📸 Capture de page", self)
        screenshot_button.triggered.connect(self.take_screenshot)
        screenshot_button.setToolTip("Capturer une image de la page actuelle.")
        
        zoom_in_button = QAction("🔍 zoom +", self)
        zoom_in_button.triggered.connect(self.zoom_in)
        zoom_in_button.setToolTip("Zoomer sur la page.")

        zoom_out_button = QAction("🔍 zoom -", self)
        zoom_out_button.triggered.connect(self.zoom_out)
        zoom_out_button.setToolTip("Dézoomer sur la page.")

        





        # Ajouter les actions au menu
        menu.addAction(show_favorites_action)
        menu.addAction(show_history_action)
        menu.addAction(enable_adblock_action)
        menu.addAction(disable_adblock_action)
        menu.addAction(full_screen_button)
        menu.addAction(screenshot_button)
        menu.addAction(zoom_in_button)
        menu.addAction(zoom_out_button)

        # Afficher le menu
        menu.exec_(self.button_Fonctionnalites.mapToGlobal(self.button_Fonctionnalites.rect().topLeft()))

    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def zoom_in(self):
        # Accéder à la page du navigateur pour obtenir et modifier le zoom
        current_zoom = self.browser.page().zoomFactor()
        self.browser.page().setZoomFactor(current_zoom + 0.1)

    def zoom_out(self):
        # Accéder à la page du navigateur pour obtenir et modifier le zoom
        current_zoom = self.browser.page().zoomFactor()
        self.browser.page().setZoomFactor(current_zoom - 0.1)
    
    def take_screenshot(self):
        # Utilisation de QWidget.grab() pour capturer une image de la fenêtre
        screenshot = self.grab()  # Prendre une capture d'écran de la fenêtre
        
        # Ouvrir une boîte de dialogue pour demander à l'utilisateur où enregistrer l'image
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer l'image", "", "Images PNG (*.png);;Tous les fichiers (*)", options=options)
        
        if file_path:
            screenshot.save(file_path, 'PNG')  # Sauvegarder l'image à l'emplacement sélectionné

    def navigate_home(self):
        """Navigue vers la page d'accueil en fonction du moteur de recherche sélectionné."""
        current_browser = self.tab_widget.currentWidget()
        selected_engine = self.search_engine_selector.currentText()  # Récupère le moteur de recherche sélectionné
        if current_browser:

            if selected_engine == "Google":
                current_browser.setUrl(QUrl("https://www.google.com"))
                # Ajouter un texte par défaut à la barre d'adresse
                self.url_bar.setText("https://www.google.com")
            elif selected_engine == "Bing":
                current_browser.setUrl(QUrl("https://www.bing.com"))
                self.url_bar.setText("https://www.bing.com")
            elif selected_engine == "DuckDuckGo":
                current_browser.setUrl(QUrl("https://duckduckgo.com"))
                self.url_bar.setText("https://duckduckgo.com")
            elif selected_engine == "Yahoo":
                current_browser.setUrl(QUrl("https://search.yahoo.com"))
                self.url_bar.setText("https://search.yahoo.com")
                    # Si aucun onglet n'est ouvert, créez-en un nouveau
                    
        elif current_browser is None:
            self.open_new_tab()

    def enable_ad_blocker(self):
        """Active le blocage des publicités."""
        blocked_domains = ["ads", "tracking", "doubleclick", "adservice"]
        self.ad_blocker = AdBlocker(blocked_domains)  # Crée une instance de l'intercepteur
        
        self.init_browser()
        
        # Change la couleur du bouton en rouge clair
        self.button_Fonctionnalites.setStyleSheet("""
                color: red; 
            }
        """)

    def init_browser(self):
        # Applique l'intercepteur à chaque onglet du navigateur
        for i in range(self.tab_widget.count()):
            browser = self.tab_widget.widget(i)
            if isinstance(browser, QWebEngineView):
                browser.page().profile().setRequestInterceptor(self.ad_blocker)

    def disable_ad_blocker(self):
        """Désactive le blocage des publicités."""
        # Supprime l'intercepteur pour chaque onglet
        for i in range(self.tab_widget.count()):
            browser = self.tab_widget.widget(i)
            if isinstance(browser, QWebEngineView):  # Vérifie que le widget est bien un QWebEngineView
                # Supprime l'intercepteur de la page
                browser.page().profile().setRequestInterceptor(None)

        # Change la couleur du bouton en rouge clair
        self.button_Fonctionnalites.setStyleSheet("""
            QPushButton {
                
            }
        """)

    def add_to_history(self, url):
        """Ajoute une URL à la base de données de l'historique en évitant les doublons, avec une date de visite personnalisée."""
        try:

            # Récupère la date et l'heure actuelles
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insère l'URL, le titre et la date dans l'historique
            self.db_cursor.execute("INSERT INTO history (url,date_visited) VALUES (?, ?)", (url, current_date))
            self.db_connection.commit()

        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout à l'historique: {e}")

    def change_search_engine(self):
        """Change le moteur de recherche basé sur la sélection."""
        self.engine = self.search_engine_selector.currentText()
        if self.engine == "Google":
            self.current_search_engine = "https://www.google.com/search?q="
        elif self.engine == "Bing":
            self.current_search_engine = "https://www.bing.com/search?q="
        elif self.engine == "DuckDuckGo":
            self.current_search_engine = "https://duckduckgo.com/?q="
        elif self.engine == "Yahoo":
            self.current_search_engine = "https://search.yahoo.com/search?p="

    def navigate_back(self):
        """Revenir à la page précédente."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.back()
            current_url = current_browser.url().toString()
            self.url_bar.setText(current_url)
            # Affiche uniquement la page actuelle après le retour
            #current_entry = current_browser.history().currentItem()
            #print(f"**********************************************************")
            #print(f"++++++++++++URL actuelle: {current_entry.url().toString()}, Titre: {current_entry.title()}++++++++++++")

    def navigate_forward(self):
        """Aller à la page suivante, si possible."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser and current_browser.history().canGoForward():
            current_browser.forward()
            current_url = current_browser.url().toString()
            self.url_bar.setText(current_url)

    def refresh(self):
        """Rafraîchir l'onglet actuel."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.reload()
            current_url = current_browser.url().toString()
            self.url_bar.setText(current_url)

    def save_to_favorites(self):
        """Ajouter l'URL actuelle aux favoris."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            url = current_browser.url().toString()
            title = current_browser.title()
            # Récupère la date et l'heure actuelles
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                self.db_cursor.execute("INSERT INTO favorites (url, title,date_visited) VALUES (?, ?, ?)", (url, title,current_date))
                self.db_connection.commit()
                self.load_favorites_from_db()
            except sqlite3.IntegrityError:
                print("Ce favori existe déjà.")

    def show_favorites(self):
        """Affiche les favoris dans un nouvel onglet."""
        favorites_browser = QWebEngineView()
        favorites_browser.setUrl(QUrl("about:blank"))
        self.url_bar.setText("about:blank")

        # HTML et CSS pour l'affichage des favoris
        html_content = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                    color: #333;
                }
                h1 {
                    color: #0056b3;
                    text-align: center;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin: 10px 0;
                    padding: 10px;
                    background: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    transition: background-color 0.3s, box-shadow 0.3s;
                }
                li:hover {
                    background-color: #f1f1f1;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }
                a {
                    text-decoration: none;
                    color: #0056b3;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                    color: #003d80;
                }
            </style>
        </head>
        <body>
            <h1>Favoris</h1>
            <ul>
        """

        # Ajout des favoris à la liste
        for fav in self.favorites:
            html_content += f"<li><p>{fav['date_visited']}</p>---<a href='{fav['url']}' target='_blank'>{fav['title'] or fav['url']}</a></li>"

        html_content += """
            </ul>
        </body>
        </html>
        """

        # Affichage du contenu HTML dans l'onglet
        favorites_browser.setHtml(html_content)

        index = self.tab_widget.addTab(favorites_browser, self.onglet_Favoris)
        self.tab_widget.setCurrentIndex(index)

    def show_history(self):
        """Affiche l'historique dans un nouvel onglet depuis la base de données avec le même style CSS que pour les favoris."""
        history_browser = QWebEngineView()  # Crée un nouveau QWebEngineView pour l'onglet
        history_browser.setUrl(QUrl("about:blank"))  # Définir une URL vide ou blanche
        self.url_bar.setText("about:blank")

        # HTML et CSS pour l'affichage de l'historique
        html_content = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                    color: #333;
                }
                h1 {
                    color: #0056b3;
                    text-align: center;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin: 10px 0;
                    padding: 10px;
                    background: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    transition: background-color 0.3s, box-shadow 0.3s;
                }
                li:hover {
                    background-color: #f1f1f1;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }
                a {
                    text-decoration: none;
                    color: #0056b3;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                    color: #003d80;
                }
            </style>
        </head>
        <body>
            <h1>Historique des Pages Visitées</h1>
            <ul>
        """

        try:
            # Récupère l'historique des pages depuis la base de données
            self.db_cursor.execute("SELECT url, date_visited FROM history ORDER BY date_visited DESC")
            rows = self.db_cursor.fetchall()

            # Affiche chaque URL dans la page HTML
            for row in rows:
                url = row[0]
                date = row[1]
                html_content += f"<li><p>{date}</p>--- <a href='{url}' target='_blank'>{url}</a></li>"

            html_content += """
            </ul>
        </body>
        </html>
        """

            # Charge le contenu HTML dans le navigateur
            history_browser.setHtml(html_content)

        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de l'historique: {e}")

        # Ouvre un nouvel onglet pour afficher l'historique
        index = self.tab_widget.addTab(history_browser, self.onglet_Historique)
        self.tab_widget.setCurrentIndex(index)

    def toggle_dark_mode(self):
        """Active/désactive le mode sombre."""
        if self.dark_mode_button.isChecked():
            dark_style = """
                QWidget {
                    background-color: rgb(133, 132, 132);
                }
                QLineEdit {
                    background-color:rgb(133, 132, 132);
                }
                QPushButton {
                    background-color: #444444;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #555555;
                }
                QComboBox {
                    background-color: #333333;
                    color: white;
                }
            """
            self.setStyleSheet(dark_style)
        else:
            self.setStyleSheet("")  # Réinitialiser le style

    def update_progress(self, progress):
        """Met à jour la barre de progression."""
        self.progress_bar.setValue(progress)

    def perform_search(self):
        """Effectuer une recherche en utilisant le moteur sélectionné, avec gestion du titre."""
        search_query = self.url_bar.text().strip()
        self.file.clear()
        if search_query:
            url = search_query
            current_browser = self.tab_widget.currentWidget()
            
            # Si aucun onglet n'est ouvert, créez-en un nouveau
            if current_browser is None:
                self.open_new_tab()
                current_browser = self.tab_widget.currentWidget()
            
            # Navigue vers l'URL dans l'onglet actuel
            if isinstance(current_browser, QWebEngineView):
                # current_browser.setUrl(QUrl(url))
                self.navigate_to_url(url,current_browser) 
                self.history.append(url)  # Ajoute l'URL à l'historique

                # Ajouter l'URL à l'historique dans la base de données
                self.add_to_history(url)
                
                # Mettre à jour le titre une fois la page chargée
                current_browser.titleChanged.connect(self.update_tab_title)
                
    def update_tab_title(self, title):
        """Met à jour le titre de l'onglet actif avec une longueur fixe et complète si nécessaire."""
        max_length = 10  # Longueur maximale du titre
        min_length = 10  # Longueur minimale de l'affichage

        # Tronquer ou compléter le titre
        if len(title) > max_length:
            truncated_title = title[:max_length] + "..."
        else:
            truncated_title = title.ljust(min_length)  # Complète avec des espaces

        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.setTabText(current_index, truncated_title)

    def download_file(self):
        """Gérer les téléchargements."""
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(self, "Enregistrer le fichier", "", "Tous les fichiers (*)")
        if file_path:
            # Téléchargement simulé, implémentation spécifique peut être ajoutée ici
            print(f"Téléchargement du fichier à: {file_path}")

    def close_tab(self, index):
        """Fermer l'onglet actuel."""
        self.tab_widget.removeTab(index)

    def show_page_info(self):
        """Affiche les informations sur la page actuelle dans un nouvel onglet."""
        current_browser = self.tab_widget.currentWidget()
        
        if current_browser and isinstance(current_browser, QWebEngineView):
            # Récupérer les informations de la page
            has_selection = current_browser.hasSelection()
            icon_url = current_browser.iconUrl().toString()
            selected_text = current_browser.selectedText() if has_selection else "Aucun texte sélectionné"
            title = current_browser.title() or "Titre non disponible"
            url = current_browser.url().toString()
            zoom_factor = current_browser.zoomFactor()

            # Créer le contenu HTML avec les informations sur la page
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background-color: #f4f4f4;
                        color: #333;
                    }}
                    h1 {{
                        color: #333;
                        text-align: center;
                    }}
                    ul {{
                        list-style-type: none;
                        padding: 0;
                    }}
                    li {{
                        margin: 8px 0;
                        padding: 10px;
                        background: #fff;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }}
                    .title {{
                        font-weight: bold;
                    }}
                    .url {{
                        color: #0066cc;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <h1>Informations sur la page</h1>
                <ul>
                    <li><span class="title">Titre :</span> {title}</li>
                    <li><span class="title">URL :</span> <a href="{url}" class="url" target="_blank">{url}</a></li>
                    <li><span class="title">Icône :</span> <img src="{icon_url}" width="16" height="16" /></li>
                    <li><span class="title">Texte sélectionné :</span> {selected_text}</li>
                    <li><span class="title">Facteur de zoom :</span> {zoom_factor}</li>
                </ul>
            </body>
            </html>
            """

            # Créer un nouveau navigateur pour afficher les informations
            info_browser = QWebEngineView()
            info_browser.setHtml(html_content)

            # Ouvrir un nouvel onglet pour afficher ces informations
            index = self.tab_widget.addTab(info_browser, "Infos Page")
            self.tab_widget.setCurrentIndex(index)
            self.url_bar.setText("about:blank")

    def open_new_tab(self):
        """Ouvre un nouvel onglet."""        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        # Ajouter un nouvel onglet avec un titre temporaire
        index = self.tab_widget.addTab(self.browser, "Nouvel Onglet")
        self.tab_widget.setCurrentIndex(index)

        # Ajouter un texte par défaut à la barre d'adresse
        self.url_bar.setText("https://www.google.com")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())

