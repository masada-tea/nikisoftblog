import mimetypes
import os
import subprocess
from datetime import datetime
from enum import Enum

import requests
import sass
import yaml
from itsdangerous import JSONWebSignatureSerializer
from little_boxes import strtobool
from little_boxes.activitypub import DEFAULT_CTX
from pymongo import MongoClient
import pymongo

from utils.key import KEY_DIR
from utils.key import get_key
from utils.key import get_secret_key
from utils.media import MediaCache

def noop():
    pass


CUSTOM_CACHE_HOOKS = False
try:
    from cache_hooks import purge as custom_cache_purge_hook
except ModuleNotFoundError:
    custom_cache_purge_hook = noop

VERSION = (
    subprocess.check_output(["git", "describe", "--always"]).split()[0].decode("utf-8")
)

DEBUG_MODE = strtobool(os.getenv("MICROBLOGPUB_DEBUG", "false"))

HEADERS = [
    "application/activity+json",
    "application/ld+json;profile=https://www.w3.org/ns/activitystreams",
    'application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
    "application/ld+json",
]


with open(os.path.join(KEY_DIR, "me.yml")) as f:
    conf = yaml.load(f)

    USERNAME = conf["username"]
    NAME = conf["name"]
    DOMAIN = conf["domain"]
    PUBLIC_DOMAIN = conf["public_url"]
    SCHEME = "https" if conf.get("https", True) else "http"
    BASE_URL = SCHEME + "://" + conf["public_url"]
    ACTOR_URL = SCHEME + "://" + conf["domain"]
    ID = BASE_URL
    SUMMARY = conf["summary"]
    ICON_URL = conf.get("icon_url",conf["default_icon"])
    PASS = conf["pass"]
    EXTRA_INBOXES = conf.get("extra_inboxes", [])
    COPYRIGHT = conf["copyright"]
    IMPRINT = conf["imprint_url"]
    PRIVACY = conf["privacy_url"]
    SOURCE_URL = conf["source_url"]
    DEFAULT_ICON = conf["default_icon"]
    FAVICON = conf["favicon_url"]
    HIDE_FOLLOWING = conf.get("hide_following", False)
    LIMIT = conf.get("limit",10)
    PORT = conf.get("port",5000)

USER_AGENT = (
    f"{requests.utils.default_user_agent()} (microblog.pub/{VERSION}; +{BASE_URL})"
)

mongo_client = MongoClient(
    host=[os.getenv("MICROBLOGPUB_MONGODB_HOST", "localhost:27017")]
)

DB_NAME = "{}_{}".format(USERNAME, DOMAIN.replace(".", "_"))
DB = mongo_client[DB_NAME]
GRIDFS = mongo_client[f"{DB_NAME}_gridfs"]
MEDIA_CACHE = MediaCache(GRIDFS, USER_AGENT)


def create_indexes():
    DB.command("compact", "activities")
    DB.activities.create_index([("remote_id", pymongo.ASCENDING)])
    DB.activities.create_index([("activity.object.id", pymongo.ASCENDING)])
    DB.activities.create_index([("meta.thread_root_parent", pymongo.ASCENDING)])
    DB.activities.create_index(
        [
            ("meta.thread_root_parent", pymongo.ASCENDING),
            ("meta.deleted", pymongo.ASCENDING),
        ]
    )
    DB.activities.create_index(
        [("activity.object.id", pymongo.ASCENDING), ("meta.deleted", pymongo.ASCENDING)]
    )
    DB.cache2.create_index(
        [
            ("path", pymongo.ASCENDING),
            ("type", pymongo.ASCENDING),
            ("arg", pymongo.ASCENDING),
        ]
    )
    DB.cache2.create_index("date", expireAfterSeconds=3600 * 12)

    # Index for the block query
    DB.activities.create_index(
        [
            ("box", pymongo.ASCENDING),
            ("type", pymongo.ASCENDING),
            ("meta.undo", pymongo.ASCENDING),
        ]
    )

    # Index for count queries
    DB.activities.create_index(
        [
            ("box", pymongo.ASCENDING),
            ("type", pymongo.ASCENDING),
            ("meta.undo", pymongo.ASCENDING),
            ("meta.deleted", pymongo.ASCENDING),
        ]
    )

    DB.activities.create_index([("box", pymongo.ASCENDING)])

    # Outbox query
    DB.activities.create_index(
        [
            ("box", pymongo.ASCENDING),
            ("type", pymongo.ASCENDING),
            ("meta.undo", pymongo.ASCENDING),
            ("meta.deleted", pymongo.ASCENDING),
            ("meta.public", pymongo.ASCENDING),
        ]
    )

    DB.activities.create_index(
        [
            ("type", pymongo.ASCENDING),
            ("activity.object.type", pymongo.ASCENDING),
            ("activity.object.inReplyTo", pymongo.ASCENDING),
            ("meta.deleted", pymongo.ASCENDING),
        ]
    )


def _drop_db():
    if not DEBUG_MODE:
        return

    mongo_client.drop_database(DB_NAME)


KEY = get_key(ID, USERNAME, DOMAIN)


JWT_SECRET = get_secret_key("jwt")
JWT = JSONWebSignatureSerializer(JWT_SECRET)


def _admin_jwt_token() -> str:
    return JWT.dumps(  # type: ignore
        {"me": "ADMIN", "ts": datetime.now().timestamp()}
    ).decode(  # type: ignore
        "utf-8"
    )


ADMIN_API_KEY = get_secret_key("admin_api_key", _admin_jwt_token)

ME = {
    "@context":[
	"https://www.w3.org/ns/activitystreams",
	"https://w3id.org/security/v1",
	{
	    "manuallyApprovesFollowers":"as:manuallyApprovesFollowers",
	    "toot":"http://joinmastodon.org/ns#",
	    "featured":{
		"@id":"toot:featured",
		"@type":"@id"
	    },
	    "alsoKnownAs":{
		"@id":"as:alsoKnownAs",
		"@type":"@id"
	    },
	    "movedTo":{
		"@id":"as:movedTo",
		"@type":"@id"
	    },
	    "schema":"http://schema.org#",
	    "PropertyValue":"schema:PropertyValue",
	    "value":"schema:value",
	    "Hashtag":"as:Hashtag",
	    "Emoji":"toot:Emoji",
	    "IdentityProof":"toot:IdentityProof",
	    "focalPoint":{
		"@container":"@list",
		"@id":"toot:focalPoint"
	    }
	}
    ],
    "type": "Person",
    "id": ID,
    "following": ID + "/following",
    "followers": ID + "/followers",
    "featured": ID + "/featured",
    "liked": ID + "/liked",
    "inbox": ID + "/inbox",
    "outbox": ID + "/outbox",
    "preferredUsername": USERNAME,
    "name": NAME,
    "summary": SUMMARY,
    "endpoints": {},
    "url": ID,
    "manuallyApprovesFollowers": False,
    "attachment": [],
    "icon": {
        "mediaType": mimetypes.guess_type(ICON_URL)[0],
        "type": "Image",
        "url": ICON_URL,
    },
    "publicKey": KEY.to_dict(),
}

# TODO(tsileo): read the config from the YAML if set
EMOJIS = "😺 😸 😹 😻 😼 😽 🙀 😿 😾"
