
{{ config(
    materialized='external',
    location='s3://raw-data/marts/fct_tiki_books.parquet'
) }}

with staging as (
    select * from {{ ref('stg_tiki_books') }}
)

select
    product_id,
    product_name,
    author_name,
    price,
    original_price,
    discount,
    discount_rate,
    rating_average,
    review_count,
    inventory_status,
    quantity_sold,
    brand_name,
    strptime(extracted_at, '%Y%m%d_%H%M%S') as extracted_at_ts
from staging
