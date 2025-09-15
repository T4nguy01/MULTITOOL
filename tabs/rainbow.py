# tabs/rainbow.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QFont
import pdfplumber
import pandas as pd

class RainbowTab(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal vertical
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Titre
        self.title = QLabel("Rainbow HUB - PDF → CSV")
        self.title.setFont(QFont("Segoe UI", 18))
        self.layout.addWidget(self.title)

        # Bouton pour ouvrir PDF
        self.btn_open_pdf = QPushButton("Importer un fichier PDF")
        self.btn_open_pdf.setObjectName("appButton")  # Pour appliquer le style QSS général
        self.btn_open_pdf.clicked.connect(self.load_pdf)
        self.layout.addWidget(self.btn_open_pdf)

        # Table pour afficher le CSV
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

        # Bouton pour sauvegarder CSV
        self.btn_save_csv = QPushButton("Exporter en CSV")
        self.btn_save_csv.setObjectName("appButton")  # Même style que l'autre bouton
        self.btn_save_csv.clicked.connect(self.save_csv)
        self.layout.addWidget(self.btn_save_csv)

        self.df = None  # DataFrame pour stocker les données

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return

        try:
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        tables.append(pd.DataFrame(table[1:], columns=table[0]))
            if tables:
                self.df = pd.concat(tables, ignore_index=True)
                self.populate_table()
        except Exception as e:
            print("Erreur lors de la lecture PDF :", e)

    def populate_table(self):
        if self.df is None:
            return
        self.table.setColumnCount(len(self.df.columns))
        self.table.setRowCount(len(self.df))
        self.table.setHorizontalHeaderLabels(self.df.columns.tolist())

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))

    def save_csv(self):
        if self.df is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return
        self.df.to_csv(file_path, index=False, sep=";")
