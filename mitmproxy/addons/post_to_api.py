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

    def __initialize(self):
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

    def __get_request_api_entrypoint_url(self) -> str:
        return f"{self.__api_entrypoint_url}{'' if self.__api_entrypoint_url.endswith('/') else '/'}request"

    def __get_response_api_entrypoint_url(self) -> str:
        return f"{self.__api_entrypoint_url}{'' if self.__api_entrypoint_url.endswith('/') else '/'}response"

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
                self.__initialize()

            if self.__regex.search(flow.request.url) is not None:
                post_data = {
                    "id": flow.id,
                    "url": flow.request.url,
                    "query": {
                        key: value for key, value in flow.request.query.items()
                    },
                    "http_type": flow.request.method,
                    "data": flow.request.content.decode() if flow.request.method == "POST" else "{}",
                    "headers": {
                        key if isinstance(key, str) else key.decode(): value if isinstance(value, str) else value.decode() for key, value in flow.request.headers.items()
                    }
                }
                logging.debug(f"request: post_data: {post_data}")

                async def process_response(*, response):
                    response_data = await response.json()
                    logging.debug(f"response_data: {response_data}")
                    if response_data["is_original_sent_onward"]:
                        pass
                    elif response_data["overriding_custom_request"]:
                        overriding_custom_request = response_data["overriding_custom_request"]
                        flow.request.url = overriding_custom_request.url
                        flow.request.query = overriding_custom_request.query
                        flow.request.method = overriding_custom_request.http_type
                        flow.request.content = overriding_custom_request.data
                        flow.request.headers = overriding_custom_request.headers
                    elif response_data["overriding_custom_response"]:
                        overriding_custom_response = response_data["overriding_custom_response"]
                        flow.response = http.Response.make(
                            status_code=overriding_custom_response.status,
                            content=overriding_custom_response.body,
                            headers=overriding_custom_response.headers
                        )
                    else:
                        raise NotImplementedError(f"Unexpected state in response_data: {response_data}")

                if self.__is_async:
                    flow.intercept()
                    async with aiohttp.ClientSession() as session:
                        async with session.post(self.__get_request_api_entrypoint_url(), json=post_data) as response:
                            logging.info(f"request: received response: {response}")
                            await process_response(
                                response=response
                            )
                    flow.resume()
                else:
                    response = requests.post(self.__get_request_api_entrypoint_url(), json=post_data)
                    await process_response(
                        response=response
                    )
                logging.debug(f"request: done post")
        finally:
            logging.debug("request method: end")

    async def response(self, flow: http.HTTPFlow) -> None:
        logging.debug(f"response method: start")
        try:
            if flow.error or not flow.live:
                return

            if not self.__is_initialized:
                self.__initialize()

            if self.__regex.search(flow.request.url) is not None:
                post_data = {
                    "request": {
                        "id": flow.id,
                        "url": flow.request.url,
                        "query": {
                            key: value for key, value in flow.request.query.items()
                        },
                        "http_type": flow.request.method,
                        "data": flow.request.content.decode() if flow.request.method == "POST" else "{}",
                        "headers": {
                            key if isinstance(key, str) else key.decode(): value if isinstance(value, str) else value.decode() for key, value in flow.request.headers.items()
                        }
                    },
                    "status": flow.response.status_code,
                    "content": flow.response.content.decode(),
                    "headers": {
                        key if isinstance(key, str) else key.decode(): value if isinstance(value, str) else value.decode() for key, value in flow.response.headers.items()
                    }
                }
                logging.debug(f"response: post_data: {post_data}")

                async def process_response(*, response):
                    response_data = await response.json()
                    logging.debug(f"response: response_data: {response_data}")
                    if response_data["is_original_sent_onward"]:
                        pass
                    elif response_data["overriding_custom_request"]:
                        raise ValueError(f"response_data[\"overriding_custom_request\"] should have been null but contained data: {response_data}")
                    elif response_data["overriding_custom_response"]:
                        overriding_custom_response = response_data["overriding_custom_response"]
                        flow.response = http.Response.make(
                            status_code=overriding_custom_response["status"],
                            content=overriding_custom_response["body"],
                            headers=overriding_custom_response["headers"]
                        )
                    else:
                        raise NotImplementedError(f"Unexpected state in response_data: {response_data}")

                if self.__is_async:
                    flow.intercept()
                    async with aiohttp.ClientSession() as session:
                        async with session.post(self.__get_response_api_entrypoint_url(), json=post_data) as response:
                            logging.info(f"response: received response: {response}")
                            await process_response(
                                response=response
                            )
                    flow.resume()
                else:
                    response = requests.post(self.__get_response_api_entrypoint_url(), json=post_data)
                    await process_response(
                        response=response
                    )
                logging.debug(f"response: done post")

        finally:
            logging.debug("response method: end")
