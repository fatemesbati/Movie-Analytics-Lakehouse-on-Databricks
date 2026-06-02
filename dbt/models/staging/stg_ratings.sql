with source as (
    select * from {{ source('raw', 'ratings') }}
),

cleaned as (
    select
        cast(userId as int64)   as user_id,
        cast(movieId as int64)  as movie_id,
        cast(rating as float64) as rating,
        timestamp_seconds(cast(timestamp as int64)) as rated_at
    from source
    where userId  is not null
      and movieId is not null
      and cast(rating as float64) between 0.5 and 5.0
),

deduplicated as (
    select *
    from cleaned
    qualify row_number() over (partition by user_id, movie_id order by rated_at desc) = 1
)

select * from deduplicated
