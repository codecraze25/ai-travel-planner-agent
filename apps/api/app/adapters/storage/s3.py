"""Object storage facade — S3/MinIO or local filesystem."""

from __future__ import annotations

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from app.adapters.storage import local as local_storage
from app.core.config import Settings, get_settings


def _use_local(settings: Settings | None = None) -> bool:
    cfg = settings or get_settings()
    return cfg.storage_backend.lower() == "local"


def create_s3_client(settings: Settings | None = None) -> BaseClient:
    cfg = settings or get_settings()
    return boto3.client(
        "s3",
        endpoint_url=cfg.s3_endpoint,
        aws_access_key_id=cfg.s3_access_key,
        aws_secret_access_key=cfg.s3_secret_key,
        region_name=cfg.s3_region,
    )


def ensure_bucket(client: BaseClient, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


def put_object(key: str, data: bytes, content_type: str = "application/pdf") -> None:
    if _use_local():
        local_storage.put_object(key, data, content_type)
        return
    settings = get_settings()
    client = create_s3_client(settings)
    ensure_bucket(client, settings.s3_bucket)
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
    )


def get_object_bytes(key: str) -> bytes:
    if _use_local():
        return local_storage.get_object_bytes(key)
    settings = get_settings()
    client = create_s3_client(settings)
    response = client.get_object(Bucket=settings.s3_bucket, Key=key)
    return bytes(response["Body"].read())


def delete_object(key: str) -> None:
    if _use_local():
        local_storage.delete_object(key)
        return
    settings = get_settings()
    client = create_s3_client(settings)
    try:
        client.delete_object(Bucket=settings.s3_bucket, Key=key)
    except ClientError:
        pass


def presigned_put_url(key: str, expires_in: int = 900) -> str:
    if _use_local():
        return local_storage.presigned_put_url(key, expires_in)
    settings = get_settings()
    client = create_s3_client(settings)
    ensure_bucket(client, settings.s3_bucket)
    url: str = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": key,
            "ContentType": "application/pdf",
        },
        ExpiresIn=expires_in,
    )
    return url


async def check_storage(settings: Settings | None = None) -> bool:
    cfg = settings or get_settings()
    if _use_local(cfg):
        return await local_storage.check_storage(cfg)
    try:
        client = create_s3_client(cfg)
        ensure_bucket(client, cfg.s3_bucket)
        client.head_bucket(Bucket=cfg.s3_bucket)
        return True
    except (BotoCoreError, ClientError, Exception):
        return False
