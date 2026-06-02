with enriched as (
    select * from {{ ref('silver_ratings_enriched') }}
),

aggregated as (
    select
        movie_id,
        title,
        release_year,
        count(*)         as total_ratings,
        round(avg(rating), 2) as avg_rating
    from enriched
    group by movie_id, title, release_year
    having count(*) >= 10
)

select *
from aggregated
order by total_ratings desc
limit 20
