#!/usr/bin/env python3
"""
VERIFICARE INSTALARE - Immortal Brain v5.0
Script pentru verificarea completă a instalării
"""

import sys
import os
from pathlib import Path


# Culori pentru output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def main():
    print("\n" + "=" * 70)
    print("  VERIFICARE INSTALARE - Immortal Brain v5.0")
    print("=" * 70 + "\n")

    errors = []
    warnings = []

    # 1. Verificare Python
    print_info("Verificare Python...")
    if sys.version_info >= (3, 8):
        print_success(f"Python {sys.version.split()[0]} (>= 3.8)")
    else:
        print_error(f"Python {sys.version.split()[0]} (< 3.8 necesar)")
        errors.append("Python prea vechi")

    # 2. Verificare structură directoare
    print_info("\nVerificare structură...")

    workspace = Path("D:\\OpenClaw_Setup\\.openclaw\\workspace")
    skill_dir = Path("D:\\OpenClaw_Setup\\skills\\immortal-brain")

    if skill_dir.exists():
        print_success(f"Director skill: {skill_dir}")
    else:
        print_error(f"Director skill lipsă: {skill_dir}")
        errors.append("Director skill nu există")

    if workspace.exists():
        print_success(f"Workspace: {workspace}")
    else:
        print_error(f"Workspace lipsă: {workspace}")
        errors.append("Workspace nu există")

    # 3. Verificare fișiere esențiale
    print_info("\nVerificare fișiere esențiale...")

    essential_files = [
        ("brain_service.py", skill_dir / "scripts" / "brain_service.py"),
        ("core_memory.py", skill_dir / "scripts" / "core_memory.py"),
        ("HEARTBEAT.md", skill_dir / "HEARTBEAT.md"),
        ("SKILL.md", skill_dir / "SKILL.md"),
    ]

    for name, filepath in essential_files:
        if filepath.exists():
            size = filepath.stat().st_size
            print_success(f"{name} ({size} bytes)")
        else:
            print_error(f"{name} - LIPSEȘTE")
            errors.append(f"Fișier lipsă: {name}")

    # 4. Verificare directoare de lucru
    print_info("\nVerificare directoare de lucru...")

    work_dirs = [
        ("memory", workspace / "memory"),
        ("Creier", workspace / "Creier"),
        ("Creier/_ARHIVA", workspace / "Creier" / "_ARHIVA"),
        ("Creier/_CIMITIR", workspace / "Creier" / "_CIMITIR"),
    ]

    for name, dirpath in work_dirs:
        if dirpath.exists():
            print_success(f"{name}/")
        else:
            print_warning(f"{name}/ - va fi creat automat")
            warnings.append(f"Director va fi creat: {name}")

    # 5. Verificare fișiere core
    print_info("\nVerificare fișiere core...")

    core_files = [
        ("SOUL.md", workspace / "SOUL.md"),
        ("TOOLS.md", workspace / "TOOLS.md"),
        ("MEMORY.md", workspace / "MEMORY.md"),
        ("USER.md", workspace / "USER.md"),
        ("IDENTITY.md", workspace / "IDENTITY.md"),
    ]

    for name, filepath in core_files:
        if filepath.exists():
            print_success(f"{name}")
        else:
            print_warning(f"{name} - va fi creat template")
            warnings.append(f"Fișier core va fi creat: {name}")

    # 6. Testare comandă de bază
    print_info("\nTestare funcționalitate...")

    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(skill_dir / "scripts" / "brain_service.py"), "help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print_success("Comanda 'help' funcționează")
        else:
            print_error("Comanda 'help' a eșuat")
            errors.append("Test funcționalitate eșuat")
    except Exception as e:
        print_error(f"Eroare test: {e}")
        errors.append(f"Eroare test: {e}")

    # 7. Verificare HEARTBEAT.md în workspace
    print_info("\nVerificare HEARTBEAT.md...")

    heartbeat_files = list(workspace.glob("HEARTBEAT*.md"))
    if heartbeat_files:
        print_success(f"HEARTBEAT.md configurat ({len(heartbeat_files)} fișier(e))")
        for hf in heartbeat_files:
            print(f"   - {hf.name}")
    else:
        print_warning("HEARTBEAT.md nu este în workspace")
        warnings.append("Copiază HEARTBEAT.md în workspace")

    # Rezultat final
    print("\n" + "=" * 70)
    print("  REZULTAT VERIFICARE")
    print("=" * 70 + "\n")

    if not errors and not warnings:
        print_success("🎉 INSTALARE PERFECTĂ! Toate verificările au trecut.")
        print("\nSistemul este gata de utilizare!")
        print("\nPentru a începe:")
        print("  1. Adaugă task-uri în: workspace/memory/*.md")
        print("  2. Așteaptă primul heartbeat (2 minute)")
        print("  3. Primești notificări automate!")
        return 0
    elif not errors:
        print_warning("⚠️  INSTALARE FUNCȚIONALĂ cu avertismente")
        print("\nAvertismente:")
        for w in warnings:
            print(f"  • {w}")
        print(
            "\nSistemul va funcționa, dar rezolvă avertismentele pentru performanță optimă."
        )
        return 0
    else:
        print_error("❌ INSTALARE INCOMPLETĂ - Probleme detectate!")
        print("\nErori critice:")
        for e in errors:
            print(f"  • {e}")
        if warnings:
            print("\nAvertismente:")
            for w in warnings:
                print(f"  • {w}")
        print("\n⚠️  Rezolvă erorile de mai sus înainte de a utiliza sistemul.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
