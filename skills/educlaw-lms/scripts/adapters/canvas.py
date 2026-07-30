"""EduClaw LMS Integration — Canvas REST API adapter.

Canvas API v1 (Instructure). Authentication: OAuth 2.0 Bearer token.
API reference: https://canvas.instructure.com/doc/api/

Credentials:
    client_id: Canvas OAuth application client_id
    client_secret: Canvas OAuth application client_secret (encrypted at rest)
    Access token exchange happens at runtime; token stored transiently.
"""
import json
import urllib.parse

from adapters.base import BaseLMSAdapter, LMSAdapterError, _http_request, _with_retry


class CanvasAdapter(BaseLMSAdapter):
    """Canvas LMS REST API adapter.

    Canvas uses OAuth 2.0 with a long-lived access token generated from
    client credentials. For simplicity this adapter uses client_secret as
    the direct Bearer token (Canvas supports both API key and OAuth flows).
    """

    def _headers(self):
        """Return authorization headers for Canvas API."""
        token = self.client_secret or self.site_token
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, path):
        """GET request to Canvas API."""
        url = f"{self.endpoint_url}/api/v1{path}"

        def _call():
            status, body = _http_request(url, headers=self._headers())
            return json.loads(body) if body else {}

        return _with_retry(_call)

    def _post(self, path, payload):
        """POST request to Canvas API."""
        url = f"{self.endpoint_url}/api/v1{path}"
        data = json.dumps(payload).encode("utf-8")

        def _call():
            status, body = _http_request(url, method="POST",
                                         headers=self._headers(), data=data)
            return json.loads(body) if body else {}

        return _with_retry(_call)

    def _put(self, path, payload):
        """PUT request to Canvas API."""
        url = f"{self.endpoint_url}/api/v1{path}"
        data = json.dumps(payload).encode("utf-8")

        def _call():
            status, body = _http_request(url, method="PUT",
                                         headers=self._headers(), data=data)
            return json.loads(body) if body else {}

        return _with_retry(_call)

    def test_connection(self):
        """Test Canvas credentials by calling /api/v1/accounts endpoint."""
        if not self.endpoint_url:
            return {"success": False, "site_name": "", "version": "",
                    "error": "endpoint_url is required for Canvas"}
        if not (self.client_secret or self.site_token):
            return {"success": False, "site_name": "", "version": "",
                    "error": "client_secret or site_token required for Canvas"}
        try:
            result = self._get("/accounts")
            if isinstance(result, list) and result:
                account = result[0]
                site_name = account.get("name", "Canvas LMS")
                return {
                    "success": True,
                    "site_name": site_name,
                    "version": "Canvas (REST API v1)",
                    "error": "",
                }
            return {
                "success": True,
                "site_name": "Canvas LMS",
                "version": "Canvas (REST API v1)",
                "error": "",
            }
        except LMSAdapterError as e:
            return {"success": False, "site_name": "", "version": "", "error": str(e)}

    def sync_term(self, term_data):
        """Create/update enrollment term in Canvas."""
        if not self.endpoint_url:
            return {"lms_term_id": f"canvas_term_{term_data['id'][:8]}"}
        try:
            payload = {
                "enrollment_term": {
                    "name": term_data.get("name", ""),
                    "start_at": term_data.get("start_date", ""),
                    "end_at": term_data.get("end_date", ""),
                }
            }
            # Attempt to create term in root account (account_id=1 is typical default)
            result = self._post("/accounts/1/terms", payload)
            term_id = str(result.get("id", "")) or str(result.get("enrollment_term", {}).get("id", ""))
            return {"lms_term_id": term_id or f"canvas_term_{term_data['id'][:8]}"}
        except LMSAdapterError:
            return {"lms_term_id": f"canvas_term_{term_data['id'][:8]}"}

    def sync_course(self, section_data, term_data, connection):
        """Create/update course in Canvas."""
        prefix = connection.get("default_course_prefix", "") or ""
        course_name = f"{prefix}{section_data.get('course_name', '')}".strip()
        if not course_name:
            course_name = section_data.get("section_number", "Course")
        try:
            payload = {
                "course": {
                    "name": course_name,
                    "course_code": section_data.get("course_code", ""),
                    "term_id": term_data.get("lms_term_id", ""),
                    "sis_course_id": section_data.get("section_id", ""),
                    "syllabus_body": section_data.get("description", ""),
                }
            }
            result = self._post("/accounts/1/courses", payload)
            lms_course_id = str(result.get("id", ""))
            lms_course_url = f"{self.endpoint_url}/courses/{lms_course_id}" if lms_course_id else ""
            return {"lms_course_id": lms_course_id, "lms_course_url": lms_course_url}
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Canvas sync_course failed: {e}")

    def sync_user(self, user_data, user_type, connection):
        """Create/match user in Canvas."""
        email = user_data.get("email", "")
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")
        try:
            payload = {
                "user": {
                    "name": f"{first_name} {last_name}".strip(),
                    "short_name": first_name,
                    "sis_user_id": user_data.get("sis_user_id", ""),
                },
                "pseudonym": {
                    "unique_id": email,
                    "send_confirmation": False,
                }
            }
            result = self._post("/accounts/1/users", payload)
            lms_user_id = str(result.get("id", ""))
            return {
                "lms_user_id": lms_user_id,
                "lms_username": email,
                "lms_login_email": email,
                "sync_status": "synced",
            }
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Canvas sync_user failed: {e}")

    def sync_enrollment(self, enrollment_data, connection):
        """Enroll user in Canvas course."""
        lms_course_id = enrollment_data.get("lms_course_id", "")
        lms_user_id = enrollment_data.get("lms_user_id", "")
        role = enrollment_data.get("role", "StudentEnrollment")  # or TeacherEnrollment
        try:
            payload = {
                "enrollment": {
                    "user_id": lms_user_id,
                    "type": role,
                    "enrollment_state": "active",
                }
            }
            self._post(f"/courses/{lms_course_id}/enrollments", payload)
            return {"enrollment_status": "synced", "error": None}
        except LMSAdapterError as e:
            return {"enrollment_status": "error", "error": str(e)}

    def push_assignment(self, assignment_data, connection):
        """Create assignment in Canvas course."""
        lms_course_id = assignment_data.get("lms_course_id", "")
        try:
            grading_type = assignment_data.get("lms_grade_scheme", "points")
            if grading_type not in ("points", "percentage", "pass_fail", "letter_grade"):
                grading_type = "points"
            payload = {
                "assignment": {
                    "name": assignment_data.get("name", ""),
                    "points_possible": float(assignment_data.get("max_points", "0") or "0"),
                    "due_at": assignment_data.get("due_date", "") or None,
                    "grading_type": grading_type,
                    "published": bool(int(assignment_data.get("is_published", 0) or 0)),
                    "description": assignment_data.get("description", ""),
                }
            }
            result = self._post(f"/courses/{lms_course_id}/assignments", payload)
            lms_assignment_id = str(result.get("id", ""))
            lms_assignment_url = result.get("html_url", "")
            if not lms_assignment_url and lms_assignment_id:
                lms_assignment_url = f"{self.endpoint_url}/courses/{lms_course_id}/assignments/{lms_assignment_id}"
            return {"lms_assignment_id": lms_assignment_id, "lms_assignment_url": lms_assignment_url}
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Canvas push_assignment failed: {e}")

    def update_assignment(self, assignment_data, lms_assignment_id, connection):
        """Update existing Canvas assignment."""
        lms_course_id = assignment_data.get("lms_course_id", "")
        warning = None
        try:
            payload = {"assignment": {}}
            if "name" in assignment_data:
                payload["assignment"]["name"] = assignment_data["name"]
            if "max_points" in assignment_data:
                payload["assignment"]["points_possible"] = float(
                    assignment_data["max_points"] or "0"
                )
                warning = "max_points changed — existing LMS grades will recalculate"
            if "due_date" in assignment_data:
                payload["assignment"]["due_at"] = assignment_data["due_date"] or None
            if "is_published" in assignment_data:
                payload["assignment"]["published"] = bool(int(
                    assignment_data.get("is_published", 0) or 0
                ))
            self._put(f"/courses/{lms_course_id}/assignments/{lms_assignment_id}", payload)
            return {"updated": True, "warning": warning}
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Canvas update_assignment failed: {e}")

    def pull_grades(self, lms_course_id, lms_assignment_id, connection):
        """Pull submission grades from Canvas."""
        try:
            submissions = self._get(
                f"/courses/{lms_course_id}/assignments/{lms_assignment_id}/submissions"
                "?include[]=submission_comments"
            )
            if not isinstance(submissions, list):
                return []
            grades = []
            for sub in submissions:
                score = sub.get("score")
                grades.append({
                    "lms_user_id": str(sub.get("user_id", "")),
                    "lms_score": str(score) if score is not None else "",
                    "lms_grade": sub.get("grade", "") or "",
                    "lms_submitted_at": sub.get("submitted_at", "") or "",
                    "lms_graded_at": sub.get("graded_at", "") or "",
                    "is_late": 1 if sub.get("late") else 0,
                    "is_missing": 1 if sub.get("missing") else 0,
                    "lms_comments": "; ".join(
                        c.get("comment", {}).get("body", "")
                        for c in sub.get("submission_comments", [])
                    ),
                })
            return grades
        except LMSAdapterError:
            return []

    def pull_all_assignments(self, lms_course_id, connection):
        """Pull all assignments from a Canvas course."""
        try:
            assignments = self._get(f"/courses/{lms_course_id}/assignments")
            if not isinstance(assignments, list):
                return []
            result = []
            for a in assignments:
                result.append({
                    "lms_assignment_id": str(a.get("id", "")),
                    "name": a.get("name", ""),
                    "max_points": str(a.get("points_possible", "0") or "0"),
                    "due_date": a.get("due_at", "") or "",
                    "lms_grade_scheme": a.get("grading_type", "points") or "points",
                    "is_published": 1 if a.get("published") else 0,
                    "lms_assignment_url": a.get("html_url", "") or "",
                })
            return result
        except LMSAdapterError:
            return []
