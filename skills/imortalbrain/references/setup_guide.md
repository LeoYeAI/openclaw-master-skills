# Ghid de Instalare și Configurare: Sistemul „Creier Nemuritor”

Acest ghid detaliază pașii necesari pentru a instala și configura sistemul „Creier Nemuritor” pe o instanță OpenClaw, asigurând o funcționare optimă și automatizată.

## 1. Pregătirea Mediului Python

### Asigură-te că Python este în PATH
Dacă la rularea `python` în terminal primești eroarea `'python:' is not recognized...`, înseamnă că Python nu este în variabila de mediu `PATH`.
**Soluția:** Când rulezi comenzi Python, folosește calea completă către executabil, de exemplu: `C:\Python314\python.exe`.

### Instalează dependențele (librăria `watchdog`)
Pentru modul de monitorizare în timp real („The Watcher”), este necesară librăria `watchdog`.

**Instalare:**
1.  Deschide un terminal (CMD sau PowerShell).
2.  Navighează la directorul unde este instalat OpenClaw (ex: `cd C:\Users\ovidi\.openclaw\workspace`).
3.  Rulează comanda (folosind calea completă la Python dacă este necesar):
    `C:\Python314\python.exe -m pip install watchdog`
    (sau `python -m pip install watchdog` dacă Python este în PATH).

## 2. Configurați Fișierele Cheie

### `brain_service.py`
Acesta este scriptul principal. Asigură-te că fișierul `brain_service.py` se află în directorul `C:\Users\ovidi\.openclaw\workspace`.

### `run_pulse.bat`
Acesta este fișierul batch care va fi apelat de Task Scheduler. Asigură-te că fișierul `run_pulse.bat` se află în directorul `C:\Users\ovidi\.openclaw\workspace` și conține următorul cod:

```batch
@echo off
:: Ascunde fereastra de consolă (rulează silentios)
if not "%1" == "max" start /MIN cmd /c %0 max & exit/b

:: Setează calea către folderul proiectului
cd /d "%USERPROFILE%\.openclaw\workspace"

:: Rulează Motorul Cognitiv (folosind calea completă la Python)
echo [PULS] Sistemul porneste procesarea...
C:\Python314\python.exe brain_service.py process

:: (Opțional) Scrie un log scurt ca să știi că a rulat
echo Puls executat la %date% %time% >> pulse_log.txt
exit
```
**Atenție:** Asigură-te că `C:\Python314\python.exe` este calea corectă către executabilul Python pe sistemul tău.

## 3. Automatizarea „Pulsului Biologic” cu Windows Task Scheduler

Pentru a rula automat procesarea memoriei la intervale regulate:

1.  **Deschide Task Scheduler:**
    *   Apasă tasta `Windows`, scrie `Task Scheduler` și deschide aplicația.
2.  **Creează un Task de Bază:**
    *   În partea dreaptă, sub secțiunea „Actions”, dă click pe `Create Basic Task...`.
3.  **Completează Detaliile Task-ului:**
    *   **Name:** Scrie `OpenClaw Brain Pulse`.
    *   **Trigger:** Selectează `Daily` (Zilnic) -> `Next`.
        *   Setează ora de începere (ex: `08:00 AM`).
        *   Selectează `Repeat task every:` și setează la `1 hour` (sau `5 minutes` pentru un creier foarte reactiv, accesând `Properties > Triggers > Edit` după creare).
    *   **Action:** Selectează `Start a program`.
        *   **Program/script:** Apasă `Browse...` și alege fișierul `C:\Users\ovidi\.openclaw\workspace\run_pulse.bat`.
        *   **Start in (Optional):** Scrie `C:\Users\ovidi\.openclaw\workspace\` (cu backslash la final).
4.  **Finalizează Crearea Task-ului:**
    *   Dă click pe `Finish`.

## 4. Rularea „Paznicului” („The Watcher”) pentru Reacție Instantanee

Pentru a monitoriza în timp real folderul `memory` și a procesa notițele instantaneu:

1.  **Deschide un terminal (CMD sau PowerShell) *nou*.**
2.  **Navighează** către directorul `C:\Users\ovidi\.openclaw\workspace`.
    `cd C:\Users\ovidi\.openclaw\workspace`
3.  **Rulează comanda:**
    `C:\Python314\python.exe brain_service.py` (fără argumentul `process`)
    *   Lasă acest terminal deschis și minimizează-l.

## 5. Utilizarea Funcției de Căutare

Pentru a interoga rapid memoria sistemului:

1.  **Asigură-te că „Paznicul” este activ** (sau rulează `brain_service.py process` o dată pentru a actualiza indexul).
2.  **Deschide un *alt* terminal (CMD sau PowerShell).**
3.  **Navighează** către directorul `C:\Users\ovidi\.openclaw\workspace`.
4.  **Rulează comanda de căutare:**
    `C:\Python314\python.exe brain_service.py cauta "query"`
    (înlocuiește `"query"` cu termenul sau tag-ul căutat, ex: `"Watcher"`, `"#test"`, `"#urgent"`)

## 6. Curățarea Memoriei Vechii (Opțional, după instalare completă)

După ce sistemul „Creier Nemuritor” este complet operațional, poți șterge fișierele vechi de test sau rapoarte remanente din folderul `memory` sau `memory/pending_reports/`.

Acest ghid complet te va ajuta să configurezi și să utilizezi pe deplin sistemul „Creier Nemuritor”.
