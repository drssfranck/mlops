-- ============================================
-- REQUÊTES POUR DATASET AIRBNB
-- ============================================

-- KPI 1: Prix moyen par type de chambre
CREATE OR REPLACE VIEW airbnb_price_by_room_type AS
SELECT
    "room type" as room_type,
    ROUND(AVG(price), 2) as avg_price,
    COUNT(*) as count
FROM sales_data
WHERE price IS NOT NULL
GROUP BY "room type"
ORDER BY avg_price DESC;

-- KPI 2: Disponibilité moyenne par quartier
CREATE OR REPLACE VIEW airbnb_availability_by_neighbourhood AS
SELECT
    neighbourhood,
    ROUND(AVG("availability 365"), 2) as avg_availability,
    COUNT(*) as listings_count
FROM sales_data
WHERE "availability 365" IS NOT NULL
GROUP BY neighbourhood
ORDER BY avg_availability DESC
LIMIT 15;

-- KPI 3: Nombre de reviews par mois
CREATE OR REPLACE VIEW airbnb_reviews_trend AS
SELECT
    DATE_TRUNC('month', "last review") as review_month,
    COUNT(*) as review_count,
    ROUND(AVG("review rate number"), 2) as avg_rating
FROM sales_data
WHERE "last review" IS NOT NULL
GROUP BY DATE_TRUNC('month', "last review")
ORDER BY review_month;

-- KPI 4: Distribution des prix
CREATE OR REPLACE VIEW airbnb_price_distribution AS
SELECT
    CASE
        WHEN price < 100 THEN '0-100'
        WHEN price < 200 THEN '100-200'
        WHEN price < 300 THEN '200-300'
        WHEN price < 500 THEN '300-500'
        ELSE '500+'
    END as price_range,
    COUNT(*) as count
FROM sales_data
WHERE price IS NOT NULL
GROUP BY price_range
ORDER BY price_range;

-- ============================================
-- REQUÊTES POUR DATASET SHOPPING
-- ============================================

-- KPI 1: Ventes totales par catégorie
CREATE OR REPLACE VIEW shopping_sales_by_category AS
SELECT
    Category,
    ROUND(SUM("Purchase Amount (USD)"), 2) as total_sales,
    COUNT(*) as transaction_count,
    ROUND(AVG("Purchase Amount (USD)"), 2) as avg_purchase
FROM sales_data
WHERE "Purchase Amount (USD)" IS NOT NULL
GROUP BY Category
ORDER BY total_sales DESC;

-- KPI 2: Ventes par localisation
CREATE OR REPLACE VIEW shopping_sales_by_location AS
SELECT
    Location,
    ROUND(SUM("Purchase Amount (USD)"), 2) as total_sales,
    COUNT(*) as customer_count
FROM sales_data
GROUP BY Location
ORDER BY total_sales DESC
LIMIT 15;

-- KPI 3: Analyse démographique
CREATE OR REPLACE VIEW shopping_demographics AS
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
GROUP BY Gender, age_group
ORDER BY Gender, age_group;

-- KPI 4: Performance des promotions
CREATE OR REPLACE VIEW shopping_promo_performance AS
SELECT
    "Promo Code Used" as promo_used,
    "Discount Applied" as discount_applied,
    COUNT(*) as transaction_count,
    ROUND(SUM("Purchase Amount (USD)"), 2) as total_sales,
    ROUND(AVG("Review Rating"), 2) as avg_rating
FROM sales_data
GROUP BY "Promo Code Used", "Discount Applied"
ORDER BY total_sales DESC;