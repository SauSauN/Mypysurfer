import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QPushButton, QProgressBar, QComboBox, QListWidget, QDialog,
    QFileDialog, QLabel, QTabWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QUrl
import sys
import os

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mon Navigateur")
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

        self.history_button = QPushButton("🕒")
        self.history_button.clicked.connect(self.show_history)

        self.dark_mode_button = QPushButton("🌙")
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

        # Nouveau bouton de recherche
        self.search_button = QPushButton("🔍 Rechercher")
        self.search_button.clicked.connect(self.perform_search)

        # Nouveau bouton pour ouvrir un nouvel onglet
        self.new_tab_button = QPushButton("+ Onglet")
        self.new_tab_button.clicked.connect(self.open_new_tab)

        # Nouveau bouton pour afficher les favoris
        self.show_favorites_button = QPushButton("Favoris")
        self.show_favorites_button.clicked.connect(self.show_favorites)

        # Nouveau bouton pour télécharger un fichier
        self.download_button = QPushButton("Télécharger")
        self.download_button.clicked.connect(self.download_file)
        
        # Nouveau bouton pour afficher les informations de la page
        self.page_info_button = QPushButton("ℹ️ Infos")
        self.page_info_button.clicked.connect(self.show_page_info)

        # Barre de progression
        self.progress_bar = QProgressBar()

        # Layout de la barre de navigation
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addWidget(self.favorites_button)
        nav_layout.addWidget(self.show_favorites_button)
        nav_layout.addWidget(self.history_button)
        nav_layout.addWidget(self.dark_mode_button)
        nav_layout.addWidget(self.search_engine_selector)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.search_button)  # Ajouter le bouton de recherche
        nav_layout.addWidget(self.download_button)
        nav_layout.addWidget(self.new_tab_button)  # Ajouter le bouton de nouvel onglet
        # Ajouter le bouton au layout de la barre de navigation
        nav_layout.addWidget(self.page_info_button)

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

        # Ajouter un premier onglet
        self.open_new_tab()

        # Signaux et slots
        self.tab_widget.currentChanged.connect(self.update_url_bar)


    def open_new_tab(self):
        """Ouvre un nouvel onglet."""        
        browser = QWebEngineView()
        browser.setUrl(QUrl("https://www.google.com"))
        index = self.tab_widget.addTab(browser, "Nouvel Onglet")
        self.tab_widget.setCurrentIndex(index)
        self.update_url_bar()  # Met à jour la barre d'URL avec l'URL de l'onglet actuel

    def update_url_bar(self):
        """Met à jour la barre d'adresse en fonction de l'onglet actif."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def navigate_to_url(self):
        """Navigue vers l'URL de la barre d'adresse."""
        url = self.url_bar.text().strip()  # On enlève les espaces superflus
        current_browser = self.tab_widget.currentWidget()
        
        if current_browser:
            # Si l'URL ne commence pas par http:// ou https://, on vérifie si elle commence par www.
            if not url.startswith("http://") and not url.startswith("https://"):
                if url.startswith("www."):
                    # Ajouter http:// si l'URL commence par www.
                    url = "http://" + url
                elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{1,3}$', url):  # Vérification d'un domaine valide
                    # Ajouter http:// si l'URL semble être un nom de domaine avec extension de 1 à 3 lettres
                    url = "http://" + url
                else:
                    # Sinon, on traite l'URL comme une recherche.
                    url = self.current_search_engine + url
            
            # Charger l'URL dans le navigateur
            current_browser.setUrl(QUrl(url))
            self.history.append(url)  # Ajoute l'URL à l'historique

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
            self.favorites.append(url)
            with open("favorites.txt", "a") as file:
                file.write(url + "\n")
            print(f"Favori ajouté : {url}")

    def show_favorites(self):
        """Affiche les favoris dans un nouvel onglet."""
        # Crée un nouvel onglet pour afficher les favoris
        favorites_browser = QWebEngineView()
        favorites_browser.setUrl(QUrl("about:blank"))  # URL vide ou blanche

        # Crée une nouvelle page HTML pour afficher les favoris
        html_content = "<html><body><h1>Favoris</h1><ul>"
        for url in self.favorites:
            html_content += f"<li><a href='{url}'>{url}</a></li>"  # Affiche chaque URL des favoris
        html_content += "</ul></body></html>"

        # Charge le contenu HTML dans le navigateur
        favorites_browser.setHtml(html_content)

        # Ajoute un nouvel onglet avec la liste des favoris
        index = self.tab_widget.addTab(favorites_browser, "Favoris")
        self.tab_widget.setCurrentIndex(index)

    def show_history(self):
        """Affiche l'historique dans un nouvel onglet."""
        history_browser = QWebEngineView()  # Crée un nouveau QWebEngineView pour l'onglet
        history_browser.setUrl(QUrl("about:blank"))  # Définir une URL vide ou blanche

        # Crée une nouvelle page HTML pour afficher l'historique
        html_content = "<html><body><h1>Historique des Pages Visitées</h1><ul>"
        for url in self.history:
            html_content += f"<li><a href='{url}'>{url}</a></li>"  # Ajoute chaque URL de l'historique
        html_content += "</ul></body></html>"

        # Charge le contenu HTML dans le navigateur
        history_browser.setHtml(html_content)

        # Ouvre un nouvel onglet pour afficher l'historique
        index = self.tab_widget.addTab(history_browser, "Historique")
        self.tab_widget.setCurrentIndex(index)

    def toggle_dark_mode(self):
        """Active/désactive le mode sombre."""
        if self.dark_mode_button.isChecked():
            dark_style = """
                QWidget {
                    background-color: black;
                    color: white;
                }
                QLineEdit {
                    background-color: #333333;
                    color: white;
                }
                QWebEngineView {
                    background-color: #333333;
                    color: black;
                }
                QPushButton {
                    background-color: #444444;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #555555;
                }
                QProgressBar {
                    background-color: #333333;
                    color: white;
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
        """Affiche les informations sur la page actuelle."""
        current_browser = self.tab_widget.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            has_selection = current_browser.hasSelection()
            icon_url = current_browser.iconUrl().toString()
            selected_text = current_browser.selectedText()
            title = current_browser.title()
            url = current_browser.url().toString()
            zoom_factor = current_browser.zoomFactor()

            # Afficher les informations dans la console (ou dans un widget dédié)
            print(f"Titre : {title}")
            print(f"URL : {url}")
            print(f"Zoom : {zoom_factor}")
            print(f"Texte sélectionné : {selected_text if has_selection else 'Aucun'}")
            print(f"URL de l'icône : {icon_url if icon_url else 'Aucune'}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
