with orders as (

    select * from {{ ref('stg_olist__orders') }}

),

customers as (

    select * from {{ ref('stg_olist__customers') }}

),

joined as (

    select
        orders.order_id,
        orders.customer_id,
        orders.order_status,
        orders.order_purchase_at,
        orders.order_approved_at,
        orders.order_delivered_carrier_at,
        orders.order_delivered_customer_at,
        orders.order_estimated_delivery_at,
        customers.customer_unique_id,
        customers.customer_city,
        customers.customer_state,
        orders.order_delivered_customer_at is not null as is_delivered,
        datediff('second', orders.order_purchase_at, orders.order_delivered_customer_at) / 86400.0 as delivery_days

    from orders
    left join customers on orders.customer_id = customers.customer_id

)

select * from joined
