with source as (

    select * from {{ source('olist', 'order_items') }}

),

renamed as (

    select
        "order_id"::varchar             as order_id,
        "order_item_id"::number         as order_item_id,
        "product_id"::varchar           as product_id,
        "seller_id"::varchar            as seller_id,
        "shipping_limit_date"::timestamp as shipping_limit_at,
        "price"::numeric(10, 2)         as price,
        "freight_value"::numeric(10, 2) as freight_value

    from source

)

select * from renamed
