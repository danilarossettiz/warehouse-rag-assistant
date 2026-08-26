with orders as (

    select * from {{ ref('int_orders__enriched') }}

),

delivered as (

    select *
    from orders
    where is_delivered

),

by_state as (

    select
        customer_state,
        count(*) as total_delivered_orders,
        avg(delivery_days) as avg_delivery_days,
        min(delivery_days) as min_delivery_days,
        max(delivery_days) as max_delivery_days

    from delivered
    group by 1

)

select * from by_state
order by avg_delivery_days
