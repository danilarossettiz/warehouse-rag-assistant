with order_items as (

    select * from {{ ref('int_order_items__enriched') }}

),

valid_items as (

    select *
    from order_items
    where order_status not in ('canceled', 'unavailable')
      and product_category_name_english is not null

),

by_category as (

    select
        product_category_name_english as product_category,
        count(distinct order_id) as total_orders,
        count(*) as total_items,
        sum(item_revenue) as total_revenue

    from valid_items
    group by 1

),

ranked as (

    select
        *,
        rank() over (order by total_orders desc) as orders_rank

    from by_category

)

select * from ranked
order by orders_rank
