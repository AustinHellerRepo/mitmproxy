# AustinHellerRepo fork differences - **INCOMPLETE**
- Added the PostToApi addon that can post intercepted requests to another server, waiting for a useful response
  - The addon will match a regex pattern against the requests, only posting those URLs that match in order to reduce general latency
  - The addon will wait for a response from the server, providing predefined action details
## Possible actions for intercepted requests
1. Send request onward as normal and send the response onward as normal
2. Send request onward as normal but post the response to the API for additional processing
    1. Send the response onward as normal
    2. Respond with hand-crafted response from server
3. Respond with hand-crafted response from server

For example, the first post with the request details may result in action #2, so that when the response is returned it will then also be posted to the server, which could either result in the response being forwarded onward as normal (2i) or a custom response from the API (2ii).

## General use cases for PostToApi addon
- Block specific content that is not possible to determine from the URL alone
- Include aggregated content with responses
  - Pull data from other sources and add to body of response
  - Reconstruct body to include data from prior responses
- Log requests and responses in custom manner

These API endpoints will be created in AustinHellerRepo as my needs require, suffixed with PostToApiService. For example, YouTubePostToApiService.

# mitmproxy

[![Continuous Integration Status](https://github.com/mitmproxy/mitmproxy/workflows/CI/badge.svg?branch=main)](https://github.com/mitmproxy/mitmproxy/actions?query=branch%3Amain)
[![Coverage Status](https://shields.mitmproxy.org/codecov/c/github/mitmproxy/mitmproxy/main.svg?label=codecov)](https://codecov.io/gh/mitmproxy/mitmproxy)
[![Latest Version](https://shields.mitmproxy.org/pypi/v/mitmproxy.svg)](https://pypi.python.org/pypi/mitmproxy)
[![Supported Python versions](https://shields.mitmproxy.org/pypi/pyversions/mitmproxy.svg)](https://pypi.python.org/pypi/mitmproxy)

``mitmproxy`` is an interactive, SSL/TLS-capable intercepting proxy with a console
interface for HTTP/1, HTTP/2, and WebSockets.

``mitmdump`` is the command-line version of mitmproxy. Think tcpdump for HTTP.

``mitmweb`` is a web-based interface for mitmproxy.

## Installation

The installation instructions are [here](https://docs.mitmproxy.org/stable/overview-installation).
If you want to install from source, see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Documentation & Help

General information, tutorials, and precompiled binaries can be found on the mitmproxy website.

[![mitmproxy.org](https://shields.mitmproxy.org/badge/https%3A%2F%2F-mitmproxy.org-blue.svg)](https://mitmproxy.org/)

The documentation for mitmproxy is available on our website:

[![mitmproxy documentation stable](https://shields.mitmproxy.org/badge/docs-stable-brightgreen.svg)](https://docs.mitmproxy.org/stable/)
[![mitmproxy documentation dev](https://shields.mitmproxy.org/badge/docs-dev-brightgreen.svg)](https://docs.mitmproxy.org/dev/)

If you have questions on how to use mitmproxy, please
use GitHub Discussions!

[![mitmproxy discussions](https://shields.mitmproxy.org/badge/help-github%20discussions-orange.svg)](https://github.com/mitmproxy/mitmproxy/discussions)

## Contributing

As an open source project, mitmproxy welcomes contributions of all forms.

[![Dev Guide](https://shields.mitmproxy.org/badge/dev_docs-CONTRIBUTING.md-blue)](./CONTRIBUTING.md)

Also, please feel free to join our developer Slack!

[![Slack Developer Chat](https://shields.mitmproxy.org/badge/slack-mitmproxy-E01563.svg)](http://slack.mitmproxy.org/)
