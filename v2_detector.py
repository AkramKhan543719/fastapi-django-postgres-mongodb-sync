import json

from datetime import datetime
from pathlib import Path
from collections import defaultdict

import cv2

from ultralytics import YOLO


# ============================================================
# CONFIGURATION
# ============================================================

VIDEOS_DIR = Path("videos")

OUTPUT_DIR = Path(
    "v2_detection_json"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# MODELS
# ============================================================

POSE_MODEL_NAME = "yolo11n-pose.pt"

OBJECT_MODEL_NAME = "yolo11n.pt"


CONFIDENCE_THRESHOLD = 0.35

FRAME_INTERVAL = 3


# ============================================================
# LOAD MODELS
# ============================================================

print()
print("=" * 70)
print("Loading V2 YOLO models")
print("=" * 70)

print(
    f"Loading pose model: "
    f"{POSE_MODEL_NAME}"
)

pose_model = YOLO(
    POSE_MODEL_NAME
)

print(
    "Pose model loaded."
)

print(
    f"Loading object model: "
    f"{OBJECT_MODEL_NAME}"
)

object_model = YOLO(
    OBJECT_MODEL_NAME
)

print(
    "Object model loaded."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def frame_to_time(
    frame_number,
    fps
):

    if fps <= 0:

        fps = 30.0

    seconds = (
        frame_number / fps
    )

    hours = int(
        seconds // 3600
    )

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(
        seconds % 60
    )

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ============================================================

def distance(
    point1,
    point2
):

    dx = (
        point1[0]
        -
        point2[0]
    )

    dy = (
        point1[1]
        -
        point2[1]
    )

    return (
        (dx * dx + dy * dy)
        ** 0.5
    )


# ============================================================

def clamp_confidence(
    value
):

    return max(
        0.0,
        min(
            1.0,
            float(value)
        )
    )


# ============================================================
# ACTIVITY CLASSIFICATION
# ============================================================

def classify_activity(
    keypoints,
    previous_center,
    current_center
):

    movement = 0.0

    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------

    if (
        previous_center is not None
        and current_center is not None
    ):

        movement = distance(
            previous_center,
            current_center
        )

    # --------------------------------------------------------
    # MOVING
    # --------------------------------------------------------

    if movement >= 12:

        return (
            "moving",
            movement
        )

    # --------------------------------------------------------
    # NO KEYPOINTS
    # --------------------------------------------------------

    if keypoints is None:

        return (
            "standing",
            movement
        )

    if len(keypoints) < 17:

        return (
            "standing",
            movement
        )

    # --------------------------------------------------------
    # POSE ANALYSIS
    # --------------------------------------------------------

    try:

        # COCO keypoints

        left_shoulder = (
            keypoints[5]
        )

        right_shoulder = (
            keypoints[6]
        )

        left_hip = (
            keypoints[11]
        )

        right_hip = (
            keypoints[12]
        )

        left_knee = (
            keypoints[13]
        )

        right_knee = (
            keypoints[14]
        )

        shoulder_y = (
            left_shoulder[1]
            +
            right_shoulder[1]
        ) / 2

        hip_y = (
            left_hip[1]
            +
            right_hip[1]
        ) / 2

        knee_y = (
            left_knee[1]
            +
            right_knee[1]
        ) / 2

        shoulder_to_hip = (
            hip_y
            -
            shoulder_y
        )

        hip_to_knee = (
            knee_y
            -
            hip_y
        )

        # ----------------------------------------------------
        # SITTING
        # ----------------------------------------------------

        if (
            shoulder_to_hip < 70
            and
            hip_to_knee < 80
        ):

            return (
                "sitting",
                movement
            )

    except Exception:

        pass

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return (
        "standing",
        movement
    )


# ============================================================
# FINALIZE ACTIVITY EVENT
# ============================================================

def finalize_activity_event(
    video_name,
    person_id,
    activity,
    start_frame,
    end_frame,
    fps,
    confidence,
    movement_total
):

    duration_frames = (
        end_frame
        -
        start_frame
    )

    duration_seconds = (
        duration_frames / fps
        if fps > 0
        else 0
    )

    return {

        "video_name":
            video_name,

        "person_id":
            person_id,

        "object_id":
            person_id,

        "object_type":
            "person",

        "activity":
            activity,

        "start_time":
            frame_to_time(
                start_frame,
                fps
            ),

        "end_time":
            frame_to_time(
                end_frame,
                fps
            ),

        "duration_seconds":
            round(
                duration_seconds,
                3
            ),

        "start_frame":
            start_frame,

        "end_frame":
            end_frame,

        "confidence":
            round(
                clamp_confidence(
                    confidence
                ),
                4
            ),

        "model_name":
            POSE_MODEL_NAME,

        "total_movement_pixels":
            round(
                movement_total,
                3
            ),

        "created_at":
            datetime.utcnow().isoformat()
    }


# ============================================================
# BUILD PERSON TIMELINES
# ============================================================

def build_persons(
    activity_events
):

    persons = {}

    for event in activity_events:

        person_id = (
            event.get(
                "person_id"
            )
        )

        if person_id is None:

            continue

        if person_id not in persons:

            persons[person_id] = {

                "person_id":
                    person_id,

                "activity_timeline":
                    []
            }

        persons[
            person_id
        ][
            "activity_timeline"
        ].append({

            "activity":
                event[
                    "activity"
                ],

            "start_frame":
                event[
                    "start_frame"
                ],

            "end_frame":
                event[
                    "end_frame"
                ],

            "start_time":
                event[
                    "start_time"
                ],

            "end_time":
                event[
                    "end_time"
                ],

            "duration_seconds":
                event[
                    "duration_seconds"
                ],

            "confidence":
                event[
                    "confidence"
                ],

            "total_movement_pixels":
                event[
                    "total_movement_pixels"
                ]
        })

    # --------------------------------------------------------
    # Sort every person's timeline
    # --------------------------------------------------------

    for person in persons.values():

        person[
            "activity_timeline"
        ].sort(
            key=lambda item:
                item[
                    "start_frame"
                ]
        )

    # --------------------------------------------------------
    # Convert dictionary → list
    # --------------------------------------------------------

    return list(
        persons.values()
    )


# ============================================================
# BUILD SUMMARY
# ============================================================

def build_summary(
    activity_events,
    object_events,
    persons
):

    activity_counts = (
        defaultdict(int)
    )

    object_type_counts = (
        defaultdict(int)
    )

    for event in activity_events:

        activity_counts[
            event["activity"]
        ] += 1

    for event in object_events:

        object_type_counts[
            event["object_type"]
        ] += 1

    vehicle_classes = {

        "car",

        "truck",

        "bus",

        "motorcycle"
    }

    total_vehicles = 0

    for event in object_events:

        if (
            event[
                "object_type"
            ]
            in vehicle_classes
        ):

            total_vehicles += 1

    return {

        "total_unique_persons":
            len(persons),

        "total_activity_events":
            len(activity_events),

        "moving_events":
            activity_counts[
                "moving"
            ],

        "standing_events":
            activity_counts[
                "standing"
            ],

        "sitting_events":
            activity_counts[
                "sitting"
            ],

        "total_objects":
            len(object_events),

        "total_vehicles":
            total_vehicles,

        "object_types":
            dict(
                object_type_counts
            )
    }


# ============================================================
# PROCESS ONE VIDEO
# ============================================================

def process_video(
    video_path
):

    print()
    print("=" * 70)

    print(
        f"Processing V2 video: "
        f"{video_path.name}"
    )

    print("=" * 70)

    cap = cv2.VideoCapture(
        str(video_path)
    )

    if not cap.isOpened():

        print(
            f"ERROR: Cannot open "
            f"{video_path}"
        )

        return

    # ========================================================
    # VIDEO INFORMATION
    # ========================================================

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:

        fps = 30.0

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    video_duration = (
        total_frames / fps
    )

    print(
        f"FPS          : {fps:.2f}"
    )

    print(
        f"Total frames : {total_frames}"
    )

    print(
        f"Duration     : "
        f"{video_duration:.2f} seconds"
    )

    # ========================================================
    # PERSON TRACKING STATE
    # ========================================================

    previous_centers = {}

    active_states = {}

    activity_events = []

    # ========================================================
    # OBJECT TRACKING STATE
    # ========================================================

    object_first_frame = {}

    object_last_frame = {}

    object_confidences = (
        defaultdict(list)
    )

    object_classes = {}

    # ========================================================
    # PROCESSING
    # ========================================================

    frame_number = 0

    while True:

        success, frame = (
            cap.read()
        )

        if not success:

            break

        frame_number += 1

        # ----------------------------------------------------
        # Process every Nth frame
        # ----------------------------------------------------

        if (
            frame_number
            % FRAME_INTERVAL
            != 0
        ):

            continue

        # ====================================================
        # PERSON POSE TRACKING
        # ====================================================

        try:

            pose_results = (
                pose_model.track(

                    frame,

                    persist=True,

                    tracker=
                        "bytetrack.yaml",

                    conf=
                        CONFIDENCE_THRESHOLD,

                    verbose=False
                )
            )

        except Exception as error:

            print(
                f"Pose error at frame "
                f"{frame_number}: "
                f"{error}"
            )

            continue

        # ====================================================
        # PROCESS PERSONS
        # ====================================================

        for result in pose_results:

            if (
                result.boxes
                is None
            ):

                continue

            if (
                result.keypoints
                is None
            ):

                continue

            boxes = (
                result.boxes
            )

            keypoints_data = (
                result
                .keypoints
                .xy
                .cpu()
                .numpy()
            )

            for index, box in enumerate(
                boxes
            ):

                # ------------------------------------------------
                # PERSON CLASS
                # ------------------------------------------------

                class_id = int(
                    box.cls[
                        0
                    ].item()
                )

                if class_id != 0:

                    continue

                # ------------------------------------------------
                # TRACK ID
                # ------------------------------------------------

                if box.id is None:

                    continue

                person_id = int(
                    box.id[
                        0
                    ].item()
                )

                confidence = float(
                    box.conf[
                        0
                    ].item()
                )

                # ------------------------------------------------
                # BOUNDING BOX CENTER
                # ------------------------------------------------

                x1, y1, x2, y2 = (

                    box.xyxy[
                        0
                    ]
                    .cpu()
                    .numpy()
                )

                center = (

                    (
                        float(x1)
                        +
                        float(x2)
                    ) / 2,

                    (
                        float(y1)
                        +
                        float(y2)
                    ) / 2
                )

                # ------------------------------------------------
                # KEYPOINTS
                # ------------------------------------------------

                keypoints = (
                    keypoints_data[
                        index
                    ]
                )

                previous_center = (
                    previous_centers.get(
                        person_id
                    )
                )

                # ------------------------------------------------
                # ACTIVITY
                # ------------------------------------------------

                activity, movement = (
                    classify_activity(

                        keypoints,

                        previous_center,

                        center
                    )
                )

                # ------------------------------------------------
                # UPDATE TRACKING
                # ------------------------------------------------

                previous_centers[
                    person_id
                ] = center

                # =================================================
                # FIRST ACTIVITY
                # =================================================

                if (
                    person_id
                    not in active_states
                ):

                    active_states[
                        person_id
                    ] = {

                        "activity":
                            activity,

                        "start_frame":
                            frame_number,

                        "last_frame":
                            frame_number,

                        "confidence":
                            confidence,

                        "movement":
                            movement
                    }

                    continue

                current_state = (
                    active_states[
                        person_id
                    ]
                )

                # =================================================
                # ACTIVITY CHANGED
                # =================================================

                if (
                    current_state[
                        "activity"
                    ]
                    != activity
                ):

                    activity_events.append(

                        finalize_activity_event(

                            video_path.name,

                            person_id,

                            current_state[
                                "activity"
                            ],

                            current_state[
                                "start_frame"
                            ],

                            current_state[
                                "last_frame"
                            ],

                            fps,

                            current_state[
                                "confidence"
                            ],

                            current_state[
                                "movement"
                            ]
                        )
                    )

                    # ---------------------------------------------
                    # START NEW ACTIVITY
                    # ---------------------------------------------

                    active_states[
                        person_id
                    ] = {

                        "activity":
                            activity,

                        "start_frame":
                            frame_number,

                        "last_frame":
                            frame_number,

                        "confidence":
                            confidence,

                        "movement":
                            movement
                    }

                else:

                    # ---------------------------------------------
                    # CONTINUE SAME ACTIVITY
                    # ---------------------------------------------

                    current_state[
                        "last_frame"
                    ] = frame_number

                    current_state[
                        "movement"
                    ] += movement

                    current_state[
                        "confidence"
                    ] = (

                        (
                            current_state[
                                "confidence"
                            ]
                            +
                            confidence
                        )
                        / 2
                    )

        # ====================================================
        # GENERAL OBJECT DETECTION
        # ====================================================

        try:

            object_results = (
                object_model.track(

                    frame,

                    persist=True,

                    tracker=
                        "bytetrack.yaml",

                    conf=
                        CONFIDENCE_THRESHOLD,

                    verbose=False
                )
            )

        except Exception:

            object_results = []

        # ====================================================
        # PROCESS OBJECTS
        # ====================================================

        for result in object_results:

            if (
                result.boxes
                is None
            ):

                continue

            for box in result.boxes:

                if box.id is None:

                    continue

                object_id = int(
                    box.id[
                        0
                    ].item()
                )

                class_id = int(
                    box.cls[
                        0
                    ].item()
                )

                confidence = float(
                    box.conf[
                        0
                    ].item()
                )

                class_name = (
                    object_model.names[
                        class_id
                    ]
                )

                # ------------------------------------------------
                # PERSON ALREADY HANDLED BY POSE MODEL
                # ------------------------------------------------

                if (
                    class_name
                    == "person"
                ):

                    continue

                # ------------------------------------------------
                # FIRST APPEARANCE
                # ------------------------------------------------

                if (
                    object_id
                    not in object_first_frame
                ):

                    object_first_frame[
                        object_id
                    ] = frame_number

                # ------------------------------------------------
                # LAST APPEARANCE
                # ------------------------------------------------

                object_last_frame[
                    object_id
                ] = frame_number

                object_classes[
                    object_id
                ] = class_name

                object_confidences[
                    object_id
                ].append(
                    confidence
                )

        # ====================================================
        # PROGRESS
        # ====================================================

        if (
            frame_number % 150
            == 0
        ):

            print(
                f"Processed frame "
                f"{frame_number}/"
                f"{total_frames}"
            )

    cap.release()

    # ========================================================
    # FINALIZE REMAINING PERSON EVENTS
    # ========================================================

    for person_id, state in (
        active_states.items()
    ):

        activity_events.append(

            finalize_activity_event(

                video_path.name,

                person_id,

                state[
                    "activity"
                ],

                state[
                    "start_frame"
                ],

                state[
                    "last_frame"
                ],

                fps,

                state[
                    "confidence"
                ],

                state[
                    "movement"
                ]
            )
        )

    # ========================================================
    # CREATE OBJECT EVENTS
    # ========================================================

    object_events = []

    for object_id in (
        object_first_frame
    ):

        start_frame = (
            object_first_frame[
                object_id
            ]
        )

        end_frame = (
            object_last_frame[
                object_id
            ]
        )

        confidences = (
            object_confidences[
                object_id
            ]
        )

        average_confidence = (

            sum(confidences)
            /
            len(confidences)

            if confidences

            else 0.0
        )

        object_events.append({

            "object_id":
                object_id,

            "object_type":
                object_classes[
                    object_id
                ],

            "start_frame":
                start_frame,

            "end_frame":
                end_frame,

            "frame_number":
                end_frame,

            "start_time":
                frame_to_time(
                    start_frame,
                    fps
                ),

            "end_time":
                frame_to_time(
                    end_frame,
                    fps
                ),

            "duration_seconds":
                round(

                    (
                        end_frame
                        -
                        start_frame
                    )
                    / fps,

                    3
                ),

            "confidence":
                round(
                    average_confidence,
                    4
                ),

            "model_name":
                OBJECT_MODEL_NAME,

            "created_at":
                datetime.utcnow()
                .isoformat()
        })

    # ========================================================
    # BUILD PERSON STRUCTURE
    # ========================================================

    persons = build_persons(
        activity_events
    )

    # ========================================================
    # BUILD SUMMARY
    # ========================================================

    summary = build_summary(

        activity_events,

        object_events,

        persons
    )

    # ========================================================
    # PROCESSING INFORMATION
    # ========================================================

    processing = {

        "status":
            "completed",

        "processor_version":
            "V2",

        "created_at":
            datetime.utcnow()
            .isoformat()
    }

    # ========================================================
    # FINAL V2 JSON
    # ========================================================

    payload = {

        # ----------------------------------------------------
        # VIDEO INFORMATION
        # ----------------------------------------------------

        "video_info": {

            "video_name":
                video_path.name,

            "model_name":
                POSE_MODEL_NAME,

            "object_model":
                OBJECT_MODEL_NAME,

            "fps":
                round(
                    fps,
                    3
                ),

            "total_frames":
                total_frames,

            "duration_seconds":
                round(
                    video_duration,
                    3
                )
        },

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        "summary":
            summary,

        # ----------------------------------------------------
        # PERSON TIMELINES
        # ----------------------------------------------------

        "persons":
            persons,

        # ----------------------------------------------------
        # OBJECT EVENTS
        # ----------------------------------------------------

        "object_events":
            object_events,

        # ----------------------------------------------------
        # ORIGINAL ACTIVITY EVENTS
        # ----------------------------------------------------

        "activity_events":
            activity_events,

        # ----------------------------------------------------
        # PROCESSING
        # ----------------------------------------------------

        "processing":
            processing
    }

    # ========================================================
    # SAVE JSON
    # ========================================================

    output_file = (

        OUTPUT_DIR
        /
        f"{video_path.stem}_v2.json"
    )

    with open(

        output_file,

        "w",

        encoding="utf-8"
    ) as file:

        json.dump(

            payload,

            file,

            indent=4
        )

    # ========================================================
    # CONSOLE OUTPUT
    # ========================================================

    print()
    print("=" * 70)

    print(
        f"V2 completed: "
        f"{video_path.name}"
    )

    print(
        f"Unique persons: "
        f"{len(persons)}"
    )

    print(
        f"Activity events: "
        f"{len(activity_events)}"
    )

    print(
        f"Object events: "
        f"{len(object_events)}"
    )

    print(
        f"JSON: "
        f"{output_file}"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    video_files = sorted(

        VIDEOS_DIR.glob(
            "*.mp4"
        )
    )

    if not video_files:

        print(
            "No MP4 videos found."
        )

        raise SystemExit

    print()
    print(
        f"Found "
        f"{len(video_files)} video(s)."
    )

    for video_file in (
        video_files
    ):

        process_video(
            video_file
        )

    print()
    print("=" * 70)

    print(
        "ALL V2 VIDEO PROCESSING COMPLETED"
    )

    print("=" * 70)