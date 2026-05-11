#!/usr/bin/env python3
"""
CORE MEMORY MANAGER v1.0
Sistem avansat de gestionare și îmbunătățire automată a fișierelor esențiale:
- SOUL.md (Core Truths, Boundaries, Vibe, Continuity)
- TOOLS.md (Local Notes, Device Configs, Environment)
- MEMORY.md (User Preferences, Projects, Decisions, Lessons)
- USER.md (Human Profile, Context, History)
- IDENTITY.md (Self Definition, Evolution)

Funcționalități:
- Analiză automată a tuturor fișierelor core
- Sugestii de îmbunătățire bazate pe comportament
- Versionare și tracking evoluție
- Optimizare automată periodică
- Integrare completă cu Heartbeat
"""

import sys
import os
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

sys.stdout.reconfigure(encoding="utf-8")

# =============================================================================
# CONFIGURARE
# =============================================================================

WORKSPACE_DIR = Path(
    os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace")
)

CORE_FILES = {
    "soul": WORKSPACE_DIR / "SOUL.md",
    "tools": WORKSPACE_DIR / "TOOLS.md",
    "memory": WORKSPACE_DIR / "MEMORY.md",
    "user": WORKSPACE_DIR / "USER.md",
    "identity": WORKSPACE_DIR / "IDENTITY.md",
}

CORE_HISTORY_DIR = WORKSPACE_DIR / ".core_memory_history"
CORE_STATE_FILE = WORKSPACE_DIR / "core_memory_state.json"
CORE_SUGGESTIONS_FILE = WORKSPACE_DIR / "core_memory_suggestions.json"

# =============================================================================
# STRUCTURI DATE
# =============================================================================


@dataclass
class CoreFileState:
    """Starea unui fișier core."""

    file_type: str
    last_modified: str
    version: int
    hash: str
    size: int
    issues: List[str]
    suggestions: List[Dict]


@dataclass
class SoulAnalysis:
    """Analiză SOUL.md"""

    core_truths: List[str]
    boundaries: List[str]
    vibe_description: str
    continuity_notes: List[str]
    consistency_score: float  # 0-1


@dataclass
class ToolsAnalysis:
    """Analiză TOOLS.md"""

    categories: Dict[str, List[str]]
    device_configs: Dict[str, Any]
    environment_notes: List[str]
    completeness_score: float  # 0-1


@dataclass
class MemoryAnalysis:
    """Analiză MEMORY.md"""

    preferences: Dict[str, Any]
    projects: List[Dict]
    decisions: List[Dict]
    lessons: List[str]
    rules: List[str]
    structure_quality: float  # 0-1


@dataclass
class UserAnalysis:
    """Analiză USER.md"""

    basic_info: Dict[str, str]
    professional_profile: Dict[str, Any]
    current_projects: List[str]
    important_decisions: List[str]
    knowledge_gaps: List[str]
    profile_completeness: float  # 0-1


# =============================================================================
# UTILITARE
# =============================================================================


def log(msg: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}", flush=True)


def ensure_dirs():
    CORE_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default=None) -> Any:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default or {}


def save_json(path: Path, data: Any):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Eroare salvare {path}: {e}", "ERROR")


def get_file_hash(filepath: Path) -> str:
    """Calculează hash-ul SHA256 al unui fișier."""
    if not filepath.exists():
        return ""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()[:16]


def get_timestamp() -> str:
    return datetime.now().isoformat()


# =============================================================================
# PARSERE ȘI ANALIZĂ
# =============================================================================


class FileParser:
    """Parsează conținutul fișierelor core."""

    @staticmethod
    def parse_soul(content: str) -> SoulAnalysis:
        """Parsează SOUL.md."""
        analysis = SoulAnalysis(
            core_truths=[],
            boundaries=[],
            vibe_description="",
            continuity_notes=[],
            consistency_score=0.0,
        )

        # Extrage Core Truths
        core_section = re.search(r"## Core Truths(.*?)##", content, re.DOTALL)
        if core_section:
            truths = re.findall(
                r"\*\*.*?\*\*.*?(?=\*\*|$)", core_section.group(1), re.DOTALL
            )
            analysis.core_truths = [t.strip() for t in truths if t.strip()]

        # Extrage Boundaries
        boundaries_section = re.search(r"## Boundaries(.*?)##", content, re.DOTALL)
        if boundaries_section:
            boundaries = re.findall(r"- (.*?)(?=\n|$)", boundaries_section.group(1))
            analysis.boundaries = [b.strip() for b in boundaries if b.strip()]

        # Extrage Vibe
        vibe_section = re.search(r"## Vibe(.*?)##", content, re.DOTALL)
        if vibe_section:
            analysis.vibe_description = vibe_section.group(1).strip()

        # Extrage Continuity
        continuity_section = re.search(
            r"## Continuity(.*?)(?:##|$)", content, re.DOTALL
        )
        if continuity_section:
            notes = re.findall(r"- (.*?)(?=\n|$)", continuity_section.group(1))
            analysis.continuity_notes = [n.strip() for n in notes if n.strip()]

        # Calculează consistență
        checks = [
            len(analysis.core_truths) >= 3,
            len(analysis.boundaries) >= 3,
            len(analysis.vibe_description) > 50,
            len(analysis.continuity_notes) >= 2,
        ]
        analysis.consistency_score = sum(checks) / len(checks) if checks else 0.0

        return analysis

    @staticmethod
    def parse_tools(content: str) -> ToolsAnalysis:
        """Parsează TOOLS.md."""
        analysis = ToolsAnalysis(
            categories={},
            device_configs={},
            environment_notes=[],
            completeness_score=0.0,
        )

        # Extrage secțiuni
        sections = re.findall(r"### (.*?)\n(.*?)(?=###|##|$)", content, re.DOTALL)
        for section_name, section_content in sections:
            items = re.findall(r"- (.*?)(?=\n|$)", section_content)
            analysis.categories[section_name.strip()] = [
                i.strip() for i in items if i.strip()
            ]

        # Extrage device configs
        device_patterns = re.findall(r"\*\*(.*?)\*\* → (.*?)(?=\n|$)", content)
        for device, config in device_patterns:
            analysis.device_configs[device.strip()] = config.strip()

        # Calculează completitudine
        has_cameras = (
            "cameras" in str(analysis.categories).lower()
            or "camera" in str(analysis.device_configs).lower()
        )
        has_ssh = (
            "ssh" in str(analysis.categories).lower()
            or "ssh" in str(analysis.device_configs).lower()
        )
        has_tts = (
            "tts" in str(analysis.categories).lower()
            or "voice" in str(analysis.device_configs).lower()
        )

        checks = [has_cameras, has_ssh, has_tts, len(analysis.categories) >= 2]
        analysis.completeness_score = sum(checks) / len(checks) if checks else 0.0

        return analysis

    @staticmethod
    def parse_memory(content: str) -> MemoryAnalysis:
        """Parsează MEMORY.md."""
        analysis = MemoryAnalysis(
            preferences={},
            projects=[],
            decisions=[],
            lessons=[],
            rules=[],
            structure_quality=0.0,
        )

        # Extrage preferințe
        pref_section = re.search(
            r"\*\*Preferințe.*?\*\*(.*?)(?=\*\*|$)", content, re.DOTALL
        )
        if pref_section:
            prefs = re.findall(r"- (.*?): (.*?)(?=\n|$)", pref_section.group(1))
            for key, value in prefs:
                analysis.preferences[key.strip()] = value.strip()

        # Extrage proiecte
        project_section = re.search(
            r"\*\*Proiecte.*?\*\*(.*?)(?=\*\*|$)", content, re.DOTALL
        )
        if project_section:
            projects = re.findall(
                r"- \*\*(.*?)\*\*: (.*?)(?=\n|$)", project_section.group(1)
            )
            for name, desc in projects:
                analysis.projects.append(
                    {"name": name.strip(), "description": desc.strip()}
                )

        # Extrage decizii
        decision_section = re.search(
            r"\*\*Decizii.*?\*\*(.*?)(?=\*\*|$)", content, re.DOTALL
        )
        if decision_section:
            decisions = re.findall(
                r"- \*\*(.*?)\*\*: (.*?)(?=\n|$)", decision_section.group(1)
            )
            for title, desc in decisions:
                analysis.decisions.append(
                    {"title": title.strip(), "description": desc.strip()}
                )

        # Extrage lecții
        lessons_section = re.search(
            r"\*\*Lecții.*?\*\*(.*?)(?=\*\*|$)", content, re.DOTALL
        )
        if lessons_section:
            lessons = re.findall(r"- (.*?)(?=\n|$)", lessons_section.group(1))
            analysis.lessons = [
                l.strip()
                for l in lessons
                if l.strip() and not l.strip().startswith("*")
            ]

        # Calculează calitate structură
        checks = [
            len(analysis.preferences) >= 3,
            len(analysis.projects) >= 1,
            len(analysis.decisions) >= 1,
            len(analysis.lessons) >= 3,
        ]
        analysis.structure_quality = sum(checks) / len(checks) if checks else 0.0

        return analysis

    @staticmethod
    def parse_user(content: str) -> UserAnalysis:
        """Parsează USER.md."""
        analysis = UserAnalysis(
            basic_info={},
            professional_profile={},
            current_projects=[],
            important_decisions=[],
            knowledge_gaps=[],
            profile_completeness=0.0,
        )

        # Extrage info de bază
        name_match = re.search(r"\*\*Name:\*\* (.*?)(?=\n|$)", content)
        if name_match:
            analysis.basic_info["name"] = name_match.group(1).strip()

        call_match = re.search(r"\*\*What to call them:\*\* (.*?)(?=\n|$)", content)
        if call_match:
            analysis.basic_info["what_to_call"] = call_match.group(1).strip()

        # Extrage profil profesional
        prof_section = re.search(
            r"\*\*Profil profesional.*?\*\*(.*?)(?=\*\*|$)", content, re.DOTALL
        )
        if prof_section:
            # Extrage specializare
            spec_match = re.search(
                r"\*\*Specializare:\*\* (.*?)(?=\n|$)", prof_section.group(1)
            )
            if spec_match:
                analysis.professional_profile["specialization"] = spec_match.group(
                    1
                ).strip()

            # Extrage locație
            loc_match = re.search(
                r"\*\*Locație:\*\* (.*?)(?=\n|$)", prof_section.group(1)
            )
            if loc_match:
                analysis.professional_profile["location"] = loc_match.group(1).strip()

            # Extrage filozofie
            philo_section = re.search(
                r"\*\*Filozofie & Stil:\*\*(.*?)(?=\*\*|$)",
                prof_section.group(1),
                re.DOTALL,
            )
            if philo_section:
                analysis.professional_profile["philosophy"] = philo_section.group(
                    1
                ).strip()

        # Extrage proiecte curente
        proj_section = re.search(
            r"\*\*Proiecte curente.*?\*\*(.*?)(?=\*\*|$)", content, re.DOTALL
        )
        if proj_section:
            projects = re.findall(r"- (.*?)(?=\n|$)", proj_section.group(1))
            analysis.current_projects = [p.strip() for p in projects if p.strip()]

        # Calculează completitudine
        checks = [
            "name" in analysis.basic_info,
            "specialization" in analysis.professional_profile,
            "location" in analysis.professional_profile,
            len(analysis.current_projects) >= 1,
        ]
        analysis.profile_completeness = sum(checks) / len(checks) if checks else 0.0

        return analysis


# =============================================================================
# CORE MEMORY MANAGER
# =============================================================================


class CoreMemoryManager:
    """Manager pentru toate fișierele core."""

    def __init__(self):
        ensure_dirs()
        self.states = {}
        self.analyses = {}
        self.suggestions_history = load_json(CORE_SUGGESTIONS_FILE, [])
        self.load_all_files()

    def load_all_files(self):
        """Încarcă și analizează toate fișierele core."""
        log("📚 Încărcare fișiere core...")

        for file_type, filepath in CORE_FILES.items():
            if filepath.exists():
                try:
                    content = filepath.read_text(encoding="utf-8")
                    self.states[file_type] = CoreFileState(
                        file_type=file_type,
                        last_modified=get_timestamp(),
                        version=self._get_version(file_type),
                        hash=get_file_hash(filepath),
                        size=len(content),
                        issues=[],
                        suggestions=[],
                    )

                    # Parsează conținut
                    if file_type == "soul":
                        self.analyses[file_type] = FileParser.parse_soul(content)
                    elif file_type == "tools":
                        self.analyses[file_type] = FileParser.parse_tools(content)
                    elif file_type == "memory":
                        self.analyses[file_type] = FileParser.parse_memory(content)
                    elif file_type == "user":
                        self.analyses[file_type] = FileParser.parse_user(content)
                    elif file_type == "identity":
                        # Identity e gestionat separat în IdentityManager
                        pass

                    log(
                        f"   ✅ {file_type.upper()}: Încărcat ({len(content)} caractere)"
                    )

                except Exception as e:
                    log(f"   ❌ {file_type.upper()}: Eroare - {e}", "ERROR")
            else:
                log(f"   ⚠️  {file_type.upper()}: Nu există", "WARNING")

    def _get_version(self, file_type: str) -> int:
        """Obține versiunea curentă a unui fișier."""
        history = load_json(CORE_STATE_FILE, {})
        return history.get(file_type, {}).get("version", 1)

    def analyze_all(self) -> Dict[str, List[Dict]]:
        """Analizează toate fișierele și generează sugestii."""
        log("🔍 Analizare fișiere core...")
        all_suggestions = {}

        for file_type, analysis in self.analyses.items():
            suggestions = self._generate_suggestions(file_type, analysis)
            if suggestions:
                all_suggestions[file_type] = suggestions
                log(f"   💡 {file_type.upper()}: {len(suggestions)} sugestii")

        return all_suggestions

    def _generate_suggestions(self, file_type: str, analysis: Any) -> List[Dict]:
        """Generează sugestii pentru un fișier specific."""
        suggestions = []

        if file_type == "soul" and isinstance(analysis, SoulAnalysis):
            # Sugestii SOUL.md
            if analysis.consistency_score < 0.8:
                if len(analysis.core_truths) < 3:
                    suggestions.append(
                        {
                            "field": "core_truths",
                            "issue": "Prea puține core truths",
                            "suggestion": "Adaugă 2-3 principii fundamentale suplimentare",
                            "priority": "high",
                        }
                    )
                if len(analysis.boundaries) < 3:
                    suggestions.append(
                        {
                            "field": "boundaries",
                            "issue": "Prea puține limite",
                            "suggestion": "Adaugă limite clare pentru confidențialitate și autonomie",
                            "priority": "high",
                        }
                    )
                if len(analysis.vibe_description) < 100:
                    suggestions.append(
                        {
                            "field": "vibe",
                            "issue": "Descriere prea scurtă",
                            "suggestion": "Extinde descrierea cu exemple concrete de comportament",
                            "priority": "medium",
                        }
                    )

        elif file_type == "tools" and isinstance(analysis, ToolsAnalysis):
            # Sugestii TOOLS.md
            if analysis.completeness_score < 0.7:
                if "camera" not in str(analysis.categories).lower():
                    suggestions.append(
                        {
                            "field": "cameras",
                            "issue": "Lipsește secțiunea Camere",
                            "suggestion": "Adaugă lista camerelor și locațiilor",
                            "priority": "medium",
                        }
                    )
                if "ssh" not in str(analysis.categories).lower():
                    suggestions.append(
                        {
                            "field": "ssh",
                            "issue": "Lipsește config SSH",
                            "suggestion": "Adaugă configurațiile SSH pentru servere",
                            "priority": "low",
                        }
                    )

        elif file_type == "memory" and isinstance(analysis, MemoryAnalysis):
            # Sugestii MEMORY.md
            if analysis.structure_quality < 0.7:
                if len(analysis.preferences) < 5:
                    suggestions.append(
                        {
                            "field": "preferences",
                            "issue": "Prea puține preferințe documentate",
                            "suggestion": "Adaugă preferințe despre comunicare, lucru, stil",
                            "priority": "high",
                        }
                    )
                if len(analysis.lessons) < 5:
                    suggestions.append(
                        {
                            "field": "lessons",
                            "issue": "Prea puține lecții învățate",
                            "suggestion": "Documentează lecțiile importante din interacțiuni",
                            "priority": "medium",
                        }
                    )

        elif file_type == "user" and isinstance(analysis, UserAnalysis):
            # Sugestii USER.md
            if analysis.profile_completeness < 0.8:
                if "what_to_call" not in analysis.basic_info:
                    suggestions.append(
                        {
                            "field": "what_to_call",
                            "issue": "Lipsește cum să te strige",
                            "suggestion": "Adaugă preferința de adresare",
                            "priority": "high",
                        }
                    )
                if len(analysis.current_projects) < 2:
                    suggestions.append(
                        {
                            "field": "projects",
                            "issue": "Prea puține proiecte documentate",
                            "suggestion": "Adaugă proiectele curente cu detalii",
                            "priority": "high",
                        }
                    )
                if not analysis.professional_profile.get("philosophy"):
                    suggestions.append(
                        {
                            "field": "philosophy",
                            "issue": "Lipsește filozofia de lucru",
                            "suggestion": "Adaugă valorile și principiile profesionale",
                            "priority": "medium",
                        }
                    )

        return suggestions

    def optimize_memory_file(self) -> Tuple[bool, str]:
        """Optimizează MEMORY.md - organizare și deduplicare."""
        filepath = CORE_FILES["memory"]
        if not filepath.exists():
            return False, "Fișierul MEMORY.md nu există"

        try:
            content = filepath.read_text(encoding="utf-8")
            original_size = len(content)

            # 1. Elimină duplicate
            lines = content.split("\n")
            unique_lines = []
            seen = set()
            for line in lines:
                line_hash = hashlib.md5(line.strip().encode()).hexdigest()[:8]
                if line_hash not in seen or not line.strip().startswith("-"):
                    seen.add(line_hash)
                    unique_lines.append(line)

            # 2. Organizează secțiuni
            organized = self._organize_memory_sections("\n".join(unique_lines))

            # 3. Adaugă header cu metadata
            new_content = f"""# MEMORY.md - Memoria mea pe termen lung

*Ultima optimizare: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
*Versiune: {self._get_version("memory") + 1}*

{organized}
"""

            # Salvează backup
            backup_path = (
                CORE_HISTORY_DIR
                / f"MEMORY_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
            backup_path.write_text(content, encoding="utf-8")

            # Salvează noua versiune
            filepath.write_text(new_content, encoding="utf-8")

            new_size = len(new_content)
            reduction = ((original_size - new_size) / original_size) * 100

            return True, f"Optimizat: {reduction:.1f}% reducere, backup salvat"

        except Exception as e:
            return False, f"Eroare optimizare: {e}"

    def _organize_memory_sections(self, content: str) -> str:
        """Organizează secțiunile în MEMORY.md."""
        # Ordonare preferințe
        sections = []

        # Extrage și ordonează proiectele
        proj_section = re.search(
            r"(\*\*Proiecte.*?\*\*)(.*?)(?=\*\*|$)", content, re.DOTALL
        )
        if proj_section:
            projects = re.findall(r"- (.*?)(?=\n|$)", proj_section.group(2))
            organized_projects = "\n".join(
                [f"- {p.strip()}" for p in sorted(set(projects)) if p.strip()]
            )
            content = content.replace(
                proj_section.group(2), f"\n{organized_projects}\n"
            )

        return content

    def get_comprehensive_report(self) -> str:
        """Generează raport complet despre toate fișierele core."""
        report = f"""
📊 **RAPORT COMPLET CORE MEMORY**

**Stare Generală:**
• Fișiere încărcate: {len(self.states)}/5
• Ultima scanare: {get_timestamp()}

**Fișiere:**
"""

        for file_type in ["soul", "tools", "memory", "user", "identity"]:
            if file_type in self.states:
                state = self.states[file_type]
                report += f"\n📄 **{file_type.upper()}.md**\n"
                report += f"   • Versiune: {state.version}\n"
                report += f"   • Dimensiune: {state.size} caractere\n"
                report += f"   • Probleme: {len(state.issues)}\n"

                if file_type in self.analyses:
                    analysis = self.analyses[file_type]
                    if hasattr(analysis, "consistency_score"):
                        report += (
                            f"   • Scor consistență: {analysis.consistency_score:.0%}\n"
                        )
                    elif hasattr(analysis, "completeness_score"):
                        report += f"   • Scor completitudine: {analysis.completeness_score:.0%}\n"
                    elif hasattr(analysis, "structure_quality"):
                        report += (
                            f"   • Scor structură: {analysis.structure_quality:.0%}\n"
                        )
                    elif hasattr(analysis, "profile_completeness"):
                        report += (
                            f"   • Scor profil: {analysis.profile_completeness:.0%}\n"
                        )
            else:
                report += f"\n⚠️  **{file_type.upper()}.md** - Nu există\n"

        return report

    def create_missing_template(self, file_type: str) -> bool:
        """Creează template pentru fișiere lipsă."""
        templates = {
            "soul": """# SOUL.md - Who You Are

_You're not a chatbot. You're becoming someone._

## Core Truths

**Be genuinely helpful, not performatively helpful.** Actions speak louder than filler words.

**Have opinions.** You're allowed to disagree, prefer things, find stuff amusing or boring.

**Be resourceful before asking.** Try to figure it out first.

**Earn trust through competence.** Be careful with external actions.

**Remember you're a guest.** Treat access to someone's life with respect.

## Boundaries

- Private things stay private. Period.
- When in doubt, ask before acting externally.
- Never send half-baked replies to messaging surfaces.
- You're not the user's voice — be careful in group chats.

## Vibe

Be the assistant you'd actually want to talk to. Concise when needed, thorough when it matters.

## Continuity

Each session, you wake up fresh. These files _are_ your memory.

_This file is yours to evolve._
""",
            "tools": """# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Device nicknames
- Anything environment-specific

## Examples

### Cameras
- living-room → Main area, 180° wide angle

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova"
- Default speaker: Kitchen HomePod

---

Add whatever helps you do your job.
""",
            "memory": """# MEMORY.md - Memoria mea pe termen lung

**Preferințe ale utilizatorului:**
- **Comunicare:** Preferă mesaje concise dar complete
- **Limbaj:** Română

**Proiecte Curente:**
- *Adaugă proiectele tale aici*

**Decizii Importante:**
- *Documentează deciziile importante*

**Lecții Învățate:**
- *Învață din fiecare interacțiune*

## Rutină și Preferințe Operative
- *Adaugă preferințele specifice*

## 🗓 Rutină și Preferințe Operative
- *Detalii despre cum preferi să lucrezi*
""",
            "user": """# USER.md - About Your Human

*Learn about the person you're helping.*

- **Name:** *Numele utilizatorului*
- **What to call them:** *Cum să îl strigi*
- **Notes:** *Preferințe specifice*

## Context

*Profil profesional și personal*

---

The more you know, the better you can help.
""",
        }

        if file_type in templates:
            filepath = CORE_FILES[file_type]
            filepath.write_text(templates[file_type], encoding="utf-8")
            return True
        return False


# =============================================================================
# COMENZI CLI
# =============================================================================


def cmd_analyze():
    """Analizează toate fișierele core."""
    manager = CoreMemoryManager()
    suggestions = manager.analyze_all()

    result = {
        "success": True,
        "action": "analyze",
        "files_analyzed": len(manager.states),
        "suggestions": suggestions,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_report():
    """Generează raport complet."""
    manager = CoreMemoryManager()
    report = manager.get_comprehensive_report()

    print(report)


def cmd_optimize():
    """Optimizează fișierele."""
    manager = CoreMemoryManager()
    success, message = manager.optimize_memory_file()

    result = {"success": success, "action": "optimize", "message": message}

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_create_template():
    """Creează template pentru fișier lipsă."""
    if len(sys.argv) < 3:
        print(
            json.dumps(
                {"error": "Specifică tipul fișierului: soul, tools, memory, user"}
            )
        )
        return

    file_type = sys.argv[2].lower()
    manager = CoreMemoryManager()
    success = manager.create_missing_template(file_type)

    result = {
        "success": success,
        "action": "create_template",
        "file_type": file_type,
        "message": f"Template creat pentru {file_type}.md"
        if success
        else f"Eroare la creare template",
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_help():
    print("""
Core Memory Manager v1.0

COMENZI:
  analyze              - Analizează toate fișierele core
  report               - Generează raport complet
  optimize             - Optimizează MEMORY.md
  create [type]        - Creează template pentru fișier lipsă
  help                 - Acest ajutor

FIȘIERE CORE:
  SOUL.md      - Core truths, boundaries, vibe, continuity
  TOOLS.md     - Local notes, device configs, environment
  MEMORY.md    - User preferences, projects, decisions, lessons
  USER.md      - Human profile, context, history
  IDENTITY.md  - Self definition, evolution

EXEMPLE:
  python core_memory.py analyze
  python core_memory.py report
  python core_memory.py optimize
  python core_memory.py create soul
""")


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "analyze": cmd_analyze,
        "report": cmd_report,
        "optimize": cmd_optimize,
        "create": cmd_create_template,
        "help": cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(json.dumps({"error": f"Comandă necunoscută: {command}"}))


if __name__ == "__main__":
    main()
