import logging

from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential_jitter

logger = logging.getLogger(__name__)

RETRY_ATTEMPTS = 3
RETRY_STOP = stop_after_attempt(RETRY_ATTEMPTS + 1)
RETRY_WAIT = wait_exponential_jitter(initial=0.5, max=5, jitter=0.25)


def retry_async(func):
    return retry(
        stop=RETRY_STOP,
        wait=RETRY_WAIT,
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(func)


def retry_sync(func):
    return retry(
        stop=RETRY_STOP,
        wait=RETRY_WAIT,
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(func)
