import os
import json
import boto3
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Dummy URL to simulate Tiki Product API
# Note: Tiki APIs change frequently, a real implementation requires reverse engineering their exact endpoints
TIKI_API_URL = "https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&include=advertisement&aggregations=2&version=home-persionalized&category=1883"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_password")
BUCKET_NAME = "raw-data"


def fetch_products():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    print(f"Fetching from: {TIKI_API_URL}")
    try:
        response = requests.get(TIKI_API_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []


def save_to_minio(data):
    if not data:
        print("No data to save")
        return

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Store extraction timestamp
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    df["extracted_at"] = ts_str

    # Sanitize complex nested types (dict/list) to strings for Parquet compatibility
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df[col] = df[col].astype(str)

    # Save a copy locally as CSV for quick preview
    preview_dir = "preview_data"
    os.makedirs(preview_dir, exist_ok=True)
    preview_path = os.path.join(preview_dir, f"tiki_products_preview_{ts_str}.csv")
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

    file_key = f"tiki_products/products_{ts_str}.parquet"
    print(f"Uploading to {BUCKET_NAME}/{file_key}")

    s3_client.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=parquet_buffer.getvalue())
    print("Upload complete.")


if __name__ == "__main__":
    products = fetch_products()
    save_to_minio(products)
