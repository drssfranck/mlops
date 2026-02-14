import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import DuckDBManager
import os

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de la session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DuckDBManager()
if 'dataset_type' not in st.session_state:
    st.session_state.dataset_type = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False


# Fonction pour charger les données
def load_data(uploaded_file):
    """Charge les données depuis un fichier uploadé"""
    try:
        # Sauvegarder temporairement le fichier
        temp_path = f"data/temp_{uploaded_file.name}"
        os.makedirs('data', exist_ok=True)

        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Charger dans DuckDB
        success, dataset_type, row_count = st.session_state.db_manager.load_csv_to_db(temp_path)

        if success:
            st.session_state.dataset_type = dataset_type
            st.session_state.data_loaded = True
            return True, dataset_type, row_count
        else:
            return False, dataset_type, 0
    except Exception as e:
        return False, str(e), 0


# Fonction pour créer les KPIs Airbnb
def create_airbnb_dashboard(filters):
    """Crée le dashboard pour les données Airbnb"""

    # Construction de la clause WHERE basée sur les filtres
    where_clauses = []
    if filters.get('neighbourhood'):
        neighbourhoods = "', '".join(filters['neighbourhood'])
        where_clauses.append(f"neighbourhood IN ('{neighbourhoods}')")
    if filters.get('room_type'):
        room_types = "', '".join(filters['room_type'])
        where_clauses.append(f"\"room type\" IN ('{room_types}')")
    if filters.get('date_range'):
        start_date, end_date = filters['date_range']
        where_clauses.append(f"\"last review\" BETWEEN '{start_date}' AND '{end_date}'")

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    # KPI 1: Prix moyen par type de chambre
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Prix moyen par type de chambre")
        query = f"""
        SELECT 
            "room type" as room_type,
            ROUND(AVG(price), 2) as avg_price,
            COUNT(*) as count
        FROM sales_data
        WHERE price IS NOT NULL AND {where_clause}
        GROUP BY "room type"
        ORDER BY avg_price DESC
        """
        df = st.session_state.db_manager.execute_query(query)

        fig = px.bar(df, x='room_type', y='avg_price',
                     title='Prix moyen ($)',
                     labels={'room_type': 'Type de chambre', 'avg_price': 'Prix moyen ($)'},
                     color='avg_price',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

        # Métriques
        total_avg = df['avg_price'].mean()
        st.metric("Prix moyen global", f"${total_avg:.2f}")

    with col2:
        st.subheader("🏘️ Top 10 Quartiers par disponibilité")
        query = f"""
        SELECT 
            neighbourhood,
            ROUND(AVG("availability 365"), 2) as avg_availability,
            COUNT(*) as listings_count
        FROM sales_data
        WHERE "availability 365" IS NOT NULL AND {where_clause}
        GROUP BY neighbourhood
        ORDER BY avg_availability DESC
        LIMIT 10
        """
        df = st.session_state.db_manager.execute_query(query)

        fig = px.bar(df, x='neighbourhood', y='avg_availability',
                     title='Disponibilité moyenne (jours/an)',
                     labels={'neighbourhood': 'Quartier', 'avg_availability': 'Jours disponibles'},
                     color='avg_availability',
                     color_continuous_scale='Greens')

        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, width='stretch')

        avg_avail = df['avg_availability'].mean()
        st.metric("Disponibilité moyenne", f"{avg_avail:.0f} jours")

    # KPI 3: Tendance des reviews
    st.subheader("📈 Tendance des avis dans le temps")
    query = f"""
    SELECT 
        DATE_TRUNC('month', "last review") as review_month,
        COUNT(*) as review_count,
        ROUND(AVG("review rate number"), 2) as avg_rating
    FROM sales_data
    WHERE "last review" IS NOT NULL AND {where_clause}
    GROUP BY DATE_TRUNC('month', "last review")
    ORDER BY review_month
    """
    df = st.session_state.db_manager.execute_query(query)

    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['review_month'], y=df['review_count'],
                                 mode='lines+markers', name='Nombre d\'avis',
                                 line=dict(color='blue', width=2)))
        fig.update_layout(title='Évolution du nombre d\'avis',
                          xaxis_title='Mois', yaxis_title='Nombre d\'avis')
        st.plotly_chart(fig, use_container_width=True)

    # KPI 4: Distribution des prix
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("💰 Distribution des prix")
        query = f"""
        SELECT 
            CASE 
                WHEN price < 100 THEN '0-100$'
                WHEN price < 200 THEN '100-200$'
                WHEN price < 300 THEN '200-300$'
                WHEN price < 500 THEN '300-500$'
                ELSE '500$+'
            END as price_range,
            COUNT(*) as count
        FROM sales_data
        WHERE price IS NOT NULL AND {where_clause}
        GROUP BY price_range
        ORDER BY price_range
        """
        df = st.session_state.db_manager.execute_query(query)

        fig = px.pie(df, values='count', names='price_range',
                     title='Répartition des logements par gamme de prix')
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("⭐ Notes moyennes")
        query = f"""
        SELECT 
            "review rate number" as rating,
            COUNT(*) as count
        FROM sales_data
        WHERE "review rate number" IS NOT NULL AND {where_clause}
        GROUP BY "review rate number"
        ORDER BY rating
        """
        df = st.session_state.db_manager.execute_query(query)

        if not df.empty:
            fig = px.bar(df, x='rating', y='count',
                         title='Distribution des notes',
                         labels={'rating': 'Note', 'count': 'Nombre de logements'},
                         color='rating',
                         color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)


# Fonction pour créer les KPIs Shopping
def create_shopping_dashboard(filters):
    """Crée le dashboard pour les données Shopping"""

    # Construction de la clause WHERE
    where_clauses = []
    if filters.get('location'):
        locations = "', '".join(filters['location'])
        where_clauses.append(f"Location IN ('{locations}')")
    if filters.get('category'):
        categories = "', '".join(filters['category'])
        where_clauses.append(f"Category IN ('{categories}')")

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    # KPI 1: Ventes par catégorie
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Ventes par catégorie")
        query = f"""
        SELECT 
            Category,
            ROUND(SUM("Purchase Amount (USD)"), 2) as total_sales,
            COUNT(*) as transaction_count,
            ROUND(AVG("Purchase Amount (USD)"), 2) as avg_purchase
        FROM sales_data
        WHERE "Purchase Amount (USD)" IS NOT NULL AND {where_clause}
        GROUP BY Category
        ORDER BY total_sales DESC
        """
        df = st.session_state.db_manager.execute_query(query)

        fig = px.bar(df, x='Category', y='total_sales',
                     title='Chiffre d\'affaires par catégorie',
                     labels={'Category': 'Catégorie', 'total_sales': 'CA ($)'},
                     color='total_sales',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

        total_sales = df['total_sales'].sum()
        st.metric("Chiffre d'affaires total", f"${total_sales:,.2f}")

    with col2:
        st.subheader("🗺️ Ventes par région")
        query = f"""
        SELECT 
            Location,
            ROUND(SUM("Purchase Amount (USD)"), 2) as total_sales,
            COUNT(*) as customer_count
        FROM sales_data
        WHERE {where_clause}
        GROUP BY Location
        ORDER BY total_sales DESC
        LIMIT 10
        """
        df = st.session_state.db_manager.execute_query(query)

        fig = px.bar(df, x='Location', y='total_sales',
                     title='Top 10 régions par CA',
                     labels={'Location': 'Région', 'total_sales': 'CA ($)'},
                     color='total_sales',
                     color_continuous_scale='Greens')
        fig.update_xaxis(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        avg_sale = df['total_sales'].mean()
        st.metric("CA moyen par région", f"${avg_sale:,.2f}")

    # KPI 3: Analyse démographique
    st.subheader("👥 Analyse démographique des clients")
    query = f"""
    SELECT 
        Gender,
        CASE 
            WHEN Age < 25 THEN '18-24'
            WHEN Age < 35 THEN '25-34'
            WHEN Age < 45 THEN '35-44'
            WHEN Age < 55 THEN '45-54'
            ELSE '55+'
        END as age_group,
        COUNT(*) as customer_count,
        ROUND(AVG("Purchase Amount (USD)"), 2) as avg_spending
    FROM sales_data
    WHERE {where_clause}
    GROUP BY Gender, age_group
    ORDER BY Gender, age_group
    """
    df = st.session_state.db_manager.execute_query(query)

    fig = px.bar(df, x='age_group', y='customer_count', color='Gender',
                 title='Répartition des clients par âge et genre',
                 labels={'age_group': 'Tranche d\'âge', 'customer_count': 'Nombre de clients'},
                 barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    # KPI 4: Performance des promotions
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🎁 Impact des promotions")
        query = f"""
        SELECT 
            "Promo Code Used" as promo_used,
            COUNT(*) as transaction_count,
            ROUND(SUM("Purchase Amount (USD)"), 2) as total_sales,
            ROUND(AVG("Review Rating"), 2) as avg_rating
        FROM sales_data
        WHERE {where_clause}
        GROUP BY "Promo Code Used"
        ORDER BY total_sales DESC
        """
        df = st.session_state.db_manager.execute_query(query)

        fig = px.pie(df, values='total_sales', names='promo_used',
                     title='CA avec/sans code promo')
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("⭐ Notes moyennes par catégorie")
        query = f"""
        SELECT 
            Category,
            ROUND(AVG("Review Rating"), 2) as avg_rating,
            COUNT(*) as review_count
        FROM sales_data
        WHERE "Review Rating" IS NOT NULL AND {where_clause}
        GROUP BY Category
        ORDER BY avg_rating DESC
        """
        df = st.session_state.db_manager.execute_query(query)

        fig = px.bar(df, x='Category', y='avg_rating',
                     title='Satisfaction client par catégorie',
                     labels={'Category': 'Catégorie', 'avg_rating': 'Note moyenne'},
                     color='avg_rating',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)


# Interface principale
def main():
    st.title("📊 Dashboard d'Analyse de Données")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Téléverser un fichier CSV",
            type=['csv'],
            help="Chargez vos données Airbnb ou Shopping"
        )

        if uploaded_file is not None:
            if st.button("📥 Charger les données", type="primary"):
                with st.spinner("Chargement en cours..."):
                    success, dataset_type, row_count = load_data(uploaded_file)

                    if success:
                        st.success(f"✅ {row_count} lignes chargées!")
                        st.info(f"📋 Type de données: **{dataset_type.upper()}**")
                    else:
                        st.error(f"❌ Erreur: {dataset_type}")

        st.markdown("---")

        # Filtres dynamiques selon le type de données
        if st.session_state.data_loaded:
            st.header("🔍 Filtres")

            filters = {}
            filter_options = st.session_state.db_manager.get_filter_options()

            if st.session_state.dataset_type == 'airbnb':
                # Filtres Airbnb
                if 'regions' in filter_options and filter_options['regions']:
                    filters['neighbourhood'] = st.multiselect(
                        "Quartiers",
                        options=filter_options['regions']
                    )

                if 'room_types' in filter_options and filter_options['room_types']:
                    filters['room_type'] = st.multiselect(
                        "Types de chambre",
                        options=filter_options['room_types']
                    )

                if 'date_range' in filter_options and filter_options['date_range'][0]:
                    min_date, max_date = filter_options['date_range']
                    filters['date_range'] = st.date_input(
                        "Période",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )

            elif st.session_state.dataset_type == 'shopping':
                # Filtres Shopping
                if 'regions' in filter_options and filter_options['regions']:
                    filters['location'] = st.multiselect(
                        "Régions",
                        options=filter_options['regions']
                    )

                if 'categories' in filter_options and filter_options['categories']:
                    filters['category'] = st.multiselect(
                        "Catégories",
                        options=filter_options['categories']
                    )

            st.session_state.filters = filters

        st.markdown("---")
        st.markdown("### 📖 À propos")
        st.markdown("""
        Cette application permet d'analyser:
        - 🏠 **Données Airbnb**: locations, prix, disponibilités
        - 🛍️ **Données Shopping**: ventes, clients, produits
        """)

    # Contenu principal
    if not st.session_state.data_loaded:
        st.info("👈 Commencez par téléverser un fichier CSV dans la barre latérale")

        # Afficher des exemples
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🏠 Dataset Airbnb")
            st.markdown("""
            - Prix et disponibilités
            - Quartiers et types de logement
            - Avis et notes
            - Analyses géographiques
            """)

        with col2:
            st.subheader("🛍️ Dataset Shopping")
            st.markdown("""
            - Ventes par catégorie
            - Analyse démographique
            - Performance des promotions
            - Satisfaction client
            """)
    else:
        # Afficher le dashboard approprié
        filters = st.session_state.get('filters', {})

        if st.session_state.dataset_type == 'airbnb':
            st.header("🏠 Tableau de bord Airbnb")
            create_airbnb_dashboard(filters)
        elif st.session_state.dataset_type == 'shopping':
            st.header("🛍️ Tableau de bord Shopping")
            create_shopping_dashboard(filters)
        else:
            st.warning("⚠️ Type de données non reconnu")


if __name__ == "__main__":
    main()