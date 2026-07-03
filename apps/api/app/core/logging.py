from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    return correlation_id_var.get()


def set_correlation_id(value: str | None) -> None:
    correlation_id_var.set(value)


def _add_correlation_id(_logger: Any, _method_name: str, event_dict: Any) -> Any:
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def configure_logging(log_level: str = "info") -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_correlation_id,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)
