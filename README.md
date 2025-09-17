# 🛠️ MultiTool

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-BETA%201.2-orange)]()
[![Build](https://img.shields.io/badge/status-active-success)]()

**MultiTool** est une application polyvalente développée en **Python** avec **PyQt6**, conçue pour la **gestion et la supervision des réseaux et systèmes**.  
Elle regroupe plusieurs outils pratiques dans une interface graphique moderne et intuitive.

---

## 🚀 Fonctionnalités principales

- **Accueil**  
  - Logo et nom de l'application  
  - Affichage de la version locale et BETA  
  - Liste des derniers commits GitHub pour suivre les nouveautés  

- **Réseaux Config**  
  - Sélection de l’interface réseau  
  - Configuration IP, masque, passerelle  

- **Ping**  
  - Pings préconfigurés vers des IP publiques et locales  
  - Résultats en temps réel dans l’interface  

- **Mikrotik**  
  - Terminal intégré avec configuration de base  
  - Boutons pour ajouter des configurations (Wi-Fi, LAN…)  
  - Pop-ups interactifs pour configurer SSID et sécurité  

- **Rainbow HUB**  
  - Gestion et configuration des périphériques Rainbow HUB  
  - Contrôle et supervision via l’interface MultiTool  

- **Paramètres**  
  - Choix du thème (Système / Clair / Sombre)  
  - Vérification et mise à jour automatique depuis GitHub  

---

## 💻 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/T4nguy01/MULTITOOL.git
cd MULTITOOL
````

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux / macOS
source env/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

> Dépendances principales : `PyQt6`, `requests`, `psutil`, `pdfplumber`, `pandas`

### 4. Lancer l’application

```bash
python main.py
```

---

## ⚙️ Configuration

Avant de lancer l’application, vous devez configurer vos paramètres pour les onglets **Mikrotik** et **Rainbow HUB**.

1. Renommez le fichier **`config.exemple.py`** en **`config.py`**
2. Modifiez son contenu selon vos besoins

> ⚠️ **Important :** Ne partagez pas votre fichier `config.py` sur GitHub, ajoutez-le dans votre `.gitignore` pour protéger vos identifiants.

---

## 🎨 Thèmes disponibles

* **Système** : suit le thème de l’OS
* **Clair** : interface lumineuse
* **Sombre** : interface sombre pour le confort visuel

---

## ⚡ Mise à jour automatique

* Vérification de la version GitHub depuis l’onglet **Paramètres**
* Téléchargement et mise à jour de l’application en un clic

---

## 🛠️ Développement

### Lancer en mode dev

```bash
python main.py --dev
```

### Structure du projet

```
MULTITOOL/
│── main.py
│── requirements.txt
│── README.md
│── config.exemple.py   # Exemple de configuration Mikrotik & Rainbow HUB
│── assets/             # Images, icônes, logos
│── modules/            # Modules fonctionnels (Réseaux, Ping, Mikrotik, Rainbow HUB…)
│── styles/             # Fichiers .qss (thèmes)
```

---

## 📝 Contribution

Les contributions sont **les bienvenues** 🎉

1. Créez une branche pour votre fonctionnalité (`feature/ma-fonctionnalite`)
2. Committez vos changements localement
3. Poussez votre branche sur GitHub
4. Ouvrez une **pull request** vers `main`

---

## 📄 Licence

Ce projet est sous licence **MIT License** © 2025

---