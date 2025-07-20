from SPYDIR.logs.log_setup import logger


_cache_dict = {}


def get(key: str) -> dict:
    """Retrieve a value from the cache using the specified key."""
    try:
        return _cache_dict[key]
    except:
        return None


def set(key: str, value, timeout=0):
    """Store a key-value pair in the cache."""

    try:
        _cache_dict[key] = value
    except:
        return None


def delete(key: str):
    """Remove a key-value pair from the cache."""

    try:
        logger.debug(f"Deleting: {key}")
        del _cache_dict[key]
    except:
        return None
