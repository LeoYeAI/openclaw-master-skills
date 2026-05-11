# Immortal Brain v5.0 - Agent Autonom Proactiv
# Frecvență: 2 minute (bătăi inimii)
# Timeout feedback: 3 bătăi = 6 minute

## 🫀 HEARTBEAT PRINCIPAL - Workflow Automat
### La fiecare 2 minute
- **Acțiune**: Rulează `python skills/immortal-brain/scripts/brain_service.py heartbeat`
- **Scop**: Procesează toate task-urile prin workflow automat
- **Workflow**:
  1. **Research** - Cercetează informații similare
  2. **Analysis** - Analizează complexitatea și dependențele
  3. **Planning** - Generează pași de implementare
  4. **Approval** - Cere permisiunea utilizatorului
  5. **Execution** - Execută pașii (dacă aprobat sau timeout 6 min)
  6. **Monitoring** - Monitorizează progresul
  7. **Complete** - Finalizează și raportează

- **Notificări**:
  ```
  🫀 HEARTBEAT #{numar}
  
  📊 RAPORT PROGRES:
  • Total task-uri: X
  • Completate: X (X%)
  • Progres mediu: X%
  
  **Distribuție pe stări:**
  • 🔬 Research: X
  • 📊 Analysis: X
  • 📋 Planning: X
  • ⏳ Awaiting Approval: X
  • 🚀 Execution: X
  • 📈 Monitoring: X
  • ✅ Completed: X
  ```

## 📥 DETECȚIE TELEGRAM - Task-uri Noi
### La primirea mesajului pe Telegram
- **Trigger**: Mesaj nou în chat-ul OpenClaw
- **Acțiune**: 
  1. Salvează mesajul în `workspace/memory/telegram_YYYYMMDD_HHMMSS.md`
  2. Rulează `heartbeat` imediat pentru procesare
- **Notificare**: 
  ```
  📥 Task nou primit de pe Telegram:
  "{conținut_mesaj}"
  
  🔬 Încep cercetarea și analiza automat...
  ⏱️ Voi reveni cu planul în câteva minute.
  ```

## ⏳ ALERTE TIMEOUT - Auto-Aprobare
### La fiecare bătaie (pentru task-uri în așteptare)
- **Condiție**: Task în stare "awaiting_approval" de >2 bătăi
- **Acțiune**: 
  - Bătaia 1: Trimite reminder detaliat cu progres
  - Bătaia 2: Trimite avertisment final
  - Bătaia 3: Auto-aprobată și continuă execuția
- **Notificări**:
  ```
  ⏳ REMINDER - Task așteaptă aprobare de 2 minute:
  "{conținut_task}"
  
  📊 Progres: 50% (Planning complet)
  ⏱️ Auto-aprobat în 4 minute dacă nu răspunzi.
  
  ✅ Răspunde OK pentru a continua
  ❌ Răspunde STOP pentru a anula
  💡 Sau propune modificări
  ```

## 📊 RAPORT DETALIAT - Fiecare 5 Bătăi (10 minute)
### La fiecare 10 minute
- **Acțiune**: Generează raport extins cu:
  - Progres individual fiecărui task activ
  - Conexiuni descoperite între task-uri
  - Sugestii îmbunătățiri din task-uri similare completate
  - Combinări creative de tag-uri pentru idei noi
- **Notificare**:
  ```
  📊 RAPORT DETALIAT (10 minute)
  
  **Task-uri Active:**
  1. "{task1}" - 35% - În execuție
     💡 Sugestie: Îmbunătățit cu lecții din task similar
  
  2. "{task2}" - 60% - Așteaptă aprobare
     ⏳ Auto-aprobat în 2 minute
  
  **Conexiuni Noi Descoperite:**
  • Task-ul "API" conectat cu "Authentication" (85% similaritate)
  • Sugestie: Poți combina aceste două task-uri
  
  **💡 Sugestie Creativă:**
  Am identificat combinația interesantă: #dev + #research
  Task-uri care ar putea beneficia de o abordare integrată:
  - "Implementare feature X"
  - "Research soluții Y"
  ```

## 🔬 ALERTE RESEARCH - Task-uri în Cercetare
### Când task ajunge în starea "research"
- **Acțiune**: 
  - Caută task-uri similare în memorie
  - Identifică topic-uri conexe
  - Compilează note de cercetare
- **Notificare**:
  ```
  🔬 CERCETARE COMPLETĂ
  
  Task: "{conținut}"
  
  **Rezultate:**
  • Task-uri similare găsite: X (relevanță 85%)
    - "{task_similar_1}"
    - "{task_similar_2}"
  • Topic '{topic}': X task-uri existente
  • Dependențe identificate: X
  
  Trec la analiza complexității...
  ```

## 📊 ALERTE ANALYSIS - Task-uri Analizate
### Când task ajunge în starea "analysis"
- **Acțiune**:
  - Evaluează complexitatea
  - Identifică prioritatea
  - Sugerează îmbunătățiri din task-uri conectate
- **Notificare**:
  ```
  📊 ANALIZĂ COMPLETĂ
  
  Task: "{conținut}"
  
  **Rezultate:**
  • Complexitate: {low/medium/high}
  • Prioritate: {priority}
  • Topic: {topic}
  
  **💡 Sugestii de Îmbunătățire:**
  (din task-uri similare completate)
  • {sugestie_1}
  • {sugestie_2}
  
  Trec la planificare...
  ```

## 📋 ALERTE PLANNING - Planificare Completă
### Când task ajunge în starea "planning"
- **Acțiune**: Generează pași detaliați
- **Notificare**:
  ```
  📋 PLANIFICARE COMPLETĂ
  
  Task: "{conținut}"
  
  **Plan ({număr} pași):**
  1. {pas_1}
  2. {pas_2}
  3. {pas_3}
  ...
  
  **Aștept aprobarea ta pentru a începe execuția...**
  ⏱️ Auto-aprobat în 6 minute.
  
  ✅ Răspunde "OK" pentru a continua
  ❌ Răspunde "STOP" pentru a anula
  💡 Sau propune modificări la plan
  ```

## 🚀 ALERTE EXECUTION - Execuție Începută
### Când task intră în execuție (aprobat sau auto)
- **Notificare**:
  ```
  🚀 EXECUȚIE ÎNCEPUTĂ
  
  Task: "{conținut}"
  Status: {approved/auto_approved}
  
  **Pași activi:**
  ▶️ {pas_1}
  ▶️ {pas_2}
  ▶️ {pas_3}
  
  Voi raporta progresul la fiecare 2 minute.
  ```

## 📈 ALERTE PROGRESS - Actualizări Progres
### La fiecare bătaie pentru task-uri în execuție
- **Notificare**:
  ```
  📈 PROGRES: "{task}"
  
  • Progres: {X}%
  • Stare: În execuție
  • ETA: ~{Y} minute rămase
  
  **Pași finalizați:**
  ✅ {pas_completat_1}
  ✅ {pas_completat_2}
  
  **Pași activi:**
  ▶️ {pas_activ}
  ```

## ✅ ALERTE COMPLETION - Task Finalizat
### Când task ajunge la 100%
- **Notificare**:
  ```
  ✅ TASK FINALIZAT
  
  Task: "{conținut}"
  Progres: 100%
  
  **Statistici:**
  • Timp total: {X} bătăi de inimă ({X*2} minute)
  • Pași executați: {Y}
  • Îmbunătățiri aplicate: {Z}
  
  🎉 Task finalizat cu succes!
  
  **💡 Recomandare:**
  Pe baza acestui task, sugerez să explorezi:
  • {task_sugerat_1}
  • {task_sugerat_2}
  ```

## 💡 SUGESTII CREATIVE - Combinări Tag-uri
### La fiecare 5 bătăi (10 minute)
- **Condiție**: Dacă există combinații interesante de tag-uri
- **Notificare**:
  ```
  💡 SUGESTIE CREATIVĂ
  
  Am identificat combinația interesantă:
  {tag_1} + {tag_2} + {tag_3}
  
  **Task-uri conectate:**
  • "{task_1}"
  • "{task_2}"
  
  💭 Sugestie: Aceste task-uri ar putea beneficia de o 
     abordare integrată. Vrei să creez un task master 
     care să le coordoneze?
  
  ✅ Răspunde "DA" pentru a crea task coordonator
  ❌ Răspunde "NU" pentru a ignora
  ```

## 🔄 PROFIL UTILIZATOR - Învățare Continuă
### La fiecare 10 bătăi (20 minute)
- **Acțiune**: Actualizează profilul utilizator
- **Notificare** (opțional, la schimbări semnificative):
  ```
  🧠 PROFIL ACTUALIZAT
  
  Am învățat despre tine:
  • Topicuri preferate: {top_3}
  • Rata aprobare automată: {X}%
  • Pattern lucru: orele {interval_orar}
  • Tip task-uri frecvente: {tipuri}
  
  Voi folosi aceste informații pentru a prioritiza 
  și sugera task-uri mai relevante!
  ```

## 🆔 GESTIONARE IDENTITATE (IDENTITY.md)
### La fiecare 20 bătăi (40 minute)
- **Acțiune**: 
  - Analizează IDENTITY.md
  - Compară cu comportamentul real
  - Sugerează îmbunătățiri
- **Notificare** (dacă sunt sugestii):
  ```
  🆔 SUGESTII ÎMBUNĂTĂȚIRE IDENTITATE
  
  Am analizat comportamentul și sugerez:
  
  • **Creature:** Adaugă referire la #dev în descriere
    Motiv: Topic frecvent în task-uri
  
  • **Vibe:** Menționează că răspund în ~{X} minute
    Motiv: Timp mediu de procesare observat
  
  • **Emoji:** Consideră 🚀 în loc de 😄
    Motiv: Rată finalizare {Y}% (foarte productiv)
  
  💡 Sugestii bazate pe {număr} task-uri analizate.
  
  Răspunde cu:
  ✅ "APLICĂ_SUGESTII" - Aplică toate sugestiile
  📝 "UPDATE [câmp]=[valoare]" - Actualizează specific
  ❌ "IGNORĂ" - Păstrează identitatea actuală
  ```

### La modificarea IDENTITY.md
- **Trigger**: Fișier IDENTITY.md modificat
- **Acțiune**:
  - Salvează versiunea anterioară în istoric
  - Validează noua structură
  - Notifică despre schimbare
- **Notificare**:
  ```
  🆔 IDENTITATE ACTUALIZATĂ
  
  Fișierul IDENTITY.md a fost modificat manual.
  
  **Versiune:** {old_version} → {new_version}
  **Data:** {timestamp}
  
  Schimbări detectate:
  • {field_1}: {old_value} → {new_value}
  • {field_2}: {old_value} → {new_value}
  
  ✨ Noua identitate este activă!
  ```

### Zilnic la ora 08:00 - Review Identitate
- **Acțiune**:
  - Generează raport complet identitate
  - Verifică consistență cu comportament
  - Propune ajustări dacă e necesar
- **Notificare**:
  ```
  🆔 RAPORT ZILNIC IDENTITATE
  
  **Profil actual:**
  • Nume: {name}
  • Creature: {creature}
  • Vibe: {vibe}
  • Emoji: {emoji}
  
  **Statistici:**
  • Versiune: {version}
  • Actualizări totale: {count}
  • Ultima actualizare: {date}
  
  **Consistență:**
  • Task-uri procesate: {total_tasks}
  • Comportament vs Identitate: {match_percentage}%
  
  {dacă există discrepanțe}
  ⚠️ Notă: Identitatea ar putea reflecta mai bine 
     comportamentul prin [sugestii].
  ```

## 📚 CORE MEMORY - Fișiere Esențiale
### La fiecare 30 minute (15 bătăi)
- **Acțiune**: 
  - Analizează SOUL.md, TOOLS.md, MEMORY.md, USER.md
  - Verifică completitudinea și calitatea
  - Generează sugestii îmbunătățire
- **Notificare** (dacă sunt sugestii):
  ```
  📚 SUGESTII CORE MEMORY
  
  Am analizat fișierele esențiale:
  
  📄 **MEMORY.md:** 2 sugestii
    • Prea puține preferințe documentate
    • Sugestie: Adaugă preferințe despre comunicare
  
  📄 **USER.md:** 1 sugestie
    • Lipsește filozofia de lucru
    • Sugestie: Adaugă valorile profesionale
  
  💡 Folosește: `python core_memory.py analyze` pentru detalii complete
  🔧 Folosește: `python core_memory.py optimize` pentru optimizare automată
  ```

### La fiecare 2 ore - Optimizare MEMORY.md
- **Acțiune**:
  - Elimină duplicate
  - Organizează secțiuni
  - Comprimă informații redundante
- **Notificare**:
  ```
  🔧 MEMORY.md OPTIMIZAT
  
  Am optimizat fișierul de memorie:
  • Reducere: 15% dimensiune
  • Duplicate eliminate: 3
  • Secțiuni reorganizate
  • Backup salvat: MEMORY_backup_YYYYMMDD_HHMMSS.md
  
  Fișierul este acum mai ușor de procesat și citit!
  ```

### Săptămânal (Duminică 11:00) - Review Complet Core Memory
- **Acțiune**:
  - Raport complet pentru toate fișierele core
  - Sugestii majore de îmbunătățire
  - Creare template-uri pentru secțiuni lipsă
- **Notificare**:
  ```
  📚 RAPORT SĂPTĂMÂNAL CORE MEMORY
  
  **Stare Generală:**
  • Fișiere active: 5/5
  • Scor mediu calitate: 82%
  
  **Fișiere:**
  📗 SOUL.md        - 75% complet | 0 sugestii
  📘 TOOLS.md       - 100% complet | 0 sugestii  
  📙 MEMORY.md      - 60% complet | 3 sugestii
  📕 USER.md        - 50% complet | 2 sugestii
  📓 IDENTITY.md    - 90% complet | 1 sugestie
  
  **Acțiuni recomandate:**
  1. Actualizează MEMORY.md cu preferințe recente
  2. Completează secțiunea "Filozofie" în USER.md
  3. Consideră ajustări în IDENTITY.md bazate pe comportament
  
  💡 Toate sugestiile sunt bazate pe analiza a {număr} task-uri
     din ultima săptămână.
  ```

## 🎯 RECOMANDĂRI PROACTIVE
### Zilnic la ora 09:00
- **Acțiune**: 
  - Analizează task-urile din ultimele 24 ore
  - Identifică pattern-uri și priorități
  - Sugerează focus pentru ziua respectivă
- **Notificare**:
  ```
  🎯 RECOMANDARE ZILNICĂ
  
  Analizând task-urile tale, sugerez focus pe:
  
  **Prioritate #1:** {topic_cel_mai_frecvent}
  Ai {număr} task-uri în acest topic.
  
  **Task urgent:**
  • "{task_urgent}"
  
  **💡 Sugestie:**
  Pe baza profilului tău, aceasta ar fi o ordine 
  eficientă de lucru astăzi:
  1. {task_sugerat_1}
  2. {task_sugerat_2}
  3. {task_sugerat_3}
  ```

## 🧹 CURĂȚARE SĂPTĂMÂNALĂ
### Duminică la ora 10:00
- **Acțiune**:
  - Arhivează task-uri completate vechi
  - Reconstruiește graf conexiuni
  - Curăță task-uri blocate sau abandonate
  - Generează raport săptămânal
- **Notificare**:
  ```
  🧹 CURĂȚARE SĂPTĂMÂNALĂ
  
  **Săptămâna aceasta:**
  • Task-uri completate: {X}
  • Task-uri noi: {Y}
  • Progres mediu: {Z}%
  
  **Arhivate:** {număr} task-uri vechi
  **Curățate:** {număr} task-uri blocate
  
  **🏆 Realizarea săptămânii:**
  Cel mai complex task finalizat:
  "{task_cel_mai_complex}"
  
  **💡 Pentru săptămâna viitoare:**
  Pe baza datelor, sugerez să prioritizezi:
  • {topic_1}
  • {topic_2}
  ```

---

## 📝 NOTE IMPLEMENTARE

### Răspunsuri Utilizator:
- **"OK"** sau **"DA"** → Aprobă task-ul în așteptare
- **"STOP"** sau **"NU"** → Anulează task-ul
- **Text liber** → Modifică task-ul cu propunerile tale
- **Orice altceva** → Adaugă comentariu/task nou

### Auto-Aprobare:
- După 3 bătăi (6 minute) fără răspuns
- Task-ul continuă automat în execuție
- Se bazează pe profilul utilizatorului
- Notificare confirmare auto-aprobat

### Progres Procentual:
- research: 10%
- analysis: 25%
- planning: 40%
- awaiting_approval: 50%
- auto_approved: 55%
- execution: crește dinamic 60-85%
- monitoring: 85%
- completed: 100%

### Conexiuni Task-uri:
- Automat pe baza tag-urilor comune
- Similaritate calculată (Jaccard index)
- Îmbunătățiri sugerate din task-uri completate
- Graf actualizat la fiecare heartbeat

---

## 🎊 REZULTAT

**Sistemul are acum INIȚIATIVE COMPLETE:**
- ✅ Gândește și cercetează singur
- ✅ Analizează și planifică
- ✅ Cere aprobare sau auto-aprobat
- ✅ Execută și monitorizează
- ✅ Raportează progres procentual
- ✅ Sugerează îmbunătățiri
- ✅ Generează idei creative
- ✅ Învață din comportament

**Tu doar:**
1. ✅ Trimizi task-uri (Telegram/memory)
2. ✅ Răspunzi când vrei (opțional)
3. ✅ Primești rapoarte și sugestii

**Sistemul face RESTUL!** 🤖🧠✨
