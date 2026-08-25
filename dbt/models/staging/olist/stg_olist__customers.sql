with source as (

    select * from {{ source('olist', 'customers') }}

),

renamed as (

    select
        "customer_id"::varchar             as customer_id,
        "customer_unique_id"::varchar      as customer_unique_id,
        "customer_zip_code_prefix"::varchar as customer_zip_code_prefix,
        "customer_city"::varchar           as customer_city,
        "customer_state"::varchar          as customer_state

    from source

)

select * from renamed
