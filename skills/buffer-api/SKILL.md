---
name: buffer
description: |
  Buffer API integration with managed authentication. Schedule and manage social media posts across multiple platforms.
  Use this skill when users want to schedule posts, manage channels, view organizations, or create content ideas in Buffer.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Buffer

Access the Buffer GraphQL API with managed authentication. Schedule and manage social media posts across Instagram, Facebook, Twitter, LinkedIn, TikTok, and more.

## Quick Start

```bash
# Get account info with organizations
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": "query { account { id email organizations { id name } } }"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/buffer/
```

Buffer uses a single GraphQL endpoint. All queries and mutations are sent as POST requests to this endpoint.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Buffer connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=buffer&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'buffer'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "a71282a3-52be-473d-9273-22b4546dc146",
    "status": "ACTIVE",
    "creation_time": "2026-03-12T00:18:28.327860Z",
    "last_updated_time": "2026-03-12T00:18:42.818009Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "buffer",
    "metadata": {},
    "method": "API_KEY"
  }
}
```

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Buffer connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({"query": "query { account { id } }"}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Maton-Connection', 'a71282a3-52be-473d-9273-22b4546dc146')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Get Account

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    query {
        account {
            id
            email
            name
            avatar
            timezone
            createdAt
            preferences {
                timeFormat
                startOfWeek
            }
        }
    }
    """
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": {
    "account": {
      "id": "69846f7479b75e6487fa3482",
      "email": "user@example.com",
      "name": "John Doe",
      "avatar": "https://...",
      "timezone": "America/New_York",
      "createdAt": "2024-01-15T10:30:00Z",
      "preferences": {
        "timeFormat": "12h",
        "startOfWeek": "sunday"
      }
    }
  }
}
```

### Get Organizations

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    query {
        account {
            organizations {
                id
                name
                channels {
                    id
                    name
                    service
                    avatar
                    isDisconnected
                }
            }
        }
    }
    """
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": {
    "account": {
      "organizations": [
        {
          "id": "69846f7479b75e6487fa3484",
          "name": "My Organization",
          "channels": [
            {
              "id": "channel123",
              "name": "My Twitter",
              "service": "twitter",
              "avatar": "https://...",
              "isDisconnected": false
            }
          ]
        }
      ]
    }
  }
}
```

### Get Channels

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    query GetChannels($organizationId: OrganizationId!) {
        channels(organizationId: $organizationId) {
            id
            name
            service
            displayName
            avatar
            timezone
            isDisconnected
            isQueuePaused
            postingSchedule {
                days
                times
            }
        }
    }
    """,
    "variables": {
        "organizationId": "69846f7479b75e6487fa3484"
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Single Channel

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    query GetChannel($channelId: ChannelId!) {
        channel(channelId: $channelId) {
            id
            name
            service
            displayName
            avatar
            timezone
            postingSchedule {
                days
                times
            }
            postingGoal {
                postsPerWeek
                progress
            }
        }
    }
    """,
    "variables": {
        "channelId": "channel123"
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### List Posts

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    query GetPosts($channelId: ChannelId!, $status: PostStatus, $first: Int) {
        posts(channelId: $channelId, status: $status, first: $first) {
            edges {
                node {
                    id
                    text
                    status
                    createdAt
                    dueAt
                    sentAt
                    channelService
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
    """,
    "variables": {
        "channelId": "channel123",
        "status": "scheduled",
        "first": 10
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Post Status Values:**
- `draft` - Saved as draft
- `scheduled` - Scheduled for publishing
- `sent` - Published
- `failed` - Failed to publish

### Get Single Post

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    query GetPost($postId: PostId!) {
        post(id: $postId) {
            id
            text
            status
            createdAt
            dueAt
            sentAt
            author {
                name
                email
            }
            channel {
                id
                name
                service
            }
            assets {
                id
                url
                type
            }
        }
    }
    """,
    "variables": {
        "postId": "post123"
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Post

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on Post {
                id
                text
                status
                dueAt
            }
            ... on InvalidInputError {
                message
            }
            ... on UnauthorizedError {
                message
            }
        }
    }
    """,
    "variables": {
        "input": {
            "channelId": "channel123",
            "text": "Hello from Buffer API!",
            "schedulingType": "scheduled",
            "dueAt": "2026-03-15T14:00:00Z",
            "mode": "queue"
        }
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**CreatePostInput Fields:**
- `channelId` (required): Target channel ID
- `text`: Post content
- `schedulingType` (required): "scheduled", "draft", or "now"
- `dueAt`: ISO 8601 datetime for scheduled posts
- `mode` (required): "queue" or "share"
- `assets`: Media attachments
- `tagIds`: Content tags
- `metadata`: Platform-specific options (see Platform Metadata section)
- `ideaId`: Link post to existing idea
- `draftId`: Create from existing draft
- `source`: Origin of post
- `aiAssisted`: Whether AI helped create content
- `saveToDraft`: Save as draft instead of scheduling

### Create Post with Instagram Metadata

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on Post { id text status }
            ... on InvalidInputError { message }
        }
    }
    """,
    "variables": {
        "input": {
            "channelId": "instagram_channel_id",
            "text": "Check out our latest post! #photography",
            "schedulingType": "scheduled",
            "dueAt": "2026-03-15T14:00:00Z",
            "mode": "queue",
            "metadata": {
                "instagram": {
                    "type": "post",
                    "firstComment": "Follow us for more!",
                    "shouldShareToFeed": True
                }
            }
        }
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Twitter Thread

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on Post { id text status }
            ... on InvalidInputError { message }
        }
    }
    """,
    "variables": {
        "input": {
            "channelId": "twitter_channel_id",
            "text": "First tweet in thread",
            "schedulingType": "scheduled",
            "dueAt": "2026-03-15T14:00:00Z",
            "mode": "queue",
            "metadata": {
                "twitter": {
                    "thread": [
                        {"text": "Second tweet in thread"},
                        {"text": "Third tweet in thread"}
                    ]
                }
            }
        }
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create LinkedIn Post with Link

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on Post { id text status }
            ... on InvalidInputError { message }
        }
    }
    """,
    "variables": {
        "input": {
            "channelId": "linkedin_channel_id",
            "text": "Check out our latest blog post!",
            "schedulingType": "scheduled",
            "dueAt": "2026-03-15T14:00:00Z",
            "mode": "queue",
            "metadata": {
                "linkedin": {
                    "linkAttachment": {
                        "url": "https://example.com/blog-post",
                        "title": "Our Latest Blog Post",
                        "description": "Read about our new features"
                    },
                    "firstComment": "What do you think?"
                }
            }
        }
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Pinterest Pin

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on Post { id text status }
            ... on InvalidInputError { message }
        }
    }
    """,
    "variables": {
        "input": {
            "channelId": "pinterest_channel_id",
            "text": "Beautiful sunset photo",
            "schedulingType": "scheduled",
            "dueAt": "2026-03-15T14:00:00Z",
            "mode": "queue",
            "metadata": {
                "pinterest": {
                    "title": "Amazing Sunset",
                    "url": "https://example.com/sunset",
                    "boardServiceId": "board_id"
                }
            }
        }
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create YouTube Video Post

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on Post { id text status }
            ... on InvalidInputError { message }
        }
    }
    """,
    "variables": {
        "input": {
            "channelId": "youtube_channel_id",
            "text": "Video description here",
            "schedulingType": "scheduled",
            "dueAt": "2026-03-15T14:00:00Z",
            "mode": "queue",
            "metadata": {
                "youtube": {
                    "title": "My Video Title",
                    "privacy": "public",
                    "categoryId": "22",
                    "notifySubscribers": True,
                    "embeddable": True,
                    "madeForKids": False
                }
            }
        }
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Idea

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    mutation CreateIdea($input: CreateIdeaInput!) {
        createIdea(input: $input) {
            ... on Idea {
                id
                title
                text
                createdAt
            }
            ... on InvalidInputError {
                message
            }
        }
    }
    """,
    "variables": {
        "input": {
            "organizationId": "69846f7479b75e6487fa3484",
            "title": "Blog post idea",
            "text": "Write about social media best practices",
            "services": ["twitter", "linkedin"]
        }
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Type Reference

### Account Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Account identifier |
| `email` | String | Primary email |
| `backupEmail` | String | Backup email address |
| `name` | String | Display name |
| `avatar` | String | Avatar URL |
| `timezone` | String | User timezone |
| `createdAt` | DateTime | Account creation date |
| `organizations` | [Organization] | Organizations the user belongs to |
| `preferences` | Preferences | User preferences (timeFormat, startOfWeek) |
| `connectedApps` | [ConnectedApp] | Third-party app connections |

### Organization Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Organization identifier |
| `name` | String | Organization name |
| `ownerEmail` | String | Owner's email |
| `channelCount` | Int | Number of connected channels |
| `channels` | [Channel] | Connected social channels |
| `members` | [Member] | Team members |
| `limits` | Limits | Plan limits and usage |

### Channel Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Channel identifier |
| `name` | String | Channel name |
| `displayName` | String | Display name |
| `service` | String | Platform (twitter, instagram, etc.) |
| `serviceId` | String | Platform-specific ID |
| `type` | String | Channel type |
| `avatar` | String | Channel avatar URL |
| `timezone` | String | Channel timezone |
| `isDisconnected` | Boolean | Connection status |
| `isLocked` | Boolean | Lock status |
| `isNew` | Boolean | Recently added |
| `isQueuePaused` | Boolean | Queue paused status |
| `postingSchedule` | PostingSchedule | Scheduled posting times (days, times) |
| `postingGoal` | PostingGoal | Weekly posting goal (postsPerWeek, progress) |
| `weeklyPostingLimit` | Int | Maximum posts per week |
| `allowedActions` | [String] | Permitted actions |
| `scopes` | [String] | OAuth scopes |
| `products` | [String] | Enabled products |
| `externalLink` | String | Link to profile |
| `linkShortening` | LinkShortening | URL shortening settings |
| `hasActiveMemberDevice` | Boolean | Mobile app connected |
| `showTrendingTopicSuggestions` | Boolean | Show trending suggestions |
| `metadata` | ChannelMetadata | Platform-specific metadata |
| `organizationId` | ID | Parent organization |
| `createdAt` | DateTime | Creation date |
| `updatedAt` | DateTime | Last update |

### Post Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Post identifier |
| `text` | String | Post content |
| `status` | PostStatus | draft, scheduled, sent, failed |
| `schedulingType` | String | scheduled, draft, now |
| `dueAt` | DateTime | Scheduled publish time |
| `sentAt` | DateTime | Actual publish time |
| `createdAt` | DateTime | Creation time |
| `updatedAt` | DateTime | Last update time |
| `author` | Author | Post creator (name, email) |
| `channel` | Channel | Target channel |
| `channelId` | ID | Channel identifier |
| `channelService` | String | Platform name |
| `ideaId` | ID | Linked idea |
| `via` | String | Creation source |
| `isCustomScheduled` | Boolean | Custom scheduled time |
| `externalLink` | String | Link to published post |
| `assets` | [Asset] | Media attachments (id, url, type) |
| `tags` | [Tag] | Content tags |
| `notes` | [Note] | Internal notes |
| `metadata` | PostMetadata | Platform-specific options |
| `notificationStatus` | String | Notification state |
| `error` | PostError | Error details if failed |
| `allowedActions` | [String] | Permitted actions |
| `sharedNow` | Boolean | Posted immediately |
| `shareMode` | String | Sharing mode |

### Idea Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Idea identifier |
| `organizationId` | ID | Parent organization |
| `content` | IdeaContent | Title, text, services |
| `groupId` | ID | Idea group |
| `position` | Int | Order in group |
| `createdAt` | DateTime | Creation date |
| `updatedAt` | DateTime | Last update |

## Platform Metadata Reference

### Instagram Metadata
| Field | Type | Description |
|-------|------|-------------|
| `type` | String | post, story, reel |
| `firstComment` | String | Auto-comment after posting |
| `link` | String | Link in bio reference |
| `geolocation` | Geolocation | Location tag |
| `shouldShareToFeed` | Boolean | Share reel to feed |
| `stickerFields` | StickerFields | Story stickers |

### Facebook Metadata
| Field | Type | Description |
|-------|------|-------------|
| `type` | String | Post type |
| `annotations` | [Annotation] | Tags and mentions |
| `linkAttachment` | LinkAttachment | Link preview (url, title, description) |
| `firstComment` | String | Auto-comment |
| `title` | String | Post title |

### LinkedIn Metadata
| Field | Type | Description |
|-------|------|-------------|
| `annotations` | [Annotation] | Tags and mentions |
| `linkAttachment` | LinkAttachment | Link preview |
| `firstComment` | String | Auto-comment |

### Twitter Metadata
| Field | Type | Description |
|-------|------|-------------|
| `retweet` | RetweetInput | Quote retweet settings |
| `thread` | [ThreadItem] | Thread tweets [{text}] |

### Pinterest Metadata
| Field | Type | Description |
|-------|------|-------------|
| `title` | String | Pin title |
| `url` | String | Destination URL |
| `boardServiceId` | String | Target board ID |

### YouTube Metadata
| Field | Type | Description |
|-------|------|-------------|
| `title` | String | Video title |
| `privacy` | String | public, unlisted, private |
| `categoryId` | String | YouTube category ID |
| `license` | String | Video license |
| `notifySubscribers` | Boolean | Send notifications |
| `embeddable` | Boolean | Allow embedding |
| `madeForKids` | Boolean | Kids content flag |

### TikTok Metadata
| Field | Type | Description |
|-------|------|-------------|
| `title` | String | Video title |

### Google Business Metadata
| Field | Type | Description |
|-------|------|-------------|
| `type` | String | Post type |
| `title` | String | Post title |
| `detailsOffer` | OfferDetails | Offer details |
| `detailsEvent` | EventDetails | Event details |
| `detailsWhatsNew` | WhatsNewDetails | Update details |

### Mastodon Metadata
| Field | Type | Description |
|-------|------|-------------|
| `thread` | [ThreadItem] | Thread toots |
| `spoilerText` | String | Content warning |

### Threads Metadata
| Field | Type | Description |
|-------|------|-------------|
| `type` | String | Post type |
| `thread` | [ThreadItem] | Thread posts |
| `linkAttachment` | LinkAttachment | Link preview |
| `topic` | String | Topic tag |
| `locationId` | String | Location ID |
| `locationName` | String | Location name |

### Bluesky Metadata
| Field | Type | Description |
|-------|------|-------------|
| `thread` | [ThreadItem] | Thread skeets |
| `linkAttachment` | LinkAttachment | Link card |

## Supported Services

Buffer supports posting to:
- Instagram
- Facebook
- Twitter/X
- LinkedIn
- Pinterest
- TikTok
- Google Business
- YouTube
- Mastodon
- Threads
- Bluesky
- StartPage

## Pagination

Posts use cursor-based pagination:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": """
    query GetPosts($channelId: ChannelId!, $first: Int, $after: String) {
        posts(channelId: $channelId, first: $first, after: $after) {
            edges {
                node {
                    id
                    text
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
    """,
    "variables": {
        "channelId": "channel123",
        "first": 10,
        "after": "cursor_from_previous_page"
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/buffer/', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Code Examples

### JavaScript

```javascript
const response = await fetch('https://gateway.maton.ai/buffer/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.MATON_API_KEY}`
  },
  body: JSON.stringify({
    query: `query { account { id email organizations { id name } } }`
  })
});
const data = await response.json();
console.log(data.data.account);
```

### Python

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/buffer/',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={
        'query': 'query { account { id email organizations { id name } } }'
    }
)
data = response.json()
print(data['data']['account'])
```

## Notes

- Buffer uses GraphQL - all requests are POST to the base endpoint
- Use introspection to discover the full schema
- Posts require a connected channel with proper permissions
- Scheduling requires timezone-aware datetime strings (ISO 8601)
- Some features require paid Buffer plans
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Buffer connection or invalid GraphQL query |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Buffer API |

**GraphQL Error Types:**
- `InvalidInputError` - Invalid mutation input
- `NotFoundError` - Resource not found
- `UnauthorizedError` - Insufficient permissions
- `LimitReachedError` - Plan limits exceeded

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `buffer`. For example:

- Correct: `https://gateway.maton.ai/buffer/`
- Incorrect: `https://gateway.maton.ai/graphql`

## Resources

- [Buffer API Documentation](https://developers.buffer.com/reference.html)
- [Buffer API Getting Started](https://developers.buffer.com/guides/getting-started.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
