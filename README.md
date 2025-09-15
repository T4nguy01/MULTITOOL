# 🛠️ MultiTool

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-BETA%201.2-orange)]()

**MultiTool** est une application polyvalente développée en **Python** avec **PyQt6**, conçue pour la gestion et la supervision des réseaux et systèmes.  
Elle combine plusieurs fonctionnalités utiles dans une interface graphique moderne et intuitive.

---

## 🚀 Fonctionnalités principales

- **Accueil** : Interface de bienvenue et informations sur la version  
  - Affichage du logo et du nom de l'application  
  - Affichage de la version locale et BETA  
  - Liste des derniers commits GitHub pour suivre les nouveautés  

- **Réseaux Config** :  
  - Sélection de l’interface réseau  
  - Configuration IP, masque, passerelle  

- **Ping** :  
  - Ping préconfigurés vers des IP publiques et locales  
  - Résultats affichés directement dans l’interface  

- **Mikrotik** :  
  - Terminal avec configuration de base affichée  
  - Boutons pour ajouter des configurations (Wi-Fi, LAN…)  
  - Pop-ups pour configurer SSID et sécurité  

- **Paramètres** :  
  - Choix du thème (Système / Clair / Sombre)  
  - Mise à jour automatique depuis GitHub  


---

## 💻 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/T4nguy01/MULTITOOL.git
cd MULTITOOL
````

### 2. Créer un environnement virtuel (optionnel mais recommandé)

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

> Dépendances principales : `PyQt6`, `requests`

### 4. Lancer l’application

```bash
python main.py
```

---

## 🎨 Thèmes disponibles

* **Système** : suit le thème de l’OS
* **Clair** : interface lumineuse
* **Sombre** : interface sombre pour le confort visuel

---

## ⚡ Mise à jour automatique

* Vérification de la version GitHub depuis l’onglet Paramètres
* Possibilité de mettre à jour directement l’application depuis l’interface

---

## 📝 Contribution

Les contributions sont les bienvenues !

**Processus recommandé** :

1. Créer une branche pour votre fonctionnalité (`feature/ma-fonctionnalité`)
2. Committer vos changements localement
3. Faire un **pull request** vers la branche `main`

---

## 📄 Licence

Ce projet est sous licence **MIT License** © 2025

```