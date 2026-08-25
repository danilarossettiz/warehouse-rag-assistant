with source as (

    select * from {{ source('olist', 'sellers') }}

),

renamed as (

    select
        "seller_id"::varchar             as seller_id,
        "seller_zip_code_prefix"::varchar as seller_zip_code_prefix,
        "seller_city"::varchar           as seller_city,
        "seller_state"::varchar          as seller_state

    from source

)

select * from renamed
