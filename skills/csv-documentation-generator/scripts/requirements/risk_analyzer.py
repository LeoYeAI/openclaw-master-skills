"""Risk Analyzer module for CSV Documentation Generator

Performs automatic risk assessment based on requirements and GAMP category.
Uses FMEA methodology with RPN calculation.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Risk:
    """Represents a single risk"""

    id: str
    risk_description: str
    requirement_id: Optional[str]
    severity: int
    likelihood: int
    detectability: int
    rpn: int
    risk_level: str  # low, medium, high, critical
    severity_level: str
    likelihood_level: str
    detectability_level: str
    mitigations: List[str]
    status: str  # identified, mitigated, accepted
    residual_rpn: Optional[int] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class RiskAnalyzer:
    """Automatic risk assessment analyzer"""

    # Severity assessment rules
    SEVERITY_RULES = {
        "esig_required": 5,  # Electronic signature - highest
        "critical_function": 5,  # Critical business function
        "patient_safety": 5,  # Patient/product safety related
        "data_integrity": 4,  # Data integrity related
        "audit_trail": 4,  # Audit trail related
        "security": 4,  # Security related
        "compliance": 4,  # Compliance related
        "business_critical": 3,  # Important business function
        "standard_function": 2,  # Standard function
        "minor_function": 1,  # Minor/optional function
    }

    # Likelihood assessment rules
    LIKELIHOOD_RULES = {
        "gamp_5": 4,  # Custom code - higher risk
        "gamp_4": 3,  # Configured COTS
        "gamp_3": 2,  # Non-configured COTS
        "external_interface": 3,  # External interfaces
        "complex_logic": 3,  # Complex business logic
        "simple_logic": 2,  # Simple logic
        "standard_module": 2,  # Standard module
    }

    # Detectability assessment rules
    DETECTABILITY_RULES = {
        "hidden_failure": 5,  # Failure not easily detectable
        "obscure_indicator": 4,  # Hard to detect
        "standard_monitoring": 3,  # Standard monitoring can detect
        "obvious_failure": 2,  # Obvious failure mode
        "immediate_detection": 1,  # Immediately detectable
    }

    # Standard mitigations by risk type
    STANDARD_MITIGATIONS = {
        "esig": [
            "实施电子签名验证",
            "配置签名含义关联",
            "启用签名审计追踪",
            "验证签名唯一性",
        ],
        "data_integrity": [
            "启用审计追踪",
            "实施数据校验",
            "配置备份策略",
            "启用事务机制",
        ],
        "security": [
            "实施访问控制",
            "配置密码策略",
            "启用会话管理",
            "实施输入验证",
        ],
        "compliance": [
            "验证合规配置",
            "执行合规检查",
            "保留合规证据",
            "定期合规审查",
        ],
        "availability": [
            "配置高可用",
            "实施监控告警",
            "配置故障转移",
            "制定应急预案",
        ],
        "default": [
            "制定缓解措施",
            "实施缓解措施",
            "验证措施有效性",
            "监控残余风险",
        ],
    }

    def __init__(
        self, project_path: Optional[Path] = None, config: Optional[Dict] = None
    ):
        self.project_path = project_path or Path.cwd()
        self.config = config or self._load_config()
        self.requirements_db = self._load_requirements_db()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_path = self.project_path / ".csv-docs-config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_requirements_db(self) -> Dict[str, Any]:
        """Load requirements database"""
        db_path = self.project_path / "requirements.json"
        if db_path.exists():
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"requirements": [], "risks": []}

    def _save_risks(self):
        """Save risks to database"""
        db_path = self.project_path / "requirements.json"
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(self.requirements_db, f, indent=2, ensure_ascii=False)

    def _get_risk_thresholds(self) -> Dict[str, int]:
        """Get RPN thresholds from config"""
        risk_config = self.config.get("risk", {})
        return risk_config.get(
            "rpn_thresholds", {"low": 25, "medium": 50, "high": 75, "critical": 125}
        )

    def _get_gamp_category(self) -> Optional[int]:
        """Get GAMP category from config or detect"""
        category = self.config.get("compliance", {}).get("gamp_category")
        if category:
            return category

        # Check requirements db
        return self.requirements_db.get("gamp_category")

    def _assess_severity(self, requirement: Dict) -> tuple[int, str]:
        """Assess risk severity for a requirement"""
        desc_lower = requirement.get("description", "").lower()
        tags = requirement.get("tags", [])
        esig = requirement.get("esig_required", False)

        # Check eSignature requirement
        if esig:
            return self.SEVERITY_RULES["esig_required"], "critical"

        # Check critical function keywords
        critical_keywords = [
            "审核",
            "审批",
            "批准",
            "critical",
            "审核",
            "patient",
            "安全",
        ]
        for keyword in critical_keywords:
            if keyword in desc_lower:
                return self.SEVERITY_RULES["patient_safety"], "critical"

        # Check data integrity keywords
        data_keywords = ["数据", "审计", "audit", "integrity", "record"]
        for keyword in data_keywords:
            if keyword in desc_lower:
                return self.SEVERITY_RULES["data_integrity"], "high"

        # Check security keywords
        security_keywords = ["密码", "权限", "认证", "security", "password", "auth"]
        for keyword in security_keywords:
            if keyword in desc_lower:
                return self.SEVERITY_RULES["security"], "high"

        # Default based on priority
        priority = requirement.get("priority", "应该")
        if priority == "必须":
            return 4, "high"
        elif priority == "应该":
            return 3, "medium"
        else:
            return 2, "low"

    def _assess_likelihood(self, requirement: Dict) -> tuple[int, str]:
        """Assess likelihood of risk occurrence"""
        gamp = self._get_gamp_category()

        if gamp == 5:
            return self.LIKELIHOOD_RULES["gamp_5"], "probable"
        elif gamp == 4:
            return self.LIKELIHOOD_RULES["gamp_4"], "occasional"
        elif gamp == 3:
            return self.LIKELIHOOD_RULES["gamp_3"], "remote"

        desc_lower = requirement.get("description", "").lower()
        if any(kw in desc_lower for kw in ["接口", "external", "integration"]):
            return self.LIKELIHOOD_RULES["external_interface"], "occasional"

        return self.LIKELIHOOD_RULES["simple_logic"], "occasional"

    def _assess_detectability(self, requirement: Dict) -> tuple[int, str]:
        """Assess likelihood of detecting failure"""
        desc_lower = requirement.get("description", "").lower()

        # Check for hidden/indirect operations
        hidden_keywords = ["后台", "异步", "batch", "background", "hidden"]
        for keyword in hidden_keywords:
            if keyword in desc_lower:
                return self.DETECTABILITY_RULES["obscure_indicator"], "difficult"

        # Default to standard monitoring
        return self.DETECTABILITY_RULES["standard_monitoring"], "moderate"

    def _calculate_rpn(self, severity: int, likelihood: int, detectability: int) -> int:
        """Calculate Risk Priority Number"""
        return severity * likelihood * detectability

    def _get_risk_level(self, rpn: int) -> str:
        """Determine risk level from RPN"""
        thresholds = self._get_risk_thresholds()
        if rpn <= thresholds["low"]:
            return "low"
        elif rpn <= thresholds["medium"]:
            return "medium"
        elif rpn <= thresholds["high"]:
            return "high"
        else:
            return "critical"

    def _get_mitigations(
        self, requirement: Dict, risk_type: str = "default"
    ) -> List[str]:
        """Get standard mitigations for a requirement"""
        esig = requirement.get("esig_required", False)

        mitigations = []

        if esig:
            mitigations.extend(self.STANDARD_MITIGATIONS["esig"])
            risk_type = "esig"

        desc_lower = requirement.get("description", "").lower()

        if any(kw in desc_lower for kw in ["数据", "audit", "record"]):
            mitigations.extend(self.STANDARD_MITIGATIONS["data_integrity"])

        if any(kw in desc_lower for kw in ["安全", "security", "password"]):
            mitigations.extend(self.STANDARD_MITIGATIONS["security"])

        if any(kw in desc_lower for kw in ["可用", "availability", "uptime"]):
            mitigations.extend(self.STANDARD_MITIGATIONS["availability"])

        if not mitigations:
            mitigations = self.STANDARD_MITIGATIONS.get(
                risk_type, self.STANDARD_MITIGATIONS["default"]
            )

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for m in mitigations:
            if m not in seen:
                seen.add(m)
                unique.append(m)

        return unique

    def _generate_risk_id(self) -> str:
        """Generate next available risk ID"""
        existing = self.requirements_db.get("risks", [])
        max_num = 0
        for r in existing:
            risk_id = r.get("id", "")
            if risk_id.startswith("RA-"):
                try:
                    num = int(risk_id.split("-")[1])
                    max_num = max(max_num, num)
                except (ValueError, IndexError):
                    continue
        return f"RA-{max_num + 1:03d}"

    def analyze_requirement(self, requirement: Dict) -> Risk:
        """Analyze a single requirement and generate risk"""
        severity, severity_level = self._assess_severity(requirement)
        likelihood, likelihood_level = self._assess_likelihood(requirement)
        detectability, detectability_level = self._assess_detectability(requirement)

        rpn = self._calculate_rpn(severity, likelihood, detectability)
        risk_level = self._get_risk_level(rpn)

        mitigations = self._get_mitigations(requirement)

        risk = Risk(
            id=self._generate_risk_id(),
            risk_description=f"风险: {requirement.get('description', '')[:100]}",
            requirement_id=requirement.get("id"),
            severity=severity,
            likelihood=likelihood,
            detectability=detectability,
            rpn=rpn,
            risk_level=risk_level,
            severity_level=severity_level,
            likelihood_level=likelihood_level,
            detectability_level=detectability_level,
            mitigations=mitigations,
            status="identified",
        )

        return risk

    def analyze_all(self) -> List[Risk]:
        """Analyze all requirements and generate risks"""
        requirements = self.requirements_db.get("requirements", [])
        risks = []

        for req in requirements:
            risk = self.analyze_requirement(req)
            risks.append(risk)

        return risks

    def add_risk(
        self,
        risk_description: str,
        requirement_id: Optional[str] = None,
        severity: int = 3,
        likelihood: int = 3,
        detectability: int = 3,
        mitigations: List[str] = None,
    ) -> Risk:
        """Manually add a risk"""
        rpn = self._calculate_rpn(severity, likelihood, detectability)
        risk_level = self._get_risk_level(rpn)

        risk = Risk(
            id=self._generate_risk_id(),
            risk_description=risk_description,
            requirement_id=requirement_id,
            severity=severity,
            likelihood=likelihood,
            detectability=detectability,
            rpn=rpn,
            risk_level=risk_level,
            severity_level=self._get_severity_label(severity),
            likelihood_level=self._get_likelihood_label(likelihood),
            detectability_level=self._get_detectability_label(detectability),
            mitigations=mitigations or [],
            status="identified",
        )

        self.requirements_db.setdefault("risks", []).append(asdict(risk))
        self._save_risks()

        return risk

    def update_risk(self, risk_id: str, **kwargs) -> bool:
        """Update a risk by ID"""
        for risk in self.requirements_db.get("risks", []):
            if risk.get("id") == risk_id:
                risk.update(kwargs)

                # Recalculate RPN if severity/likelihood/detectability changed
                if all(
                    k in kwargs for k in ["severity", "likelihood", "detectability"]
                ):
                    risk["rpn"] = (
                        risk["severity"] * risk["likelihood"] * risk["detectability"]
                    )
                    risk["risk_level"] = self._get_risk_level(risk["rpn"])

                self._save_risks()
                return True
        return False

    def get_risks(
        self,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        requirement_id: Optional[str] = None,
    ) -> List[Risk]:
        """Get risks with optional filters"""
        risks = [Risk(**r) for r in self.requirements_db.get("risks", [])]

        if risk_level:
            risks = [r for r in risks if r.risk_level == risk_level]

        if status:
            risks = [r for r in risks if r.status == status]

        if requirement_id:
            risks = [r for r in risks if r.requirement_id == requirement_id]

        return risks

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk assessment summary"""
        risks = self.requirements_db.get("risks", [])

        summary = {
            "total": len(risks),
            "by_level": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "by_status": {"identified": 0, "mitigated": 0, "accepted": 0},
            "high_priority": [],
        }

        for risk in risks:
            level = risk.get("risk_level", "low")
            status = risk.get("status", "identified")
            summary["by_level"][level] = summary["by_level"].get(level, 0) + 1
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

            if level in ["critical", "high"]:
                summary["high_priority"].append(
                    {
                        "id": risk.get("id"),
                        "description": risk.get("risk_description", "")[:50],
                        "rpn": risk.get("rpn", 0),
                    }
                )

        return summary

    @staticmethod
    def _get_severity_label(value: int) -> str:
        labels = {5: "critical", 4: "high", 3: "medium", 2: "low", 1: "negligible"}
        return labels.get(value, "unknown")

    @staticmethod
    def _get_likelihood_label(value: int) -> str:
        labels = {
            5: "frequent",
            4: "probable",
            3: "occasional",
            2: "remote",
            1: "improbable",
        }
        return labels.get(value, "unknown")

    @staticmethod
    def _get_detectability_label(value: int) -> str:
        labels = {
            5: "almost_impossible",
            4: "difficult",
            3: "moderate",
            2: "easy",
            1: "almost_certain",
        }
        return labels.get(value, "unknown")
