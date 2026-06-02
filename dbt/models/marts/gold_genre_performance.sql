with movies_exploded as (
    select
        movie_id,
        genre
    from {{ ref('stg_movies') }},
    unnest(split(genres, '|')) as genre
    where genres != '(no genres listed)'
),

ratings as (
    select * from {{ ref('stg_ratings') }}
),

joined as (
    select
        g.genre,
        r.rating
    from ratings r
    join movies_exploded g on r.movie_id = g.movie_id
)

select
    genre,
    round(avg(rating), 2) as avg_rating,
    count(*)              as total_ratings
from joined
group by genre
order by total_ratings desc
