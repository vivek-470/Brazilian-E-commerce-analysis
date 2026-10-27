use BrazilianECommerce
select * from Customer


-- 1. Check Primary Key Uniqueness
SELECT customer_id, COUNT(*) AS cnt 
FROM Customer
GROUP BY customer_id 
HAVING COUNT(*) > 1;
--There are no duplicates records in Customer table

SELECT order_id, COUNT(*) AS cnt 
FROM orders 
GROUP BY order_id 
HAVING COUNT(*) > 1;
--There are no duplicates records in Orders table


SELECT product_id, COUNT(*) AS cnt 
FROM products 
GROUP BY product_id 
HAVING COUNT(*) > 1;
--There are no duplicates records in Product table

SELECT seller_id, COUNT(*) AS cnt 
FROM sellers 
GROUP BY seller_id 
HAVING COUNT(*) >1;
--There are no duplicates records in Product table

-- 2. Identify delivered orders missing customer delivery timestamps
SELECT 
    order_status,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS missing_delivery_dates,
    SUM(CASE WHEN order_approved_at IS NULL THEN 1 ELSE 0 END) AS missing_approval_dates
FROM orders
GROUP BY order_status;

-- 3. Check if delivered date precedes purchase date
SELECT COUNT(*) AS delivered_before_purchased
FROM orders
WHERE order_delivered_customer_date < order_purchase_timestamp;
--There are no invalid purchase dates

-- Check if delivery exceeded estimated delivery date (late deliveries)
SELECT COUNT(*) AS late_deliveries
FROM orders
WHERE order_delivered_customer_date > order_estimated_delivery_date;

-- 4. Order items without matching parent orders
SELECT COUNT(*) AS orphan_items
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 5. Audit Negative or Zero Values
SELECT COUNT(*) AS invalid_prices 
FROM order_items WHERE price <= 0;

SELECT COUNT(*) AS invalid_payments 
FROM order_payments 
WHERE payment_value <= 0;

-- 6. Audit Missing Product Translations
SELECT COUNT(*) AS untranslated_products
FROM products p
LEFT JOIN product_category_name_translation t 
    ON p.product_category_name = t.product_category_name
WHERE t.product_category_name_english IS NULL 
  AND p.product_category_name IS NOT NULL;

--Late delivered order and review on late orders
SELECT 
    COUNT(*) AS total_delivered_orders,
    SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_orders
FROM dbo.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;

-- Average rating for late vs on-time orders
SELECT 
    CASE 
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late'
        ELSE 'On-Time'
    END AS status,
    COUNT(*) AS total_orders,
    AVG(CAST(r.review_score AS FLOAT)) AS avg_rating
FROM orders o
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY 
    CASE 
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late'
        ELSE 'On-Time'
    END;

SELECT 
    order_id,
    order_item_id,
    price,
    freight_value,
    -- Option A: Freight to Price Ratio
    Round(freight_value / NULLIF(price, 0),2) AS freight_to_price_ratio,
    
    -- Option B: Freight % of Total Item Cost
    ROUND((freight_value / NULLIF(price + freight_value, 0)) * 100, 2) AS freight_pct_of_total
FROM order_items;


select c.customer_state,
avg(datediff(day,o.order_delivered_customer_date,o.order_estimated_delivery_date)) as delivery_time,
avg(cast(r.review_score as float)) as avg_rating
from orders o
left join Customer c
on o.customer_id=c.customer_id
left join order_reviews r
on o.order_id=r.order_id
group by c.customer_state
order by  delivery_time desc


SELECT 
    o.order_id,
    c.customer_state,
    s.seller_state,
    
    -- Feature 1: Interstate flag (1 if across state lines, else 0)
    CASE WHEN s.seller_state <> c.customer_state THEN 1 ELSE 0 END AS is_interstate,
    
    -- Feature 2: Delivery delay in days (actual - estimated)
    DATEDIFF(DAY, o.order_estimated_delivery_date, o.order_delivered_customer_date) AS delivery_delay_days,
    
    -- Feature 3: Carrier transit duration in days (carrier dispatch to delivery)
    DATEDIFF(DAY, o.order_delivered_carrier_date, o.order_delivered_customer_date) AS carrier_transit_days,
    
    -- Feature 4: Seller handover latency in days (purchase to carrier dispatch)
    DATEDIFF(DAY, o.order_purchase_timestamp, o.order_delivered_carrier_date) AS seller_dispatch_days,
    
    -- Feature 5 & 6: Financials and Freight Ratio
    oi.price,
    oi.freight_value,
    ROUND(oi.freight_value / NULLIF(oi.price, 0), 4) AS freight_to_price_ratio,
    
    -- Feature 7: Product weight in grams
    p.product_weight_g,
    
    -- Target Variable: 1 = Low Rating (<= 2 stars), 0 = High Rating (>= 3 stars)
    CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END AS is_dissatisfied

FROM dbo.orders o
JOIN dbo.Customer c 
    ON o.customer_id = c.customer_id
JOIN dbo.order_items oi 
    ON o.order_id = oi.order_id
JOIN dbo.sellers s 
    ON oi.seller_id = s.seller_id
JOIN dbo.products p 
    ON oi.product_id = p.product_id
JOIN dbo.order_reviews r 
    ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_delivered_carrier_date IS NOT NULL
  AND oi.price > 0;