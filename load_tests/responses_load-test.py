import os
import json
import uuid
import sys
from pathlib import Path

from locust import HttpUser, task, between, events

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from helpers.load_test_helper import run_locust_load_test

RESPONSES_MODEL = os.environ.get("LOCUST_RESPONSES_MODEL", "gpt-5-codex")
RESPONSES_ENDPOINT = os.environ.get("LOCUST_RESPONSES_ENDPOINT", "v1/responses")
RESPONSES_USER = os.environ.get("LOCUST_RESPONSES_USER", "my-new-end-user-1")
RESPONSES_PROMPT_TEMPLATE = os.environ.get(
    "LOCUST_RESPONSES_PROMPT_TEMPLATE",
    "System: You are a helpful assistant.\nUser: Ping {uuid} respond with a short acknowledgement.",
)
RESPONSES_PROMPT_REPEAT = int(os.environ.get("LOCUST_RESPONSES_PROMPT_REPEAT", "1"))

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


class ResponsesUser(HttpUser):
    wait_time = between(0.5, 1)

    def on_start(self):
        api_key = os.environ.get("LOCUST_API_KEY")
        if not api_key:
            raise RuntimeError("LOCUST_API_KEY environment variable is required.")
        self.api_key = api_key
        self.client.headers.update({"Authorization": f"Bearer {self.api_key}"})

    @task
    def litellm_responses(self):
        prompt = RESPONSES_PROMPT_TEMPLATE.format(uuid=uuid.uuid4()) * RESPONSES_PROMPT_REPEAT

        payload = {
            "model": RESPONSES_MODEL,
            "input": prompt,
            "user": RESPONSES_USER,
        }

        response = self.client.post(RESPONSES_ENDPOINT, json=payload)

        if response.status_code == 200:
            data = response.json()

            output_text = ""
            if "output" in data:
                try:
                    output_text = data["output"][0]["content"][0]["text"]
                except (IndexError, KeyError):
                    output_text = str(data["output"])
            print("Response:", output_text)
        else:
            with open("error.txt", "a") as error_log:
                error_log.write(response.text + "\n")


if __name__ == "__main__":
    duration = int(os.environ.get("LOCUST_RESPONSES_DURATION_SECONDS", "60"))
    users = int(os.environ.get("LOCUST_RESPONSES_USER_COUNT", "1"))
    spawn = float(os.environ.get("LOCUST_RESPONSES_SPAWN_RATE", "1.0"))
    host = os.environ.get(
        "LOCUST_RESPONSES_HOST",
         
    )

    stats_summary = run_locust_load_test(
        duration_seconds=duration,
        user_count=users,
        spawn_rate=spawn,
        host=host,
        user_classes=[ResponsesUser],
        events=events,
        overhead_durations=overhead_durations,
    )

    print(json.dumps(stats_summary, indent=2))


