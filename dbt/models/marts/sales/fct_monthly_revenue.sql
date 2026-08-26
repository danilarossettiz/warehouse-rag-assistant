with order_items as (

    select * from {{ ref('int_order_items__enriched') }}

),

valid_items as (

    select *
    from order_items
    where order_status not in ('canceled', 'unavailable')

),

monthly as (

    select
        order_purchase_month,
        count(distinct order_id) as total_orders,
        sum(item_revenue) as total_revenue,
        sum(item_revenue) / nullif(count(distinct order_id), 0) as avg_revenue_per_order

    from valid_items
    group by 1

)

select * from monthly
order by order_purchase_month
