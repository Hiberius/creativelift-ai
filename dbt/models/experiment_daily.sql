select
  organization_id,
  experiment_id,
  variant_id,
  date_trunc('day', timestamp) as event_date,
  count(*) filter (where event_name = 'impression') as impressions,
  count(*) filter (where event_name in ('signup', 'lead', 'purchase', 'custom_conversion')) as conversions,
  sum(coalesce(value, 0)) as revenue
from {{ ref('creative_events') }}
group by 1, 2, 3, 4
