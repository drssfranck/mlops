# 📊 MBA ESG – Management Opérationnel  
## Interactive Business Analytics Dashboard

---

## 📌 Présentation du Projet

Ce projet a été réalisé dans le cadre de l’évaluation **MBA ESG – Management Opérationnel**.

L’objectif est de développer une **application web interactive** permettant :

- 📤 Le téléversement d’un fichier CSV  
- 🗄️ Le stockage et l’interrogation des données via DuckDB  
- 📊 La visualisation de 4 indicateurs clés de performance (KPI)  
- 🎛️ L’application de filtres dynamiques (date, région, produit)  

L’application a été développée avec :

- **Streamlit**
- **DuckDB**
- **Pandas**
- **Plotly**
- **Git & GitHub**

---

# 🏗️ Architecture de l’Application

L’application repose sur une architecture en trois couches :

### 1️⃣ Interface Utilisateur (Frontend)
- Upload CSV
- Filtres dynamiques
- Affichage des KPI
- Visualisations interactives

### 2️⃣ Logique Métier (Backend Python)
- Traitement des données
- Gestion des filtres
- Exécution des requêtes SQL
- Préparation des données pour visualisation

### 3️⃣ Base de Données
- DuckDB (base embarquée locale)
- Stockage des données CSV
- Requêtes SQL pour les indicateurs

---

# 🚀 Fonctionnalités

✅ Téléversement de fichiers CSV  
✅ Stockage automatique dans DuckDB  
✅ 4 KPI dynamiques :  

- 💰 Chiffre d’affaires total  
- 📍 Ventes par région  
- 📈 Évolution des ventes dans le temps  
- 🏆 Top produits  

✅ Filtres dynamiques :
- Par date  
- Par région  
- Par produit  

✅ Visualisations interactives avec Plotly  

---

# 🛠️ Technologies Utilisées

- Python 3.10+
- Streamlit
- DuckDB
- Pandas
- Plotly
- GitHub Actions (CI)

---

# ⚙️ Installation et Exécution

## 1️⃣ Cloner le repository

```bash
git clone https://github.com/votre-username/mbaesg-management-dashboard.git
cd mbaesg-management-dashboard
