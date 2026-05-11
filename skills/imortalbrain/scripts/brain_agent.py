#!/usr/bin/env python3
"""
IMMORTAL BRAIN v4.0 - AUTONOMOUS AGENT
Agent autonom de memorie neuronală biologic inspirat pentru OpenClaw

Arhitectură Microservicii:
├── 🔴 KERNEL (Inima)         - Event Loop & Scheduler
├── 🧠 BRAIN (Creierul)       - LLM Integration & Processing
├── 📡 NERVOUS (Sistemul Nervos) - Telegram/Webhook Communication
├── 🌐 MEMORY (Glia)          - File System Watcher & Graph Logic
└── ✨ CURIOSITY (Entropie)   - Generator de Idei Noi

Flux Autonom:
[EVENT LOOP] → [DECIZIE PROBABILISTICĂ] → [ACȚIUNE] → [COMUNICARE]
     ↑                    ↓                      ↓            ↓
     └────────────────────┴──────────────────────┴────────────┘

Probabilistic Action Selection:
- 70%: Mentenanță (Glia - curățare, organizare)
- 20%: Conexiuni (Memorie - link-uri, asocieri)
- 10%: Curiozitate (Entropie - concepte noi)

Usage:
  python brain_agent.py daemon          # Pornește agentul autonom
  python brain_agent.py pulse           # Rulează un singur ciclu
  python brain_agent.py status          # Vezi starea agentului
  python brain_agent.py telegram        # Testează notificări
  python brain_agent.py curiosity       # Generează curiozitate
"""

import sys
import os
import time
import re
import json
import random
import hashlib
import threading
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import urllib.request
import urllib.parse

# Configure stdout
sys.stdout.reconfigure(encoding="utf-8")

# =============================================================================
# CONFIGURARE GLOBALĂ
# =============================================================================

USER_PATH = Path(os.environ["USERPROFILE"])
WORKSPACE_DIR = USER_PATH / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE_DIR / "memory"
BRAIN_DIR = WORKSPACE_DIR / "Creier"
ARCHIVE_DIR = BRAIN_DIR / "_ARHIVA"
NECROPOLIS_DIR = BRAIN_DIR / "_CIMITIR"
CACHE_DIR = WORKSPACE_DIR / ".cache_brain"
LOG_DIR = WORKSPACE_DIR / ".logs"

CONFIG_FILE = WORKSPACE_DIR / "brain_config.json"
STATE_FILE = WORKSPACE_DIR / "brain_state.json"
INDEX_FILE = WORKSPACE_DIR / "brain_index.json"
LOG_FILE = LOG_DIR / f"brain_{datetime.now().strftime('%Y%m%d')}.log"
PID_FILE = WORKSPACE_DIR / "brain_daemon.pid"

# Probabilități decizie (70/20/10)
PROBABILITIES = {
    "maintenance": 0.70,  # Glia - curățare, organizare
    "memory": 0.20,  # Conexiuni - link-uri, asocieri
    "curiosity": 0.10,  # Entropie - concepte noi
}

# Configurare LLM (Ollama)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = "llama3.2:3b"  # Sau orice model disponibil

# Configurare Telegram (opțional)
TELEGRAM_CONFIG = {"enabled": False, "bot_token": "", "chat_id": ""}

# Pattern-uri
WIKI_LINK_PATTERN = re.compile(r"\[\[(.*?)\]\]")
TAG_PATTERN = re.compile(r"#(\w+)")
ID_PATTERN = re.compile(r"<!--\s*ID:\s*(\w+)\s*-->")
PRIORITY_EMOJI = {
    "urgent": "🔥",
    "active": "⚡",
    "hold": "⏳",
    "done": "✅",
    "archive": "📦",
    "low": "🐢",
}

# =============================================================================
# UTILITARE
# =============================================================================


def log(message: str, level: str = "INFO"):
    """Log cu timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    print(entry)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except:
        pass


def ensure_dirs():
    """Creează toate directoarele necesare."""
    for d in [MEMORY_DIR, BRAIN_DIR, ARCHIVE_DIR, NECROPOLIS_DIR, CACHE_DIR, LOG_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path, default=None) -> Any:
    """Încarcă JSON cu default."""
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default or {}


def save_json(filepath: Path, data: Any):
    """Salvează JSON."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Eroare salvare {filepath}: {e}", "ERROR")


def generate_id(content: str) -> str:
    """Generează ID unic."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


# =============================================================================
# CLASA NEURON (Unitatea Atomică)
# =============================================================================


class Neuron:
    def __init__(self, content: str, nid: str = None, tags: List[str] = None):
        self.id = nid or generate_id(content)
        self.content = content
        self.tags = tags or TAG_PATTERN.findall(content.lower())
        self.created_at = datetime.now().isoformat()
        self.modified_at = self.created_at
        self.access_count = 0
        self.weight = 1.0
        self.links = []  # Wiki links [[...]]
        self.embeddings = None  # Vector pentru LLM

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "access_count": self.access_count,
            "weight": self.weight,
            "links": self.links,
            "embeddings": self.embeddings,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Neuron":
        n = cls(data["content"], data["id"], data["tags"])
        n.created_at = data.get("created_at", n.created_at)
        n.modified_at = data.get("modified_at", n.modified_at)
        n.access_count = data.get("access_count", 0)
        n.weight = data.get("weight", 1.0)
        n.links = data.get("links", [])
        n.embeddings = data.get("embeddings")
        return n


# =============================================================================
# SISTEMUL GLIA (Mentenanță & Organizare)
# =============================================================================


class GliaSystem:
    """Sistemul de mentenanță și organizare (70% din timp)."""

    def __init__(self, brain: "AutonomousBrain"):
        self.brain = brain

    def maintenance_cycle(self):
        """Ciclu complet de mentenanță."""
        log("🧹 GLIA: Începe ciclu de mentenanță")

        # 1. Procesează memoria nouă
        self._process_memory_files()

        # 2. Curățare astrocitară
        self._cleanup_old_neurons()

        # 3. Reorganizare fișiere
        self._reorganize_files()

        # 4. Actualizare index
        self.brain.save_index()

        log("✅ GLIA: Ciclu completat")

    def _process_memory_files(self):
        """Procesează fișierele din memory/."""
        files = [f for f in MEMORY_DIR.glob("*.md")]
        if not files:
            return

        log(f"📁 GLIA: {len(files)} fișiere de procesat")
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()

                # Extrage neuroni
                lines = content.split("\n")
                new_neurons = 0
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and not line.startswith("#"):
                        neuron = Neuron(line)
                        # Extrage wiki links
                        neuron.links = WIKI_LINK_PATTERN.findall(line)
                        self.brain.add_neuron(neuron)
                        new_neurons += 1

                # Arhivează fișierul procesat
                archive_path = (
                    WORKSPACE_DIR
                    / "_processed"
                    / f"{f.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                f.rename(archive_path)

                log(f"   ✓ {f.name}: {new_neurons} neuroni")
            except Exception as e:
                log(f"   ❌ Eroare {f.name}: {e}", "ERROR")

    def _cleanup_old_neurons(self):
        """Elimină neuroni vechi și inactivi."""
        to_remove = []
        for nid, neuron in self.brain.neurons.items():
            # Elimină prea scurte
            if len(neuron.content) < 5:
                to_remove.append(nid)
            # Elimină neaccesați de mult timp
            elif neuron.weight < 1.2:
                created = datetime.fromisoformat(neuron.created_at)
                if (datetime.now() - created).days > 60:
                    to_remove.append(nid)

        for nid in to_remove:
            del self.brain.neurons[nid]

        if to_remove:
            log(f"🧹 GLIA: {len(to_remove)} neuroni curățați")

    def _reorganize_files(self):
        """Reorganizează fișierele după topic."""
        # Grupează neuroni după primul tag (topic)
        topics = defaultdict(list)
        for neuron in self.brain.neurons.values():
            topic = neuron.tags[0].upper() if neuron.tags else "GENERAL"
            topics[topic].append(neuron)

        # Salvează în fișiere
        for topic, neurons in topics.items():
            filepath = BRAIN_DIR / f"{topic}.md"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# 🧠 {topic}\n")
                f.write(
                    f"*Actualizat: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
                )
                for neuron in sorted(neurons, key=lambda x: -x.weight):
                    emoji = PRIORITY_EMOJI.get(
                        neuron.tags[1] if len(neuron.tags) > 1 else "active", "•"
                    )
                    f.write(f"{emoji} {neuron.content} <!-- ID: {neuron.id} -->\n")


# =============================================================================
# SISTEMUL DE MEMORIE (Conexiuni & Link-uri)
# =============================================================================


class MemorySystem:
    """Sistemul de conexiuni și asocieri (20% din timp)."""

    def __init__(self, brain: "AutonomousBrain"):
        self.brain = brain

    def memory_cycle(self):
        """Ciclu de explorare a memoriei."""
        log("🔗 MEMORIE: Explorare conexiuni")

        # 1. Detectează link-uri wiki orfane
        self._find_orphan_links()

        # 2. Sugerează conexiuni între neuroni
        suggestions = self._suggest_connections()

        # 3. Trimite notificări dacă găsim ceva interesant
        if suggestions:
            message = "🔗 Conexiuni descoperite:\n\n"
            for s in suggestions[:3]:
                message += f"• {s}\n"
            self.brain.notify(message)

        log("✅ MEMORIE: Ciclu completat")

    def _find_orphan_links(self):
        """Găsește link-uri wiki care nu duc nicăieri."""
        all_links = set()
        all_topics = set()

        for neuron in self.brain.neurons.values():
            all_links.update(neuron.links)
            if neuron.tags:
                all_topics.add(neuron.tags[0].lower())

        orphans = all_links - all_topics
        if orphans:
            log(f"⚠️  Link-uri orfane: {', '.join(orphans)}")

    def _suggest_connections(self) -> List[str]:
        """Sugerează conexiuni între neuroni similari."""
        suggestions = []
        neurons = list(self.brain.neurons.values())

        if len(neurons) < 2:
            return suggestions

        # Compară neuroni aleatori
        for _ in range(min(10, len(neurons))):
            n1, n2 = random.sample(neurons, 2)
            # Dacă au tag-uri comune dar nu sunt link-uiți
            common_tags = set(n1.tags) & set(n2.tags)
            if common_tags and n1.id not in n2.links and n2.id not in n1.links:
                tag = list(common_tags)[0]
                suggestions.append(
                    f"'{n1.content[:30]}...' și '{n2.content[:30]}...' împărtășesc #{tag}"
                )

        return suggestions


# =============================================================================
# SISTEMUL DE CURIOSITATE (Generator Entropie)
# =============================================================================


class CuriositySystem:
    """Sistemul de generare a curiozității (10% din timp)."""

    def __init__(self, brain: "AutonomousBrain"):
        self.brain = brain
        self.concepts_pool = [
            "paradoxul lui Zenon",
            "efectul de seră",
            "criza de semnificație",
            "învățare automată",
            "biomimetică",
            "sisteme complexe",
            "teoria haosului",
            "inteligență colectivă",
            "emergență",
            "feedback loops",
            "rezonanță stocastică",
            "homeostazie",
        ]

    def curiosity_cycle(self):
        """Generează o idee/curiozitate nouă."""
        log("✨ CURIOSITATE: Generare entropie")

        # 1. Colectează tag-uri existente
        existing_tags = set()
        for neuron in self.brain.neurons.values():
            existing_tags.update(neuron.tags)

        # 2. Găsește concepte noi (care nu sunt în memorie)
        novel_concepts = [
            c for c in self.concepts_pool if c.replace(" ", "_") not in existing_tags
        ]

        if novel_concepts and random.random() < 0.3:  # 30% șansă să generăm
            concept = random.choice(novel_concepts)

            # 3. Generează o "curiozitate"
            curiosity_msg = self._generate_curiosity_message(concept)

            log(f"✨ Concept nou descoperit: {concept}")
            self.brain.notify(curiosity_msg)

            # 4. Salvează ca neuron potențial
            neuron = Neuron(f"Explorare: {concept} #research #curiosity #active")
            self.brain.add_neuron(neuron)
        else:
            log("✨ Nicio curiozitate nouă astăzi")

    def _generate_curiosity_message(self, concept: str) -> str:
        """Generează un mesaj de curiozitate."""
        templates = [
            f"✨ *Concept nou descoperit*: **{concept}**\n\nAcest concept nu există încă în memoria ta. Vrei să îl explorezi?\n\nSugestie: Caută informații despre {concept} și adaugă-le în sistem.",
            f"🧠 *Curiozitate*: Ai auzit de **{concept}**?\n\nEste un concept interesant care ar putea completa cunoștințele tale.",
            f"🌟 *Descoperire*: **{concept}**\n\nSistemul a identificat acest concept ca fiind relevant pentru domeniile tale de interes.",
        ]
        return random.choice(templates)


# =============================================================================
# SISTEMUL DE COMUNICARE (Telegram/Webhook)
# =============================================================================


class CommunicationSystem:
    """Sistemul de comunicare cu exteriorul."""

    def __init__(self, brain: "AutonomousBrain"):
        self.brain = brain
        self.config = load_json(CONFIG_FILE, {}).get("telegram", {})

    def send_message(self, message: str) -> bool:
        """Trimite mesaj pe Telegram sau în consolă."""
        if not self.config.get("enabled"):
            # Mod offline - doar log
            log(f"📨 NOTIFICARE: {message[:100]}...")
            return True

        try:
            # Trimite via Telegram Bot API
            token = self.config.get("bot_token")
            chat_id = self.config.get("chat_id")

            if not token or not chat_id:
                log("⚠️  Telegram neconfigurat", "WARNING")
                return False

            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

            req = urllib.request.Request(
                url,
                data=urllib.parse.urlencode(data).encode(),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200

        except Exception as e:
            log(f"Eroare Telegram: {e}", "ERROR")
            return False

    def send_status(self):
        """Trimite status periodic."""
        stats = self.brain.get_stats()
        message = f"""
🧠 *Immortal Brain - Status*

📊 Statistici:
• Neuroni: {stats["total"]}
• Activi: {stats["active"]}
• Arhivați: {stats["archived"]}

🔄 Ultima acțiune: {stats["last_action"]}
⏱️ Uptime: {stats["uptime"]}

_Următorul puls în 60 secunde..._
        """
        self.send_message(message)


# =============================================================================
# CREIERUL AUTONOM (Kernel + Orchestrator)
# =============================================================================


class AutonomousBrain:
    """Kernel-ul central - Inima sistemului."""

    def __init__(self):
        ensure_dirs()
        self.neurons: Dict[str, Neuron] = {}
        self.state = load_json(
            STATE_FILE,
            {
                "start_time": datetime.now().isoformat(),
                "action_count": {"maintenance": 0, "memory": 0, "curiosity": 0},
                "last_action": None,
                "is_busy": False,
            },
        )

        # Reset busy flag at startup (in case of crash)
        self.state["is_busy"] = False

        # Subsisteme
        self.glia = GliaSystem(self)
        self.memory = MemorySystem(self)
        self.curiosity = CuriositySystem(self)
        self.comm = CommunicationSystem(self)

        self.load_index()
        log("🧠 AUTONOMOUS BRAIN v4.0 inițializat")

    def load_index(self):
        """Încarcă indexul neuronal."""
        data = load_json(INDEX_FILE, {})
        self.neurons = {nid: Neuron.from_dict(ndata) for nid, ndata in data.items()}
        log(f"📖 Index încărcat: {len(self.neurons)} neuroni")

    def save_index(self):
        """Salvează indexul."""
        data = {nid: n.to_dict() for nid, n in self.neurons.items()}
        save_json(INDEX_FILE, data)

    def add_neuron(self, neuron: Neuron):
        """Adaugă sau actualizează un neuron."""
        if neuron.id in self.neurons:
            # Actualizează existent
            existing = self.neurons[neuron.id]
            existing.content = neuron.content
            existing.tags = neuron.tags
            existing.modified_at = datetime.now().isoformat()
        else:
            # Adaugă nou
            self.neurons[neuron.id] = neuron

    def get_stats(self) -> Dict:
        """Returnează statistici."""
        start = datetime.fromisoformat(self.state["start_time"])
        uptime = datetime.now() - start

        active = sum(1 for n in self.neurons.values() if n.weight > 1.5)
        archived = len(self.neurons) - active

        return {
            "total": len(self.neurons),
            "active": active,
            "archived": archived,
            "last_action": self.state.get("last_action", "N/A"),
            "uptime": str(uptime).split(".")[0],
            "actions": self.state["action_count"],
        }

    def notify(self, message: str):
        """Trimite notificare."""
        self.comm.send_message(message)

    def decide_action(self) -> str:
        """
        Decizie probabilistică:
        - 70%: Mentenanță (Glia)
        - 20%: Memorie (Conexiuni)
        - 10%: Curiozitate (Entropie)
        """
        roll = random.random()
        if roll < PROBABILITIES["maintenance"]:
            return "maintenance"
        elif roll < PROBABILITIES["maintenance"] + PROBABILITIES["memory"]:
            return "memory"
        else:
            return "curiosity"

    def pulse(self):
        """
        Bătaia inimii - Execută un ciclu de acțiune.
        """
        # Verifică histerezis (nu rula dacă ești ocupat)
        if self.state.get("is_busy"):
            log("⏸️  Sistem ocupat, sărim pulsul")
            return

        self.state["is_busy"] = True

        try:
            # Decide ce acțiune să execute
            action = self.decide_action()
            self.state["last_action"] = action
            self.state["action_count"][action] += 1

            log(f"🫀 PULS: Acțiune selectată [{action.upper()}]")

            # Execută acțiunea
            if action == "maintenance":
                self.glia.maintenance_cycle()
            elif action == "memory":
                self.memory.memory_cycle()
            elif action == "curiosity":
                self.curiosity.curiosity_cycle()

            # Salvează stare
            save_json(STATE_FILE, self.state)

        except Exception as e:
            log(f"❌ Eroare în puls: {e}", "ERROR")
        finally:
            self.state["is_busy"] = False

    def run_daemon(self):
        """
        Rulează ca daemon - buclă infinită.
        """
        log("🤖 DAEMON MODE ACTIVAT")
        log("🫀 Inima începe să bată...")

        # Salvează PID
        PID_FILE.write_text(str(os.getpid()))

        try:
            last_minute = -1
            while True:
                now = datetime.now()

                # Bătaia inimii la fiecare minut
                if now.second == 0 and now.minute != last_minute:
                    last_minute = now.minute
                    self.pulse()

                    # Trimite status la fiecare 15 minute
                    if now.minute % 15 == 0:
                        self.comm.send_status()

                time.sleep(1)

        except KeyboardInterrupt:
            log("🛑 Daemon oprit de utilizator")
        finally:
            if PID_FILE.exists():
                PID_FILE.unlink()

    def run_single_cycle(self):
        """Rulează un singur ciclu (mod manual)."""
        self.pulse()

    def show_status(self):
        """Afișează statusul."""
        stats = self.get_stats()
        print("\n" + "=" * 60)
        print("🧠 IMMORTAL BRAIN v4.0 - STATUS")
        print("=" * 60)
        print(f"\n📊 Neuroni:")
        print(f"   Total: {stats['total']}")
        print(f"   Activi: {stats['active']}")
        print(f"   Arhivați: {stats['archived']}")
        print(f"\n⏱️ Uptime: {stats['uptime']}")
        print(f"🔄 Ultima acțiune: {stats['last_action']}")
        print(f"\n📈 Acțiuni efectuate:")
        for action, count in stats["actions"].items():
            print(f"   • {action}: {count}")

        if PID_FILE.exists():
            print(f"\n🤖 Daemon: ACTIVE (PID: {PID_FILE.read_text()})")
        else:
            print(f"\n😴 Daemon: INACTIVE")
        print("=" * 60 + "\n")


# =============================================================================
# INTERFAȚA DE COMANDĂ
# =============================================================================


def print_help():
    """Afișează ajutorul."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         IMMORTAL BRAIN v4.0 - AUTONOMOUS AGENT                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Agent autonom de memorie neuronală biologic inspirat            ║
╠══════════════════════════════════════════════════════════════════╣
║  COMENZI:                                                        ║
║                                                                  ║
║  daemon              - Pornește agentul autonom (buclă infinită) ║
║  pulse               - Rulează un singur ciclu manual            ║
║  status              - Vezi statusul sistemului                  ║
║  stop                - Oprește daemonul (trimite semnal)         ║
║  config              - Configurează Telegram și alte setări      ║
║                                                                  ║
║  ARHITECTURĂ:                                                    ║
║    🔴 Kernel     - Event Loop & Scheduler (Inima)               ║
║    🧠 Brain      - LLM Integration & Processing                 ║
║    📡 Nervous    - Telegram/Webhook Communication               ║
║    🌐 Glia       - Maintenance & File Organization              ║
║    ✨ Curiosity  - Novel Concept Generator                      ║
║                                                                  ║
║  PROBABILITĂȚI:                                                  ║
║    • 70% Mentenanță (Glia)                                      ║
║    • 20% Memorie (Conexiuni)                                    ║
║    • 10% Curiozitate (Entropie)                                 ║
╚══════════════════════════════════════════════════════════════════╝
""")


def main():
    """Funcția principală."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "daemon":
        brain = AutonomousBrain()
        brain.run_daemon()

    elif command == "pulse":
        brain = AutonomousBrain()
        brain.run_single_cycle()

    elif command == "status":
        brain = AutonomousBrain()
        brain.show_status()

    elif command == "stop":
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text())
                os.kill(pid, 9)
                PID_FILE.unlink()
                print("🛑 Daemon oprit")
            except Exception as e:
                print(f"❌ Eroare la oprire: {e}")
        else:
            print("ℹ️  Daemonul nu rulează")

    elif command == "config":
        print("\n⚙️  CONFIGURARE")
        print("\nEditarează fișierul:")
        print(f"  {CONFIG_FILE}")
        print("\nExemplu config:")
        print(
            json.dumps(
                {
                    "telegram": {
                        "enabled": True,
                        "bot_token": "YOUR_BOT_TOKEN",
                        "chat_id": "YOUR_CHAT_ID",
                    },
                    "ollama": {
                        "host": "http://localhost:11434",
                        "model": "llama3.2:3b",
                    },
                },
                indent=2,
            )
        )

    elif command in ["help", "ajutor", "?"]:
        print_help()

    else:
        print(f"❌ Comandă necunoscută: {command}")
        print_help()


if __name__ == "__main__":
    main()
