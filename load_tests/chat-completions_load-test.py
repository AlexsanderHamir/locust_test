import os
import json
import uuid
import sys
from pathlib import Path

from locust import HttpUser, task, between, events

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from helpers.load_test_helper import resolve_host, run_locust_load_test

# Configuration
CHAT_MODEL = os.environ.get("LOCUST_CHAT_MODEL", "db-openai-endpoint")
CHAT_ENDPOINT = os.environ.get("LOCUST_CHAT_ENDPOINT", "chat/completions")
CHAT_USER = os.environ.get("LOCUST_CHAT_USER", "my-new-end-user-1")
CHAT_MESSAGE_TEMPLATE = os.environ.get(
    "LOCUST_CHAT_MESSAGE_TEMPLATE",
    "{uuid} This is a test there will be no cache hits and we'll fill up the context",
)
CHAT_MESSAGE_REPEAT = int(os.environ.get("LOCUST_CHAT_MESSAGE_REPEAT", "150"))

# Custom metric to track LiteLLM overhead duration
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
                # Report as custom metric
                events.request.fire(
                    request_type="Custom",
                    name="LiteLLM Overhead Duration (ms)",
                    response_time=duration_ms,
                    response_length=0,
                )
            except (ValueError, TypeError):
                pass


class MyUser(HttpUser):
    wait_time = between(0.5, 1)  # Random wait time between requests

    def on_start(self):
        api_key = os.environ.get("LOCUST_API_KEY")
        if not api_key:
            raise RuntimeError("LOCUST_API_KEY environment variable is required.")
        self.api_key = api_key
        self.client.headers.update({"Authorization": f"Bearer {self.api_key}"})

    @task
    def litellm_completion(self):
        # no cache hits with this
        content = CHAT_MESSAGE_TEMPLATE.format(uuid=uuid.uuid4()) * CHAT_MESSAGE_REPEAT
        payload = {
            "model": CHAT_MODEL,
            "messages": [{"role": "user", "content": content}],
            "user": CHAT_USER,
        }
        response = self.client.post(CHAT_ENDPOINT, json=payload)

        if response.status_code != 200:
            # log the errors in error.txt
            with open("error.txt", "a") as error_log:
                error_log.write(response.text + "\n")


if __name__ == "__main__":
    duration = int(os.environ.get("LOCUST_CHAT_DURATION_SECONDS", "60"))
    users = int(os.environ.get("LOCUST_CHAT_USER_COUNT", "1"))
    spawn = float(os.environ.get("LOCUST_CHAT_SPAWN_RATE", "1.0"))
    host = resolve_host(None, "LOCUST_CHAT_HOST")

    stats_summary = run_locust_load_test(
        duration_seconds=duration,
        user_count=users,
        spawn_rate=spawn,
        host=host,
        user_classes=[MyUser],
        events=events,
        overhead_durations=overhead_durations,
    )

    print(json.dumps(stats_summary, indent=2))


