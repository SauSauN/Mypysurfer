import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

# Fenêtre principale
root = tk.Tk()
root.title("Profil Utilisateur")
root.geometry("1000x700")

# Bannière
banner_frame = tk.Frame(root, bg="blue", height=200)
banner_frame.pack(fill="x")
banner_label = tk.Label(banner_frame, text="Bannière", bg="blue", fg="white", font=("Arial", 20))
banner_label.pack(pady=50)

# Photo de profil
profile_frame = tk.Frame(root)
profile_frame.pack(pady=10)
profile_pic = tk.Label(profile_frame, text="Photo de Profil", bg="gray", width=10, height=5)
profile_pic.grid(row=0, column=0, padx=20)
tk.Label(profile_frame, text="Jean Dupont", font=("Arial", 18)).grid(row=0, column=1, sticky="w")
tk.Label(profile_frame, text="@jeandupont", font=("Arial", 12), fg="gray").grid(row=1, column=1, sticky="w")
tk.Label(profile_frame, text="Bio : Passionné par la photographie et le développement web.").grid(row=2, column=1, sticky="w")

# Statistiques
stats_frame = tk.Frame(root)
stats_frame.pack(pady=10)
tk.Label(stats_frame, text="Publications : 25", font=("Arial", 12)).grid(row=0, column=0, padx=20)
tk.Label(stats_frame, text="Amis : 120", font=("Arial", 12)).grid(row=0, column=1, padx=20)
tk.Label(stats_frame, text="Abonnés : 300", font=("Arial", 12)).grid(row=0, column=2, padx=20)

# Section des Publications récentes
posts_frame = tk.LabelFrame(root, text="Publications récentes")
posts_frame.pack(pady=10, fill="both", expand=True)
for i in range(10):
    tk.Label(posts_frame, text=f"Publication {i+1} : Exemple de contenu...", anchor="w").pack(fill="x")

# Boutons d'action
actions_frame = tk.Frame(root)
actions_frame.pack(pady=10)
tk.Button(actions_frame, text="Modifier le profil", width=15).grid(row=0, column=0, padx=10)
tk.Button(actions_frame, text="Envoyer un message", width=15).grid(row=0, column=1, padx=10)
tk.Button(actions_frame, text="Se déconnecter", width=15).grid(row=0, column=2, padx=10)

root.mainloop()
