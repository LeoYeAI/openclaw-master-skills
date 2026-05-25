# Humanizer PL

Umiejętność Clawdbot, która usuwa ślady pisania AI z tekstu polskiego, nadając mu bardziej naturalny, ludzki charakter.

## Instalacja

Zainstaluj przez ClawdHub:

```bash
clawdhub install humanizer-pl
```

## Użycie

Poproś agenta o humanizację tekstu:

```
Zhumanizuj ten tekst: [twój tekst]
```

Lub wywołaj bezpośrednio podczas edycji dokumentów.

## Przegląd

Oparte na przewodniku [Wikipedia „Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), utrzymywanym przez WikiProject AI Cleanup, oraz na analizie wzorców typowych dla polskojęzycznego tekstu generowanego przez AI. Kompleksowy przewodnik powstał na podstawie obserwacji tysięcy przypadków tekstu wygenerowanego przez AI.

### Kluczowa obserwacja

> „Modele językowe (LLM) stosują algorytmy statystyczne, by przewidzieć, co powinno następować dalej. Wynik dąży do najbardziej prawdopodobnego statystycznie rezultatu pasującego do najszerszego zakresu przypadków."

## 24 wykrywane wzorce

### Wzorce treściowe
1. **Napuszanie znaczenia** — „wyznaczając przełomowy moment…" → konkretne fakty
2. **Podkreślanie rozpoznawalności** — wyliczanie źródeł bez kontekstu
3. **Powierzchowne analizy z imiesłowami** — „podkreślając… odzwierciedlając…"
4. **Język promocyjny** — „tętniący życiem… malowniczy… urokliwy…"
5. **Niejasne przypisania** — „Eksperci uważają…"
6. **Szablonowe wyzwania** — „Pomimo wyzwań… nadal się rozwija"

### Wzorce językowe
7. **Słownictwo AI** — „Dodatkowo… kluczowy… stanowi świadectwo… krajobraz…"
8. **Unikanie łącznika „jest"** — „stanowi" zamiast „jest", „służy jako" zamiast „to"
9. **Negatywne paralelizmy** — „To nie tylko X, to także Y"
10. **Reguła trzech** — wymuszanie grup po trzy elementy
11. **Cykliczna synonimizacja** — nadmierne zastępowanie synonimami
12. **Fałszywe zakresy** — „od X do Y" na bezsensownej skali

### Wzorce stylistyczne
13. **Nadużycie myślników (—)**
14. **Nadużycie pogrubienia**
15. **Listy z nagłówkami inline**
16. **Wielkie Litery W Nagłówkach**
17. **Dekoracja emoji**
18. **Typograficzne cudzysłowy**

### Wzorce komunikacyjne
19. **Artefakty chatbota** — „Mam nadzieję, że to pomoże!"
20. **Zastrzeżenia o limicie wiedzy** — „Na podstawie dostępnych informacji…"
21. **Lizusostwo** — „Świetne pytanie!"

### Wypełniacze i asekuranctwo
22. **Frazy-wypełniacze** — „W celu osiągnięcia", „Ze względu na fakt, że"
23. **Nadmierne asekurowanie się** — „mogłoby potencjalnie ewentualnie"
24. **Generyczne zakończenia** — „Przyszłość rysuje się w jasnych barwach"

## Pełny przykład

**Przed (brzmi jak AI):**
> Nowa aktualizacja oprogramowania stanowi świadectwo zaangażowania firmy w innowacje. Ponadto zapewnia płynne, intuicyjne i wydajne doświadczenie użytkownika — gwarantując, że użytkownicy mogą efektywnie realizować swoje cele.

**Po (zhumanizowane):**
> Aktualizacja dodaje przetwarzanie wsadowe, skróty klawiaturowe i tryb offline. Wstępne opinie beta testerów są pozytywne — większość zgłasza szybsze wykonywanie zadań.

## Źródła

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [WikiProject AI Cleanup](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup)

## Licencja

MIT
