"""Requirements parsing module for CSV Documentation Generator

Parses source code to extract requirements, detects electronic signature needs,
and manages the requirements database.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime


STANDARD_MODULES = {
    "user_mgmt": {
        "name": "用户管理 / User Management",
        "name_cn": "用户管理",
        "prefix": "UM",
        "keywords": [
            "用户",
            "user",
            "账户",
            "account",
            "登录",
            "login",
            "认证",
            "auth",
            "密码",
            "password",
            "角色",
            "role",
            "权限",
            "permission",
        ],
    },
    "audit_trail": {
        "name": "审计追踪 / Audit Trail",
        "name_cn": "审计追踪",
        "prefix": "AT",
        "keywords": ["审计", "audit", "日志", "log", "追踪", "trace", "记录", "record"],
    },
    "data_mgmt": {
        "name": "数据管理 / Data Management",
        "name_cn": "数据管理",
        "prefix": "DM",
        "keywords": [
            "数据",
            "data",
            "数据库",
            "database",
            "存储",
            "storage",
            "备份",
            "backup",
            "恢复",
            "recovery",
        ],
    },
    "business_func": {
        "name": "业务功能 / Business Functions",
        "name_cn": "业务功能",
        "prefix": "BF",
        "keywords": [
            "业务",
            "business",
            "功能",
            "function",
            "流程",
            "process",
            "工作流",
            "workflow",
        ],
    },
    "reporting": {
        "name": "报告功能 / Reporting",
        "name_cn": "报告功能",
        "prefix": "RP",
        "keywords": ["报告", "report", "导出", "export", "打印", "print", "报表"],
    },
    "integration": {
        "name": "接口集成 / Integration",
        "name_cn": "接口集成",
        "prefix": "INT",
        "keywords": ["接口", "api", "integration", "集成", "对接", "integration"],
    },
    "security": {
        "name": "安全 / Security",
        "name_cn": "安全",
        "prefix": "SEC",
        "keywords": [
            "安全",
            "security",
            "加密",
            "encrypt",
            "解密",
            "decrypt",
            "TLS",
            "SSL",
            "防火墙",
            "firewall",
        ],
    },
    "compliance": {
        "name": "合规 / Compliance",
        "name_cn": "合规",
        "prefix": "CMP",
        "keywords": [
            "合规",
            "compliance",
            "法规",
            "regulation",
            "ALCOA",
            "Part 11",
            "Annex 11",
            "GxP",
        ],
    },
}


@dataclass
class TestCaseLink:
    """Represents a link to a test case"""

    type: str  # IQ, OQ, PQ
    id: str
    description: str = ""


@dataclass
class Requirement:
    """Represents a single requirement"""

    id: str
    type: str  # URS, FS, TS
    description: str
    priority: str  # 必须, 应该, 可以
    module: str = "business_func"  # default module
    risk_level: str = "M"  # H (High), M (Medium), L (Low)
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    esig_required: bool = False
    esig_category: Optional[str] = None
    fs_ref: Optional[str] = None
    ts_ref: Optional[str] = None
    test_cases: List[TestCaseLink] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: str = "draft"  # draft, verified, failed

    def __post_init__(self):
        if self.test_cases is None:
            self.test_cases = []
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class RequirementsParser:
    """Parse source code to extract requirements"""

    # Comment patterns for requirement markers
    # New standardized format: @REQ URS-001 - description
    COMMENT_PATTERNS = [
        r"//\s*@REQ\s+(URS-\d{3})\s*-\s*(.+)",  # // @REQ URS-001 - description
        r"#\s*@REQ\s+(URS-\d{3})\s*-\s*(.+)",  # # @REQ URS-001 - description
        r"/\*\s*@REQ\s+(URS-\d{3})\s*-\s*(.+?)\*/",  # /* @REQ URS-001 - description */
        r"<!--\s*@REQ\s+(URS-\d{3})\s*-\s*(.+)-->",  # <!-- @REQ URS-001 - description -->
        r"@req\s+(?!URS)(\w+-\d+)\s+(.+)",  # @req ABC-001 description (legacy, must not start with URS)
        r"@requirement\s+(?!URS)(\w+-\d+)\s+(.+)",  # @requirement ABC-001 description (legacy)
        r"#\s*(\w+-\d+)[:\s]+(.+)",  # URS-001: description
        r"#\s*\[(\w+-\d+)\]\s*(.+)",  # [URS-001] description
        r"<!--\s*(\w+-\d+)\s+(.+)-->",  # HTML comment style
    ]

    # Legacy AI-friendly patterns (for backward compatibility)
    # These are kept for old code that uses @URS[module] format
    AI_COMMENT_PATTERNS = [
        r"//\s*@URS\[(\w+)\]\s+(.+)",  # // @URS[user_mgmt] description
        r"#\s*@URS\[(\w+)\]\s+(.+)",  # # @URS[user_mgmt] description
        r"/\*\s*@URS\[(\w+)\]\s+(.+)\*/",  # /* @URS[user_mgmt] description */
        r"--\s*@URS\[(\w+)\]\s+(.+)",  # -- @URS[user_mgmt] description (Haskell/SQL)
    ]

    # Test case association patterns
    TEST_CASE_PATTERNS = [
        r"//\s*@TEST\[(\w+-\w+-\d+)\]\s*-\s*(.*)",  # // @TEST[OQ-UM-001] - description
        r"#\s*@TEST\[(\w+-\w+-\d+)\]\s*-\s*(.*)",  # # @TEST[OQ-UM-001] - description
        r"/\*\s*@TEST\[(\w+-\w+-\d+)\]\s*-\s*(.*?)\*/",  # /* @TEST[OQ-UM-001] - description */
    ]

    # FS/TS reference patterns
    FS_TS_PATTERNS = [
        r"//\s*@FS\s+(FS-\d{3})",  # // @FS FS-001
        r"#\s*@FS\s+(FS-\d{3})",  # # @FS FS-001
        r"//\s*@TS\s+(TS-\d{3})",  # // @TS TS-001
        r"#\s*@TS\s+(TS-\d{3})",  # # @TS TS-001
    ]

    # Risk level patterns
    RISK_PATTERNS = [
        r"//\s*@RISK\s+([HML])",  # // @RISK H
        r"#\s*@RISK\s+([HML])",  # # @RISK H
        r"/\*\s*@RISK\s+([HML])\s*/",  # /* @RISK H */
    ]

    # Priority keywords
    PRIORITY_KEYWORDS = {
        "必须": "必须",
        "must": "必须",
        "required": "必须",
        "应该": "应该",
        "should": "应该",
        "建议": "应该",
        "可以": "可以",
        "could": "可以",
        "may": "可以",
    }

    # eSignature related keywords (configurable)
    ESIG_KEYWORDS = [
        # Chinese
        "签名",
        "签字",
        "签署",
        "电子签名",
        "签章",
        "审核",
        "审批",
        "批准",
        "核验",
        "确认",
        "电子记录",
        "record",
        "approval",
        # English
        "sign",
        "signature",
        "signing",
        "review",
        "approve",
        "authorize",
        "electronic signature",
        "e-sign",
        "digital signature",
        "certified",
    ]

    # eSignature categories
    ESIG_CATEGORIES = {
        "workflow_approval": ["审核", "审批", "批准", "review", "approve", "authorize"],
        "document_signing": ["签名", "sign", "signature", "签署"],
        "record_confirmation": ["确认", "核验", "confirm", "verify"],
        "data_certification": ["认证", "证明", "certify", "certificate"],
    }

    def __init__(
        self, project_path: Optional[Path] = None, config: Optional[Dict] = None
    ):
        self.project_path = project_path or Path.cwd()
        self.config = config or {}
        self.requirements_db = self._load_requirements_db()
        self._load_esig_keywords()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_path = self.project_path / ".csv-docs-config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_esig_keywords(self):
        """Load eSignature keywords from config"""
        compliance_config = self.config.get("compliance", {})
        configured_keywords = compliance_config.get("esig_keywords", [])
        if configured_keywords:
            self.ESIG_KEYWORDS = configured_keywords

    def _load_requirements_db(self) -> Dict[str, Any]:
        """Load requirements database"""
        db_path = self.project_path / "requirements.json"
        if db_path.exists():
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "1.0",
            "requirements": [],
            "risks": [],
            "test_results": [],
            "commit_links": [],
        }

    def _save_requirements_db(self):
        """Save requirements database"""
        db_path = self.project_path / "requirements.json"
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(self.requirements_db, f, indent=2, ensure_ascii=False)

    def _generate_id(self, req_type: str) -> str:
        """Generate next available ID for requirement type"""
        existing = [
            r
            for r in self.requirements_db.get("requirements", [])
            if r.get("id", "").startswith(f"{req_type}-")
        ]

        max_num = 0
        for r in existing:
            try:
                num = int(r["id"].split("-")[1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                continue

        return f"{req_type}-{max_num + 1:03d}"

    def _detect_esig(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect if text relates to electronic signature"""
        text_lower = text.lower()
        for category, keywords in self.ESIG_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return True, category
        return False, None

    def _extract_priority(self, text: str) -> str:
        """Extract priority from text"""
        text_lower = text.lower()
        for keyword, priority in self.PRIORITY_KEYWORDS.items():
            if keyword.lower() in text_lower:
                return priority
        return "应该"  # Default

    def _infer_module(self, text: str, file_path: Optional[str] = None) -> str:
        """Infer module from text and optionally file path"""
        text_lower = text.lower()

        # Check file path first if provided
        if file_path:
            path_lower = file_path.lower()
            for module_id, module_info in STANDARD_MODULES.items():
                for keyword in module_info.get("keywords", []):
                    if keyword.lower() in path_lower:
                        return module_id

        # Then check text content
        for module_id, module_info in STANDARD_MODULES.items():
            for keyword in module_info.get("keywords", []):
                if keyword.lower() in text_lower:
                    return module_id

        return "business_func"  # Default module

    def _infer_risk_level(self, text: str) -> str:
        """Infer risk level from text keywords"""
        text_lower = text.lower()

        # High risk keywords
        high_risk_keywords = [
            "安全",
            "security",
            "加密",
            "encrypt",
            "解密",
            "decrypt",
            "权限",
            "permission",
            "访问控制",
            "access control",
            "合规",
            "compliance",
            "法规",
            "regulation",
            "电子签名",
            "electronic signature",
            "e-sign",
            "审计",
            "audit",
            "critical",
        ]

        # Low risk keywords
        low_risk_keywords = [
            "简单",
            "simple",
            "基础",
            "basic",
            "文档",
            "documentation",
            "报表",
            "report",
        ]

        for keyword in high_risk_keywords:
            if keyword.lower() in text_lower:
                return "H"

        for keyword in low_risk_keywords:
            if keyword.lower() in text_lower:
                return "L"

        return "M"  # Default medium risk

    def _parse_requirement_from_match(
        self, match: re.Match, file_path: str, line_num: int
    ) -> Optional[Requirement]:
        """Parse a requirement from regex match"""
        groups = match.groups()

        # Try to extract ID and description
        if len(groups) == 2:
            req_id = groups[0]
            description = groups[1]
        elif len(groups) == 1:
            req_id = None
            description = groups[0]
        else:
            return None

        if not description or len(description.strip()) < 3:
            return None

        # Determine type from ID or file analysis
        req_type = "URS"  # Default
        if req_id:
            prefix = req_id.split("-")[0] if "-" in req_id else req_id[:3]
            if prefix.upper() in ["URS", "FS", "TS"]:
                req_type = prefix.upper()
        else:
            # Infer from file path
            path_lower = file_path.lower()
            if "test" in path_lower or "_test" in path_lower:
                req_type = "TS"
            elif "spec" in path_lower or "feature" in path_lower:
                req_type = "FS"

        # Generate ID if not provided
        if not req_id:
            req_id = self._generate_id(req_type)

        # Extract priority
        priority = self._extract_priority(description)

        # Detect eSignature requirement
        esig_required, esig_category = self._detect_esig(description)

        # Infer module from description
        module = self._infer_module(description, file_path)

        # Infer risk level from description keywords
        risk_level = self._infer_risk_level(description)

        return Requirement(
            id=req_id,
            type=req_type,
            description=description.strip(),
            priority=priority,
            module=module,
            risk_level=risk_level,
            source_file=file_path,
            source_line=line_num,
            esig_required=esig_required,
            esig_category=esig_category,
            status="draft",
        )

    def parse_file(self, file_path: Path) -> List[Requirement]:
        """Parse a single file for requirements"""
        requirements = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (UnicodeDecodeError, IOError):
            return requirements

        for line_num, line in enumerate(lines, 1):
            # Try standard patterns first
            for pattern in self.COMMENT_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    req = self._parse_requirement_from_match(
                        match, str(file_path), line_num
                    )
                    if req:
                        requirements.append(req)
                        break

            # Then try AI-friendly patterns
            for pattern in self.AI_COMMENT_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    req = self._parse_ai_requirement_from_match(
                        match, str(file_path), line_num
                    )
                    if req:
                        requirements.append(req)
                        break

        return requirements

    def _parse_ai_requirement_from_match(
        self, match: re.Match, file_path: str, line_num: int
    ) -> Optional[Requirement]:
        """Parse an AI-friendly requirement marker like @URS[module] description"""
        groups = match.groups()

        if len(groups) < 2:
            return None

        module = groups[0]
        description = groups[1].strip()

        if not description or len(description) < 3:
            return None

        if module not in STANDARD_MODULES:
            return None

        esig_required, esig_category = self._detect_esig(description)
        priority = self._extract_priority(description)
        req_id = self._generate_id("URS")

        return Requirement(
            id=req_id,
            type="URS",
            description=description,
            priority=priority,
            module=module,
            source_file=file_path,
            source_line=line_num,
            esig_required=esig_required,
            esig_category=esig_category,
            status="draft",
        )

    def parse_directory(
        self, directory: Path, extensions: Optional[List[str]] = None
    ) -> List[Requirement]:
        """Parse all files in a directory"""
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".java", ".cs", ".go", ".rs"]

        all_requirements = []

        for ext in extensions:
            for file_path in directory.rglob(f"*{ext}"):
                # Skip common non-source directories
                skip_dirs = [
                    "node_modules",
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".git",
                    "test",
                    "tests",
                ]
                if any(skip in file_path.parts for skip in skip_dirs):
                    continue

                requirements = self.parse_file(file_path)
                all_requirements.extend(requirements)

        return all_requirements

    def add_requirement(
        self,
        description: str,
        req_type: str = "URS",
        priority: Optional[str] = None,
        module: Optional[str] = None,
        source_file: Optional[str] = None,
        source_line: Optional[int] = None,
    ) -> Requirement:
        """Manually add a requirement"""
        esig_required, esig_category = self._detect_esig(description)

        if not priority:
            priority = self._extract_priority(description)

        inferred_module: str = module if module else self._infer_module(description)

        req_id = self._generate_id(req_type)

        requirement = Requirement(
            id=req_id,
            type=req_type,
            description=description,
            priority=priority,
            module=inferred_module,
            source_file=source_file,
            source_line=source_line,
            esig_required=esig_required,
            esig_category=esig_category,
            status="draft",
        )

        self.requirements_db.setdefault("requirements", []).append(asdict(requirement))
        self._save_requirements_db()

        return requirement

    def get_requirements(
        self,
        req_type: Optional[str] = None,
        esig_only: bool = False,
        status: Optional[str] = None,
    ) -> List[Requirement]:
        """Get requirements with optional filters"""
        requirements = [
            Requirement(**r) for r in self.requirements_db.get("requirements", [])
        ]

        if req_type:
            requirements = [r for r in requirements if r.type == req_type]

        if esig_only:
            requirements = [r for r in requirements if r.esig_required]

        if status:
            requirements = [r for r in requirements if r.status == status]

        return requirements

    def update_requirement(self, req_id: str, **kwargs) -> bool:
        """Update a requirement by ID"""
        for req in self.requirements_db.get("requirements", []):
            if req.get("id") == req_id:
                req.update(kwargs)
                req["updated_at"] = datetime.now().isoformat()
                self._save_requirements_db()
                return True
        return False

    def delete_requirement(self, req_id: str) -> bool:
        """Delete a requirement by ID"""
        requirements = self.requirements_db.get("requirements", [])
        for i, req in enumerate(requirements):
            if req.get("id") == req_id:
                requirements.pop(i)
                self._save_requirements_db()
                return True
        return False

    def get_esig_requirements(self) -> List[Requirement]:
        """Get all requirements that require electronic signature"""
        return self.get_requirements(esig_only=True)

    def get_next_id(self, req_type: str = "URS") -> str:
        """Get the next available ID for a requirement type"""
        return self._generate_id(req_type)
