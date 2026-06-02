with source as (
    select * from {{ source('raw', 'movies') }}
)

select
    cast(movieId as int64)                           as movie_id,
    title,
    genres,
    safe_cast(regexp_extract(title, r'\((\d{4})\)$') as int64) as release_year
from source
where movieId is not null
