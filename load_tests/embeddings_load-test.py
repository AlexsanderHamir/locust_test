import json
import os
import uuid
import sys
from pathlib import Path

from locust import HttpUser, task, between, events

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from helpers.load_test_helper import run_locust_load_test

EMBEDDINGS_MODEL = os.environ.get("LOCUST_EMBEDDINGS_MODEL", "db-openai-endpoint")
EMBEDDINGS_ENDPOINT = os.environ.get("LOCUST_EMBEDDINGS_ENDPOINT", "embeddings")
EMBEDDINGS_USER = os.environ.get("LOCUST_EMBEDDINGS_USER", "my-new-end-user-1")
EMBEDDINGS_MESSAGE_TEMPLATE = os.environ.get(
    "LOCUST_EMBEDDINGS_MESSAGE_TEMPLATE",
    "{uuid} This is a test there will be no cache hits and we'll fill up the context",
)
EMBEDDINGS_MESSAGE_REPEAT = int(os.environ.get("LOCUST_EMBEDDINGS_MESSAGE_REPEAT", "150"))

overhead_durations = []


@events.request.add_listener
def on_request(**kwargs):
    response = kwargs.get("response")
    if response and hasattr(response, "headers") and response.headers:
        overhead_duration = response.headers.get("x-litellm-overhead-duration-ms")
        if overhead_duration:
            try:
                duration_ms = float(overhead_duration)
                overhead_durations.append(duration_ms)
                events.request.fire(
                    request_type="Custom",
                    name="LiteLLM Overhead Duration (ms)",
                    response_time=duration_ms,
                    response_length=0,
                )
            except (ValueError, TypeError):
                pass


class EmbeddingsUser(HttpUser):
    wait_time = between(0.5, 1)

    def on_start(self):
        api_key = os.environ.get("LOCUST_API_KEY")
        if not api_key:
            raise RuntimeError("LOCUST_API_KEY environment variable is required.")
        self.api_key = api_key
        self.client.headers.update({"Authorization": f"Bearer {self.api_key}"})

    @task
    def litellm_embeddings(self):
        content = EMBEDDINGS_MESSAGE_TEMPLATE.format(uuid=uuid.uuid4()) * EMBEDDINGS_MESSAGE_REPEAT
        payload = {
            "model": EMBEDDINGS_MODEL,
            "input": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "user": EMBEDDINGS_USER,
        }
        response = self.client.post(EMBEDDINGS_ENDPOINT, json=payload)

        if response.status_code != 200:
            with open("error.txt", "a") as error_log:
                error_log.write(response.text + "\n")


if __name__ == "__main__":
    duration = int(os.environ.get("LOCUST_EMBEDDINGS_DURATION_SECONDS", "60"))
    users = int(os.environ.get("LOCUST_EMBEDDINGS_USER_COUNT", "1"))
    spawn = float(os.environ.get("LOCUST_EMBEDDINGS_SPAWN_RATE", "1.0"))
    host = os.environ.get(
        "LOCUST_EMBEDDINGS_HOST",
         
    )

    stats_summary = run_locust_load_test(
        duration_seconds=duration,
        user_count=users,
        spawn_rate=spawn,
        host=host,
        user_classes=[EmbeddingsUser],
        events=events,
        overhead_durations=overhead_durations,
    )

    print(json.dumps(stats_summary, indent=2))


