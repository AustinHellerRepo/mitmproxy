import ipaddress
import logging
import re
import requests
import asyncio
import aiohttp
from typing import Optional

from mitmproxy import ctx, exceptions, flowfilter, http, version

logging.debug("loaded PostToApi class")


class PostToApi:

    def __init__(self):
        self.__is_initialized = False
        self.__api_entrypoint_url = None
        self.__regex = None
        self.__is_async = None

    def load(self, loader):
        loader.add_option(
            "api_entrypoint_url",
            Optional[str],
            None,
            """
            The API entrypoint URL that the request will be posted to.
            """,
        )
        loader.add_option(
            "request_url_regex_pattern",
            Optional[str],
            None,
            """
            The regex that filters the incoming URL requests so that not everything is sent to the API entrypoint.
            """,
        )
        loader.add_option(
            "is_async",
            bool,
            True,
            """
            If true, asyncio is used. If false, requests is used.
            """,
        )

    async def request(self, flow: http.HTTPFlow) -> None:
        logging.debug(f"request method: start")
        try:
            if flow.response or flow.error or not flow.live:
                return

            if not self.__is_initialized:
                api_entrypoint_url = ctx.options.api_entrypoint_url
                request_url_regex_pattern = ctx.options.request_url_regex_pattern
                if api_entrypoint_url is None or request_url_regex_pattern is None:
                    error_message = f"Both options are required."
                    logging.error(error_message)
                    raise Exception(error_message)
                self.__api_entrypoint_url = api_entrypoint_url
                self.__regex = re.compile(ctx.options.request_url_regex_pattern)
                self.__is_async = ctx.options.is_async
                self.__is_initialized = True

            if self.__regex.search(flow.request.url) is not None:
                post_data = {
                    "url": flow.request.url,
                    "http_type": flow.request.method,
                    "data": flow.request.content.decode() if flow.request.method == "POST" else "{}",
                    "headers": "{ \"test\": \"here\" }"
                }
                logging.debug(f"post_data: {post_data}")
                if self.__is_async:
                    flow.intercept()
                    async with aiohttp.ClientSession() as session:
                        async with session.post(self.__api_entrypoint_url, json=post_data) as response:
                            logging.info(f"received response: {response}")
                            response_data = await response.json()
                            logging.debug(f"response_data: {response_data}")
                            flow.resume()
                else:
                    requests.post(self.__api_entrypoint_url, json=post_data)
                logging.debug(f"done post")
        finally:
            logging.debug("request method: end")
