import tkinter as tk

# Création de la fenêtre principale
root = tk.Tk()
root.title("Exemple relief solid")

# Création d'un label avec une bordure solide
label = tk.Label(root, text="Bordure Solid", borderwidth=5, relief="ridge")
label.pack(padx=20, pady=20)

# Lancement de la boucle principale
root.mainloop()
