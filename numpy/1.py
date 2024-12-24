import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime

# Initialiser la base de données
def init_db():
    conn = sqlite3.connect("social_network.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL, 
            content TEXT NOT NULL,
            created_at TEXT NOT NULL, 
            likes INTEGER DEFAULT 0,  -- New column to store the number of likes
            FOREIGN KEY(user_id) REFERENCES users(id)
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

        # Champ pour le contenu de la publication
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
        c.execute("SELECT id, first_name, last_name, email FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            self.current_user_id = user[0]
            self.current_user_firstname = f"{user[1]}"
            self.current_user_name = f" {user[2]}"
            self.current_user_email = user[3]  # Ajoutez l'email ici
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
        title = self.post_title_entry.get()  # Récupérer le titre
        content = self.post_content_entry.get("1.0", tk.END).strip()  # Récupérer le contenu

        if not title or not content:
            messagebox.showerror("Erreur", "Le titre et le contenu de la publication ne peuvent pas être vides.")
            return

        # Récupérer la date et l'heure actuelles
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Insertion de la publication avec le titre, le contenu et la date
        c.execute("INSERT INTO posts (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
                (self.current_user_id, title, content, created_at))

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

        # Titre de l'écran "Actualités"
        tk.Label(self.root, text="Actualités", font=("Arial", 16)).pack(pady=10)
        
        # Implémentez ici la logique pour afficher les actualités.

        # Boutons en bas (communs à tous les panels)
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

        # Frame au centre profil
        frame_center = tk.Frame(self.root, height=200, bd=2, relief="solid")
        frame_center.pack(side="top", fill="both", expand=True) 

        # Frame gauche principale
        self.frame_left = tk.Frame(frame_center, width=200, height=300, bg="lightblue",  bd=1, relief="solid")
        self.frame_left.pack(side="left", fill="both", expand=True)  # positionner à gauche

        # Frame droite principale
        self.frame_right = tk.Frame(frame_center, width=200, height=300, bg="lightgreen", bd=2, relief="solid")
        self.frame_right.pack(side="right", fill="both", expand=True)  # positionner à droite


        # Frame en haut in gauche principale
        top_frame = tk.Frame(self.frame_left, bg="lightblue", width=200, height=100)
        top_frame.pack(side="top", fill="x")  # "top" positionne la frame en haut et "fill='x'" fait en sorte qu'elle occupe toute la largeur

        # Frame en bas in gauche principale
        bottom_frame = tk.Frame(self.frame_left, bg="lightgreen", width=200, height=200,  bd=2, relief="groove")
        bottom_frame.pack(side="bottom", fill="x")  # "bottom" positionne la frame en bas


        # Frame gauche in Frame en haut in gauche principale
        self.top_frame_left = tk.Frame(top_frame, width=100, height=100,  bd=2, relief="groove")
        self.top_frame_left.pack(side="left", fill="both", expand=True)  # positionner à gauche

        # Frame droite in Frame en haut in gauche principale
        self.top_frame_right = tk.Frame(top_frame, width=100, height=100,  bd=2, relief="groove")
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

        # Boutons existants dans le profil
        tk.Button(bottom_frame, text="Ajouter une publication", command=self.add_post_screen).pack(pady=5)
        tk.Button(bottom_frame, text="Déconnexion", command=self.logout).pack(pady=10)

        # Affichage des publications sur la frame de droite
        self.display_posts_on_right()

        # Ajouter les boutons "Actualités", "Messages", "Profil" en bas
        self.add_bottom_buttons()

    def display_posts_on_right(self):
        # Création du canvas pour les publications
        canvas = tk.Canvas(self.frame_right)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar associée au canvas
        scrollbar = tk.Scrollbar(self.frame_right, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Création d'un frame à l'intérieur du canvas pour contenir les publications
        frame_posts = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame_posts, anchor="nw")

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Récupérer toutes les publications de l'utilisateur
        c.execute('''
            SELECT id, title, content, created_at, likes
            FROM posts
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (self.current_user_id,))
        posts = c.fetchall()
        conn.close()

        # Affichage des publications dans le frame à l'intérieur du canvas
        for post_id, title, content, created_at, likes in posts:
            # Créer un Frame pour chaque publication avec une bordure
            post_frame = tk.Frame(frame_posts, bd=2, relief="solid", padx=10, pady=10)
            post_frame.pack(fill="x", padx=10, pady=5)

            # Ajouter la date et le titre
            tk.Label(post_frame, text=f"Date: {created_at}", font=("Arial", 8, "italic")).pack(pady=2)
            tk.Label(post_frame, text=f"Titre: {title}", font=("Arial", 12, "bold")).pack(pady=2)
            tk.Label(post_frame, text=f"{content}", wraplength=400, justify="left").pack(anchor="w", padx=10, pady=5)

            # Ajouter le nombre de likes
            like_label = tk.Label(post_frame, text=f"Likes: {likes}", font=("Arial", 10))
            like_label.pack(side="left", padx=5)

            # Bouton de like
            tk.Button(post_frame, text="Like", command=lambda post_id=post_id, like_label=like_label: self.like_post(post_id, like_label)).pack(side="left", padx=5)

            # Boutons pour éditer et supprimer
            tk.Button(post_frame, text="Editer", command=lambda post_id=post_id: self.edit_post(post_id)).pack(side="left", padx=5)
            tk.Button(post_frame, text="Supprimer", command=lambda post_id=post_id: self.delete_post(post_id, post_frame)).pack(side="left", padx=5)

        # Mettre à jour la taille du canvas en fonction du contenu
        frame_posts.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def like_post(self, post_id, like_label):
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()

        # Augmenter le nombre de likes de 1
        c.execute('''
            UPDATE posts
            SET likes = likes + 1
            WHERE id = ?
        ''', (post_id,))
        conn.commit()

        # Récupérer le nouveau nombre de likes
        c.execute('''
            SELECT likes
            FROM posts
            WHERE id = ?
        ''', (post_id,))
        new_likes = c.fetchone()[0]
        conn.close()

        # Mettre à jour l'affichage des likes
        like_label.config(text=f"Likes: {new_likes}")

    def edit_post(self, post_id):
        self.clear_screen()

        # Récupérer les informations du post
        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('''
            SELECT title, content
            FROM posts
            WHERE id = ?
        ''', (post_id,))
        title, content = c.fetchone()
        conn.close()

        # Champ pour le titre de la publication
        tk.Label(self.root, text="Titre :").pack()
        edit_title_entry = tk.Entry(self.root)
        edit_title_entry.insert(0, title)
        edit_title_entry.pack(pady=5)

        # Champ pour le contenu de la publication
        tk.Label(self.root, text="Contenu :").pack()
        edit_content_entry = tk.Text(self.root, height=5, width=40)
        edit_content_entry.insert(tk.END, content)
        edit_content_entry.pack(pady=5)

        # Bouton pour enregistrer les modifications
        tk.Button(self.root, text="Enregistrer", command=lambda: self.save_edited_post(post_id, edit_title_entry, edit_content_entry)).pack(pady=5)
        tk.Button(self.root, text="Retour", command=self.view_posts_screen).pack(pady=5)

    def save_edited_post(self, post_id, edit_title_entry, edit_content_entry):
        new_title = edit_title_entry.get()
        new_content = edit_content_entry.get("1.0", tk.END).strip()

        if not new_title or not new_content:
            messagebox.showerror("Erreur", "Le titre et le contenu ne peuvent pas être vides.")
            return

        conn = sqlite3.connect("social_network.db")
        c = conn.cursor()
        c.execute('''
            UPDATE posts
            SET title = ?, content = ?
            WHERE id = ?
        ''', (new_title, new_content, post_id))
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


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()
