# Informații despre HEARTBEAT.md (Uz Intern Agent)

Acest fișier explică rolul `HEARTBEAT.md` în funcționarea internă a agentului Proton, separat de sistemul „Creier Nemuritor”.

## Rolul HEARTBEAT.md

`HEARTBEAT.md` este un fișier intern, esențial pentru gestionarea stării și a comunicării proactive a agentului. El servește ca o listă de verificare pentru agent, permițându-i să:

*   **Monitorizeze starea internă:** Verifică periodic dacă există alerte, instrucțiuni noi sau alte elemente care necesită atenție.
*   **Decidă proactivitatea:** Pe baza conținutului din `HEARTBEAT.md` (sau a lipsei acestuia), agentul decide dacă este necesar să trimită un mesaj (ex: o actualizare de stare, o întrebare) sau pur și simplu să răspundă `NO_REPLY` la un „puls” (`systemEvent: internal_biological_pulse`).
*   **Gestioneze răspunsurile la pulsuri:** Fără `HEARTBEAT.md`, agentul nu ar avea o referință rapidă pentru a evalua dacă trebuie să comunice ceva la un heartbeat.

## Cum Funcționează

Atunci când agentul primește un semnal de „puls biologic” (`systemEvent: internal_biological_pulse`), el citește `HEARTBEAT.md`.

*   **Dacă `HEARTBEAT.md` conține elemente care necesită atenție:** Agentul le procesează și comunică (dacă este cazul) utilizatorului.
*   **Dacă `HEARTBEAT.md` este gol sau nu conține nimic ce necesită acțiune imediată:** Agentul răspunde `NO_REPLY` (conform strategiei convenite), evitând comunicarea redundantă.

**Important:** `HEARTBEAT.md` este destinat uzului intern al agentului și nu este direct legat de gestionarea notițelor sau a task-urilor tale în sistemul „Creier Nemuritor”. Este un mecanism de autoreglare și de comunicare proactivă a agentului.
