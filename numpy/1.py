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

    # Table des publications
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL, 
            content TEXT NOT NULL,
            theme TEXT, 
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Utilisation de DATETIME
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

        tk.Label(self.root, text="Contenu :").pack()
        self.post_content_entry = tk.Text(self.root, height=5, width=40)
        self.post_content_entry.pack(pady=5)

        tk.Button(self.root, text="Publier", command=self.add_post).pack(pady=5)
        tk.Button(self.root, text="Retour", command=self.main_screen).pack(pady=5)

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

        if not title or not content:
            messagebox.showerror("Erreur", "Le titre et le contenu de la publication ne peuvent pas être vides.")
            return

        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts (user_id, title, content, theme, created_at) VALUES (?, ?, ?, ?, ?)",
                (self.current_user_id, title, content, theme, created_at))
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

        # Assurez-vous que frame_right existe
        self.frme_right = tk.Frame(self.root)  # Initialiser frame_right si elle n'existe pas
        self.frme_right.pack(side="right", fill="both", expand=True)

        # Titre de l'écran "Actualités"
        tk.Label(self.root, text="Actualités", font=("Arial", 16)).pack(pady=10)

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

        # Récupérer des publications aléatoires
        c.execute('''
            SELECT p.id, p.title, p.content, p.created_at
            FROM posts p
            ORDER BY RANDOM()
            LIMIT 10
        ''')
        posts = c.fetchall()
        conn.close()

        # Affichage des publications dans le frame à l'intérieur du canvas
        for post_id, title, content, created_at in posts:
            # Créer un Frame pour chaque publication
            post_frme = tk.Frame(frme_posts, bd=2, relief="solid", padx=11, pady=10, width=38)
            post_frme.pack(fill="x", padx=8, pady=5)

            # Frame supérieur : Informations générales (date, titre)
            letop_frme = tk.Frame(post_frme, padx=47, pady=10, width=559)
            letop_frme.pack(fill="x", pady=5)

            # Ajouter le titre à gauche dans le Frame supérieur
            tk.Label(letop_frme, text=f"Titre: {title}", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            # Ajouter un Label vide pour créer un espace
            tk.Label(letop_frme, text="  ", width=30).pack(side="left")

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

            # Boutons pour éditer et supprimer
            tk.Button(button_frme, text="Supprimer", bg="red", command=lambda post_id=post_id: self.delete_post(post_id, post_frame)).pack(side="right", padx=5)
            tk.Button(button_frme, text="Editer", bg="lightgreen", command=lambda post_id=post_id: self.edit_post(post_id)).pack(side="right", padx=5)

            # Bouton de like
            tk.Button(button_frme, text="Like", bg="lightblue", command=lambda post_id=post_id, like_label=like_label: self.like_post(post_id, like_label, self.current_user_id)).pack(side="right", padx=5)

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
        bott_frame = tk.Frame(self.frame_left, bg="white", height=130)
        bott_frame.pack(side="bottom", fill="x")

        # Configuration de la grille pour bott_frame
        bott_frame.grid_rowconfigure(0, weight=1)  # Cela rend la première ligne élastique
        bott_frame.grid_columnconfigure(0, weight=1)  # Cela rend la première colonne élastique
        bott_frame.grid_columnconfigure(1, weight=1)  # Ajout d'une seconde colonne élastique

        # Frame interne à bott_frame (ajout d'une grille à l'intérieur de bott_frame)
        lebot_fra = tk.Frame(bott_frame, bg="white", height=10)
        lebot_fra.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # Frame en haut

        # Ajouter des boutons "Ami" et "Abonné"
        ami_button = tk.Button(bott_frame, text="Ami", bg="lightblue", width=15)
        ami_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")  # Premier bouton dans la première colonne

        abonne_button = tk.Button(bott_frame, text="Abonné", bg="lightgreen", width=15)
        abonne_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")  # Deuxième bouton dans la deuxième colonne
        
        # Frame en haut in gauche principale
        letop_fra = tk.Frame(top_frame,  width=20, height=10, bg="white")
        letop_fra.pack(side="top", fill="x")  # "top" positionne la frame en haut et "fill='x'" fait en sorte qu'elle occupe toute la largeur

        # Frame en bas in gauche principale
        lebottom_fra = tk.Frame(top_frame, width=20, height=20, bg="white")
        lebottom_fra.pack(side="bottom", fill="x", pady=10)  # Frame au bas de l'écran



        tk.Label(lebot_fra, text=f"{self.current_user_bio}").pack(pady=5)

        # Boutons alignés horizontalement dans le bottom_frame
        tk.Button(lebottom_fra, text="Ajouter une publication", command=self.add_post_screen).pack(side="left", padx=10)
        tk.Button(lebottom_fra, text="Modifier mon profil", command=self.edit_profile_screen).pack(side="left", padx=10)
        tk.Button(lebottom_fra, text="Déconnexion", command=self.logout, bg="red").pack(side="right", padx=10)

        


        # Frame gauche in Frame en haut in gauche principale
        self.top_frame_left = tk.Frame(top_frame, width=10, height=10,  bd=2, relief="groove")
        self.top_frame_left.pack(side="left", fill="both", expand=True)  # positionner à gauche

        # Frame droite in Frame en haut in gauche principale
        self.top_frame_right = tk.Frame(top_frame, width=10, height=10,  bd=2, relief="groove")
        self.top_frame_right.pack(side="right", fill="both", expand=True)  # positionner à droite




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
            SELECT p.id, p.title, p.content, p.created_at
            FROM posts p
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
        ''', (self.current_user_id,))
        posts = c.fetchall()
        conn.close()

        # Affichage des publications dans le frame à l'intérieur du canvas
        for post_id, title, content, created_at in posts:
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

            # Bouton de like
            tk.Button(button_frame, text="Like", bg="lightblue", command=lambda post_id=post_id, like_label=like_label: self.like_post(post_id, like_label, self.current_user_id)).pack(side="right", padx=5)

        # Mettre à jour la taille du canvas en fonction du contenu
        frame_posts.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def like_post(self, post_id, like_label, user_id):
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
        else:
            # Si l'utilisateur n'a pas encore aimé ce post, on ajoute un like
            c.execute('''
                INSERT INTO likes (post_id, user_id)
                VALUES (?, ?)
            ''', (post_id, user_id))

        conn.commit()

        # Calculer le nouveau nombre de likes en comptant les entrées dans la table `likes`
        c.execute('''
            SELECT COUNT(*) FROM likes WHERE post_id = ?
        ''', (post_id,))
        new_likes = c.fetchone()[0]
        conn.close()

        # Mettre à jour l'affichage des likes
        like_label.config(text=f"Likes: {new_likes}")

    def edit_post(self, post_id):
        self.clear_screen()

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('''
            SELECT title, content, theme
            FROM posts
            WHERE id = ?
        ''', (post_id,))
        title, content, theme = c.fetchone()
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

        tk.Label(self.root, text="Contenu :").pack()
        edit_content_entry = tk.Text(self.root, height=5, width=40)
        edit_content_entry.insert(tk.END, content)
        edit_content_entry.pack(pady=5)

        tk.Button(self.root, text="Enregistrer",
                command=lambda: self.save_edited_post(post_id, edit_title_entry, edit_theme_var, edit_content_entry)).pack(pady=5)
        tk.Button(self.root, text="Retour", command=self.view_posts_screen).pack(pady=5)

    def save_edited_post(self, post_id, edit_title_entry, edit_theme_var, edit_content_entry):
        new_title = edit_title_entry.get()
        new_theme = edit_theme_var.get()
        new_content = edit_content_entry.get("1.0", tk.END).strip()

        if not new_title or not new_content:
            messagebox.showerror("Erreur", "Le titre, le thème et le contenu ne peuvent pas être vides.")
            return

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('''
            UPDATE posts
            SET title = ?, theme = ?, content = ?
            WHERE id = ?
        ''', (new_title, new_theme, new_content, post_id))
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
        edit_bio_entry = tk.Entry(self.root)
        edit_bio_entry.insert(0, self.current_user_bio if self.current_user_bio else "")
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
        new_bio = bio_entry.get()  # Récupérer la nouvelle bio

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


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()
