---
name: google-classroom
description: |
  Google Classroom API integration with managed OAuth. Manage courses, assignments, students, teachers, and announcements.
  Use this skill when users want to create courses, manage coursework, track student submissions, or post announcements.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
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

# Google Classroom

Access the Google Classroom API with managed OAuth authentication. Manage courses, coursework, students, teachers, announcements, and submissions.

## Quick Start

```bash
# List all courses
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-classroom/v1/courses')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/google-classroom/{api-path}
```

The Google Classroom API uses the path pattern:
```
https://gateway.maton.ai/google-classroom/v1/{resource}
```

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

Manage your Google Classroom OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=google-classroom&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'google-classroom'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python3 <<'EOF'
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
    "connection_id": "8efa1361-0e86-40b1-a63b-53a5051f8ac6",
    "status": "ACTIVE",
    "creation_time": "2026-02-14T00:00:00.000000Z",
    "last_updated_time": "2026-02-14T00:00:00.000000Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "google-classroom",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Google Classroom connections, specify which one to use with the `Maton-Connection` header:

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-classroom/v1/courses')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '8efa1361-0e86-40b1-a63b-53a5051f8ac6')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Courses

#### List Courses

```bash
GET /v1/courses
GET /v1/courses?courseStates=ACTIVE
GET /v1/courses?teacherId=me
GET /v1/courses?studentId=me
GET /v1/courses?pageSize=10
```

**Query Parameters:**
- `courseStates` - Filter by state: `ACTIVE`, `ARCHIVED`, `PROVISIONED`, `DECLINED`, `SUSPENDED`
- `teacherId` - Filter by teacher ID (use `me` for current user)
- `studentId` - Filter by student ID (use `me` for current user)
- `pageSize` - Number of results per page (max 100)
- `pageToken` - Token for next page

**Response:**
```json
{
  "courses": [
    {
      "id": "825635865485",
      "name": "Introduction to Programming",
      "section": "Section A",
      "descriptionHeading": "CS 101",
      "description": "Learn the basics of programming",
      "ownerId": "102753038276005039640",
      "creationTime": "2026-02-14T01:53:58.991Z",
      "updateTime": "2026-02-14T01:53:58.991Z",
      "enrollmentCode": "3qsua37m",
      "courseState": "ACTIVE",
      "alternateLink": "https://classroom.google.com/c/ODI1NjM1ODY1NDg1",
      "guardiansEnabled": false
    }
  ],
  "nextPageToken": "..."
}
```

#### Get Course

```bash
GET /v1/courses/{courseId}
```

#### Create Course

```bash
POST /v1/courses
Content-Type: application/json

{
  "name": "Course Name",
  "section": "Section A",
  "descriptionHeading": "Course Title",
  "description": "Course description",
  "ownerId": "me"
}
```

**Response:**
```json
{
  "id": "825637533405",
  "name": "Course Name",
  "section": "Section A",
  "ownerId": "102753038276005039640",
  "courseState": "PROVISIONED",
  "enrollmentCode": "abc123"
}
```

#### Update Course

```bash
PATCH /v1/courses/{courseId}?updateMask=name,description
Content-Type: application/json

{
  "name": "Updated Course Name",
  "description": "Updated description"
}
```

**Note:** Use `updateMask` query parameter to specify which fields to update.

#### Delete Course

```bash
DELETE /v1/courses/{courseId}
```

**Note:** Courses must be archived before deletion. To archive, update the course with `courseState: "ARCHIVED"`.

### Course Work (Assignments)

#### List Course Work

```bash
GET /v1/courses/{courseId}/courseWork
GET /v1/courses/{courseId}/courseWork?courseWorkStates=PUBLISHED
GET /v1/courses/{courseId}/courseWork?orderBy=dueDate
```

**Query Parameters:**
- `courseWorkStates` - Filter by state: `PUBLISHED`, `DRAFT`, `DELETED`
- `orderBy` - Sort by: `dueDate`, `updateTime`
- `pageSize` - Number of results per page
- `pageToken` - Token for next page

#### Get Course Work

```bash
GET /v1/courses/{courseId}/courseWork/{courseWorkId}
```

#### Create Course Work

```bash
POST /v1/courses/{courseId}/courseWork
Content-Type: application/json

{
  "title": "Assignment Title",
  "description": "Assignment description",
  "workType": "ASSIGNMENT",
  "state": "PUBLISHED",
  "maxPoints": 100,
  "dueDate": {
    "year": 2026,
    "month": 3,
    "day": 15
  },
  "dueTime": {
    "hours": 23,
    "minutes": 59
  }
}
```

**Work Types:**
- `ASSIGNMENT` - Regular assignment
- `SHORT_ANSWER_QUESTION` - Short answer question
- `MULTIPLE_CHOICE_QUESTION` - Multiple choice question

**States:**
- `DRAFT` - Not visible to students
- `PUBLISHED` - Visible to students

#### Update Course Work

```bash
PATCH /v1/courses/{courseId}/courseWork/{courseWorkId}?updateMask=title,description
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}
```

#### Delete Course Work

```bash
DELETE /v1/courses/{courseId}/courseWork/{courseWorkId}
```

### Student Submissions

#### List Student Submissions

```bash
GET /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions
GET /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions?states=TURNED_IN
```

**Query Parameters:**
- `states` - Filter by state: `NEW`, `CREATED`, `TURNED_IN`, `RETURNED`, `RECLAIMED_BY_STUDENT`
- `userId` - Filter by student ID
- `pageSize` - Number of results per page
- `pageToken` - Token for next page

**Note:** Course work must be in `PUBLISHED` state to list submissions.

**Response:**
```json
{
  "studentSubmissions": [
    {
      "courseId": "825635865485",
      "courseWorkId": "825637404958",
      "id": "Cg4I8ufNwwYQ7tSZgYIB",
      "userId": "102753038276005039640",
      "creationTime": "2026-02-14T02:30:00.000Z",
      "state": "NEW",
      "alternateLink": "https://classroom.google.com/..."
    }
  ]
}
```

#### Get Student Submission

```bash
GET /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions/{submissionId}
```

#### Grade Submission

```bash
PATCH /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions/{submissionId}?updateMask=assignedGrade,draftGrade
Content-Type: application/json

{
  "assignedGrade": 95,
  "draftGrade": 95
}
```

#### Return Submission

```bash
POST /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions/{submissionId}:return
Content-Type: application/json

{}
```

### Teachers

#### List Teachers

```bash
GET /v1/courses/{courseId}/teachers
```

**Response:**
```json
{
  "teachers": [
    {
      "courseId": "825635865485",
      "userId": "102753038276005039640",
      "profile": {
        "id": "102753038276005039640",
        "name": {
          "givenName": "John",
          "familyName": "Doe",
          "fullName": "John Doe"
        },
        "emailAddress": "john.doe@example.com"
      }
    }
  ]
}
```

#### Get Teacher

```bash
GET /v1/courses/{courseId}/teachers/{userId}
```

#### Add Teacher

```bash
POST /v1/courses/{courseId}/teachers
Content-Type: application/json

{
  "userId": "teacher@example.com"
}
```

#### Remove Teacher

```bash
DELETE /v1/courses/{courseId}/teachers/{userId}
```

### Students

#### List Students

```bash
GET /v1/courses/{courseId}/students
```

#### Get Student

```bash
GET /v1/courses/{courseId}/students/{userId}
```

#### Add Student

```bash
POST /v1/courses/{courseId}/students
Content-Type: application/json

{
  "userId": "student@example.com"
}
```

#### Remove Student

```bash
DELETE /v1/courses/{courseId}/students/{userId}
```

### Announcements

#### List Announcements

```bash
GET /v1/courses/{courseId}/announcements
GET /v1/courses/{courseId}/announcements?announcementStates=PUBLISHED
```

#### Get Announcement

```bash
GET /v1/courses/{courseId}/announcements/{announcementId}
```

#### Create Announcement

```bash
POST /v1/courses/{courseId}/announcements
Content-Type: application/json

{
  "text": "Announcement text content",
  "state": "PUBLISHED"
}
```

**States:**
- `DRAFT` - Not visible to students
- `PUBLISHED` - Visible to students

#### Update Announcement

```bash
PATCH /v1/courses/{courseId}/announcements/{announcementId}?updateMask=text
Content-Type: application/json

{
  "text": "Updated announcement text"
}
```

#### Delete Announcement

```bash
DELETE /v1/courses/{courseId}/announcements/{announcementId}
```

### Topics

#### List Topics

```bash
GET /v1/courses/{courseId}/topics
```

#### Get Topic

```bash
GET /v1/courses/{courseId}/topics/{topicId}
```

#### Create Topic

```bash
POST /v1/courses/{courseId}/topics
Content-Type: application/json

{
  "name": "Topic Name"
}
```

#### Update Topic

```bash
PATCH /v1/courses/{courseId}/topics/{topicId}?updateMask=name
Content-Type: application/json

{
  "name": "Updated Topic Name"
}
```

#### Delete Topic

```bash
DELETE /v1/courses/{courseId}/topics/{topicId}
```

### Course Work Materials

#### List Course Work Materials

```bash
GET /v1/courses/{courseId}/courseWorkMaterials
```

#### Get Course Work Material

```bash
GET /v1/courses/{courseId}/courseWorkMaterials/{courseWorkMaterialId}
```

### Invitations

#### List Invitations

```bash
GET /v1/invitations?courseId={courseId}
GET /v1/invitations?userId=me
```

**Note:** Either `courseId` or `userId` is required.

#### Create Invitation

```bash
POST /v1/invitations
Content-Type: application/json

{
  "courseId": "825635865485",
  "userId": "user@example.com",
  "role": "STUDENT"
}
```

**Roles:**
- `STUDENT`
- `TEACHER`
- `OWNER`

#### Accept Invitation

```bash
POST /v1/invitations/{invitationId}:accept
```

#### Delete Invitation

```bash
DELETE /v1/invitations/{invitationId}
```

### User Profiles

#### Get Current User

```bash
GET /v1/userProfiles/me
```

**Response:**
```json
{
  "id": "102753038276005039640",
  "name": {
    "givenName": "John",
    "familyName": "Doe",
    "fullName": "John Doe"
  },
  "emailAddress": "john.doe@example.com",
  "permissions": [
    {
      "permission": "CREATE_COURSE"
    }
  ],
  "verifiedTeacher": false
}
```

#### Get User Profile

```bash
GET /v1/userProfiles/{userId}
```

### Course Aliases

#### List Course Aliases

```bash
GET /v1/courses/{courseId}/aliases
```

## Pagination

The Google Classroom API uses token-based pagination. Responses include a `nextPageToken` when more results are available.

```bash
GET /v1/courses?pageSize=10
```

**Response:**
```json
{
  "courses": [...],
  "nextPageToken": "Ci8KLRIrEikKDmIMCLK8v8wGEIDQrsYBCgsI..."
}
```

To get the next page:

```bash
GET /v1/courses?pageSize=10&pageToken=Ci8KLRIrEikKDmIMCLK8v8wGEIDQrsYBCgsI...
```

## Code Examples

### JavaScript

```javascript
// List all courses
const response = await fetch(
  'https://gateway.maton.ai/google-classroom/v1/courses',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.courses);
```

### Python

```python
import os
import requests

# List all courses
response = requests.get(
    'https://gateway.maton.ai/google-classroom/v1/courses',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
print(data['courses'])
```

### Create Assignment Example

```python
import os
import requests

course_id = "825635865485"

# Create an assignment
assignment = {
    "title": "Week 1 Homework",
    "description": "Complete exercises 1-10",
    "workType": "ASSIGNMENT",
    "state": "PUBLISHED",
    "maxPoints": 100,
    "dueDate": {"year": 2026, "month": 3, "day": 15},
    "dueTime": {"hours": 23, "minutes": 59}
}

response = requests.post(
    f'https://gateway.maton.ai/google-classroom/v1/courses/{course_id}/courseWork',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json=assignment
)
print(response.json())
```

## Notes

- **updateMask Required**: PATCH requests require the `updateMask` query parameter specifying which fields to update
- **Course Deletion**: Courses must be archived (`courseState: "ARCHIVED"`) before they can be deleted
- **Student Submissions**: Course work must be in `PUBLISHED` state to access student submissions
- **User IDs**: Use `me` to refer to the current authenticated user
- **Timestamps**: Dates use `{year, month, day}` format; times use `{hours, minutes}` format
- **IMPORTANT**: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request, invalid argument, or precondition failed |
| 401 | Invalid API key or expired token |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict (e.g., user already enrolled) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Google Classroom API |

### Common Errors

**Precondition check failed (400)**
- When deleting a course: Course must be archived first
- When listing submissions: Course work must be published

**Permission denied (403)**
- User doesn't have required role (teacher/owner) for the operation
- Attempting to access guardian information without proper scopes

## Resources

- [Google Classroom API Documentation](https://developers.google.com/workspace/classroom/reference/rest)
- [Course Resource Reference](https://developers.google.com/workspace/classroom/reference/rest/v1/courses)
- [CourseWork Resource Reference](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork)
- [StudentSubmissions Reference](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
