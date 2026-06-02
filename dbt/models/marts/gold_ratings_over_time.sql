with ratings as (
    select * from {{ ref('stg_ratings') }}
)

select
    date_trunc(rated_at, month)  as month,
    count(*)                     as total_ratings,
    round(avg(rating), 2)        as avg_rating
from ratings
group by month
order by month
