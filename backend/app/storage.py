import os
from google.cloud import storage
from .config import settings
from datetime import timedelta


def _get_client():
    # If service account JSON path provided, use it
    if settings.GCP_SERVICE_ACCOUNT_JSON:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GCP_SERVICE_ACCOUNT_JSON
    return storage.Client()


def upload_bytes(bucket_name: str, blob_name: str, data: bytes, content_type: str = "image/png") -> str:
    client = _get_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)
    blob.make_public()
    return blob.public_url


def generate_v4_put_object_signed_url(bucket_name: str, blob_name: str, expiration: int = 15 * 60) -> str:
    client = _get_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(version="v4", expiration=timedelta(seconds=expiration), method="PUT", content_type="application/octet-stream")
    return url
