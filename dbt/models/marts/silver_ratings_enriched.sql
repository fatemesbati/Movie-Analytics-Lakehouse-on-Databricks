with ratings as (
    select * from {{ ref('stg_ratings') }}
),

movies as (
    select * from {{ ref('stg_movies') }}
)

select
    r.user_id,
    r.movie_id,
    r.rating,
    r.rated_at,
    m.title,
    m.genres,
    m.release_year
from ratings r
left join movies m on r.movie_id = m.movie_id
