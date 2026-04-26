import time
import os
import boto3
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Tiki Book Category ID: 8322
DEFAULT_CATEGORY_ID = 8322
# Tiki usually caps listings at 50 pages
DEFAULT_NUM_PAGES = 10  # Default 10 pages (~400 books)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_password")
BUCKET_NAME = "raw-data"


def fetch_products(category_id=DEFAULT_CATEGORY_ID, num_pages=DEFAULT_NUM_PAGES):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    all_products = []

    for page in range(1, num_pages + 1):
        api_url = (
            "https://tiki.vn/api/personalish/v1/blocks/listings?"
            f"limit=40&include=advertisement&aggregations=2&"
            f"version=home-persionalized&category={category_id}&page={page}"
        )
        print(f"Fetching page {page} from: {api_url}")

        try:
            response = requests.get(api_url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if not data:
                    print(f"No more data at page {page}. Stopping.")
                    break
                all_products.extend(data)
                print(f"Fetched {len(data)} products from page {page}")
            else:
                print(f"Failed to fetch page {page}: {response.status_code}")
                break
        except requests.RequestException as e:
            print(f"Request failed at page {page}: {e}")
            break

        # Be nice to Tiki
        time.sleep(1)

    return all_products


def save_to_minio(data):
    if not data:
        print("No data to save")
        return

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Store extraction timestamp
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    df["extracted_at"] = ts_str

    # Sanitize complex nested types (dict/list) for Parquet compatibility
    # This is important for DuckDB/Trino to handle columns easily
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df[col] = df[col].astype(str)

    # Save a copy locally as CSV for quick preview
    preview_dir = "preview_data"
    os.makedirs(preview_dir, exist_ok=True)
    preview_path = os.path.join(preview_dir, f"tiki_books_preview_{ts_str}.csv")
    df.to_csv(preview_path, index=False)
    print(f"Local CSV preview saved to: {preview_path}")

    # Convert to Parquet formatting
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)

    # Init MinIO client
    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

    file_key = f"tiki_products/books_{ts_str}.parquet"
    print(f"Uploading {len(df)} products to {BUCKET_NAME}/{file_key}")

    s3_client.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=parquet_buffer.getvalue())
    print("Upload complete.")


if __name__ == "__main__":
    # You can increase num_pages to fetch more data (max 50)
    products = fetch_products(category_id=8322, num_pages=20)
    save_to_minio(products)
