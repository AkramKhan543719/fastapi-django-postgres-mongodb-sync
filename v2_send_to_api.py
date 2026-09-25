import json

import requests

from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = (
    "http://127.0.0.1:8000"
    "/api/v2/activity-events"
)

JSON_DIR = Path(
    "v2_detection_json"
)


# ============================================================
# SEND ONE JSON FILE
# ============================================================

def send_json_file(
    json_file
):

    print()
    print(
        "=" * 70
    )

    print(
        f"Sending: "
        f"{json_file.name}"
    )

    print(
        "=" * 70
    )

    try:

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as file:

            payload = json.load(
                file
            )

        response = requests.post(

            API_URL,

            json=payload,

            timeout=120
        )

        if response.status_code == 201:

            data = response.json()

            print(
                "SUCCESS"
            )

            print(
                f"Activity events: "
                f"{data.get('activity_events', 0)}"
            )

            print(
                f"Object events: "
                f"{data.get('object_events', 0)}"
            )

            print(
                f"Database IDs: "
                f"{len(data.get('event_ids', []))}"
            )

            return True

        print(
            "FAILED"
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            response.text
        )

        return False

    except requests.RequestException as error:

        print(
            "REQUEST ERROR:"
        )

        print(
            error
        )

        return False

    except Exception as error:

        print(
            "ERROR:"
        )

        print(
            error
        )

        return False


# ============================================================
# MAIN
# ============================================================

def send_all_json_files():

    if not JSON_DIR.exists():

        print(
            f"Directory not found: "
            f"{JSON_DIR}"
        )

        return

    json_files = sorted(
        JSON_DIR.glob(
            "*_v2.json"
        )
    )

    if not json_files:

        print(
            "No V2 JSON files found."
        )

        return

    print()
    print(
        f"Found "
        f"{len(json_files)} V2 JSON file(s)."
    )

    successful = 0

    failed = 0

    for json_file in json_files:

        if send_json_file(
            json_file
        ):

            successful += 1

        else:

            failed += 1

    print()
    print(
        "=" * 70
    )

    print(
        "V2 JSON UPLOAD COMPLETED"
    )

    print(
        "=" * 70
    )

    print(
        f"Files processed : "
        f"{len(json_files)}"
    )

    print(
        f"Successful      : "
        f"{successful}"
    )

    print(
        f"Failed          : "
        f"{failed}"
    )

    print(
        "=" * 70
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    send_all_json_files()