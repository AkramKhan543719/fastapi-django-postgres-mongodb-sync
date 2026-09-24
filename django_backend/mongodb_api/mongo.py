from pymongo import MongoClient


MONGO_URI = "mongodb://127.0.0.1:27017"

MONGO_DATABASE = "deepstream_mongodb"


# ============================================================
# MongoDB Client
# ============================================================

client = MongoClient(MONGO_URI)

db = client[MONGO_DATABASE]


# ============================================================
# Detection Events Collection
# ============================================================

detection_events_collection = db["detection_events"]


# ============================================================
# MongoDB Connection Test
# ============================================================

def test_mongodb_connection():

    try:

        client.admin.command("ping")

        print("MongoDB connected successfully!")

        print(
            "MongoDB database:",
            MONGO_DATABASE
        )

        return True

    except Exception as e:

        print("MongoDB connection failed:")

        print(e)

        return False