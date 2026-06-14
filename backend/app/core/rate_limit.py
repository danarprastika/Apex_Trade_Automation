from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config.settings import settings

INTERNAL_API_LIMIT = "1000/minute"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=(INTERNAL_API_LIMIT,),
)
