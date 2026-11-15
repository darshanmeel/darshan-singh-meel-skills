{#- One row per order line (order_line_id). Late rows arrive up to 3 days after updated_at. -#}
{{ config(
    materialized='incremental',
    unique_key='order_line_id',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
) }}

with source as (
    select * from {{ ref('stg_erp__order_lines') }}
    {% if is_incremental() %}
    where updated_at >= (select dateadd(day, -3, max(updated_at)) from {{ this }})
    {% endif %}
),

deduped as (
    select *
    from source
    qualify row_number() over (partition by order_line_id order by updated_at desc) = 1
)

select
    order_line_id,
    order_id,
    line_no,
    status,
    amount,
    updated_at
from deduped
