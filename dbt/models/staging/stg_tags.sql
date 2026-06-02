with source as (
    select * from {{ source('raw', 'tags') }}
)

select
    cast(userId  as int64)  as user_id,
    cast(movieId as int64)  as movie_id,
    tag,
    timestamp_seconds(cast(timestamp as int64)) as tagged_at
from source
where userId  is not null
  and movieId is not null
  and tag     is not null
  and trim(tag) != ''
