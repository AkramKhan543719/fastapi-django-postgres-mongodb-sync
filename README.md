# FastAPI + Django + PostgreSQL + MongoDB AI Detection Pipeline — V2

## AI Video Detection, Human Activity Tracking & Database Synchronization

A production-oriented computer vision pipeline that processes video using YOLO-based detection and pose estimation, tracks detected persons and objects, converts continuous observations into meaningful activity events, stores structured events in PostgreSQL through FastAPI, and synchronizes the stored data to MongoDB through Django.

V2 extends the original V1 detection pipeline with **human activity analysis, person tracking, activity timelines, object events, structured JSON generation, duplicate-event protection, and PostgreSQL → MongoDB synchronization**.


### Project

**FastAPI + Django + PostgreSQL + MongoDB AI Detection Pipeline — V2**

### Project Focus

* Computer Vision
* YOLO-based Object Detection
* Human Activity Tracking
* Person Tracking and Identification
* FastAPI Backend Development
* PostgreSQL Data Storage
* Django Backend Synchronization
* MongoDB Data Management
* Event Deduplication
* AI Video Analytics

### Technologies

`Python` · `YOLO` · `FastAPI` · `Django` · `PostgreSQL` · `MongoDB` · `SQLAlchemy` · `Pydantic` · `Git` · `GitHub`


---

## 1. Overview

Traditional object detection produces repeated frame-level observations:

```text
Frame 100 → Person detected
Frame 101 → Person detected
Frame 102 → Person detected
Frame 103 → Person detected
...
```

While useful for computer vision inference, this format is not ideal for analytics.

V2 converts those repeated observations into meaningful events:

```text
Person 1
Activity: Sitting
Start: 00:00:05
End:   00:00:15
Duration: 10 seconds
```

Therefore, V2 answers questions such as:

* Which person was detected?
* What activity were they performing?
* When did the activity start?
* When did it end?
* How long did it continue?
* Which frame range represents the activity?
* What other objects were detected?
* Has the same event already been stored?
* Has the PostgreSQL record already been synchronized to MongoDB?

---

# 2. V1 → V2 Evolution

## V1

The original pipeline primarily focused on object detection and database storage:

```text
VIDEO
  ↓
YOLO Detection
  ↓
Detection JSON
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
Django
  ↓
MongoDB
```

V1 primarily answered:

> What objects were detected?

---

## V2

V2 introduces temporal activity analysis and tracking:

```text
VIDEO
  ↓
YOLO Detection / Pose Estimation
  ↓
Object Detection
  ↓
Person Tracking
  ↓
Person ID
  ↓
Movement / Pose Analysis
  ↓
Activity Classification
  ├── Moving
  ├── Standing
  └── Sitting
  ↓
Activity Event Generation
  ↓
V2 JSON
  ↓
FastAPI V2
  ↓
Event Hash / Duplicate Protection
  ↓
PostgreSQL
  ↓
Django Synchronization
  ↓
MongoDB
```

V2 therefore changes the system from a **frame-detection pipeline** into a **time-based activity-event pipeline**.

---

# 3. Complete System Architecture

```text
                         ┌─────────────────────┐
                         │       VIDEO         │
                         │   MP4 / Input       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌──────────────────────────┐
                    │       V2 PROCESSOR       │
                    │                          │
                    │ YOLO Detection           │
                    │ Pose Estimation          │
                    │ Person Tracking          │
                    │ Movement Analysis         │
                    │ Activity Classification  │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
             ┌──────────────┐         ┌──────────────┐
             │    PERSONS   │         │    OBJECTS   │
             └──────┬───────┘         └──────┬───────┘
                    │                        │
                    ▼                        │
             ┌──────────────┐                │
             │ PERSON ID    │                │
             │ TRACKING     │                │
             └──────┬───────┘                │
                    │                        │
                    ▼                        │
             ┌──────────────┐                │
             │   ACTIVITY   │                │
             │   ANALYSIS   │                │
             └──────┬───────┘                │
                    │                        │
          ┌─────────┼─────────┐              │
          ▼         ▼         ▼              │
       MOVING   STANDING   SITTING           │
          │         │         │              │
          └─────────┼─────────┘              │
                    │                        │
                    ▼                        ▼
             ┌────────────────────────────────┐
             │        EVENT GENERATION        │
             │                                │
             │ Start Frame                    │
             │ End Frame                      │
             │ Start Time                     │
             │ End Time                       │
             │ Duration                       │
             │ Confidence                     │
             └───────────────┬────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     V2 JSON     │
                    │                 │
                    │ Activity Events │
                    │ Object Events   │
                    │ Summary         │
                    │ Metadata        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    FASTAPI V2   │
                    │                 │
                    │ POST            │
                    │ /api/v2/        │
                    │ activity-events │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ EVENT HASH      │
                    │ DUPLICATE CHECK │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                  NEW              EXISTING
                    │                 │
                    ▼                 ▼
                 INSERT              SKIP
                    │
                    ▼
              ┌──────────────┐
              │ PostgreSQL   │
              │              │
              │ detection_   │
              │ events       │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │    Django    │
              │ Synchronizer │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │   MongoDB    │
              │              │
              │ Synchronized │
              │ Documents    │
              └──────────────┘
```

---

# 4. V2 Processing Pipeline

## Step 1 — Video Input

The processor receives video files such as:

```text
video1.mp4
video2.mp4
video3.mp4
```

The video is read frame-by-frame.

---

## Step 2 — YOLO Detection / Pose Estimation

The YOLO-based models analyze the video frames.

The pipeline can identify humans and other scene objects.

Typical object categories can include:

```text
person
car
bus
truck
motorcycle
bicycle
```

For human detections, additional tracking and activity analysis are performed.

---

# 5. Person Tracking

Detected people are associated with tracking identities.

For example:

```text
Frame 100 → Person 1
Frame 101 → Person 1
Frame 102 → Person 1
Frame 103 → Person 1
```

If the person's activity changes:

```text
Person 1
   │
   ├── Standing
   │
   ├── Moving
   │
   └── Sitting
```

the activity events remain associated with the tracked person during that processing run.

### Important distinction

Person tracking and database duplicate protection solve different problems.

**Tracking ID:**

> Which detections belong to the same person across frames?

**Event hash:**

> Has this exact event already been stored in the database?

---

# 6. Activity Classification

V2 classifies human activity into three primary states:

```text
MOVING
STANDING
SITTING
```

The activity state is determined using the tracking and movement/pose information available during processing.

---

## Moving

Example:

```text
Person 1
Activity: Moving

00:00:05 ───────── 00:00:12
```

---

## Standing

Example:

```text
Person 1
Activity: Standing

00:00:12 ───────── 00:00:20
```

---

## Sitting

Example:

```text
Person 1
Activity: Sitting

00:00:20 ───────── 00:00:35
```

---

# 7. Activity Event Generation

Instead of generating one database event for every frame, continuous activity is grouped into an activity interval.

For example:

```text
Frame 150 → Sitting
Frame 151 → Sitting
Frame 152 → Sitting
...
Frame 450 → Sitting
```

becomes:

```json
{
    "person_id": 1,
    "activity": "sitting",
    "start_frame": 150,
    "end_frame": 450,
    "start_time": "00:00:05",
    "end_time": "00:00:15",
    "duration_seconds": 10
}
```

This makes the data more meaningful for analytics and reduces unnecessary repetition.

---

# 8. Activity Event Schema

A V2 activity event contains information such as:

| Field                   | Description                 |
| ----------------------- | --------------------------- |
| `video_name`            | Source video                |
| `person_id`             | Tracked person identifier   |
| `object_id`             | Optional object identifier  |
| `object_type`           | Detected object class       |
| `activity`              | Moving, standing or sitting |
| `start_time`            | Activity start time         |
| `end_time`              | Activity end time           |
| `duration_seconds`      | Duration of activity        |
| `start_frame`           | First frame of activity     |
| `end_frame`             | Last frame of activity      |
| `confidence`            | Detection confidence        |
| `model_name`            | Model used                  |
| `total_movement_pixels` | Measured movement           |
| `created_at`            | Event creation time         |

---

# 9. Object Events

V2 also stores detections for non-human objects.

Example:

```json
{
    "object_type": "car",
    "object_id": 4,
    "frame_number": 420,
    "confidence": 0.91
}
```

This allows the pipeline to retain broader scene information rather than focusing only on people.

---

# 10. V2 JSON

Each processed video generates a V2 JSON file.

Example:

```json
{
    "video_name": "office_activity.mp4",
    "model_name": "yolo11n-pose",
    "object_model": "YOLO",
    "fps": 30,
    "total_frames": 900,
    "duration_seconds": 30,
    "summary": {
        "total_persons": 4,
        "moving": 2,
        "standing": 1,
        "sitting": 1
    },
    "activity_events": [
        {
            "video_name": "office_activity.mp4",
            "person_id": 1,
            "object_type": "person",
            "activity": "sitting",
            "start_time": "00:00:05",
            "end_time": "00:00:15",
            "duration_seconds": 10,
            "start_frame": 150,
            "end_frame": 450,
            "confidence": 0.94,
            "model_name": "yolo11n-pose",
            "total_movement_pixels": 12.5
        }
    ],
    "object_events": [],
    "created_at": "2026-09-25T10:00:00"
}
```

---

# 11. V2 Output

Generated JSON files are stored in:

```text
v2_detection_json/
```

Example:

```text
v2_detection_json/
│
├── video1_v2.json
├── video2_v2.json
├── video3_v2.json
├── video4_v2.json
├── video5_v2.json
└── video6_v2.json
```

---

# 12. FastAPI V2

FastAPI acts as the ingestion layer between the V2 processor and PostgreSQL.

### Main endpoint

```http
POST /api/v2/activity-events
```

### Test endpoint

```http
GET /api/v2/activity-events/test
```

Example response:

```json
{
    "message": "Detection API v2 is working",
    "version": "v2"
}
```

### API responsibilities

FastAPI is responsible for:

1. Receiving V2 JSON.
2. Validating the payload.
3. Processing activity events.
4. Processing object events.
5. Generating event hashes.
6. Checking for existing events.
7. Inserting new events.
8. Skipping duplicates.
9. Returning database IDs and processing statistics.

---

# 13. PostgreSQL

The primary event table is:

```text
detection_events
```

Important columns include:

```text
id
video_name
event_type
class_name
confidence
timestamp
frame_number
json_data
created_at
sync_status
synced_at
event_hash
```

### Event types

V2 primarily uses:

```text
activity_event
object_detection_v2
```

---

# 14. Duplicate Event Protection

One of the major V2 improvements is event-level duplicate protection.

Each event receives a SHA-256 fingerprint.

Conceptually:

```text
Video Name
     +
Event Type
     +
Event JSON
     │
     ▼
 SHA-256
     │
     ▼
event_hash
```

The resulting hash is stored in PostgreSQL.

---

## Duplicate Detection Flow

```text
             Incoming Event
                    │
                    ▼
             Generate Hash
                    │
                    ▼
          Search event_hash
                    │
             ┌──────┴──────┐
             │             │
             ▼             ▼
           EXISTS        NOT FOUND
             │             │
             ▼             ▼
            SKIP         INSERT
             │             │
             └──────┬──────┘
                    ▼
                Response
```

Therefore:

```text
First submission
       ↓
INSERT

Same event submitted again
       ↓
Same event_hash
       ↓
DUPLICATE
       ↓
SKIP
```

This prevents the API from repeatedly inserting the same event when the same generated JSON is submitted more than once.

---

# 15. Person Tracking vs Duplicate Protection

These mechanisms should not be confused.

### Person tracking

Handles identity across frames:

```text
Frame 100 → Person 1
Frame 101 → Person 1
Frame 102 → Person 1
```

### Event hashing

Handles database duplication:

```text
Submission 1 → INSERT
Submission 2 → SAME HASH → SKIP
```

Both are required for a reliable activity-processing pipeline.

---

# 16. Django Synchronization

Django acts as the synchronization layer between PostgreSQL and MongoDB.

The flow is:

```text
PostgreSQL
     │
     │ sync_status = PENDING
     ▼
Django Management Command
     │
     ▼
Read pending records
     │
     ▼
Insert into MongoDB
     │
     ▼
Successful?
    / \
  YES  NO
   │    │
   ▼    ▼
SYNCED FAILED
```

The command is:

```bash
python manage.py sync_postgres_to_mongo
```

---

# 17. Synchronization Status

Each event has a synchronization state.

### PENDING

The event has not yet been successfully synchronized.

```text
sync_status = PENDING
```

### SYNCED

The event has successfully reached MongoDB.

```text
sync_status = SYNCED
```

### FAILED

Synchronization encountered an error.

```text
sync_status = FAILED
```

---

# 18. MongoDB

MongoDB acts as the downstream document-oriented database.

The synchronized data can be used for:

* Activity analytics
* Object analytics
* Video analytics
* Reporting
* Dashboards
* Future AI/ML processing
* Flexible event queries

---

# 19. End-to-End Architecture

```text
                         VIDEO
                           │
                           ▼
                  YOLO / POSE MODEL
                           │
                           ▼
                    OBJECT DETECTION
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
           PERSONS                    OBJECTS
              │                         │
              ▼                         │
        PERSON TRACKING                 │
              │                         │
              ▼                         │
        PERSON ID                      │
              │                         │
              ▼                         │
       MOVEMENT / POSE                 │
              │                         │
       ┌──────┼──────┐                  │
       ▼      ▼      ▼                  │
    MOVING STANDING SITTING             │
       │      │      │                  │
       └──────┼──────┘                  │
              │                         │
              ▼                         ▼
        ACTIVITY EVENTS          OBJECT EVENTS
              │                         │
              └──────────┬──────────────┘
                         ▼
                      V2 JSON
                         │
                         ▼
                    FASTAPI V2
                         │
                         ▼
                 PYDANTIC VALIDATION
                         │
                         ▼
                   EVENT HASH
                         │
                         ▼
                DUPLICATE CHECK
                    /         \
                  NEW       EXISTING
                   │            │
                   ▼            ▼
                INSERT         SKIP
                   │
                   ▼
               POSTGRESQL
                   │
                   ▼
                 DJANGO
                   │
                   ▼
           MONGODB SYNCHRONIZATION
                   │
                   ▼
                MONGODB
```

---

# 20. Project Structure

```text
fastapi-django-postgres-mongodb-sync/
│
├── api/
│   ├── v1/
│   │   └── ...
│   │
│   └── v2/
│       ├── __init__.py
│       └── activities.py
│
├── v2_detection_json/
│   ├── video1_v2.json
│   ├── video2_v2.json
│   ├── video3_v2.json
│   ├── video4_v2.json
│   ├── video5_v2.json
│   └── video6_v2.json
│
├── django_backend/
│   ├── authentication/
│   ├── config/
│   ├── mongodb_api/
│   ├── synchronization/
│   │   ├── management/
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── manage.py
│   └── run_sync.bat
│
├── main.py
├── database.py
├── models.py
├── logger_config.py
├── v2_send_to_api.py
└── README.md
```

---

# 21. Running V2

## 21.1 Start FastAPI

From the project root:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 21.2 Process Videos

Run the V2 video processor.

The processor generates:

```text
v2_detection_json/
```

Each video produces a corresponding JSON file.

---

## 21.3 Upload V2 JSON

From the project root:

```bash
python v2_send_to_api.py
```

The script discovers:

```text
v2_detection_json/*_v2.json
```

and sends each file to:

```text
POST /api/v2/activity-events
```

Example:

```text
Found 6 V2 JSON file(s).

Sending: video1_v2.json
SUCCESS

Sending: video2_v2.json
SUCCESS

...

V2 JSON UPLOAD COMPLETED
```

---

## 21.4 Synchronize PostgreSQL → MongoDB

Move into the Django backend:

```bash
cd django_backend
```

Run:

```bash
python manage.py sync_postgres_to_mongo
```

Example:

```text
Starting PostgreSQL to MongoDB synchronization...

Synchronization completed.
Total pending records : 241
Successfully synced   : 241
Already synced        : 0
Failed                : 0

PostgreSQL to MongoDB synchronization completed successfully.
```

---

# 22. PostgreSQL Verification

View V2 records:

```sql
SELECT
    id,
    video_name,
    event_type,
    class_name,
    confidence,
    frame_number,
    sync_status,
    json_data,
    event_hash,
    created_at,
    synced_at
FROM detection_events
WHERE event_type IN (
    'activity_event',
    'object_detection_v2'
)
ORDER BY id;
```

---

# 23. Activity Analytics Queries

## Activity count

```sql
SELECT
    event_type,
    COUNT(*) AS total
FROM detection_events
WHERE event_type = 'activity_event'
GROUP BY event_type;
```

## Activity distribution

```sql
SELECT
    json_data->>'activity' AS activity,
    COUNT(*) AS total
FROM detection_events
WHERE event_type = 'activity_event'
GROUP BY json_data->>'activity'
ORDER BY total DESC;
```

## Activity per person

```sql
SELECT
    json_data->>'person_id' AS person_id,
    json_data->>'activity' AS activity,
    COUNT(*) AS total
FROM detection_events
WHERE event_type = 'activity_event'
GROUP BY
    json_data->>'person_id',
    json_data->>'activity'
ORDER BY person_id;
```

## Video-wise activity

```sql
SELECT
    video_name,
    json_data->>'activity' AS activity,
    COUNT(*) AS total
FROM detection_events
WHERE event_type = 'activity_event'
GROUP BY
    video_name,
    json_data->>'activity'
ORDER BY
    video_name,
    activity;
```

---

# 24. Duplicate Verification

To check whether duplicate hashes exist:

```sql
SELECT
    event_hash,
    COUNT(*) AS occurrences
FROM detection_events
GROUP BY event_hash
HAVING COUNT(*) > 1;
```

With the unique event-hash constraint correctly applied, the same hash should not appear in multiple records.

---

# 25. Example Activity Timeline

A person's activity can be represented as:

```text
Person 1
│
├── Standing
│   00:00:00 ───────── 00:00:05
│
├── Moving
│   00:00:05 ───────── 00:00:12
│
├── Sitting
│   00:00:12 ───────── 00:00:30
│
└── Moving
    00:00:30 ───────── 00:00:38
```

This gives downstream systems a meaningful temporal representation of the video.

---

# 26. Mentor Requirement → V2 Implementation

| Requirement                                | Implementation             |
| ------------------------------------------ | -------------------------- |
| Detect people                              | YOLO detection             |
| Track people                               | Tracking system            |
| Maintain person identity during processing | Person tracking ID         |
| Detect movement                            | Movement analysis          |
| Detect standing                            | Activity classification    |
| Detect sitting                             | Activity classification    |
| Record activity start                      | `start_time`               |
| Record activity end                        | `end_time`                 |
| Calculate activity duration                | `duration_seconds`         |
| Record activity frame range                | `start_frame`, `end_frame` |
| Detect vehicles/objects                    | Object detection           |
| Generate structured output                 | V2 JSON                    |
| Store events                               | FastAPI + SQLAlchemy       |
| Prevent duplicate event insertion          | `event_hash`               |
| Synchronize data                           | Django                     |
| Store downstream documents                 | MongoDB                    |
| Track synchronization                      | `sync_status`, `synced_at` |

---

# 27. Technology Stack

| Layer                   | Technology             |
| ----------------------- | ---------------------- |
| Language                | Python                 |
| Computer Vision         | YOLO / Pose Estimation |
| Tracking                | Object/person tracking |
| API                     | FastAPI                |
| Validation              | Pydantic               |
| ORM                     | SQLAlchemy             |
| Primary Database        | PostgreSQL             |
| Synchronization Backend | Django                 |
| Secondary Database      | MongoDB                |
| HTTP Client             | Requests               |
| API Documentation       | Swagger / OpenAPI      |
| Version Control         | Git / GitHub           |

---

# 28. Key Design Principles

## Separation of Responsibilities

```text
Computer Vision
      ↓
JSON Generation
      ↓
FastAPI
      ↓
PostgreSQL
      ↓
Django Synchronization
      ↓
MongoDB
```

Each layer has a specific responsibility.

---

## Structured Events

V2 converts frame-level detections into meaningful time-based activity events.

---

## API Validation

Pydantic validates the incoming V2 payload before database insertion.

---

## Duplicate Protection

SHA-256 event hashes prevent the same event from being inserted multiple times.

---

## Synchronization Tracking

PostgreSQL maintains synchronization state before and after MongoDB synchronization.

---

# 29. V1 and V2 Compatibility

V2 extends the existing architecture rather than replacing the entire system.

```text
                 PROJECT
                    │
             ┌──────┴──────┐
             │             │
            V1             V2
             │             │
       Raw Detection   Activity Events
             │             │
             │       Person Tracking
             │             │
             │       Object Events
             │             │
             │       Event Hash
             │             │
             └──────┬──────┘
                    │
                    ▼
               PostgreSQL
                    │
                    ▼
                  Django
                    │
                    ▼
                 MongoDB
```

---

# 30. Future Extensions

The architecture can be extended toward a future V3 / production deployment:

```text
V3
 │
 ├── NVIDIA DeepStream
 ├── TensorRT inference
 ├── GPU acceleration
 ├── Real-time video streams
 ├── RTSP camera support
 ├── WebSocket events
 ├── Live dashboards
 ├── Multi-camera tracking
 ├── Cross-camera identity tracking
 ├── Automated alerts
 └── Advanced activity recognition
```

---

# 31. Current V2 Workflow

The implemented workflow is:

```text
VIDEO
  │
  ▼
V2 PROCESSOR
  │
  ▼
PERSON / OBJECT DETECTION
  │
  ▼
PERSON TRACKING
  │
  ▼
ACTIVITY CLASSIFICATION
  │
  ├── Moving
  ├── Standing
  └── Sitting
  │
  ▼
ACTIVITY + OBJECT EVENTS
  │
  ▼
V2 JSON
  │
  ▼
FASTAPI V2
  │
  ▼
EVENT HASH
  │
  ▼
DUPLICATE CHECK
  │
  ├── NEW → INSERT
  │
  └── EXISTING → SKIP
  │
  ▼
POSTGRESQL
  │
  ▼
DJANGO
  │
  ▼
MONGODB
```

---

# 32. Why V2 Matters

The main improvement in V2 is the transition from **raw detections to meaningful events**.

Instead of storing:

```text
Person detected at frame 300
Person detected at frame 301
Person detected at frame 302
Person detected at frame 303
```

the system can represent:

```text
Person 1
Activity: Standing
Start: 00:00:10
End: 00:00:18
Duration: 8 seconds
```

This makes the resulting data substantially more useful for analytics, reporting, monitoring and downstream applications.

---

# 33. Final Summary

V2 transforms the original detection pipeline into an activity-aware video analytics architecture.

The complete flow is:

```text
VIDEO
  ↓
YOLO / POSE
  ↓
DETECTION
  ↓
TRACKING
  ↓
PERSON ID
  ↓
ACTIVITY ANALYSIS
  ↓
MOVING / STANDING / SITTING
  ↓
START / END / DURATION
  ↓
OBJECT EVENTS
  ↓
V2 JSON
  ↓
FASTAPI
  ↓
EVENT HASH
  ↓
DUPLICATE CHECK
  ↓
POSTGRESQL
  ↓
DJANGO
  ↓
MONGODB
```

The system therefore converts raw video observations into structured, time-based events while providing:

* Person tracking
* Activity classification
* Activity timelines
* Object detection
* Structured JSON
* API validation
* PostgreSQL storage
* Event-level duplicate protection
* Django-based synchronization
* MongoDB storage
* Synchronization status tracking

**V2 represents the transition from simple object detection to a structured video activity analytics pipeline.**

## 👨‍💻 Author

**Pathan Mohammed Akram Khan**
B.Tech — Computer Science & Engineering (Artificial Intelligence & Machine Learning)
Alliance University, Bangalore, India

### Repository

This repository contains the implementation of the **V2 AI Video Detection and Activity Tracking Pipeline**, developed as part of the Proglint internship/project work.

---

## 📌 Project Ownership

Developed and maintained by **Akram Khan** as an AI/ML and backend engineering project, integrating computer vision processing with a production-oriented API and database synchronization architecture.
