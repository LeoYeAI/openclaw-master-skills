#!/usr/bin/env python3
"""Smart Email Agent v3 — Setup inicial."""
import json, os, shutil, sys
from datetime import datetime
from pathlib import Path

WS = Path.home() / '.openclaw' / 'workspace'

def ok(m):   print(f"  ✅ {m}")
def warn(m): print(f"  ⚠️  {m}")
def err(m):  print(f"  ❌ {m}"); 

def check_prereqs():
    print("\n── Prerequisitos")
    if shutil.which('gog'): ok("gog CLI instalado")
    else: warn("gog no encontrado — instalar: npm i -g gogcli  o  brew install gogcli")
    gog_acc = os.environ.get('GOG_ACCOUNT')
    if gog_acc: ok(f"GOG_ACCOUNT = {gog_acc}")
    else: err("GOG_ACCOUNT no configurado — requerido"); return False
    if os.environ.get('ANTHROPIC_API_KEY'): ok("ANTHROPIC_API_KEY configurado")
    else: err("ANTHROPIC_API_KEY no configurado — requerido para análisis IA"); return False
    for k in ['EMAIL_BUDGET_USD', 'NOTIFY_CHANNEL', 'SAFE_BROWSING_API_KEY']:
        v = os.environ.get(k)
        if v: ok(f"{k} = {v}")
        else: warn(f"{k} no configurado (opcional)")
    return True

def init_budget():
    print("\n── Presupuesto")
    f = WS / 'budget_tracker.json'
    if f.exists():
        d = json.loads(f.read_text())
        pct = round(d['spent_usd'] / d['budget_usd'] * 100)
        ok(f"${d['spent_usd']:.3f} / ${d['budget_usd']:.2f} ({pct}%) — mes {d['month']}")
        return
    budget = float(os.environ.get('EMAIL_BUDGET_USD', '1.00'))
    f.write_text(json.dumps({
        "month": datetime.now().strftime('%Y-%m'),
        "budget_usd": budget, "spent_usd": 0.0,
        "alert_at_pct": [60, 80, 95], "sessions": []
    }, indent=2))
    ok(f"Inicializado: ${budget:.2f}/mes")

def init_learnings():
    print("\n── Learnings")
    d = WS / '.learnings'
    d.mkdir(exist_ok=True)
    for fn in ['LEARNINGS.md', 'ERRORS.md']:
        fp = d / fn
        if not fp.exists():
            fp.write_text(f"# {fn.replace('.md','')}\n\n")
            ok(f"Creado: .learnings/{fn}")
        else:
            n = fp.read_text().count('**Status**: pending')
            ok(f".learnings/{fn} — {n} pendientes")

def check_gog_auth():
    print("\n── Autenticación Gmail")
    import subprocess
    r = subprocess.run(['gog', 'auth', 'status'], capture_output=True, text=True)
    if r.returncode == 0: ok(f"Autenticado: {r.stdout.strip()}")
    else: warn(f"No autenticado — ejecutar: gog auth add {os.environ.get('GOG_ACCOUNT', 'tu@gmail.com')}")

if __name__ == '__main__':
    print("═══════════════════════════════════════")
    print("  Smart Email Agent v3 — Setup Inicial")
    print("═══════════════════════════════════════")
    if not check_prereqs(): sys.exit(1)
    init_budget()
    init_learnings()
    check_gog_auth()
    print("\n✅ Listo.")
    print("   Activar hook: openclaw hooks enable smart-email-agent\n")
