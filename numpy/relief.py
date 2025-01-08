import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class PDFViewer(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout(self)

        # Zone de texte pour entrer l'URL du PDF
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText('Entrez l\'URL du fichier PDF')

        # Bouton pour charger le PDF
        load_button = QPushButton('Charger PDF', self)
        load_button.clicked.connect(self.load_pdf)

        # QWebEngineView pour afficher le PDF
        self.webEngineView = QWebEngineView()

        # Ajouter les éléments à la mise en page
        vbox.addWidget(self.url_bar)
        vbox.addWidget(load_button)
        vbox.addWidget(self.webEngineView)

        self.setLayout(vbox)

        # Configuration de la fenêtre
        self.setWindowTitle('Visualiser un PDF en ligne')
        self.setGeometry(300, 300, 800, 600)
        self.show()

    def load_pdf(self):
        """Charge un PDF à partir de l'URL donnée."""
        pdf_url = self.url_bar.text()
        if pdf_url:
            # Charge le fichier PDF dans le QWebEngineView
            self.webEngineView.setUrl(QUrl(pdf_url))

def main():
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
