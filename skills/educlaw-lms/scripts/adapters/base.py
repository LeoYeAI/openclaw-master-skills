"""EduClaw LMS Integration — Abstract base adapter.

Defines the common interface all LMS adapters must implement.
Provides shared retry logic and HTTP helpers.
"""
import json
import time
import urllib.request
import urllib.error
import urllib.parse


class LMSAdapterError(Exception):
    """Raised when an LMS API call fails after all retries."""
    def __init__(self, message, http_status=None):
        super().__init__(message)
        self.http_status = http_status


def _http_request(url, method="GET", headers=None, data=None, timeout=30):
    """Make an HTTP request using urllib (stdlib only).

    Args:
        url: Full URL to request.
        method: HTTP method string.
        headers: dict of request headers.
        data: bytes or None for request body.
        timeout: socket timeout in seconds.

    Returns:
        Tuple (status_code, response_body_str).

    Raises:
        LMSAdapterError on network or HTTP error.
    """
    req = urllib.request.Request(url, data=data, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise LMSAdapterError(
            f"HTTP {e.code}: {e.reason} — {body[:200]}", http_status=e.code
        )
    except urllib.error.URLError as e:
        raise LMSAdapterError(f"Network error: {e.reason}")
    except Exception as e:
        raise LMSAdapterError(f"Request failed: {e}")


def _with_retry(fn, max_attempts=3, base_delay=1.0):
    """Call fn() with exponential backoff retry on LMSAdapterError.

    Retries on transient errors (5xx, network). Does NOT retry on 4xx.

    Args:
        fn: Zero-arg callable that may raise LMSAdapterError.
        max_attempts: Maximum number of attempts.
        base_delay: Initial delay in seconds (doubles each retry).

    Returns:
        Return value of fn() on success.

    Raises:
        LMSAdapterError after all attempts exhausted.
    """
    last_error = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except LMSAdapterError as e:
            last_error = e
            # Don't retry on 4xx client errors
            if e.http_status and 400 <= e.http_status < 500:
                raise
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    raise last_error


class BaseLMSAdapter:
    """Abstract base class for all LMS adapters.

    Subclasses must implement:
      - test_connection() → {success, site_name, version, error}
      - sync_term(term_data) → {lms_term_id}
      - sync_course(section_data, term_data, connection) → {lms_course_id, lms_course_url}
      - sync_user(user_data, connection) → {lms_user_id, lms_username, lms_login_email, sync_status}
      - sync_enrollment(enrollment_data, connection) → {enrollment_status}
      - push_assignment(assignment_data, connection) → {lms_assignment_id, lms_assignment_url}
      - update_assignment(assignment_data, lms_assignment_id, connection) → {updated}
      - pull_grades(lms_course_id, lms_assignment_id, connection) → list of grade dicts
      - pull_all_assignments(lms_course_id, connection) → list of assignment dicts

    All methods wrap HTTP calls in _with_retry(). Credential decryption is
    the caller's responsibility; adapters receive plaintext credentials.
    """

    def __init__(self, conn_row, decrypted_creds=None):
        """Initialize adapter with connection config.

        Args:
            conn_row: dict-like row from educlaw_lms_connection.
            decrypted_creds: dict with plaintext credential values:
                {client_secret, site_token, google_credentials}
        """
        if isinstance(conn_row, dict):
            self.conn = conn_row
        else:
            self.conn = dict(conn_row)
        self.creds = decrypted_creds or {}
        self.endpoint_url = (self.conn.get("endpoint_url") or "").rstrip("/")
        self.client_id = self.conn.get("client_id") or ""
        self.client_secret = self.creds.get("client_secret") or ""
        self.site_token = self.creds.get("site_token") or ""
        self.google_credentials = self.creds.get("google_credentials") or ""

    def test_connection(self):
        """Test connectivity and credentials.

        Returns:
            dict with keys: success (bool), site_name (str), version (str), error (str)
        """
        raise NotImplementedError

    def sync_term(self, term_data):
        """Create or update academic term/session in LMS.

        Args:
            term_data: dict with keys: id, name, start_date, end_date

        Returns:
            dict with key: lms_term_id (str)
        """
        raise NotImplementedError

    def sync_course(self, section_data, term_data, connection):
        """Create or update course/class in LMS.

        Args:
            section_data: dict with section fields (course_code, name, etc.)
            term_data: dict with term fields and lms_term_id
            connection: dict with lms connection settings

        Returns:
            dict with keys: lms_course_id (str), lms_course_url (str)
        """
        raise NotImplementedError

    def sync_user(self, user_data, user_type, connection):
        """Create or match user in LMS.

        Args:
            user_data: dict with user fields (email, first_name, last_name, etc.)
            user_type: 'student' or 'instructor'
            connection: dict with lms connection settings

        Returns:
            dict with keys: lms_user_id (str), lms_username (str),
                            lms_login_email (str), sync_status (str)
        """
        raise NotImplementedError

    def sync_enrollment(self, enrollment_data, connection):
        """Enroll user in LMS course.

        Args:
            enrollment_data: dict with lms_course_id, lms_user_id, role, action
            connection: dict with lms connection settings

        Returns:
            dict with key: enrollment_status (str), error (str or None)
        """
        raise NotImplementedError

    def push_assignment(self, assignment_data, connection):
        """Create assignment in LMS.

        Args:
            assignment_data: dict with name, max_points, due_date, is_published,
                             lms_course_id, description, lms_grade_scheme
            connection: dict with lms connection settings

        Returns:
            dict with keys: lms_assignment_id (str), lms_assignment_url (str)
        """
        raise NotImplementedError

    def update_assignment(self, assignment_data, lms_assignment_id, connection):
        """Update existing LMS assignment.

        Args:
            assignment_data: dict with changed fields
            lms_assignment_id: LMS-side assignment ID
            connection: dict with lms connection settings

        Returns:
            dict with key: updated (bool), warning (str or None)
        """
        raise NotImplementedError

    def pull_grades(self, lms_course_id, lms_assignment_id, connection):
        """Pull submission grades for an assignment from LMS.

        Args:
            lms_course_id: LMS course/class ID
            lms_assignment_id: LMS assignment/line-item ID
            connection: dict with lms connection settings

        Returns:
            list of dicts, each with:
                lms_user_id (str), lms_score (str), lms_grade (str),
                lms_submitted_at (str), lms_graded_at (str),
                is_late (int), is_missing (int), lms_comments (str)
        """
        raise NotImplementedError

    def pull_all_assignments(self, lms_course_id, connection):
        """Pull all assignments from an LMS course.

        Args:
            lms_course_id: LMS course/class ID
            connection: dict with lms connection settings

        Returns:
            list of dicts, each with:
                lms_assignment_id (str), name (str), max_points (str),
                due_date (str), lms_grade_scheme (str), is_published (int),
                lms_assignment_url (str)
        """
        raise NotImplementedError
