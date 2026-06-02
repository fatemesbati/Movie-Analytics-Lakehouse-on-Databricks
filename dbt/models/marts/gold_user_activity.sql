with ratings as (
    select * from {{ ref('stg_ratings') }}
),

user_stats as (
    select
        user_id,
        count(*)              as total_ratings,
        round(avg(rating), 2) as avg_rating,
        min(rated_at)         as first_rated_at,
        max(rated_at)         as last_rated_at
    from ratings
    group by user_id
)

select
    case
        when total_ratings >= 100 then 'power_user'
        when total_ratings >= 20  then 'active'
        else 'casual'
    end                                    as user_segment,
    count(*)                               as user_count,
    round(avg(total_ratings), 1)           as avg_ratings_per_user,
    round(avg(avg_rating), 2)              as avg_rating
from user_stats
group by user_segment
order by user_count desc
