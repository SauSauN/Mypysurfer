import re
import sqlite3

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTabWidget, QWidget, QMenu, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
    
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QPushButton, QProgressBar, QComboBox, QListWidget, QDialog,
    QFileDialog, QLabel, QTabWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineCore import QWebEngineHttpRequest
import sys
import os

from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocked_domains):
        super().__init__()
        self.blocked_domains = blocked_domains

    def interceptRequest(self, info):
        """Intercepte les requêtes et bloque les domaines publicitaires."""
        url = info.requestUrl().toString()
        if any(domain in url for domain in self.blocked_domains):
            info.block(True)  # Bloque la requête


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

        self.forward_button = QPushButton(">")
        self.forward_button.clicked.connect(self.navigate_forward)

        self.refresh_button = QPushButton("⟳")
        self.refresh_button.clicked.connect(self.refresh)

        self.home_button = QPushButton("🏠")
        self.home_button.clicked.connect(self.open_new_tab)

        self.favorites_button = QPushButton("⭐")
        self.favorites_button.clicked.connect(self.save_to_favorites)

        self.dark_mode_button = QPushButton("🌙")
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

        # Nouveau bouton de recherche
        self.search_button = QPushButton("🔍 Rechercher")
        self.search_button.clicked.connect(self.perform_search)

        # Nouveau bouton pour ouvrir un nouvel onglet
        self.new_tab_button = QPushButton("+ Onglet")
        self.new_tab_button.clicked.connect(self.open_new_tab)

        # Nouveau bouton pour télécharger un fichier
        self.download_button = QPushButton("Télécharger")
        self.download_button.clicked.connect(self.download_file)
        
        # Nouveau bouton pour afficher les informations de la page
        self.page_info_button = QPushButton("ℹ️ Infos")
        self.page_info_button.clicked.connect(self.show_page_info)

        # Add a button to show the functionalities
        self.button_Fonctionnalites = QPushButton("Fonctionnalités")
        self.button_Fonctionnalites.clicked.connect(self.show_functionality_menu)

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

        # Initialisation des favoris SQLite
        self.init_favorites_db()

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

    def navigate_to_url(self):  
        """Navigue vers l'URL de la barre d'adresse.""" 
        url = self.url_bar.text().strip()  # Enlève les espaces superflus
        current_browser = self.tab_widget.currentWidget()

        if current_browser:
            # Cas 1 : Si l'URL commence par http:// ou https://, on la charge directement.
            if url.startswith("http://") or url.startswith("https://"):
                pass
            
            # Cas 2 : Si l'URL commence par www., on ajoute http:// au début.
            elif url.startswith("www."):
                url = "http://" + url
            
            # Cas 4 : Si l'URL correspond à un domaine valide avec TLD (comme facebook.com).
            elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,10}$', url):  # TLD plus flexibles
                url = "http://" + url
            
            # Cas 3 : Sinon, il s'agit probablement d'une recherche.
            else:
                url = f"{self.current_search_engine}{url}"
            
            # Créer un objet QWebEngineHttpRequest pour personnaliser la requête
            request = QWebEngineHttpRequest(QUrl(url))
            
            # Ajouter des en-têtes personnalisés (si nécessaire)
            request.setRawHeader("User-Agent", "MonUserAgent")

            # Charger la page avec la requête (en utilisant load(request)) ou en utilisant load(url) directement
            current_browser.load(request)  # Vous pouvez également utiliser `current_browser.setUrl(QUrl(url))` si vous voulez une solution plus simple.

    def show_functionality_menu(self):
        """Affiche un menu avec des fonctionnalités."""
        menu = QMenu(self)
        
        # Créer les actions du menu
        show_favorites_action = QAction("Afficher les favoris", self)
        show_favorites_action.triggered.connect(self.show_favorites)

        show_history_action = QAction("Afficher l'historique", self)
        show_history_action.triggered.connect(self.show_history)
        
        enable_adblock_action = QAction("Activer AdBlock", self)
        enable_adblock_action.triggered.connect(self.enable_ad_blocker)
        
        disable_adblock_action = QAction("Désactiver AdBlock", self)
        disable_adblock_action.triggered.connect(self.disable_ad_blocker)

        # Ajouter les actions au menu
        menu.addAction(show_favorites_action)
        menu.addAction(show_history_action)
        menu.addAction(enable_adblock_action)
        menu.addAction(disable_adblock_action)

        # Afficher le menu
        menu.exec_(self.button_Fonctionnalites.mapToGlobal(self.button_Fonctionnalites.rect().topLeft()))

    def enable_ad_blocker(self):
        """Active le blocage des publicités."""
        blocked_domains = ["ads", "tracking", "doubleclick", "adservice"]
        self.ad_blocker = AdBlocker(blocked_domains)  # Crée une instance de l'intercepteur
        
        # Appliquer l'intercepteur à chaque onglet
        for i in range(self.tab_widget.count()):
            browser = self.tab_widget.widget(i)
            if hasattr(browser, "page"):
                browser.page().profile().setUrlRequestInterceptor(self.ad_blocker)
        
        self.statusBar().showMessage("AdBlock activé")

    def disable_ad_blocker(self):
        """Désactive le blocage des publicités."""
        # Supprime l'intercepteur pour chaque onglet
        for i in range(self.tab_widget.count()):
            browser = self.tab_widget.widget(i)
            if hasattr(browser, "page"):
                browser.page().profile().setUrlRequestInterceptor(None)
        
        self.statusBar().showMessage("AdBlock désactivé")

    def add_to_history(self, url):
        """Ajoute une URL à la base de données de l'historique en évitant les doublons, avec une date de visite personnalisée."""
        try:
            # Vérifie si l'URL existe déjà dans l'historique
            self.db_cursor.execute("SELECT 1 FROM history WHERE url = ?", (url,))
            if self.db_cursor.fetchone():
                print(f"L'URL {url} est déjà dans l'historique.")
                return  # Si l'URL existe déjà, on ne l'ajoute pas

            # Récupère la date et l'heure actuelles
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insère l'URL, le titre et la date dans l'historique
            self.db_cursor.execute("INSERT INTO history (url,date_visited) VALUES (?, ?)", (url, current_date))
            self.db_connection.commit()

        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout à l'historique: {e}")

    def change_search_engine(self):
        """Change le moteur de recherche basé sur la sélection."""
        engine = self.search_engine_selector.currentText()
        if engine == "Google":
            self.current_search_engine = "https://www.google.com/search?q="
        elif engine == "Bing":
            self.current_search_engine = "https://www.bing.com/search?q="
        elif engine == "DuckDuckGo":
            self.current_search_engine = "https://duckduckgo.com/?q="
        elif engine == "Yahoo":
            self.current_search_engine = "https://search.yahoo.com/search?p="

    def navigate_home(self):
        """Navigue vers la page d'accueil."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("https://www.google.com"))

    def navigate_back(self):
        """Revenir à la page précédente."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.back()

    def navigate_forward(self):
        """Aller à la page suivante."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.forward()

    def refresh(self):
        """Rafraîchir l'onglet actuel."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.reload()

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
                print(f"Favori ajouté : {url} - {title}")
            except sqlite3.IntegrityError:
                print("Ce favori existe déjà.")

    def show_favorites(self):
        """Affiche les favoris dans un nouvel onglet."""
        favorites_browser = QWebEngineView()
        favorites_browser.setUrl(QUrl("about:blank"))

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
                html_content += f"<li><p>{date}</p>---<a href='{url}' target='_blank'>{url}</a></li>"

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
        if search_query:
            url = self.current_search_engine + search_query
            current_browser = self.tab_widget.currentWidget()
            
            # Si aucun onglet n'est ouvert, créez-en un nouveau
            if current_browser is None:
                self.open_new_tab()
                current_browser = self.tab_widget.currentWidget()
            
            # Navigue vers l'URL dans l'onglet actuel
            if isinstance(current_browser, QWebEngineView):
                current_browser.setUrl(QUrl(url))
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

    def open_new_tab(self):
        """Ouvre un nouvel onglet."""        
        browser = QWebEngineView()
        browser.setUrl(QUrl("https://www.google.com"))
        index = self.tab_widget.addTab(browser, "Nouvel Onglet")
        self.tab_widget.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
