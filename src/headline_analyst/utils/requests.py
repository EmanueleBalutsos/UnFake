import asyncio
import httpx
from typing import Any, Optional

async def httpx_request_with_retries(
        method: str,
        url: str,
        *,
        client: Optional[httpx.AsyncClient] = None,
        max_retries: int = 3,
        timeout: float = 30.0,
        backoff_factor: float = 1.5,
        retry_statuses: tuple = (500, 502, 503, 504),
        **kwargs: Any) -> httpx.Response:
    """
    Make an HTTP request with retries using httpx.AsyncClient.

    Args:
        method: HTTP method ("GET", "POST", etc.)
        url: request URL
        client: optional shared AsyncClient
        max_retries: number of retries before failing
        timeout: request timeout (seconds)
        backoff_factor: exponential backoff multiplier
        retry_statuses: HTTP status codes to retry on
        **kwargs: passed to httpx request (json, headers, etc.)

    Returns:
        httpx.Response

    Raises:
        httpx.HTTPError after final failure
    """

    attempt = 0
    last_exc = None # exception from the last attempt, to raise if all retries fail

    close_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=timeout) # create a client if none is passed

    try:
        while attempt <= max_retries:
            try: # catches HTTP errors
                response = await client.request(
                    method,
                    url,
                    timeout=timeout,
                    **kwargs,
                )

                if response.status_code not in retry_statuses: # http success or non-retryable error
                    response.raise_for_status() # raise for non-success status codes
                    return response

                # Retry on bad status
                last_exc = httpx.HTTPStatusError(
                    f"Retryable status: {response.status_code}",
                    request=response.request,
                    response=response,
                )

            # also catch network errors and timeouts to retry
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.NetworkError) as e:
                last_exc = e

            attempt += 1

            if attempt > max_retries:
                break

            sleep_time = backoff_factor ** attempt
            await asyncio.sleep(sleep_time)

        raise last_exc # final failure

    finally: # close client if we created it in this method, otherwise leave it open for the caller to manage
        if close_client:
            await client.aclose()