import io
import time

import boto3
import pandas as pd
import requests

from crawler.fetch_tiki import fetch_products, save_to_minio


# ── helpers ─────────────────────────────────────────────────────────────────


def _product(id_):
    return {"id": id_, "name": f"Book {id_}", "price": id_ * 1000}


def _response(status, data):
    class R:
        status_code = status

        def json(self):
            return {"data": data}

    return R()


def _mock_get(responses):
    """Return a requests.get replacement that yields from *responses*.
    Raise the item directly if it is an Exception instance."""
    it = iter(responses)

    def mock(url, headers, timeout):
        try:
            val = next(it)
        except StopIteration:
            raise AssertionError("_mock_get ran out of responses — add more items to the list")
        if isinstance(val, Exception):
            raise val
        return val

    return mock


class _MockS3:
    def __init__(self):
        self.calls = []

    def put_object(self, **kwargs):
        self.calls.append(kwargs)


# ── fetch_products ───────────────────────────────────────────────────────────


def test_fetch_single_page(monkeypatch):
    monkeypatch.setattr(requests, "get", _mock_get([_response(200, [_product(1), _product(2)])]))
    monkeypatch.setattr(time, "sleep", lambda s: None)

    assert fetch_products(num_pages=1) == [_product(1), _product(2)]


def test_fetch_multiple_pages(monkeypatch):
    monkeypatch.setattr(requests, "get", _mock_get([
        _response(200, [_product(1), _product(2)]),
        _response(200, [_product(3)]),
    ]))
    monkeypatch.setattr(time, "sleep", lambda s: None)

    result = fetch_products(num_pages=2)

    assert [p["id"] for p in result] == [1, 2, 3]


def test_fetch_stops_on_empty_data(monkeypatch):
    monkeypatch.setattr(requests, "get", _mock_get([
        _response(200, [_product(1)]),
        _response(200, []),
    ]))
    monkeypatch.setattr(time, "sleep", lambda s: None)

    assert fetch_products(num_pages=5) == [_product(1)]


def test_fetch_stops_on_non_200(monkeypatch):
    monkeypatch.setattr(requests, "get", _mock_get([
        _response(200, [_product(1)]),
        _response(429, []),
    ]))
    monkeypatch.setattr(time, "sleep", lambda s: None)

    assert fetch_products(num_pages=5) == [_product(1)]


def test_fetch_stops_on_exception(monkeypatch):
    monkeypatch.setattr(requests, "get", _mock_get([
        _response(200, [_product(1)]),
        requests.RequestException("timeout"),
    ]))
    monkeypatch.setattr(time, "sleep", lambda s: None)

    assert fetch_products(num_pages=3) == [_product(1)]


# ── save_to_minio ────────────────────────────────────────────────────────────


def test_save_empty_data_does_nothing(monkeypatch, tmp_path):
    called = []
    monkeypatch.setattr(boto3, "client", lambda *a, **kw: called.append(1))
    monkeypatch.chdir(tmp_path)

    save_to_minio([])

    assert called == []
    assert not (tmp_path / "preview_data").exists()


def test_save_stringifies_nested_columns(monkeypatch, tmp_path):
    s3 = _MockS3()
    monkeypatch.setattr(boto3, "client", lambda *a, **kw: s3)
    monkeypatch.chdir(tmp_path)

    save_to_minio([{"id": 1, "meta": {"k": "v"}, "tags": ["a", "b"]}])

    df = pd.read_parquet(io.BytesIO(s3.calls[0]["Body"]))
    assert isinstance(df["meta"][0], str)
    assert isinstance(df["tags"][0], str)


def test_save_uploads_parquet_to_minio(monkeypatch, tmp_path):
    s3 = _MockS3()
    monkeypatch.setattr(boto3, "client", lambda *a, **kw: s3)
    monkeypatch.chdir(tmp_path)

    save_to_minio([_product(1), _product(2)])

    assert len(s3.calls) == 1
    call = s3.calls[0]
    assert call["Bucket"] == "raw-data"
    assert call["Key"].startswith("tiki_products/books_")
    assert call["Key"].endswith(".parquet")
    df = pd.read_parquet(io.BytesIO(call["Body"]))
    assert len(df) == 2
    assert "extracted_at" in df.columns


def test_save_creates_csv_preview(monkeypatch, tmp_path):
    s3 = _MockS3()
    monkeypatch.setattr(boto3, "client", lambda *a, **kw: s3)
    monkeypatch.chdir(tmp_path)

    save_to_minio([_product(1)])

    csv_files = list((tmp_path / "preview_data").glob("tiki_books_preview_*.csv"))
    assert len(csv_files) == 1
