# 🔧 INSTALARE RAPIDĂ - 3 Pași

## Pasul 1: Găsește Python

**Deschide CMD și scrie:**
```cmd
where python
```

**Dacă nu returnează nimic, caută manual:**
```cmd
dir "C:\Python*" /b
dir "C:\Users\%USERNAME%\AppData\Local\Programs\Python\" /b
```

**Notează calea. De exemplu:** `C:\Python39\python.exe`

---

## Pasul 2: Copiază Fișierele

**Deschide CMD ca Administrator și scrie:**

```cmd
mkdir "D:\OpenClaw_Setup\.openclaw\workspace\memory"
mkdir "D:\OpenClaw_Setup\.openclaw\workspace\Creier"
mkdir "D:\OpenClaw_Setup\.openclaw\workspace\Creier\_ARHIVA"
mkdir "D:\OpenClaw_Setup\.openclaw\workspace\Creier\_CIMITIR"

copy "D:\OpenClaw_Setup\skills\immortal-brain\HEARTBEAT.md" "D:\OpenClaw_Setup\.openclaw\workspace\HEARTBEAT_immortal_brain.md"
```

---

## Pasul 3: Testează

**Folosește calea Python găsită la Pasul 1:**

```cmd
cd "D:\OpenClaw_Setup\skills\immortal-brain"

"C:\Python39\python.exe" scripts\brain_service.py help
```

**Înlocuiește `C:\Python39\python.exe` cu calea ta reală.**

---

## 🎯 Dacă Funcționează

Vei vedea mesajul de ajutor. Atunci sistemul este gata!

## ❌ Dacă NU Funcționează

**Spune-mi exact ce eroare apare și rezolvăm împreună!**

---

## 📱 Alternativ: Rulează TEST_INSTALL.bat

**Dublează click pe:** `D:\OpenClaw_Setup\skills\immortal-brain\TEST_INSTALL.bat`

Acesta va:
1. Găsi Python automat
2. Testa toate componentele
3. Spune exact ce e în regulă și ce nu

**Dacă nici acesta nu merge, copiază aici mesajul de eroare și îl rezolv!**
