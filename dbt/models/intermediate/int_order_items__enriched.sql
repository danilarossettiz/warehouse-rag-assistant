with order_items as (

    select * from {{ ref('stg_olist__order_items') }}

),

orders as (

    select * from {{ ref('stg_olist__orders') }}

),

products as (

    select * from {{ ref('stg_olist__products') }}

),

category_translations as (

    select * from {{ ref('stg_olist__product_category_translations') }}

),

joined as (

    select
        order_items.order_id,
        order_items.order_item_id,
        order_items.product_id,
        order_items.seller_id,
        order_items.price,
        order_items.freight_value,
        order_items.price + order_items.freight_value as item_revenue,
        orders.order_status,
        orders.order_purchase_at,
        date_trunc('month', orders.order_purchase_at)::date as order_purchase_month,
        products.product_category_name,
        coalesce(
            category_translations.product_category_name_english,
            products.product_category_name
        ) as product_category_name_english

    from order_items
    left join orders on order_items.order_id = orders.order_id
    left join products on order_items.product_id = products.product_id
    left join category_translations
        on products.product_category_name = category_translations.product_category_name

)

select * from joined
