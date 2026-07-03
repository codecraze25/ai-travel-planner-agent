from __future__ import annotations

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import Settings, get_settings


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


async def check_storage(settings: Settings | None = None) -> bool:
    cfg = settings or get_settings()
    try:
        client = create_s3_client(cfg)
        ensure_bucket(client, cfg.s3_bucket)
        client.head_bucket(Bucket=cfg.s3_bucket)
        return True
    except (BotoCoreError, ClientError, Exception):
        return False
