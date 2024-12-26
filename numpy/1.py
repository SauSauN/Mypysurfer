import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime

# Initialiser la base de données
import sqlite3

def init_db():
    conn = sqlite3.connect("social_network.db")
    c = conn.cursor()

    # Table des utilisateurs
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password TEXT NOT NULL,
            bio TEXT  NULL 
        )
    ''')

    # Table des demandes d'amis (relation unidirectionnelle)
    c.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')

    # Table des publications
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL, 
            content TEXT NOT NULL,
            theme TEXT, 
            visibility TEXT CHECK(visibility IN ('public', 'private')) DEFAULT 'public',  
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  
            likes INTEGER DEFAULT 0,  -- Nombre de likes
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Table des relations d'amis (relation bidirectionnelle)
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            PRIMARY KEY(user_id, friend_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(friend_id) REFERENCES users(id)
        )
    ''')

    # Table des abonnés (abonnement unidirectionnel)
    c.execute('''
        CREATE TABLE IF NOT EXISTS followers (
            user_id INTEGER NOT NULL,
            follower_id INTEGER NOT NULL,
            PRIMARY KEY(user_id, follower_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(follower_id) REFERENCES users(id)
        )
    ''')

    # Table des likes
    c.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(post_id, user_id),
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Table des messages (pour la messagerie privée entre utilisateurs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Classe principale de l'application
class SocialNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Réseau Social")
        self.current_user_id = None
        self.current_user_name = None

        # Interface de connexion
        self.login_screen()

    def login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Connexion", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Email :").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Mot de passe :").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Se connecter", command=self.login).pack(pady=5)
        tk.Button(self.root, text="S'inscrire", command=self.register_screen).pack()

    def register_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Inscription", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Prénom :").pack()
        self.reg_first_name_entry = tk.Entry(self.root)
        self.reg_first_name_entry.pack()

        tk.Label(self.root, text="Nom :").pack()
        self.reg_last_name_entry = tk.Entry(self.root)
        self.reg_last_name_entry.pack()

        tk.Label(self.root, text="Email :").pack()
        self.reg_email_entry = tk.Entry(self.root)
        self.reg_email_entry.pack()

        tk.Label(self.root, text="Numéro de téléphone :").pack()
        self.reg_phone_entry = tk.Entry(self.root)
        self.reg_phone_entry.pack()

        tk.Label(self.root, text="Mot de passe :").pack()
        self.reg_password_entry = tk.Entry(self.root, show="*")
        self.reg_password_entry.pack()

        tk.Button(self.root, text="S'inscrire", command=self.register).pack(pady=5)
        tk.Button(self.root, text="Retour", command=self.login_screen).pack()

    def main_screen(self):
        self.clear_screen()

        # Titre de bienvenue
        tk.Label(self.root, text=f"Bienvenue, {self.current_user_name}!", font=("Arial", 16)).pack(pady=10)

        # Boutons existants
        tk.Button(self.root, text="Ajouter une publication", command=self.add_post_screen).pack(pady=5)
        tk.Button(self.root, text="Voir les publications", command=self.view_posts_screen).pack(pady=5)
        tk.Button(self.root, text="Déconnexion", command=self.logout).pack(pady=10)

        # Boutons "Actualités", "Messages", "Profil" au bas
        self.add_bottom_buttons()

    def add_bottom_buttons(self):
        # Création d'un Frame pour les boutons en bas
        frame_bottom = tk.Frame(self.root)
        frame_bottom.pack(side="bottom", fill="x", pady=10)

        # Bouton pour "Actualités", centré dans le frame
        tk.Button(frame_bottom, text="Actualités", command=self.view_news).pack(side="left", padx=5, expand=True)

        # Bouton pour "Messages", centré dans le frame
        tk.Button(frame_bottom, text="Messages", command=self.view_messages).pack(side="left", padx=5, expand=True)

        # Bouton pour "Profil", centré dans le frame
        tk.Button(frame_bottom, text="Profil", command=self.view_profile).pack(side="left", padx=5, expand=True)

    def add_post_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Nouvelle Publication", font=("Arial", 16)).pack(pady=10)

        # Champ pour le titre de la publication
        tk.Label(self.root, text="Titre :").pack()
        self.post_title_entry = tk.Entry(self.root)
        self.post_title_entry.pack(pady=5)

        tk.Label(self.root, text="Thème :").pack()
        themes = [
            "Cuisine", "Voyage", "Décoration", "Technologie", "Sport",
            "Musique", "Cinéma", "Lecture", "Art", "Histoire", 
            "Mode", "Science", "Animaux", "Santé", "Bien-être",
            "Photographie", "Éducation", "Environnement", "Finance", 
            "Entrepreneuriat", "Gaming", "Humour", "Actualités", 
            "Politique", "Spiritualité", "Familial", "DIY", 
            "Automobile", "Beauté", "Relations", "Culture", 
            "Littérature", "Nature", "Technologie émergente", 
            "Espace", "Voyages exotiques", "Fêtes", "Psychologie", 
            "Langues", "Jardinage", "Films d'animation", 
            "Documentaires", "Astronomie", "Artisanat"
        ]
        self.post_theme_var = tk.StringVar(self.root)
        self.post_theme_var.set(themes[0])  # Valeur par défaut
        self.post_theme_menu = tk.OptionMenu(self.root, self.post_theme_var, *themes)
        self.post_theme_menu.pack(pady=5)

        # Boutons pour la visibilité (public ou privé)
        tk.Label(self.root, text="Visibilité :").pack()
        self.post_visibility_var = tk.StringVar(value="public")  # Valeur par défaut : public
        tk.Radiobutton(self.root, text="Public", variable=self.post_visibility_var, value="public").pack()
        tk.Radiobutton(self.root, text="Privé", variable=self.post_visibility_var, value="private").pack()

        tk.Label(self.root, text="Contenu :").pack()
        self.post_content_entry = tk.Text(self.root, height=5, width=40)
        self.post_content_entry.pack(pady=5)

        # Associer un événement pour surveiller la saisie
        self.post_content_entry.bind("<KeyRelease>", self.adjust_line_length)

        tk.Button(self.root, text="Publier", command=self.add_post).pack(pady=5)
        tk.Button(self.root, text="Retour", command=self.main_screen).pack(pady=5)

    def adjust_line_length(self, event):
        max_length = 110  # Longueur maximale d'une ligne
        content = self.post_content_entry.get("1.0", "end-1c")  # Obtenir le texte
        lines = content.split("\n")  # Diviser le contenu en lignes

        # Réorganiser le texte pour déplacer le surplus à la ligne suivante
        new_content = []
        for line in lines:
            while len(line) > max_length:
                # Ajouter la partie qui tient dans la limite
                new_content.append(line[:max_length])
                # Garder le reste pour la prochaine ligne
                line = line[max_length:]
            new_content.append(line)  # Ajouter la ligne restante

        # Mettre à jour le contenu du widget
        self.post_content_entry.delete("1.0", "end")
        self.post_content_entry.insert("1.0", "\n".join(new_content))

    def view_posts_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Publications", font=("Arial", 16)).pack(pady=10)

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer toutes les publications avec le titre, le contenu et la date
        c.execute('''
            SELECT users.first_name || " " || users.last_name, posts.title, posts.content, posts.created_at
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.id DESC
        ''')
        posts = c.fetchall()
        conn.close()

        # Affichage des publications
        for name, title, content, created_at in posts:
            # Affichage du nom de l'utilisateur, du titre, du contenu et de la date
            tk.Label(self.root, text=f"{name} - {created_at}", font=("Arial", 10, "italic")).pack(pady=2)
            tk.Label(self.root, text=f"Titre: {title}", font=("Arial", 12, "bold")).pack(pady=2)
            tk.Label(self.root, text=f"{content}", wraplength=400, justify="left").pack(anchor="w", padx=10, pady=5)

        tk.Button(self.root, text="Retour", command=self.main_screen).pack(pady=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        email = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute("SELECT id, first_name, last_name, email, bio,phone, password FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            self.current_user_id = user[0]
            self.current_user_firstname = f"{user[1]}"
            self.current_user_name = f" {user[2]}"
            self.current_user_email = user[3]  # Ajoutez l'email ici
            self.current_user_bio = user[4] 
            self.current_user_phone = user[5] 
            self.current_user_password = user[6] 
            self.main_screen()
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect.")

    def register(self):
        first_name = self.reg_first_name_entry.get()
        last_name = self.reg_last_name_entry.get()
        email = self.reg_email_entry.get()
        phone = self.reg_phone_entry.get()
        password = self.reg_password_entry.get()

        if not (first_name and last_name and email and password):
            messagebox.showerror("Erreur", "Tous les champs obligatoires doivent être remplis.")
            return

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users (first_name, last_name, email, phone, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, phone, password))
            conn.commit()
            messagebox.showinfo("Succès", "Inscription réussie. Vous pouvez maintenant vous connecter.")
            self.login_screen()
        except sqlite3.IntegrityError as e:
            if "email" in str(e):
                messagebox.showerror("Erreur", "Cet email est déjà utilisé.")
            elif "phone" in str(e):
                messagebox.showerror("Erreur", "Ce numéro de téléphone est déjà utilisé.")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'inscription.")
        finally:
            conn.close()

    def add_post(self):
        title = self.post_title_entry.get()
        content = self.post_content_entry.get("1.0", tk.END).strip()
        theme = self.post_theme_var.get()
        visibility = self.post_visibility_var.get()  # Récupération de la visibilité

        if not title or not content:
            messagebox.showerror("Erreur", "Le titre et le contenu de la publication ne peuvent pas être vides.")
            return

        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts (user_id, title, content, theme, visibility, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (self.current_user_id, title, content, theme, visibility, created_at))
        conn.commit()
        conn.close()

        messagebox.showinfo("Succès", "Publication ajoutée.")
        self.main_screen()

    def logout(self):
        self.current_user_id = None
        self.current_user_firstname = None
        self.current_user_name = None
        self.current_user_email = None  # Réinitialisation de l'email
        self.login_screen()

    def view_news(self):
        self.clear_screen()
        # Création de frame_center comme conteneur principal
        frme_center = tk.Frame(root, bg="white", bd=1, relief="solid")
        frme_center.pack(fill="both", expand=True)  # Remplir toute la fenêtre

        # Utilisation de grid pour un contrôle précis
        frme_center.grid_columnconfigure(0, weight=1)  # Colonne gauche avec un poids réduit
        frme_center.grid_columnconfigure(1, weight=5)  # Colonne droite avec un poids plus élevé

        # Configuration des lignes pour frame_center
        frme_center.grid_rowconfigure(0, weight=1)  # Permet à la ligne 0 de s'étirer verticalement

        # Frame gauche principale
        self.frme_left = tk.Frame(frme_center, bg="white", height=10)
        self.frme_left.grid(row=0, column=0, sticky="ns")  # Remplir verticalement mais conserver une largeur réduite

        # Frame droite principale
        self.frme_right = tk.Label(frme_center, bg="white")
        self.frme_right.grid(row=0, column=1, sticky="nsew",padx=10, pady=10)  # Remplir tout l'espace disponible


        # Frame Top dans frme_left
        self.frame_top = tk.Frame(self.frme_left, bg="white", height=10)
        self.frame_top.pack(side="top", fill="x")  # Remplir horizontalement


        # Frame Bottom dans frme_left
        self.frame_bottom = tk.Frame(self.frme_left, height=200, bg="white", bd=1, relief="solid", width=9)
        self.frame_bottom.pack(side="bottom", fill="x")  # Remplir horizontalement
        self.display_users(self.frame_bottom, self.current_user_id)


        # Ajout de la barre de recherche en haut
        search_frame = tk.Frame(self.frame_top, bg="white")
        search_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        search_label = tk.Label(search_frame, text="Rechercher:", font=("Arial", 12))
        search_label.pack(side="left", padx=10)

        search_entry = tk.Entry(search_frame, font=("Arial", 12))
        search_entry.pack(side="left", fill="x", padx=10, expand=True)

        # Bouton de recherche
        search_button = tk.Button(search_frame, text="Rechercher", font=("Arial", 12), command=lambda: self.search_posts(search_entry.get()))
        search_button.pack(side="right", padx=10)

        # Création du canvas pour les publications
        cnvas = tk.Canvas(self.frme_right, bg="white")
        cnvas.pack(side="left", fill="both", expand=True)

        # Scrollbar associée au canvas
        scrollbr = tk.Scrollbar(self.frme_right, orient="vertical", command=cnvas.yview)
        scrollbr.pack(side="right", fill="y")
        cnvas.configure(yscrollcommand=scrollbr.set)

        # Création d'un frame à l'intérieur du canvas pour contenir les publications
        frme_posts = tk.Frame(cnvas, bg="white")
        cnvas.create_window((0, 0), window=frme_posts, anchor="center")

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer des publications aléatoires
        c.execute('''
            SELECT p.id, p.title, p.content, p.created_at, u.first_name, u.last_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.visibility = 'public'
            ORDER BY RANDOM()
            LIMIT 10
        ''')
        posts = c.fetchall()
        conn.close()

        # Affichage des publications dans le frame à l'intérieur du canvas
        for post_id, title, content, created_at, first_name, last_name in posts:

            post_frme = tk.Frame(frme_posts,  padx=11, pady=10, width=8)
            post_frme.pack(fill="x", padx=8, pady=5, anchor="center")  # "w" pour aligner à gauche



            # Frame supérieur : Informations générales (date, titre)
            letop_frme = tk.Frame(post_frme, padx=47, pady=10, width=9)
            letop_frme.pack(fill="x", pady=5)

            # Ajouter le titre à gauche dans le Frame supérieur
            tk.Label(letop_frme, text=f"Titre: {title}", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            # Ajouter un Label vide pour créer un espace
            tk.Label(letop_frme, text="  ", width=30).pack(side="left")

            # Ajouter le propriétaire en haut à gauche
            tk.Label(letop_frme, text=f"{first_name} {last_name}", font=("Arial", 10, "bold")).pack(side="right", padx=10)

            # Ajouter la date à droite dans le Frame supérieur
            tk.Label(letop_frme, text=f"Date: {created_at}", font=("Arial", 8, "italic")).pack(side="right", padx=5)

            # Frame central : Contenu principal de la publication
            lecentrl_frame = tk.Frame(post_frme, padx=47, pady=10, width=9)
            lecentrl_frame.pack(fill="x", pady=5)

            # Ajouter le contenu principal dans le Frame central
            tk.Label(lecentrl_frame, text=f"{content}", wraplength=600, justify="left").pack(side="left", padx=10)

            # Frame inférieur : Actions (likes, boutons)
            lebottom_frme = tk.Frame(post_frme, padx=47, pady=10, width=9)
            lebottom_frme.pack(fill="x", pady=5)

            # Récupérer le nombre de likes pour cette publication
            conn = sqlite3.connect("social_network.db")
            c = conn.cursor()
            c.execute('''
                SELECT COUNT(*) FROM likes WHERE post_id = ?
            ''', (post_id,))
            likes = c.fetchone()[0]
            
            # Vérifier si l'utilisateur a déjà liké ce post
            c.execute('''
                SELECT * FROM likes WHERE post_id = ? AND user_id = ?
            ''', (post_id, self.current_user_id))
            like_entry = c.fetchone()
            
            
            # Déterminer la couleur et le texte du bouton en fonction de l'état du like
            if like_entry:
                like_button_text = "Liké"
                like_button_color = "lightyellow"
            else:
                like_button_text = "Like"
                like_button_color = "lightblue"

            conn.close()

            # Ajouter le nombre de likes dans le Frame inférieur
            like_lbel = tk.Label(lebottom_frme, text=f"Likes: {likes}", font=("Arial", 10))
            like_lbel.pack(side="left", padx=5)

            # Boutons (Supprimer, Éditer, Like) dans le Frame inférieur
            button_frme = tk.Frame(lebottom_frme, padx=47, pady=10, width=559)
            button_frme.pack(side="right", padx=10)

            # Créer le bouton de like en utilisant la configuration
            bouton_like = tk.Button(button_frme, text=like_button_text, bg=like_button_color)

            # Mettre à jour le bouton avec l'action
            bouton_like.config(command=lambda post_id=post_id, bouton_like=bouton_like, like_lbel=like_lbel: self.like_post(post_id, bouton_like, like_lbel, self.current_user_id))
            bouton_like.pack(side="right", padx=5)

        # Mettre à jour la taille du canvas en fonction du contenu
        frme_posts.update_idletasks()
        cnvas.config(scrollregion=cnvas.bbox("all"))

        # Ajout des boutons en bas
        self.add_bottom_buttons()

    def view_messages(self):
        self.clear_screen()

        # Titre de l'écran "Messages"
        tk.Label(self.root, text="Messages", font=("Arial", 16)).pack(pady=10)
        
        # Implémentez ici la logique pour afficher les messages.

        # Boutons en bas (communs à tous les panels)
        self.add_bottom_buttons()

    def view_profile(self):
        self.clear_screen()
        # Création de frame_center comme conteneur principal
        frame_center = tk.Frame(root, bg="white", bd=1, relief="solid")
        frame_center.pack(fill="both", expand=True)  # Remplir toute la fenêtre

        # Utilisation de grid pour un contrôle précis
        frame_center.grid_columnconfigure(0, weight=1)  # Colonne gauche avec un poids réduit
        frame_center.grid_columnconfigure(1, weight=4)  # Colonne droite avec un poids plus élevé

        # Configuration des lignes pour frame_center
        frame_center.grid_rowconfigure(0, weight=1)  # Permet à la ligne 0 de s'étirer verticalement

        # Frame gauche principale
        self.frame_left = tk.Frame(frame_center, bg="white")
        self.frame_left.grid(row=0, column=0, sticky="ns")  # Remplir verticalement mais conserver une largeur réduite

        # Frame droite principale
        self.frame_right = tk.Frame(frame_center, bg="white")
        self.frame_right.grid(row=0, column=1, sticky="nsew")  # Remplir tout l'espace disponible


        # Frame en haut in gauche principale
        top_frame = tk.Frame(self.frame_left,  width=20, height=130, bg="white")
        top_frame.pack(side="top", fill="x") 

        # Frame en bas dans le frame_left
        bott_frame = tk.Frame(top_frame, bg="white", height=130)
        bott_frame.pack(side="bottom", fill="x")

        # Configuration de la grille pour bott_frame
        bott_frame.grid_rowconfigure(0, weight=1)  # Cela rend la première ligne élastique
        bott_frame.grid_columnconfigure(0, weight=1)  # Cela rend la première colonne élastique
        bott_frame.grid_columnconfigure(1, weight=1)  # Ajout d'une seconde colonne élastique
        bott_frame.grid_columnconfigure(2, weight=1)  # Troisième colonne élastique

        # Frame interne à bott_frame (ajout d'une grille à l'intérieur de bott_frame)
        lebot_fra = tk.Frame(bott_frame, bg="white", height=10)
        lebot_fra.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # Frame en haut


        # Frame en haut in gauche principale
        letop_fra = tk.Frame(top_frame,  width=20, height=10, bg="white")
        letop_fra.pack(side="top", fill="x")  # "top" positionne la frame en haut et "fill='x'" fait en sorte qu'elle occupe toute la largeur

        # Frame en bas in gauche principale
        lebottom_fra = tk.Frame(top_frame, width=20, height=20, bg="white")
        lebottom_fra.pack(side="bottom", fill="x", pady=10)  # Frame au bas de l'écran

        # Configuration de la grille pour lebottom_fra
        lebottom_fra.grid_rowconfigure(0, weight=1)  # Première ligne élastique
        lebottom_fra.grid_columnconfigure(0, weight=1)  # Première colonne élastique
        lebottom_fra.grid_columnconfigure(1, weight=1)  # Deuxième colonne élastique
        lebottom_fra.grid_columnconfigure(2, weight=1)  # Troisième colonne élastique



        # Boutons alignés horizontalement dans lebottom_fra
        Publication_button = tk.Button(lebottom_fra, text="Publication", command=self.add_post_screen, width=15)
        Publication_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")  # Premier bouton dans la première colonne

        Profil_button = tk.Button(lebottom_fra, text="Profil", command=self.edit_profile_screen, width=15)
        Profil_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")  # Deuxième bouton dans la deuxième colonne

        Deconnexion_button = tk.Button(lebottom_fra, text="Déconnexion", command=self.logout, bg="red", width=15)
        Deconnexion_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")  # Troisième bouton dans la troisième colonne


        # Frame en bas in gauche principale
        lebottom = tk.Frame(bott_frame, width=20, height=20,  bd=2, relief="solid")
        lebottom.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Frame en bas in gauche principale
        leboframe = tk.Frame(bott_frame, width=2, height=2,  bd=2, relief="solid")
        leboframe.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Texte à afficher dans le Label
        bio_text = self.current_user_bio

        if bio_text == None:
            bio_text = "##"

        # Si le texte commence par '#', on le laisse tel quel ou on effectue un traitement
        if bio_text.startswith("#"):
            bio_text = bio_text.strip()  # Enlever les espaces au début et à la fin, mais conserver le '#'



        # Limiter la taille du Label
        label = tk.Label(lebottom, 
                        text=bio_text, 
                        anchor="w",       # Aligner à gauche
                        justify="left",   # Justification du texte
                        width=40,         # Largeur en caractères (non en pixels)
                        wraplength=300)   # Largeur max en pixels pour le texte avant qu'il se coupe

        label.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        # Frame gauche in Frame en haut in gauche principale
        self.top_frame_left = tk.Frame(top_frame, width=10, height=10,  bd=2, relief="groove")
        self.top_frame_left.pack(side="left", fill="both", expand=True)  # positionner à gauche

        # Frame droite in Frame en haut in gauche principale
        self.top_frame_right = tk.Frame(top_frame, width=10, height=10,  bd=2, relief="groove")
        self.top_frame_right.pack(side="right", fill="both", expand=True)  # positionner à droite
        

        # Ajouter une Listbox pour afficher les amis
        lebo = tk.Listbox(leboframe, width=52, height=8)
        lebo.pack(padx=10, pady=10, fill="both", expand=True)

        # Afficher la liste des amis par défaut
        self.show_friends_list(lebo)

        # Ajouter un bouton "Retour" pour vider la Listbox et fermer la fenêtre
        back_button = tk.Button(leboframe, text="Retour",   command=self.show_friends_list(lebo))
        back_button.pack(side="left", padx=10, pady=10)

        # Ajouter un bouton "Invitations envoyées"
        sent_invitations_button = tk.Button(
            leboframe, text="Envoyées", bg="orange", width=15,
            command=lambda: self.show_sent_invitations(lebo)
        )
        sent_invitations_button.pack(side="right", padx=10, pady=10)  # Ligne supplémentaire

        # Ajouter un bouton "Accepter" pour accepter une invitation
        accept_button = tk.Button(leboframe, text="Accepter", command=lambda: self.accept_friend_request(lebo))
        accept_button.pack(side="right", padx=10, pady=10)

        # Ajouter un bouton "Retirer" pour retirer un ami
        remove_button = tk.Button(leboframe, text="Retirer", command=lambda: self.remove_friend(lebo))
        remove_button.pack(side="right", padx=10, pady=10)



        # Ajouter des boutons "Ami", "Abonné" et "Invitation"
        ami_button = tk.Button(
            bott_frame,
            text="Ami",
            bg="lightblue",
            width=15,
            command=lambda: self.show_friends_list(lebo)
        )
        ami_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")  # Premier bouton dans la première colonne

        abonne_button = tk.Button(
            bott_frame,
            text="Abonné",
            bg="lightgreen",
            width=15,
            command=lambda: self.show_follow_list(lebo)
        )
        abonne_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")  # Deuxième bouton dans la deuxième colonne

        invit_button = tk.Button(
            bott_frame,
            text="Invitation",
            bg="lightyellow",
            width=15,
            command=lambda: self.show_invitation_list(lebo)
        )
        invit_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")  # Troisième bouton dans la troisième colonne

        # Affichage des informations du profil 
        # Récupérer uniquement la première lettre de chaque variable
        # print(self.current_user_firstname, self.current_user_name)

        letter1 = self.current_user_firstname[0] if self.current_user_firstname else ""
        letter2 = self.current_user_name.strip()[0] if self.current_user_name else ""
        print(letter1,letter2)
        # Création du label avec une taille de police plus grande
        tk.Label(
            self.top_frame_left, 
            text=f"{letter1}{letter2}", 
            font=("Arial", 24, "bold")  # Police Arial, taille 24, style gras
        ).pack(pady=24)


        tk.Label(self.top_frame_right, text=f"{self.current_user_firstname}{self.current_user_name}").pack(pady=5)
        tk.Label(self.top_frame_right, text=f"Email: {self.current_user_email}").pack(pady=5)



        # Affichage des publications sur la frame de droite
        self.display_posts_on_right()

        # Ajouter les boutons "Actualités", "Messages", "Profil" en bas
        self.add_bottom_buttons()

    def display_posts_on_right(self):
        # Création du canvas pour les publications
        canvas = tk.Canvas(self.frame_right, bg="white")
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar associée au canvas
        scrollbar = tk.Scrollbar(self.frame_right, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Création d'un frame à l'intérieur du canvas pour contenir les publications
        frame_posts = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=frame_posts, anchor="nw")

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer toutes les publications de l'utilisateur
        c.execute('''
            SELECT p.id, p.title, p.content, p.created_at, p.visibility
            FROM posts p
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
        ''', (self.current_user_id,))
        posts = c.fetchall()
        conn.close()

        # Affichage des publications dans le frame à l'intérieur du canvas
        for post_id, title, content, created_at, visibility in posts:
            # Créer un Frame pour chaque publication
            post_frame = tk.Frame(frame_posts, bd=2, relief="solid", padx=11, pady=10, width=38)
            post_frame.pack(fill="x", padx=8, pady=5)

            # Frame supérieur : Informations générales (date, titre)
            letop_frame = tk.Frame(post_frame, padx=47, pady=10, width=559)
            letop_frame.pack(fill="x", pady=5)

            # Ajouter le titre à gauche dans le Frame supérieur
            tk.Label(letop_frame, text=f"Titre: {title}", font=("Arial", 12, "bold")).pack(side="left", padx=10)

            # Ajouter un Label vide pour créer un espace
            tk.Label(letop_frame, text="  ", width=30).pack(side="left")

            # Ajouter la date à droite dans le Frame supérieur
            tk.Label(letop_frame, text=f"Date: {created_at}", font=("Arial", 8, "italic")).pack(side="right", padx=5)        

            # Ajouter la visibilité à droite
            visibility_text = "Public" if visibility == "public" else "Privé"
            tk.Label(letop_frame, text=f"Visibilité: {visibility_text}", font=("Arial", 10)).pack(side="right", padx=5)

            # Frame central : Contenu principal de la publication
            lecentral_frame = tk.Frame(post_frame, padx=47, pady=10, width=559)
            lecentral_frame.pack(fill="x", pady=5)

            # Ajouter le contenu principal dans le Frame central
            tk.Label(lecentral_frame, text=f"{content}", wraplength=600, justify="left").pack(side="left", padx=10)

            # Frame inférieur : Actions (likes, boutons)
            lebottom_frame = tk.Frame(post_frame, padx=47, pady=10, width=559)
            lebottom_frame.pack(fill="x", pady=5)

            # Récupérer le nombre de likes pour cette publication
            conn = sqlite3.connect("social_network.db")
            c = conn.cursor()
            c.execute('''
                SELECT COUNT(*) FROM likes WHERE post_id = ?
            ''', (post_id,))
            likes = c.fetchone()[0]
            
            # Vérifier si l'utilisateur a déjà liké ce post
            c.execute('''
                SELECT * FROM likes WHERE post_id = ? AND user_id = ?
            ''', (post_id, self.current_user_id))
            like_entry = c.fetchone()
            
            # Déterminer la couleur et le texte du bouton en fonction de l'état du like
            if like_entry:
                like_button_text = "Liké"
                like_button_color = "lightyellow"
            else:
                like_button_text = "Like"
                like_button_color = "lightblue"

            conn.close()

            # Ajouter le nombre de likes dans le Frame inférieur
            like_label = tk.Label(lebottom_frame, text=f"Likes: {likes}", font=("Arial", 10))
            like_label.pack(side="left", padx=5)

            # Boutons (Supprimer, Éditer, Like) dans le Frame inférieur
            button_frame = tk.Frame(lebottom_frame, padx=47, pady=10, width=559)
            button_frame.pack(side="right", padx=10)

            # Boutons pour éditer et supprimer
            tk.Button(button_frame, text="Supprimer", bg="red", command=lambda post_id=post_id: self.delete_post(post_id, post_frame)).pack(side="right", padx=5)
            tk.Button(button_frame, text="Editer", bg="lightgreen", command=lambda post_id=post_id: self.edit_post(post_id)).pack(side="right", padx=5)

            # Créer le bouton de like en utilisant la configuration
            bouton_like = tk.Button(button_frame, text=like_button_text, bg=like_button_color)

            # Mettre à jour le bouton avec l'action
            bouton_like.config(command=lambda post_id=post_id, bouton_like=bouton_like, like_label=like_label: self.like_post(post_id, bouton_like, like_label, self.current_user_id))
            bouton_like.pack(side="right", padx=5)

        # Mettre à jour la taille du canvas en fonction du contenu
        frame_posts.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def show_friends_list(self,friends_listbox):
        # Vider la Listbox
        friends_listbox.delete(0, tk.END)

        # Connexion à la base de données pour récupérer les amis
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer les amis de l'utilisateur actuel
        c.execute(''' 
            SELECT u.first_name, u.last_name, f.friend_id
            FROM users u
            JOIN friends f ON f.friend_id = u.id
            WHERE f.user_id = ? 
        ''', (self.current_user_id,))
        friends = c.fetchall()
        conn.close()

        # Ajouter les amis à la Listbox
        for friend in friends:
            friends_listbox.insert(tk.END, f"{friend[0]} {friend[1]}")

    # Fonction pour vider la Listbox et fermer la fenêtre
    def clear_listbox(self,friends_listbox):
        friends_listbox.delete(0, tk.END)

    # Fonction pour afficher les abonnés
    def show_follow_list(self, followers_listbox):
        # Vider la Listbox
        followers_listbox.delete(0, tk.END)

        # Connexion à la base de données pour récupérer les abonnés
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer les abonnés de l'utilisateur actuel
        c.execute('''
            SELECT u.first_name, u.last_name
            FROM users u
            JOIN followers f ON f.follower_id = u.id
            WHERE f.user_id = ?
        ''', (self.current_user_id,))
        followers = c.fetchall()
        conn.close()

        # Ajouter les abonnés à la Listbox
        for follower in followers:
            followers_listbox.insert(tk.END, f"{follower[0]} {follower[1]}")

    # Fonction pour afficher les invitations
    def show_invitation_list(self, invitations_listbox):
        # Vider la Listbox
        invitations_listbox.delete(0, tk.END)

        # Connexion à la base de données pour récupérer les invitations
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer les invitations reçues par l'utilisateur actuel
        c.execute('''
            SELECT u.first_name, u.last_name, fr.status
            FROM users u
            JOIN friend_requests fr ON fr.sender_id = u.id
            WHERE fr.receiver_id = ?
        ''', (self.current_user_id,))
        invitations = c.fetchall()
        conn.close()

        # Ajouter les invitations reçues à la Listbox
        for invitation in invitations:
            invitations_listbox.insert(tk.END, f"{invitation[0]} {invitation[1]} - {invitation[2]}")


    def show_sent_invitations(self, invitations_listbox):
        # Vider la Listbox
        invitations_listbox.delete(0, tk.END)

        # Connexion à la base de données
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer les invitations envoyées
        c.execute('''
            SELECT u.first_name, u.last_name, fr.status
            FROM users u
            JOIN friend_requests fr ON fr.receiver_id = u.id
            WHERE fr.sender_id = ?
        ''', (self.current_user_id,))
        sent_invitations = c.fetchall()
        conn.close()

        # Ajouter les invitations envoyées à la Listbox
        for invitation in sent_invitations:
            invitations_listbox.insert(tk.END, f"{invitation[0]} {invitation[1]} - {invitation[2]}")


    def like_post(self, post_id, bouton_like, like_label, user_id):
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Vérifier si l'utilisateur a déjà aimé ce post
        c.execute('''
            SELECT * FROM likes
            WHERE post_id = ? AND user_id = ?
        ''', (post_id, user_id))
        like_entry = c.fetchone()

        if like_entry:
            # Si l'utilisateur a déjà aimé ce post, on enlève le like
            c.execute(''' 
                DELETE FROM likes
                WHERE post_id = ? AND user_id = ?
            ''', (post_id, user_id))
            bouton_like.config(text="Like", bg="lightblue")
        else:
            # Si l'utilisateur n'a pas encore aimé ce post, on ajoute un like
            c.execute(''' 
                INSERT INTO likes (post_id, user_id)
                VALUES (?, ?)
            ''', (post_id, user_id))
            bouton_like.config(text="Liké", bg="lightyellow")

        conn.commit()

        # Calculer le nouveau nombre de likes en comptant les entrées dans la table `likes`
        c.execute('''
            SELECT COUNT(*) FROM likes WHERE post_id = ?
        ''', (post_id,))
        new_likes = c.fetchone()[0]
        conn.close()

        # Mettre à jour l'affichage des likes
        like_label.config(text=f"Likes: {new_likes}")

        # Mettre à jour immédiatement l'affichage
        bouton_like.update()
        like_label.update()

    def edit_post(self, post_id):
        self.clear_screen()

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('''
            SELECT title, content, theme, visibility
            FROM posts
            WHERE id = ?
        ''', (post_id,))
        title, content, theme, visibility = c.fetchone()
        conn.close()

        tk.Label(self.root, text="Titre :").pack()
        edit_title_entry = tk.Entry(self.root)
        edit_title_entry.insert(0, title)
        edit_title_entry.pack(pady=5)

        tk.Label(self.root, text="Thème :").pack()
        themes = [
            "Cuisine", "Voyage", "Décoration", "Technologie", "Sport",
            "Musique", "Cinéma", "Lecture", "Art", "Histoire", 
            "Mode", "Science", "Animaux", "Santé", "Bien-être",
            "Photographie", "Éducation", "Environnement", "Finance", 
            "Entrepreneuriat", "Gaming", "Humour", "Actualités", 
            "Politique", "Spiritualité", "Familial", "DIY", 
            "Automobile", "Beauté", "Relations", "Culture", 
            "Littérature", "Nature", "Technologie émergente", 
            "Espace", "Voyages exotiques", "Fêtes", "Psychologie", 
            "Langues", "Jardinage", "Films d'animation", 
            "Documentaires", "Astronomie", "Artisanat"
        ]
        edit_theme_var = tk.StringVar(self.root)
        edit_theme_var.set(theme if theme else themes[0])  # Utilisez le thème existant ou un par défaut
        tk.OptionMenu(self.root, edit_theme_var, *themes).pack(pady=5)

        # Boutons pour la visibilité (public ou privé)
        tk.Label(self.root, text="Visibilité :").pack()
        visibility_var = tk.StringVar(value=visibility)  # Utilisez la visibilité actuelle comme valeur par défaut
        tk.Radiobutton(self.root, text="Public", variable=visibility_var, value="public").pack()
        tk.Radiobutton(self.root, text="Privé", variable=visibility_var, value="private").pack()

        tk.Label(self.root, text="Contenu :").pack()
        edit_content_entry = tk.Text(self.root, height=5, width=40)
        edit_content_entry.insert(tk.END, content)
        edit_content_entry.pack(pady=5)

        tk.Button(self.root, text="Enregistrer",
                command=lambda: self.save_edited_post(post_id, edit_title_entry, edit_theme_var, edit_content_entry, visibility_var)).pack(pady=5)
        tk.Button(self.root, text="Retour", command=self.view_posts_screen).pack(pady=5)

    def save_edited_post(self, post_id, edit_title_entry, edit_theme_var, edit_content_entry, visibility_var):
        new_title = edit_title_entry.get()
        new_theme = edit_theme_var.get()
        new_content = edit_content_entry.get("1.0", tk.END).strip()
        new_visibility = visibility_var.get()

        if not new_title or not new_content:
            messagebox.showerror("Erreur", "Le titre, le thème et le contenu ne peuvent pas être vides.")
            return

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('''
            UPDATE posts
            SET title = ?, theme = ?, content = ?, visibility = ?
            WHERE id = ?
        ''', (new_title, new_theme, new_content, new_visibility, post_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Succès", "Publication modifiée.")
        self.view_posts_screen()

    def delete_post(self, post_id, post_frame):
        # Demander une confirmation avant la suppression
        response = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette publication?")
        if response:
            conn = sqlite3.connect("social_network.db")
            c = conn.cursor()

            # Supprimer la publication de la base de données
            c.execute('''
                DELETE FROM posts
                WHERE id = ?
            ''', (post_id,))
            conn.commit()
            conn.close()

            # Supprimer le frame de la publication de l'interface
            post_frame.destroy()

    def edit_profile_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Modifier mon profil", font=("Arial", 16)).pack(pady=10)

        # Prénom
        tk.Label(self.root, text="Prénom :").pack()
        edit_first_name_entry = tk.Entry(self.root)
        edit_first_name_entry.insert(0, self.current_user_firstname)
        edit_first_name_entry.pack(pady=5)

        # Nom
        tk.Label(self.root, text="Nom :").pack()
        edit_last_name_entry = tk.Entry(self.root)
        edit_last_name_entry.insert(0, self.current_user_name.strip())
        edit_last_name_entry.pack(pady=5)

        # Email (non modifiable ici, car il doit être unique)
        tk.Label(self.root, text="Email :").pack()
        edit_email_entry = tk.Entry(self.root)
        edit_email_entry.insert(0, self.current_user_email)
        edit_email_entry.config(state="disabled")  # Désactiver le champ email
        edit_email_entry.pack(pady=5)

        # Téléphone
        tk.Label(self.root, text="Téléphone :").pack()
        edit_phone_entry = tk.Entry(self.root)
        edit_phone_entry.insert(0, self.current_user_phone)
        edit_phone_entry.pack(pady=5)

        # Bio (ajout de la bio dans le formulaire)
        tk.Label(self.root, text="Bio :").pack()
        edit_bio_entry = tk.Text(self.root, height=5, width=40)

        # Insérer la bio de l'utilisateur si elle existe, sinon rien
        if self.current_user_bio:
            edit_bio_entry.insert("1.0", self.current_user_bio)

        edit_bio_entry.pack(pady=5)


        # Mot de passe
        tk.Label(self.root, text="Mot de passe :").pack()
        edit_password_entry = tk.Entry(self.root, show="*")
        edit_password_entry.insert(0, self.current_user_password)
        edit_password_entry.pack(pady=5)

        # Bouton de validation
        tk.Button(self.root, text="Enregistrer", command=lambda: self.save_edited_profile(edit_first_name_entry, edit_last_name_entry, edit_phone_entry, edit_password_entry, edit_bio_entry)).pack(pady=5)
        tk.Button(self.root, text="Retour", command=self.view_profile).pack(pady=5)

    def save_edited_profile(self, first_name_entry, last_name_entry, phone_entry, password_entry, bio_entry):
        new_first_name = first_name_entry.get()
        new_last_name = last_name_entry.get()
        new_phone = phone_entry.get()
        new_password = password_entry.get()
        new_bio =  bio_entry.get("1.0", "end").strip() 

        # Validation des champs
        if not new_first_name or not new_last_name or not new_password:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
            return

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Mettre à jour les informations de l'utilisateur, y compris la bio
        c.execute('''
            UPDATE users
            SET first_name = ?, last_name = ?, phone = ?, password = ?, bio = ?
            WHERE id = ?
        ''', (new_first_name, new_last_name, new_phone, new_password, new_bio, self.current_user_id))

        conn.commit()
        conn.close()

        # Mettre à jour les informations en mémoire
        self.current_user_firstname = new_first_name
        self.current_user_name = new_last_name
        self.current_user_phone = new_phone
        self.current_user_password = new_password
        self.current_user_bio = new_bio  # Mise à jour de la bio

        messagebox.showinfo("Succès", "Profil mis à jour avec succès.")
        self.view_profile()

    def search_posts(self, search_term):
        self.clear_screen()
        # Création de frame_center comme conteneur principal
        frme_center = tk.Frame(root, bg="white", bd=1, relief="solid")
        frme_center.pack(fill="both", expand=True)  # Remplir toute la fenêtre

        # Utilisation de grid pour un contrôle précis
        frme_center.grid_columnconfigure(0, weight=1)  # Colonne gauche avec un poids réduit
        frme_center.grid_columnconfigure(1, weight=4)  # Colonne droite avec un poids plus élevé

        # Configuration des lignes pour frame_center
        frme_center.grid_rowconfigure(0, weight=1)  # Permet à la ligne 0 de s'étirer verticalement

        # Frame gauche principale
        self.frme_left = tk.Frame(frme_center, bg="white", height=10)
        self.frme_left.grid(row=0, column=0, sticky="ns")  # Remplir verticalement mais conserver une largeur réduite

        # Frame droite principale
        self.frme_right = tk.Frame(frme_center, bg="white")
        self.frme_right.grid(row=0, column=1, sticky="nsew")  # Remplir tout l'espace disponible


        # Frame Top dans frme_left
        self.frame_top = tk.Frame(self.frme_left, bg="lightblue", height=10)
        self.frame_top.pack(side="top", fill="x")  # Remplir horizontalement

        # Ajout de la barre de recherche en haut
        search_frame = tk.Frame(self.frame_top, bg="lightblue", height=10)
        search_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        search_label = tk.Label(search_frame, text="Rechercher:", font=("Arial", 12))
        search_label.pack(side="left", padx=10)

        search_entry = tk.Entry(search_frame, font=("Arial", 12))
        search_entry.insert(0, search_term)  # Remplir le champ de recherche avec le terme
        search_entry.pack(side="left", fill="x", padx=10, expand=True)

        # Bouton de recherche
        search_button = tk.Button(search_frame, text="Rechercher", font=("Arial", 12), command=lambda: self.search_posts(search_entry.get()))
        search_button.pack(side="right", padx=10)

        # Création du canvas pour les publications
        cnvas = tk.Canvas(self.frme_right, bg="white")
        cnvas.pack(side="left", fill="both", expand=True)

        # Scrollbar associée au canvas
        scrollbr = tk.Scrollbar(self.frme_right, orient="vertical", command=cnvas.yview)
        scrollbr.pack(side="right", fill="y")
        cnvas.configure(yscrollcommand=scrollbr.set)

        # Création d'un frame à l'intérieur du canvas pour contenir les publications
        frme_posts = tk.Frame(cnvas, bg="white")
        cnvas.create_window((0, 0), window=frme_posts, anchor="nw")

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Recherche des publications par titre ou contenu correspondant au terme de recherche
        c.execute('''
            SELECT p.id, p.title, p.content, p.created_at, u.first_name, u.last_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE (p.title LIKE ? OR p.content LIKE ?)
            AND p.visibility = 'public'
            ORDER BY p.created_at DESC
        ''', ('%' + search_term + '%', '%' + search_term + '%'))

        posts = c.fetchall()
        conn.close()

        if not posts:
            tk.Label(frme_posts, text="Aucun résultat trouvé.", font=("Arial", 14), fg="red").pack()

        # Affichage des publications dans le frame à l'intérieur du canvas
        for post_id, title, content, created_at, first_name, last_name in posts:
            # Créer un Frame pour chaque publication
            post_frme = tk.Frame(frme_posts, bd=2, relief="solid", padx=11, pady=10, width=38)
            post_frme.pack(fill="x", padx=8, pady=5)

            # Frame supérieur : Informations générales (date, titre)
            letop_frme = tk.Frame(post_frme, padx=47, pady=10, width=559)
            letop_frme.pack(fill="x", pady=5)

            # Ajouter le titre à gauche dans le Frame supérieur
            tk.Label(letop_frme, text=f"Titre: {title}", font=("Arial", 12, "bold")).pack(side="left", padx=10)

            # Ajouter le propriétaire en haut à gauche
            tk.Label(letop_frme, text=f"{first_name} {last_name}", font=("Arial", 10, "bold")).pack(side="right", padx=10)

            # Ajouter la date à droite dans le Frame supérieur
            tk.Label(letop_frme, text=f"Date: {created_at}", font=("Arial", 8, "italic")).pack(side="right", padx=5)

            # Frame central : Contenu principal de la publication
            lecentrl_frame = tk.Frame(post_frme, padx=47, pady=10, width=559)
            lecentrl_frame.pack(fill="x", pady=5)

            # Ajouter le contenu principal dans le Frame central
            tk.Label(lecentrl_frame, text=f"{content}", wraplength=600, justify="left").pack(side="left", padx=10)

            # Frame inférieur : Actions (likes, boutons)
            lebottom_frme = tk.Frame(post_frme, padx=47, pady=10, width=559)
            lebottom_frme.pack(fill="x", pady=5)

            # Récupérer le nombre de likes pour cette publication
            conn = sqlite3.connect("social_network.db")
            c = conn.cursor()
            c.execute('''
                SELECT COUNT(*) FROM likes WHERE post_id = ?
            ''', (post_id,))
            likes = c.fetchone()[0]
            conn.close()

            # Ajouter le nombre de likes dans le Frame inférieur
            like_lbel = tk.Label(lebottom_frme, text=f"Likes: {likes}", font=("Arial", 10))
            like_lbel.pack(side="left", padx=5)

            # Boutons (Supprimer, Éditer, Like) dans le Frame inférieur
            button_frme = tk.Frame(lebottom_frme, padx=47, pady=10, width=559)
            button_frme.pack(side="right", padx=10)

            # Bouton de like
            tk.Button(button_frme, text="Like", bg="lightblue", command=lambda post_id=post_id, like_label=like_lbel: self.like_post(post_id, like_label, self.current_user_id)).pack(side="right", padx=5)

        # Mettre à jour la taille du canvas en fonction du contenu
        frme_posts.update_idletasks()
        cnvas.config(scrollregion=cnvas.bbox("all"))

        # Ajout des boutons en bas
        self.add_bottom_buttons()

    def display_users(self, frame_bottom, sender_id):
        # Récupérer tous les utilisateurs aléatoirement depuis la base de données
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('''SELECT id, first_name, last_name, email FROM users ORDER BY RANDOM() LIMIT 90''')  # Limiter à 10 utilisateurs
        users = c.fetchall()
        conn.close()

        # Création d'une Listbox pour afficher les utilisateurs
        self.user_listbox = tk.Listbox(frame_bottom, height=29, selectmode=tk.SINGLE, width=9)
        self.user_listbox.pack(fill="both", padx=10, pady=10)

        # Stockage des IDs d'utilisateurs dans un dictionnaire pour la sélection
        self.user_map = {}

        # Affichage des utilisateurs dans la Listbox
        for user_id, first_name, last_name, email in users:
            user_info = f"{first_name} {last_name} *------* {email}"
            self.user_listbox.insert(tk.END, user_info)
            self.user_map[user_info] = user_id  # Associer l'info utilisateur à l'ID

        # Boutons pour envoyer des demandes d'ami ou s'abonner
        button_frame = tk.Frame(frame_bottom, bg="white")
        button_frame.pack(fill="x", padx=10, pady=10)

        invite_button = tk.Button(
            button_frame, text="Inviter", 
            command=lambda: self.handle_friend_request(sender_id), bg="lightgreen"
        )
        invite_button.pack(side="left", padx=10)

        follow_button = tk.Button(
            button_frame, text="S'abonner", 
            command=lambda: self.handle_follow(sender_id), bg="red"
        )
        follow_button.pack(side="left", padx=10)

    def handle_friend_request(self, sender_id):
        # Obtenir l'utilisateur sélectionné
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un utilisateur.")
            return

        selected_user_info = self.user_listbox.get(selection[0])
        receiver_id = self.user_map[selected_user_info]

        # Vérifier et envoyer la demande
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('SELECT * FROM friend_requests WHERE sender_id = ? AND receiver_id = ?', (sender_id, receiver_id))
        request = c.fetchone()

        if request:
            messagebox.showinfo("Info", "Demande déjà envoyée.")
        else:
            c.execute('INSERT INTO friend_requests (sender_id, receiver_id) VALUES (?, ?)', (sender_id, receiver_id))
            conn.commit()
            messagebox.showinfo("Succès", "Demande d'ami envoyée.")
        
        conn.close()

    def handle_follow(self, sender_id):
        # Obtenir l'utilisateur sélectionné
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un utilisateur.")
            return

        selected_user_info = self.user_listbox.get(selection[0])
        receiver_id = self.user_map[selected_user_info]

        # Ajouter l'abonnement
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('SELECT * FROM followers WHERE user_id = ? AND follower_id = ?', (receiver_id, sender_id))
        follow = c.fetchone()

        if follow:
            messagebox.showinfo("Info", "Vous êtes déjà abonné.")
        else:
            c.execute('INSERT INTO followers (user_id, follower_id) VALUES (?, ?)', (receiver_id, sender_id))
            conn.commit()
            messagebox.showinfo("Succès", "Vous êtes maintenant abonné.")
        
        conn.close()

    def accept_friend_request(self, invitations_listbox):
        # Récupérer la sélection de la Listbox
        selected_item = invitations_listbox.get(tk.ACTIVE)
        if not selected_item:
            return  # Ne rien faire si rien n'est sélectionné

        # Extraire les informations de l'invitation
        friend_name = selected_item.split(" - ")[0]  # Exemple: "John Doe - pending"
        first_name, last_name = friend_name.split(" ")

        # Connexion à la base de données
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer l'ID de l'ami depuis son nom
        c.execute('''
            SELECT id FROM users
            WHERE first_name = ? AND last_name = ?
        ''', (first_name, last_name))
        friend_id = c.fetchone()
        if friend_id:
            friend_id = friend_id[0]
        else:
            conn.close()
            return  # Ne pas continuer si l'ami n'existe pas

        # Ajouter dans la table friends
        c.execute('''
            INSERT OR IGNORE INTO friends (user_id, friend_id)
            VALUES (?, ?), (?, ?)
        ''', (self.current_user_id, friend_id, friend_id, self.current_user_id))

        # Marquer la demande comme acceptée
        c.execute('''
            UPDATE friend_requests
            SET status = 'accepted'
            WHERE receiver_id = ? AND sender_id = ?
        ''', (self.current_user_id, friend_id))

        conn.commit()
        conn.close()

        # Retirer l'entrée de la Listbox
        invitations_listbox.delete(tk.ACTIVE)

    def remove_friend(self, friends_listbox):
        # Récupérer la sélection de la Listbox
        selected_item = friends_listbox.get(tk.ACTIVE)
        if not selected_item:
            return  # Ne rien faire si rien n'est sélectionné

        # Extraire le prénom et nom de l'ami
        first_name, last_name = selected_item.split(" ")

        # Connexion à la base de données
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer l'ID de l'ami depuis son nom
        c.execute('''
            SELECT id FROM users
            WHERE first_name = ? AND last_name = ?
        ''', (first_name, last_name))
        friend_id = c.fetchone()
        if friend_id:
            friend_id = friend_id[0]
        else:
            conn.close()
            return  # Ne pas continuer si l'ami n'existe pas

        # Supprimer la relation dans les deux sens
        c.execute('''
            DELETE FROM friends
            WHERE (user_id = ? AND friend_id = ?)
            OR (user_id = ? AND friend_id = ?)
        ''', (self.current_user_id, friend_id, friend_id, self.current_user_id))

        conn.commit()
        conn.close()

        # Retirer l'entrée de la Listbox
        friends_listbox.delete(tk.ACTIVE)


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()
