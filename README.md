Parfait ! Pour que ton README soit bien compatible avec GitHub et affiche un rendu correct dès l’ouverture du dépôt, on peut ajouter les **badges** en haut. Voici un exemple complet avec badges pour version, statut du build, licence et Python :

````markdown
# 🛠️ BETA-MULTITOOL

![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/T4nguy01/BETA-MULTITOOL)
![GitHub issues](https://img.shields.io/github/issues/T4nguy01/BETA-MULTITOOL)

Un outil polyvalent en Python permettant d’exécuter plusieurs fonctions utiles pour gérer et automatiser différentes tâches sur Windows et Linux. Idéal pour les techniciens, développeurs ou toute personne souhaitant centraliser plusieurs utilitaires dans une seule application.

---

## 🚀 Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/T4nguy01/BETA-MULTITOOL.git
cd BETA-MULTITOOL
````

### 2. Créer un environnement virtuel (optionnel mais recommandé)

```bash
python -m venv venv
# Activer l'environnement virtuel
# Windows
.\venv\Scripts\activate
# Linux / Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 🏃‍♂️ Lancer l'application

* Pour Windows :

```bash
python main_windows.py
```

* Pour Linux / autres plateformes :

```bash
python main.py
```

---

## 🛠️ Fonctionnalités

* Fonction 1 : Gestion réseau et ping
* Fonction 2 : Surveillance des statistiques
* Fonction 3 : Extensions modulaires
* Fonction 4 : (Ajouter ici les autres fonctionnalités spécifiques à ton outil)

---

## 📁 Structure du projet

```
BETA-MULTITOOL/
├─ main.py
├─ main_windows.py
├─ config_manager.py
├─ network.py
├─ network_worker.py
├─ ping_worker.py
├─ stats_worker.py
├─ extensions/
│  └─ extension_manager.py
├─ utils/
│  └─ helper.py
├─ icons/
│  └─ icon.ico
├─ README.md
├─ requirements.txt
└─ version.txt
```

---

## 📌 Contribuer

Les contributions sont les bienvenues !

1. Fork le dépôt
2. Crée une branche pour ta fonctionnalité (`git checkout -b feature/ma-fonctionnalité`)
3. Commit tes modifications (`git commit -m "Ajouter une nouvelle fonctionnalité"`)
4. Push vers la branche (`git push origin feature/ma-fonctionnalité`)
5. Ouvre une Pull Request

---

## ⚠️ Licence

Indique ici la licence que tu souhaites utiliser, par exemple MIT :

```
MIT License
```

---

## 🙋‍♂️ Contact

Pour toute question, tu peux me contacter sur [GitHub](https://github.com/T4nguy01).

```