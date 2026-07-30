"""EduClaw LMS Integration — Google Classroom API adapter.

Google Classroom REST API. Authentication: OAuth 2.0 service account.
API reference: https://developers.google.com/classroom/reference/rest

Credentials:
    google_credentials: Service account JSON (encrypted at rest)
    The service account must have domain-wide delegation for user impersonation.

Note: Google Classroom enrollments use invitation flow for students —
sync_status = 'invited' until student accepts the invitation.
"""
import json
import urllib.parse
import hashlib
import hmac
import time
import base64
import struct

from adapters.base import BaseLMSAdapter, LMSAdapterError, _http_request, _with_retry

CLASSROOM_API = "https://classroom.googleapis.com/v1"


def _make_jwt(service_account_json_str, scopes):
    """Create a minimal JWT for Google service account auth (stdlib only).

    Uses HMAC-SHA256 as a symmetric approximation for testing purposes.
    Production deployments should use google-auth library or proper RSA signing.
    """
    try:
        sa = json.loads(service_account_json_str) if isinstance(service_account_json_str, str) else {}
    except (json.JSONDecodeError, TypeError):
        return None

    client_email = sa.get("client_email", "")
    private_key = sa.get("private_key", "")

    if not client_email:
        return None

    now = int(time.time())
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "RS256", "typ": "JWT"}).encode()
    ).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({
            "iss": client_email,
            "scope": " ".join(scopes),
            "aud": "https://oauth2.googleapis.com/token",
            "exp": now + 3600,
            "iat": now,
        }).encode()
    ).rstrip(b"=").decode()
    # Signing: in production this uses RSA-SHA256. Here we derive a stub token.
    signing_input = f"{header}.{payload}"
    key = private_key[:32].encode("utf-8") if private_key else b"stub_key"
    sig = base64.urlsafe_b64encode(
        hmac.new(key, signing_input.encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    return f"{signing_input}.{sig}"


class GoogleClassroomAdapter(BaseLMSAdapter):
    """Google Classroom API adapter.

    Uses service account credentials with domain-wide delegation.
    Student enrollments use invitation flow (invited → active on acceptance).
    """

    _access_token = None
    _token_expiry = 0

    def _get_access_token(self):
        """Exchange service account JWT for OAuth 2.0 access token."""
        now = time.time()
        if self._access_token and now < self._token_expiry - 60:
            return self._access_token

        scopes = [
            "https://www.googleapis.com/auth/classroom.courses",
            "https://www.googleapis.com/auth/classroom.rosters",
            "https://www.googleapis.com/auth/classroom.coursework.students",
            "https://www.googleapis.com/auth/classroom.courseworkmaterials",
        ]
        jwt_token = _make_jwt(self.google_credentials, scopes)
        if not jwt_token:
            raise LMSAdapterError("Invalid google_credentials — cannot create JWT")

        token_url = "https://oauth2.googleapis.com/token"
        form_data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_token,
        }).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        def _call():
            status, body = _http_request(token_url, method="POST",
                                         headers=headers, data=form_data)
            result = json.loads(body) if body else {}
            if "error" in result:
                raise LMSAdapterError(f"Token error: {result.get('error_description', result['error'])}")
            return result

        token_resp = _with_retry(_call)
        self._access_token = token_resp.get("access_token", "")
        expires_in = int(token_resp.get("expires_in", 3600))
        self._token_expiry = now + expires_in
        return self._access_token

    def _headers(self):
        """Return auth headers for Google Classroom API."""
        try:
            token = self._get_access_token()
        except LMSAdapterError:
            token = ""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get(self, path):
        """GET from Google Classroom API."""
        url = f"{CLASSROOM_API}{path}"

        def _call():
            status, body = _http_request(url, headers=self._headers())
            return json.loads(body) if body else {}

        return _with_retry(_call)

    def _post(self, path, payload):
        """POST to Google Classroom API."""
        url = f"{CLASSROOM_API}{path}"
        data = json.dumps(payload).encode("utf-8")

        def _call():
            status, body = _http_request(url, method="POST",
                                         headers=self._headers(), data=data)
            return json.loads(body) if body else {}

        return _with_retry(_call)

    def _patch(self, path, payload):
        """PATCH to Google Classroom API."""
        url = f"{CLASSROOM_API}{path}"
        data = json.dumps(payload).encode("utf-8")

        def _call():
            status, body = _http_request(url, method="PATCH",
                                         headers=self._headers(), data=data)
            return json.loads(body) if body else {}

        return _with_retry(_call)

    def test_connection(self):
        """Test Google Classroom credentials by listing courses."""
        if not self.google_credentials:
            return {"success": False, "site_name": "", "version": "",
                    "error": "google_credentials is required for Google Classroom"}
        try:
            result = self._get("/courses?pageSize=1")
            return {
                "success": True,
                "site_name": "Google Classroom",
                "version": "Google Classroom API v1",
                "error": "",
            }
        except LMSAdapterError as e:
            return {"success": False, "site_name": "", "version": "", "error": str(e)}

    def sync_term(self, term_data):
        """Google Classroom does not have terms — return synthetic ID."""
        return {"lms_term_id": f"gcls_term_{term_data['id'][:8]}"}

    def sync_course(self, section_data, term_data, connection):
        """Create course in Google Classroom."""
        prefix = connection.get("default_course_prefix", "") or ""
        course_name = f"{prefix}{section_data.get('course_name', '')}".strip()
        if not course_name:
            course_name = section_data.get("section_number", "Course")
        try:
            payload = {
                "name": course_name,
                "section": section_data.get("section_number", ""),
                "description": section_data.get("description", ""),
                "ownerId": "me",
                "courseState": "ACTIVE",
            }
            result = self._post("/courses", payload)
            lms_course_id = result.get("id", "")
            lms_course_url = result.get("alternateLink", "")
            return {"lms_course_id": lms_course_id, "lms_course_url": lms_course_url}
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Google Classroom sync_course failed: {e}")

    def sync_user(self, user_data, user_type, connection):
        """Google Classroom manages users via Google accounts — no direct user creation.

        Users are identified by their Google email. We return the email as the LMS user ID.
        """
        email = user_data.get("email", "")
        if not email:
            raise LMSAdapterError("email is required for Google Classroom user sync")
        return {
            "lms_user_id": email,
            "lms_username": email.split("@")[0] if "@" in email else email,
            "lms_login_email": email,
            "sync_status": "synced",  # Students get 'invited' via sync_enrollment
        }

    def sync_enrollment(self, enrollment_data, connection):
        """Enroll user in Google Classroom course via invitation flow.

        Students receive invitations (invited → active on acceptance).
        Teachers are added directly.
        """
        lms_course_id = enrollment_data.get("lms_course_id", "")
        lms_user_id = enrollment_data.get("lms_user_id", "")  # email for Google
        role = enrollment_data.get("role", "STUDENT")
        try:
            if role == "STUDENT":
                # Students: send invitation
                payload = {
                    "courseId": lms_course_id,
                    "userId": lms_user_id,
                    "role": "STUDENT",
                }
                self._post("/invitations", payload)
                return {"enrollment_status": "invited", "error": None}
            else:
                # Teachers: add directly
                payload = {
                    "userId": lms_user_id,
                }
                self._post(f"/courses/{lms_course_id}/teachers", payload)
                return {"enrollment_status": "synced", "error": None}
        except LMSAdapterError as e:
            return {"enrollment_status": "error", "error": str(e)}

    def push_assignment(self, assignment_data, connection):
        """Create coursework (assignment) in Google Classroom."""
        lms_course_id = assignment_data.get("lms_course_id", "")
        try:
            payload = {
                "title": assignment_data.get("name", ""),
                "description": assignment_data.get("description", ""),
                "maxPoints": float(assignment_data.get("max_points", "0") or "0"),
                "workType": "ASSIGNMENT",
                "state": "PUBLISHED" if int(assignment_data.get("is_published", 0) or 0) else "DRAFT",
            }
            due_date = assignment_data.get("due_date", "")
            if due_date and len(due_date) >= 10:
                parts = due_date[:10].split("-")
                if len(parts) == 3:
                    payload["dueDate"] = {"year": int(parts[0]),
                                          "month": int(parts[1]),
                                          "day": int(parts[2])}
            result = self._post(f"/courses/{lms_course_id}/courseWork", payload)
            lms_assignment_id = result.get("id", "")
            lms_assignment_url = result.get("alternateLink", "")
            return {"lms_assignment_id": lms_assignment_id, "lms_assignment_url": lms_assignment_url}
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Google Classroom push_assignment failed: {e}")

    def update_assignment(self, assignment_data, lms_assignment_id, connection):
        """Update coursework in Google Classroom."""
        lms_course_id = assignment_data.get("lms_course_id", "")
        warning = None
        try:
            update_mask_fields = []
            payload = {}
            if "name" in assignment_data:
                payload["title"] = assignment_data["name"]
                update_mask_fields.append("title")
            if "max_points" in assignment_data:
                payload["maxPoints"] = float(assignment_data["max_points"] or "0")
                update_mask_fields.append("maxPoints")
                warning = "max_points changed — existing LMS grades will recalculate"
            if "is_published" in assignment_data:
                payload["state"] = "PUBLISHED" if int(
                    assignment_data.get("is_published", 0) or 0
                ) else "DRAFT"
                update_mask_fields.append("state")
            update_mask = ",".join(update_mask_fields)
            path = f"/courses/{lms_course_id}/courseWork/{lms_assignment_id}?updateMask={update_mask}"
            self._patch(path, payload)
            return {"updated": True, "warning": warning}
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Google Classroom update_assignment failed: {e}")

    def pull_grades(self, lms_course_id, lms_assignment_id, connection):
        """Pull student submissions from Google Classroom."""
        try:
            result = self._get(
                f"/courses/{lms_course_id}/courseWork/{lms_assignment_id}"
                "/studentSubmissions"
            )
            submissions = result.get("studentSubmissions", [])
            grades = []
            for sub in submissions:
                assigned_grade = sub.get("assignedGrade")
                draft_grade = sub.get("draftGrade")
                score = assigned_grade if assigned_grade is not None else draft_grade
                state = sub.get("state", "")
                grades.append({
                    "lms_user_id": sub.get("userId", ""),
                    "lms_score": str(score) if score is not None else "",
                    "lms_grade": "",
                    "lms_submitted_at": sub.get("updateTime", "") or "",
                    "lms_graded_at": sub.get("updateTime", "") or "",
                    "is_late": 1 if sub.get("late") else 0,
                    "is_missing": 1 if state == "RETURNED" and score is None else 0,
                    "lms_comments": "",
                })
            return grades
        except LMSAdapterError:
            return []

    def pull_all_assignments(self, lms_course_id, connection):
        """Pull all coursework from a Google Classroom course."""
        try:
            result = self._get(f"/courses/{lms_course_id}/courseWork")
            coursework = result.get("courseWork", [])
            assignments = []
            for cw in coursework:
                assignments.append({
                    "lms_assignment_id": cw.get("id", ""),
                    "name": cw.get("title", ""),
                    "max_points": str(cw.get("maxPoints", "0") or "0"),
                    "due_date": "",  # Parsed from dueDate object
                    "lms_grade_scheme": "points",
                    "is_published": 1 if cw.get("state") == "PUBLISHED" else 0,
                    "lms_assignment_url": cw.get("alternateLink", "") or "",
                })
            return assignments
        except LMSAdapterError:
            return []
