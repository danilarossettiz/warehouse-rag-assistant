with source as (

    select * from {{ source('olist', 'products') }}

),

renamed as (

    select
        "product_id"::varchar                as product_id,
        "product_category_name"::varchar     as product_category_name,
        "product_name_lenght"::number         as product_name_length,
        "product_description_lenght"::number  as product_description_length,
        "product_photos_qty"::number          as product_photos_qty,
        "product_weight_g"::number             as product_weight_g,
        "product_length_cm"::number             as product_length_cm,
        "product_height_cm"::number             as product_height_cm,
        "product_width_cm"::number              as product_width_cm

    from source

)

select * from renamed
