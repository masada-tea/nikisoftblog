# microblog.pub - Nikisoft edition
<p align="center">
<img src="https://sos-ch-dk-2.exo.io/microblogpub/microblobpub.png" width="200" height="200" border="0" alt="microblog.pub">
</p>
<p align="center">A self-hosted, single-user, <a href="https://activitypub.rocks">ActivityPub</a> powered microblog.</p>
**Quite early state but already stable enough for hosting your blog**
## Features

 - Implements a basic [ActivityPub](https://activitypub.rocks/) server (with federation)
   - Compatible with [Mastodon](https://github.com/tootsuite/mastodon) and others (Pleroma, Hubzilla...)
   - Also implements a remote follow compatible with Mastodon instances
 - Exposes your outbox as a basic microblog
 - Implements [IndieAuth](https://indieauth.spec.indieweb.org/) endpoints (authorization and token endpoint)
   - U2F support
   - You can use your ActivityPub identity to login to other websites/app
 - Comes with an admin UI with notifications and the stream of people you follow
 - Allows you to attach files to your notes
   - Privacy-aware image upload endpoint that strip EXIF meta data before storing the file
 - Microformats aware (exports `h-feed`, `h-entry`, `h-cards`, ...)
 - Exports RSS/Atom/[JSON](https://jsonfeed.org/) feeds
    - You stream/timeline is also available in an (authenticated) JSON feed
 - Comes with a tiny HTTP API to help posting new content and and read your inbox/notifications
 - Easy to "cache" (the external/public-facing microblog part)
   - With a good setup, cached content can be served most of the time
   - You can setup a "purge" hook to let you invalidate cache when the microblog was updated
 - Deployable with Docker (Docker compose for everything: dev, test and deployment)

## ActivityPub

microblog.pub implements an [ActivityPub](http://activitypub.rocks/) server, it implements both the client to server API and the federated server to server API.

Activities are verified using HTTP Signatures or by fetching the content on the remote server directly.

## Running your instance

### Dependencies

Please make sure that you have the following software installed when starting the installation:
- Python 3
- Python 3 Virtualenv
- Go
- MongoDB

### Installation

```shell
$ git clone https://notabug.org/nipos/nikisoftblog
$ cd nikisoftblog
$ make install
$ sudo make pt-install
$ make config
$ make password
$ sudo make services
$ sudo systemctl enable poussetaches
$ sudo systemctl start poussetaches
$ sudo systemctl enable microblog
$ sudo systemctl start microblog
``` 

### Configuration

```shell
$ make password
Password: <enter a password; nothing will show on screen>
$2b$12$iW497g...
```

Edit `config/me.yml` to add the above-generated password, like so:

```
username: 'username'
name: 'Your Name'
icon_url: 'https://you-avatar-url'
domain: 'your-domain.tld'
summary: 'your summary'
https: true
pass: $2b$12$iW497g...
```

## API

Your admin API key can be found at `config/admin_api_key.key`.

## ActivityPub API

### GET /

Returns the actor profile, with links to all the "standard" collections.

### GET /tags/:tag

Special collection that reference notes with the given tag.

### GET /stream

Special collection that returns the stream/inbox as displayed in the UI.

## User API

The user API is used by the admin UI (and requires a CSRF token when used with a regular user session), but it can also be accessed with an API key.

All the examples are using [HTTPie](https://httpie.org/).

### POST /api/note/delete{?id}

Deletes the given note `id` (the note must from the instance outbox).

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/note/delete Authorization:'Bearer <token>' id=http://microblob.pub/outbox/<note_id>/activity
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<delete_id>"
}
```

### POST /api/note/pin{?id}

Adds the given note `id` (the note must from the instance outbox) to the featured collection (and pins it on the homepage).

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/note/pin Authorization:'Bearer <token>' id=http://microblob.pub/outbox/<note_id>/activity
```

#### Response

```json
{
    "pinned": true
}
```

### POST /api/note/unpin{?id}

Removes the given note `id` (the note must from the instance outbox) from the featured collection (and un-pins it).

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/note/unpin Authorization:'Bearer <token>' id=http://microblob.pub/outbox/<note_id>/activity
```

#### Response

```json
{
    "pinned": false
}
```

### POST /api/like{?id}

Likes the given activity.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/like Authorization:'Bearer <token>' id=http://activity-iri.tld
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<like_id>"
}
```

### POST /api/boost{?id}

Boosts/Announces the given activity.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/boost Authorization:'Bearer <token>' id=http://activity-iri.tld
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<announce_id>"
}
```

### POST /api/block{?actor}

Blocks the given actor, all activities from this actor will be dropped after that.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/block Authorization:'Bearer <token>' actor=http://actor-iri.tld/
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<block_id>"
}
```

### POST /api/follow{?actor}

Follows the given actor.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/follow Authorization:'Bearer <token>' actor=http://actor-iri.tld/
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<follow_id>"
}
```

### POST /api/new_note{?content,reply}

Creates a new note. `reply` is the IRI of the "replied" note if any.

Answers a **201** (Created) status code.

You can pass the `content` and `reply` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/new_note Authorization:'Bearer <token>' content=hello
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<create_id>"
}
```


### GET /api/stream


#### Example

```shell
$ http GET https://microblog.pub/api/stream Authorization:'Bearer <token>'
```

#### Response

```json
```
