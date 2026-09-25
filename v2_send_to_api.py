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
# CONVERT PROCESSOR JSON → API JSON
# ============================================================

def convert_payload(raw_payload):

    # --------------------------------------------------------
    # VIDEO INFORMATION
    # --------------------------------------------------------

    video_info = raw_payload.get(
        "video_info",
        {}
    )

    video_name = video_info.get(
        "video_name"
    )

    video_duration_seconds = video_info.get(
        "duration_seconds",
        0
    )

    if not video_name:

        raise ValueError(
            "video_info.video_name missing"
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = raw_payload.get(
        "summary",
        {}
    )

    # --------------------------------------------------------
    # PERSONS
    # --------------------------------------------------------

    persons = []

    for person in raw_payload.get(
        "persons",
        []
    ):

        person_id = person.get(
            "person_id"
        )

        activity_timeline = person.get(
            "activity_timeline",
            []
        )

        activities = []

        for activity in activity_timeline:

            activities.append({

                "activity":
                    activity.get(
                        "activity",
                        "unknown"
                    ),

                "start_time":
                    activity.get(
                        "start_time",
                        "00:00:00"
                    ),

                "end_time":
                    activity.get(
                        "end_time",
                        "00:00:00"
                    ),

                "duration_seconds":
                    activity.get(
                        "duration_seconds",
                        0
                    ),

                "start_frame":
                    activity.get(
                        "start_frame"
                    ),

                "end_frame":
                    activity.get(
                        "end_frame"
                    ),

                "confidence":
                    activity.get(
                        "confidence",
                        0
                    ),

                "model_name":
                    video_info.get(
                        "model_name"
                    ),

                "total_movement_pixels":
                    activity.get(
                        "total_movement_pixels",
                        0
                    )

            })

        persons.append({

            "person_id":
                person_id,

            "activities":
                activities

        })

    # --------------------------------------------------------
    # FINAL API PAYLOAD
    # --------------------------------------------------------

    api_payload = {

        "video_name":
            video_name,

        "video_duration_seconds":
            video_duration_seconds,

        "summary":
            summary,

        "persons":
            persons

    }

    return api_payload


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
        f"Sending: {json_file.name}"
    )

    print(
        "=" * 70
    )

    try:

        # ----------------------------------------------------
        # READ PROCESSOR JSON
        # ----------------------------------------------------

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as file:

            raw_payload = json.load(
                file
            )

        # ----------------------------------------------------
        # CONVERT JSON FORMAT
        # ----------------------------------------------------

        payload = convert_payload(
            raw_payload
        )

        # ----------------------------------------------------
        # PRINT BASIC INFORMATION
        # ----------------------------------------------------

        print(
            f"Video: "
            f"{payload['video_name']}"
        )

        print(
            f"Persons: "
            f"{len(payload['persons'])}"
        )

        total_activities = sum(

            len(
                person["activities"]
            )

            for person in payload["persons"]

        )

        print(
            f"Activities: "
            f"{total_activities}"
        )

        # ----------------------------------------------------
        # SEND REQUEST
        # ----------------------------------------------------

        response = requests.post(

            API_URL,

            json=payload,

            timeout=120

        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if response.status_code == 201:

            data = response.json()

            print()
            print(
                "SUCCESS"
            )

            print(
                f"Video: "
                f"{data.get('video_name')}"
            )

            print(
                f"Persons received: "
                f"{data.get('persons_received', 0)}"
            )

            print(
                f"Activities received: "
                f"{data.get('activities_received', 0)}"
            )

            print(
                f"Activities inserted: "
                f"{data.get('activities_inserted', 0)}"
            )

            print(
                f"Duplicates skipped: "
                f"{data.get('skipped_duplicates', 0)}"
            )

            print(
                f"Database IDs: "
                f"{len(data.get('event_ids', []))}"
            )

            return True

        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        print()
        print(
            "FAILED"
        )

        print(
            "HTTP Status:",
            response.status_code
        )

        print(
            "API Response:"
        )

        print(
            response.text
        )

        return False

    except requests.RequestException as error:

        print()
        print(
            "REQUEST ERROR:"
        )

        print(
            error
        )

        return False

    except Exception as error:

        print()
        print(
            "ERROR:"
        )

        print(
            error
        )

        return False


# ============================================================
# SEND ALL JSON FILES
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