
select
    id as product_id,
    name as product_name,
    author_name,
    try_cast(price as integer) as price,
    try_cast(original_price as integer) as original_price,
    try_cast(discount as integer) as discount,
    try_cast(discount_rate as float) as discount_rate,
    try_cast(rating_average as float) as rating_average,
    try_cast(review_count as integer) as review_count,
    inventory_status,
    try_cast(regexp_extract(quantity_sold, '''value'':\s*([0-9]+)', 1) as integer) as quantity_sold,
    brand_name,
    extracted_at
from read_parquet('s3://raw-data/tiki_products/*.parquet')
