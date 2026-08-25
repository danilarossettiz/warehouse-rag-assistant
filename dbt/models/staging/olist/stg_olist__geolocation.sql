with source as (

    select * from {{ source('olist', 'geolocation') }}

),

renamed as (

    select
        "geolocation_zip_code_prefix"::varchar as geolocation_zip_code_prefix,
        "geolocation_lat"::float               as geolocation_lat,
        "geolocation_lng"::float               as geolocation_lng,
        "geolocation_city"::varchar            as geolocation_city,
        "geolocation_state"::varchar           as geolocation_state

    from source

)

select * from renamed
