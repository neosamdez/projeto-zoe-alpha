import json
import logging
from typing import Optional, Any
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

REDIS_URL = getattr(settings, "REDIS_URL", "redis://redis:6379/0")

_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            _redis_client.ping()
            logger.info("Redis conectado: %s", REDIS_URL)
        except redis.ConnectionError:
            logger.warning("Redis indisponível — cache desabilitado")
            _redis_client = None
    return _redis_client  # type: ignore


def cache_get(key: str) -> Optional[Any]:
    client = get_redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except (redis.RedisError, json.JSONDecodeError):
        return None


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    client = get_redis()
    if client is None:
        return
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
    except redis.RedisError:
        logger.warning("Falha ao gravar cache: %s", key)


def cache_delete(key: str) -> None:
    client = get_redis()
    if client is None:
        return
    try:
        client.delete(key)
    except redis.RedisError:
        pass


def cache_invalidate(prefix: str) -> None:
    client = get_redis()
    if client is None:
        return
    try:
        for key in client.scan_iter(match=f"{prefix}*"):
            client.delete(key)
    except redis.RedisError:
        pass
