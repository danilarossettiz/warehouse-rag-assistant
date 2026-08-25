with source as (

    select * from {{ source('olist', 'order_reviews') }}

),

renamed as (

    select
        "review_id"::varchar                  as review_id,
        "order_id"::varchar                    as order_id,
        "review_score"::number                 as review_score,
        "review_comment_title"::varchar        as review_comment_title,
        "review_comment_message"::varchar      as review_comment_message,
        "review_creation_date"::timestamp      as review_created_at,
        "review_answer_timestamp"::timestamp   as review_answered_at

    from source

)

select * from renamed
