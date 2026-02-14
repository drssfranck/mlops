import duckdb
import pandas as pd
import os
from pathlib import Path


class DuckDBManager:
    """Gestionnaire de base de données DuckDB pour l'application"""

    def __init__(self, db_path='database/data.duckdb'):
        """Initialise la connexion à la base de données"""
        # Créer le dossier database s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)

    def detect_dataset_type(self, df):
        """Détecte automatiquement le type de jeu de données"""
        columns = df.columns.tolist()

        # Vérifier si c'est le dataset Airbnb
        airbnb_indicators = ['host id', 'neighbourhood', 'room type', 'price', 'availability 365']
        if all(col in columns for col in airbnb_indicators):
            return 'airbnb'

        # Vérifier si c'est le dataset Shopping
        shopping_indicators = ['Customer ID', 'Category', 'Purchase Amount (USD)', 'Item Purchased']
        if all(col in columns for col in shopping_indicators):
            return 'shopping'

        return 'unknown'

    def clean_airbnb_data(self, df):
        """Nettoie et prépare les données Airbnb"""
        df_clean = df.copy()

        # Nettoyer la colonne price (enlever $ et espaces)
        if 'price' in df_clean.columns:
            df_clean['price'] = df_clean['price'].str.replace('$', '').str.replace(',', '').str.strip()
            df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce')

        # Nettoyer service fee
        if 'service fee' in df_clean.columns:
            df_clean['service fee'] = df_clean['service fee'].str.replace('$', '').str.replace(',', '').str.strip()
            df_clean['service fee'] = pd.to_numeric(df_clean['service fee'], errors='coerce')

        # Convertir last review en date
        if 'last review' in df_clean.columns:
            df_clean['last review'] = pd.to_datetime(df_clean['last review'], errors='coerce')

        return df_clean

    def clean_shopping_data(self, df):
        """Nettoie et prépare les données Shopping"""
        df_clean = df.copy()

        # S'assurer que Purchase Amount est numérique
        if 'Purchase Amount (USD)' in df_clean.columns:
            df_clean['Purchase Amount (USD)'] = pd.to_numeric(df_clean['Purchase Amount (USD)'], errors='coerce')

        # S'assurer que Review Rating est numérique
        if 'Review Rating' in df_clean.columns:
            df_clean['Review Rating'] = pd.to_numeric(df_clean['Review Rating'], errors='coerce')

        return df_clean

    def load_csv_to_db(self, csv_path, table_name='sales_data'):
        """Charge un fichier CSV dans DuckDB"""
        try:
            # Lire le CSV
            df = pd.read_csv(csv_path,low_memory=False)

            # Détecter le type de dataset
            dataset_type = self.detect_dataset_type(df)

            # Nettoyer les données selon le type
            if dataset_type == 'airbnb':
                df = self.clean_airbnb_data(df)
            elif dataset_type == 'shopping':
                df = self.clean_shopping_data(df)

            # Supprimer la table si elle existe
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")

            # Créer la table à partir du DataFrame
            self.conn.register('df_temp', df)
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_temp")
            self.conn.unregister('df_temp')

            return True, dataset_type, len(df)
        except Exception as e:
            return False, str(e), 0

    def execute_query(self, query):
        """Exécute une requête SQL et retourne un DataFrame"""
        try:
            result = self.conn.execute(query).df()
            return result
        except Exception as e:
            raise Exception(f"Erreur lors de l'exécution de la requête: {str(e)}")

    def get_table_info(self, table_name='sales_data'):
        """Obtient des informations sur une table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT 1"
            df = self.execute_query(query)
            return {
                'columns': df.columns.tolist(),
                'exists': True
            }
        except:
            return {
                'columns': [],
                'exists': False
            }

    def get_filter_options(self, table_name='sales_data'):
        """Récupère les options de filtrage disponibles selon le type de données"""
        info = self.get_table_info(table_name)

        if not info['exists']:
            return {}

        columns = info['columns']
        options = {}

        # Pour Airbnb
        if 'neighbourhood' in columns:
            query = f"SELECT DISTINCT neighbourhood FROM {table_name} WHERE neighbourhood IS NOT NULL ORDER BY neighbourhood"
            options['regions'] = self.execute_query(query)['neighbourhood'].tolist()

            query = f"SELECT DISTINCT \"room type\" FROM {table_name} WHERE \"room type\" IS NOT NULL ORDER BY \"room type\""
            options['room_types'] = self.execute_query(query)['room type'].tolist()

            query = f"SELECT MIN(\"last review\") as min_date, MAX(\"last review\") as max_date FROM {table_name} WHERE \"last review\" IS NOT NULL"
            dates = self.execute_query(query)
            options['date_range'] = (dates['min_date'].iloc[0], dates['max_date'].iloc[0])

        # Pour Shopping
        elif 'Location' in columns:
            query = f"SELECT DISTINCT Location FROM {table_name} WHERE Location IS NOT NULL ORDER BY Location"
            options['regions'] = self.execute_query(query)['Location'].tolist()

            query = f"SELECT DISTINCT Category FROM {table_name} WHERE Category IS NOT NULL ORDER BY Category"
            options['categories'] = self.execute_query(query)['Category'].tolist()

            query = f"SELECT DISTINCT \"Item Purchased\" FROM {table_name} WHERE \"Item Purchased\" IS NOT NULL ORDER BY \"Item Purchased\""
            options['items'] = self.execute_query(query)['Item Purchased'].tolist()

        return options

    def close(self):
        """Ferme la connexion à la base de données"""
        self.conn.close()
