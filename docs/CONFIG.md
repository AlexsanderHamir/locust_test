# Load Test Configuration

Each Locust scenario is configured exclusively through environment variables. This document lists all supported variables, grouped by scope, along with their defaults and usage.

## Global / Shared Variables

These apply across scripts when set:

- `LOCUST_API_KEY` *(required)* – API key used for Authorization header in every user class.

## Chat Completions Scenario (`load_tests/chat-completions_load-test.py`)

- `LOCUST_CHAT_MODEL` (default `db-openai-endpoint`)
- `LOCUST_CHAT_ENDPOINT` (default `chat/completions`)
- `LOCUST_CHAT_USER` (default `my-new-end-user-1`)
- `LOCUST_CHAT_MESSAGE_TEMPLATE`
  - Default: `{uuid} This is a test there will be no cache hits and we'll fill up the context`
  - `uuid` placeholder is replaced with a unique value per request.
- `LOCUST_CHAT_MESSAGE_REPEAT` (default `150`)
- `LOCUST_CHAT_DURATION_SECONDS` (default `60`)
- `LOCUST_CHAT_USER_COUNT` (default `1`)
- `LOCUST_CHAT_SPAWN_RATE` (default `1.0`)
- `LOCUST_CHAT_HOST` (default `https://litellm-automated-performance-testing.onrender.com/`)

## Embeddings Scenario (`load_tests/embeddings_load-test.py`)

- `LOCUST_EMBEDDINGS_MODEL` (default `text-embedding-3-large`)
- `LOCUST_EMBEDDINGS_ENDPOINT` (default `embeddings`)
- `LOCUST_EMBEDDINGS_USER` (default `my-new-end-user-1`)
- `LOCUST_EMBEDDINGS_MESSAGE_TEMPLATE`
  - Default: `{uuid} This is a test there will be no cache hits and we'll fill up the context`
- `LOCUST_EMBEDDINGS_MESSAGE_REPEAT` (default `150`)
- `LOCUST_EMBEDDINGS_DURATION_SECONDS` (default `60`)
- `LOCUST_EMBEDDINGS_USER_COUNT` (default `1`)
- `LOCUST_EMBEDDINGS_SPAWN_RATE` (default `1.0`)
- `LOCUST_EMBEDDINGS_HOST` (default `https://litellm-automated-performance-testing.onrender.com/`)

## Responses Scenario (`load_tests/responses_load-test.py`)

- `LOCUST_RESPONSES_MODEL` (default `gpt-5-codex`)
- `LOCUST_RESPONSES_ENDPOINT` (default `v1/responses`)
- `LOCUST_RESPONSES_USER` (default `my-new-end-user-1`)
- `LOCUST_RESPONSES_PROMPT_TEMPLATE`
  - Default: `System: You are a helpful assistant.\nUser: Ping {uuid} respond with a short acknowledgement.`
- `LOCUST_RESPONSES_PROMPT_REPEAT` (default `1`)
- `LOCUST_RESPONSES_DURATION_SECONDS` (default `60`)
- `LOCUST_RESPONSES_USER_COUNT` (default `1`)
- `LOCUST_RESPONSES_SPAWN_RATE` (default `1.0`)
- `LOCUST_RESPONSES_HOST` (default `https://litellm-automated-performance-testing.onrender.com/`)



