PySurf - Un navigateur web simple en Python



PySurf est un navigateur web léger et personnalisable développé en Python avec PyQt5. Il offre des fonctionnalités essentielles comme la navigation par onglets, la gestion des favoris, un bloqueur de publicités et bien plus encore.

🚀 Fonctionnalités

🗂 Navigation par onglets : Ouvrez plusieurs pages web dans des onglets séparés.

🚫 Blocage de publicités : Bloque les publicités et les trackers avec une liste de domaines prédéfinis.

🕘 Historique : Conserve un historique des pages visitées.

⭐ Favoris : Ajoutez et gérez vos sites web préférés.

🔍 Moteurs de recherche : Choisissez parmi Google, Bing, DuckDuckGo et Yahoo.

🌙 Mode sombre : Activez ou désactivez le mode sombre pour un meilleur confort visuel.

📸 Capture d'écran : Prenez une capture d'écran de la page actuelle.

🔍 Zoom : Ajustez l'affichage des pages web.

⌨ Raccourcis clavier : Utilisez des raccourcis pratiques pour une navigation rapide.

📥 Téléchargements : Gérez les fichiers téléchargés directement depuis le navigateur.

🛠 Installation

📌 Prérequis

Python 3.7 ou supérieur

PyQt5

PyQtWebEngine

📦 Installation des dépendances

pip install PyQt5 PyQtWebEngine

▶ Exécution du navigateur

Clonez ce dépôt ou téléchargez les fichiers sources, puis exécutez le script principal :

python browser.py

🎮 Utilisation

Fonctionnalité

Description

🔎 Barre d'adresse

Entrez une URL ou une requête et appuyez sur Entrée.

➕ Nouvel onglet

Cliquez sur + ou utilisez Ctrl+T.

⭐ Ajouter aux favoris

Cliquez sur l'étoile pour sauvegarder un site.

📜 Historique

Accédez à l'historique via le menu Fonctionnalités.

🌙 Mode sombre

Activez/désactivez via l'icône 🌙.

📸 Capture d'écran

Capturez la page actuelle depuis le menu.

🔍 Zoom

Ajustez l'affichage via le menu.

🛠 Personnalisation

Vous pouvez modifier PySurf selon vos besoins :

Ajouter des domaines à bloquer dans la classe AdBlocker.

Changer les moteurs de recherche dans le fichier de configuration.

Modifier le design en ajustant les styles CSS de l'interface PyQt5.
