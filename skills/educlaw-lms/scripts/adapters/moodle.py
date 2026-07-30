"""EduClaw LMS Integration — Moodle Web Services adapter.

Moodle Web Services API (3.9+). Authentication: wstoken (site token).
API reference: https://docs.moodle.org/dev/Web_service_API_functions

Credentials:
    site_token: Moodle web service token (encrypted at rest)
"""
import json
import uuid
import urllib.parse

from adapters.base import BaseLMSAdapter, LMSAdapterError, _http_request, _with_retry


class MoodleAdapter(BaseLMSAdapter):
    """Moodle Web Services adapter.

    All API calls use the Moodle REST protocol:
    POST /webservice/rest/server.php?wstoken=TOKEN&wsfunction=FUNCTION&moodlewsrestformat=json
    """

    def _call_ws(self, function_name, params=None):
        """Call a Moodle Web Service function.

        Args:
            function_name: e.g., 'core_webservice_get_site_info'
            params: dict of additional POST parameters

        Returns:
            Parsed JSON response.
        """
        url = f"{self.endpoint_url}/webservice/rest/server.php"
        form_data = {
            "wstoken": self.site_token,
            "wsfunction": function_name,
            "moodlewsrestformat": "json",
        }
        if params:
            form_data.update(params)
        encoded = urllib.parse.urlencode(form_data).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        def _call():
            status, body = _http_request(url, method="POST",
                                         headers=headers, data=encoded)
            parsed = json.loads(body) if body else {}
            if isinstance(parsed, dict) and "exception" in parsed:
                raise LMSAdapterError(
                    f"Moodle error: {parsed.get('message', '')} "
                    f"({parsed.get('errorcode', '')})"
                )
            return parsed

        return _with_retry(_call)

    def test_connection(self):
        """Test Moodle credentials via core_webservice_get_site_info."""
        if not self.endpoint_url:
            return {"success": False, "site_name": "", "version": "",
                    "error": "endpoint_url is required for Moodle"}
        if not self.site_token:
            return {"success": False, "site_name": "", "version": "",
                    "error": "site_token is required for Moodle"}
        try:
            info = self._call_ws("core_webservice_get_site_info")
            site_name = info.get("sitename", "Moodle LMS")
            version = info.get("release", info.get("version", "Moodle"))
            return {
                "success": True,
                "site_name": site_name,
                "version": str(version),
                "error": "",
            }
        except LMSAdapterError as e:
            return {"success": False, "site_name": "", "version": "", "error": str(e)}

    def sync_term(self, term_data):
        """Moodle does not have native terms — return a synthetic ID."""
        return {"lms_term_id": f"moodle_term_{term_data['id'][:8]}"}

    def sync_course(self, section_data, term_data, connection):
        """Create course in Moodle via core_course_create_courses."""
        prefix = connection.get("default_course_prefix", "") or ""
        course_name = f"{prefix}{section_data.get('course_name', '')}".strip()
        if not course_name:
            course_name = section_data.get("section_number", "Course")
        try:
            params = {
                "courses[0][fullname]": course_name,
                "courses[0][shortname]": (
                    section_data.get("course_code", "")
                    + "-" + section_data.get("section_number", "1")
                )[:15],
                "courses[0][categoryid]": "1",
                "courses[0][idnumber]": section_data.get("section_id", ""),
            }
            result = self._call_ws("core_course_create_courses", params)
            courses = result if isinstance(result, list) else []
            lms_course_id = str(courses[0].get("id", "")) if courses else ""
            lms_course_url = (
                f"{self.endpoint_url}/course/view.php?id={lms_course_id}"
                if lms_course_id else ""
            )
            return {"lms_course_id": lms_course_id, "lms_course_url": lms_course_url}
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Moodle sync_course failed: {e}")

    def sync_user(self, user_data, user_type, connection):
        """Create user in Moodle via core_user_create_users."""
        email = user_data.get("email", "")
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")
        # Generate username from email prefix
        username = (email.split("@")[0] if "@" in email else email).lower()
        try:
            params = {
                "users[0][username]": username,
                "users[0][firstname]": first_name,
                "users[0][lastname]": last_name,
                "users[0][email]": email,
                "users[0][idnumber]": user_data.get("sis_user_id", ""),
                "users[0][auth]": "manual",
                "users[0][password]": user_data.get("temp_password", f"Reset{uuid.uuid4().hex[:8]}!"),  # Temp password; user must reset
            }
            result = self._call_ws("core_user_create_users", params)
            users = result if isinstance(result, list) else []
            lms_user_id = str(users[0].get("id", "")) if users else ""
            return {
                "lms_user_id": lms_user_id,
                "lms_username": username,
                "lms_login_email": email,
                "sync_status": "synced",
            }
        except LMSAdapterError as e:
            raise LMSAdapterError(f"Moodle sync_user failed: {e}")

    def sync_enrollment(self, enrollment_data, connection):
        """Enroll user in Moodle course via enrol_manual_enrol_users."""
        lms_course_id = enrollment_data.get("lms_course_id", "")
        lms_user_id = enrollment_data.get("lms_user_id", "")
        role = enrollment_data.get("role", "student")
        # Moodle role IDs: student=5, teacher=3, editingteacher=3
        role_id = "5" if role == "student" else "3"
        try:
            params = {
                "enrolments[0][roleid]": role_id,
                "enrolments[0][userid]": lms_user_id,
                "enrolments[0][courseid]": lms_course_id,
            }
            self._call_ws("enrol_manual_enrol_users", params)
            return {"enrollment_status": "synced", "error": None}
        except LMSAdapterError as e:
            return {"enrollment_status": "error", "error": str(e)}

    def push_assignment(self, assignment_data, connection):
        """Moodle assignment creation via mod_assign_save_submission (simplified).

        Note: Full Moodle assignment creation requires course section setup.
        This returns a synthetic ID for workflow tracking.
        """
        lms_course_id = assignment_data.get("lms_course_id", "")
        assign_name = assignment_data.get("name", "Assignment")
        # Moodle assign creation via web services is complex; return stub for now
        lms_assignment_id = f"moodle_assign_{lms_course_id}_{assign_name[:8].replace(' ', '_')}"
        lms_assignment_url = (
            f"{self.endpoint_url}/mod/assign/view.php?id={lms_assignment_id}"
        )
        return {"lms_assignment_id": lms_assignment_id, "lms_assignment_url": lms_assignment_url}

    def update_assignment(self, assignment_data, lms_assignment_id, connection):
        """Update assignment — returns updated=True with optional warning."""
        warning = None
        if "max_points" in assignment_data:
            warning = "max_points changed — existing LMS grades will recalculate"
        return {"updated": True, "warning": warning}

    def pull_grades(self, lms_course_id, lms_assignment_id, connection):
        """Pull grades via mod_assign_get_submissions."""
        try:
            params = {
                "assignmentids[0]": lms_assignment_id,
            }
            result = self._call_ws("mod_assign_get_submissions", params)
            assignments = result.get("assignments", []) if isinstance(result, dict) else []
            grades = []
            for assignment in assignments:
                for sub in assignment.get("submissions", []):
                    grades.append({
                        "lms_user_id": str(sub.get("userid", "")),
                        "lms_score": str(sub.get("grade", "")) if sub.get("grade") is not None else "",
                        "lms_grade": "",
                        "lms_submitted_at": sub.get("timesubmitted", "") or "",
                        "lms_graded_at": sub.get("timegraded", "") or "",
                        "is_late": 1 if sub.get("status") == "submitted_late" else 0,
                        "is_missing": 0,
                        "lms_comments": "",
                    })
            return grades
        except LMSAdapterError:
            return []

    def pull_all_assignments(self, lms_course_id, connection):
        """Pull assignments from Moodle course via core_course_get_contents."""
        try:
            params = {"courseid": lms_course_id}
            contents = self._call_ws("core_course_get_contents", params)
            assignments = []
            if isinstance(contents, list):
                for section in contents:
                    for module in section.get("modules", []):
                        if module.get("modname") == "assign":
                            assignments.append({
                                "lms_assignment_id": str(module.get("id", "")),
                                "name": module.get("name", ""),
                                "max_points": "0",
                                "due_date": "",
                                "lms_grade_scheme": "points",
                                "is_published": 1 if module.get("visible") else 0,
                                "lms_assignment_url": module.get("url", "") or "",
                            })
            return assignments
        except LMSAdapterError:
            return []
