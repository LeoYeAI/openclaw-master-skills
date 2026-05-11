"""Test results parser module for CSV Documentation Generator

Parses test results from various frameworks (JUnit XML, pytest JSON, etc.)
and updates requirement verification status.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TestResult:
    """Represents a test result"""

    test_id: str
    test_name: str
    status: str  # pass, fail, skip
    duration: Optional[float] = None
    requirement_id: Optional[str] = None
    test_type: Optional[str] = None  # IQ, OQ, PQ
    executed_at: Optional[str] = None
    error_message: Optional[str] = None


class TestResultsParser:
    """Parse test results from various formats"""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.requirements_db = self._load_requirements_db()

    def _load_requirements_db(self) -> Dict[str, Any]:
        """Load requirements database"""
        db_path = self.project_path / "requirements.json"
        if db_path.exists():
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"test_results": []}

    def _save_test_results(self):
        """Save test results to database"""
        db_path = self.project_path / "requirements.json"
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(self.requirements_db, f, indent=2, ensure_ascii=False)

    def parse_junit_xml(self, xml_path: Path) -> List[TestResult]:
        """Parse JUnit XML format (from Maven, Gradle, etc.)"""
        results = []

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for testcase in root.iter("testcase"):
                test_id = testcase.get("name", "unknown")
                classname = testcase.get("classname", "")

                # Determine status
                status = "pass"
                error_msg = None

                if testcase.find("failure") is not None:
                    status = "fail"
                    failure = testcase.find("failure")
                    error_msg = (
                        failure.get("message", "") if failure is not None else None
                    )
                elif testcase.find("skipped") is not None:
                    status = "skip"

                # Extract duration
                duration_str = testcase.get("time")
                duration = float(duration_str) if duration_str else None

                # Try to link to requirement ID
                requirement_id = self._extract_requirement_id(
                    classname
                ) or self._extract_requirement_id(test_id)

                result = TestResult(
                    test_id=classname + "." + test_id if classname else test_id,
                    test_name=test_id,
                    status=status,
                    duration=duration,
                    requirement_id=requirement_id,
                    test_type=self._infer_test_type(test_id),
                    executed_at=datetime.now().isoformat(),
                    error_message=error_msg,
                )
                results.append(result)

        except Exception as e:
            print(f"Error parsing JUnit XML: {e}")

        return results

    def parse_pytest_json(self, json_path: Path) -> List[TestResult]:
        """Parse pytest JSON format"""
        results = []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for test in data.get("tests", []):
                test_id = test.get("nodeid", "unknown")
                outcome = test.get("outcome", "unknown")

                status = "pass"
                if outcome == "failed":
                    status = "fail"
                elif outcome == "skipped":
                    status = "skip"

                duration = test.get("duration")

                # Extract requirement ID from test nodeid
                requirement_id = self._extract_requirement_id(test_id)

                result = TestResult(
                    test_id=test_id,
                    test_name=test.get("name", test_id),
                    status=status,
                    duration=duration,
                    requirement_id=requirement_id,
                    test_type=self._infer_test_type(test_id),
                    executed_at=datetime.now().isoformat(),
                    error_message=test.get("longrepr"),
                )
                results.append(result)

        except Exception as e:
            print(f"Error parsing pytest JSON: {e}")

        return results

    def parse_nunit_xml(self, xml_path: Path) -> List[TestResult]:
        """Parse NUnit XML format"""
        results = []

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for testcase in root.iter("test-case"):
                test_id = testcase.get("fullname", testcase.get("name", "unknown"))
                result_state = testcase.get("result", "Unknown")

                status = "pass"
                if result_state in ["Failed", "Error"]:
                    status = "fail"
                elif result_state in ["Skipped", "Inconclusive"]:
                    status = "skip"

                duration_str = testcase.get("duration")
                duration = float(duration_str) if duration_str else None

                requirement_id = self._extract_requirement_id(test_id)

                result = TestResult(
                    test_id=test_id,
                    test_name=testcase.get("name", test_id),
                    status=status,
                    duration=duration,
                    requirement_id=requirement_id,
                    test_type=self._infer_test_type(test_id),
                    executed_at=datetime.now().isoformat(),
                )
                results.append(result)

        except Exception as e:
            print(f"Error parsing NUnit XML: {e}")

        return results

    def parse_directory(self, directory: Path) -> List[TestResult]:
        """Parse all test result files in a directory"""
        all_results = []

        # JUnit XML
        for xml_file in directory.rglob("*.xml"):
            if "junit" in xml_file.name.lower() or "TEST-" in xml_file.name:
                results = self.parse_junit_xml(xml_file)
                all_results.extend(results)

        # pytest JSON
        for json_file in directory.rglob("*.json"):
            if "pytest" in json_file.name.lower() or "test-results" in str(json_file):
                results = self.parse_pytest_json(json_file)
                all_results.extend(results)

        # NUnit XML
        for nunit_xml in directory.rglob("*.xml"):
            if "nunit" in nunit_xml.name.lower():
                results = self.parse_nunit_xml(nunit_xml)
                all_results.extend(results)

        return all_results

    def _extract_requirement_id(self, text: str) -> Optional[str]:
        """Extract requirement ID from test name or class"""
        import re

        pattern = (
            r"\b(URS-\d{3}|FS-\d{3}|TS-\d{3}|IQ-\d{3}|OQ-\d{3}|PQ-\d{3}|RA-\d{3})\b"
        )
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else None

    def _infer_test_type(self, test_id: str) -> str:
        """Infer test type from test ID"""
        test_id_upper = test_id.upper()
        if "IQ-" in test_id_upper:
            return "IQ"
        elif "OQ-" in test_id_upper:
            return "OQ"
        elif "PQ-" in test_id_upper:
            return "PQ"
        elif "TEST" in test_id_upper:
            return "OQ"  # Default to OQ for generic tests
        return "OQ"

    def add_manual_result(
        self,
        test_id: str,
        test_name: str,
        status: str,
        test_type: str = "OQ",
        requirement_id: str = None,
    ) -> TestResult:
        """Manually add a test result"""
        result = TestResult(
            test_id=test_id,
            test_name=test_name,
            status=status,
            requirement_id=requirement_id,
            test_type=test_type,
            executed_at=datetime.now().isoformat(),
        )

        self.requirements_db.setdefault("test_results", []).append(asdict(result))
        self._save_test_results()

        return result

    def get_results(
        self, test_type: Optional[str] = None, status: Optional[str] = None
    ) -> List[TestResult]:
        """Get test results with optional filters"""
        results = [
            TestResult(**tr) for tr in self.requirements_db.get("test_results", [])
        ]

        if test_type:
            results = [r for r in results if r.test_type == test_type]

        if status:
            results = [r for r in results if r.status == status]

        return results

    def get_results_summary(self) -> Dict[str, Any]:
        """Get test results summary"""
        results = self.requirements_db.get("test_results", [])

        total = len(results)
        passed = len([r for r in results if r.get("status") == "pass"])
        failed = len([r for r in results if r.get("status") == "fail"])
        skipped = len([r for r in results if r.get("status") == "skip"])

        by_type = {
            "IQ": {"total": 0, "pass": 0, "fail": 0},
            "OQ": {"total": 0, "pass": 0, "fail": 0},
            "PQ": {"total": 0, "pass": 0, "fail": 0},
        }

        for r in results:
            t = r.get("test_type", "OQ")
            s = r.get("status", "fail")
            if t in by_type:
                by_type[t]["total"] += 1
                if s == "pass":
                    by_type[t]["pass"] += 1
                elif s == "fail":
                    by_type[t]["fail"] += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
            "by_type": by_type,
        }

    def update_requirement_status(self, requirement_id: str, new_status: str) -> bool:
        """Update requirement status based on test results"""
        for req in self.requirements_db.get("requirements", []):
            if req.get("id") == requirement_id:
                req["status"] = new_status
                self._save_test_results()
                return True
        return False

    def link_results_to_requirements(self) -> Dict[str, int]:
        """Link test results to requirements and update requirement status

        Returns:
            Dict with counts of linked, updated, and failed links
        """
        stats = {
            "linked": 0,
            "updated": 0,
            "failed": 0,
            "not_found": 0,
        }

        for result in self.get_results():
            if not result.requirement_id:
                stats["failed"] += 1
                continue

            # Determine new status based on test result
            if result.status == "pass":
                new_status = "verified"
            elif result.status == "fail":
                new_status = "failed"
            else:
                new_status = "pending"

            # Update requirement status
            success = self.update_requirement_status(result.requirement_id, new_status)

            if success:
                stats["linked"] += 1
                stats["updated"] += 1
            else:
                stats["not_found"] += 1

        return stats
