from PyQt5.QtWidgets import QApplication, QMainWindow

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Définir le titre de la fenêtre
        self.setWindowTitle("PySurf")

        # Agrandir la fenêtre à l'écran dès l'exécution (maximiser la fenêtre)
        self.showMaximized()

        # Assurez-vous qu'aucune modification de la taille ne se produit après l'initialisation
        # Exemple : self.resize(1024, 768) si vous ne voulez pas que la fenêtre se réduise automatiquement

        # Afficher la fenêtre
        self.show()

# Application PyQt5
if __name__ == "__main__":
    app = QApplication([])
    window = Browser()
    app.exec_()
