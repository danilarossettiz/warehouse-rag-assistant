with source as (

    select * from {{ source('olist', 'orders') }}

),

renamed as (

    select
        "order_id"::varchar                          as order_id,
        "customer_id"::varchar                        as customer_id,
        "order_status"::varchar                       as order_status,
        "order_purchase_timestamp"::timestamp          as order_purchase_at,
        "order_approved_at"::timestamp                 as order_approved_at,
        "order_delivered_carrier_date"::timestamp      as order_delivered_carrier_at,
        "order_delivered_customer_date"::timestamp     as order_delivered_customer_at,
        "order_estimated_delivery_date"::timestamp     as order_estimated_delivery_at

    from source

)

select * from renamed
