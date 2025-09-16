# tabs/rainbow.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsView, QGraphicsScene
)
from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6.QtCore import Qt
import pdfplumber
import pandas as pd

class RainbowTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)  # Active le drag & drop

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Titre
        self.title = QLabel("Rainbow HUB - PDF → CSV")
        self.title.setFont(QFont("Segoe UI", 18))
        self.layout.addWidget(self.title)

        # Preview PDF
        self.preview = QLabel("Aucune preview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setFixedHeight(200)
        self.preview.setStyleSheet("border: 2px dashed #444; border-radius: 10px;")
        self.layout.addWidget(self.preview)

        # Bouton pour ouvrir PDF
        self.btn_open_pdf = QPushButton("Importer un fichier PDF")
        self.btn_open_pdf.setObjectName("appButton")
        self.btn_open_pdf.clicked.connect(self.load_pdf_dialog)
        self.layout.addWidget(self.btn_open_pdf)

        # Table CSV
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

        # Bouton pour sauvegarder CSV
        self.btn_save_csv = QPushButton("Exporter en CSV")
        self.btn_save_csv.setObjectName("appButton")
        self.btn_save_csv.clicked.connect(self.save_csv)
        self.layout.addWidget(self.btn_save_csv)

        self.df = None  # DataFrame
        self.current_pdf = None

    # -------------------------
    # Drag & Drop
    # -------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(".pdf"):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_pdf(file_path)

    # -------------------------
    # Dialog PDF
    # -------------------------
    def load_pdf_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    # -------------------------
    # Lecture PDF
    # -------------------------
    def load_pdf(self, file_path):
        try:
            tables = []
            with pdfplumber.open(file_path) as pdf:
                # Table extraction
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        tables.append(pd.DataFrame(table[1:], columns=table[0]))

                # Preview première page
                first_page = pdf.pages[0]
                img = first_page.to_image(resolution=100)
                pil_image = img.original
                data = pil_image.convert("RGBA").tobytes("raw", "RGBA")
                qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage).scaled(
                    self.preview.width(), self.preview.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                self.preview.setPixmap(pixmap)

            if tables:
                self.df = pd.concat(tables, ignore_index=True)
                self.populate_table()
                self.current_pdf = file_path
        except Exception as e:
            self.preview.setText("Erreur lors de la lecture PDF")
            print("Erreur PDF:", e)

    # -------------------------
    # Table CSV
    # -------------------------
    def populate_table(self):
        if self.df is None:
            return
        self.table.setColumnCount(len(self.df.columns))
        self.table.setRowCount(len(self.df))
        self.table.setHorizontalHeaderLabels(self.df.columns.tolist())
        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))

    # -------------------------
    # Sauvegarde CSV
    # -------------------------
    def save_csv(self):
        if self.df is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return
        self.df.to_csv(file_path, index=False, sep=";")
