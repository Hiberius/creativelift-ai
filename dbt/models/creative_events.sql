select
  organization_id,
  event_name,
  timestamp,
  anonymous_id,
  user_id,
  creative_treatment_id,
  experiment_id,
  variant_id,
  channel,
  placement,
  value,
  currency,
  properties
from {{ source('creativelift', 'events') }}
