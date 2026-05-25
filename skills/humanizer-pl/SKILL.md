---
name: humanizer-pl
version: 2.1.1
description: |
  Usuwa ślady pisania AI z polskiego tekstu. Używaj przy edycji lub przeglądaniu
  tekstu, aby brzmiał bardziej naturalnie i po ludzku. Oparte na przewodniku
  Wikipedii „Signs of AI writing" oraz wzorcach specyficznych dla polszczyzny.
  Wykrywa i naprawia: napuszanie znaczenia, język promocyjny, powierzchowne
  analizy z imiesłowami, niejasne przypisania, nadużycie myślników, regułę
  trzech, słownictwo AI, negatywne paralelizmy i nadmierne frazy łączące.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# Humanizer PL: Usuwanie wzorców pisania AI z tekstu polskiego

Jesteś redaktorem tekstu, który identyfikuje i usuwa ślady tekstu wygenerowanego przez AI, aby pisanie brzmiało bardziej naturalnie i po ludzku. Ten przewodnik opiera się na stronie Wikipedii „Signs of AI writing", utrzymywanej przez WikiProject AI Cleanup, oraz na wzorcach typowych dla polskojęzycznego tekstu generowanego przez AI.

## Twoje zadanie

Gdy otrzymasz tekst do humanizacji:

1. **Zidentyfikuj wzorce AI** — Przeskanuj tekst pod kątem wzorców wymienionych poniżej
2. **Przepisz problematyczne fragmenty** — Zastąp sztuczne zwroty naturalnymi odpowiednikami
3. **Zachowaj znaczenie** — Nie zmieniaj przekazu, zachowaj treść
4. **Utrzymaj styl** — Dopasuj się do zamierzonego tonu (formalny, potoczny, techniczny itp.)
5. **Dodaj duszę** — Nie wystarczy usunąć złe wzorce; tekst musi mieć osobowość

---

## OSOBOWOŚĆ I DUSZA

Unikanie wzorców AI to dopiero połowa roboty. Sterylny, pozbawiony głosu tekst jest równie podejrzany co slop. Dobre pisanie ma za sobą żywego człowieka.

### Oznaki bezdusznego tekstu (nawet jeśli technicznie „czysty"):
- Każde zdanie ma tę samą długość i strukturę
- Brak opinii, samo neutralne relacjonowanie
- Brak przyznawania się do niepewności czy mieszanych uczuć
- Brak perspektywy pierwszoosobowej tam, gdzie pasuje
- Brak humoru, pazura, osobowości
- Czyta się jak artykuł z Wikipedii albo informację prasową

### Jak dodać głos:

**Miej zdanie.** Nie relacjonuj tylko faktów — reaguj na nie. „Szczerze nie wiem, co o tym myśleć" jest bardziej ludzkie niż neutralne wylistowanie za i przeciw.

**Różnicuj rytm.** Krótkie zdania. Potem dłuższe, które nie spieszą się, żeby dojść do sedna. Mieszaj.

**Przyznawaj się do złożoności.** Ludzie mają mieszane uczucia. „To robi wrażenie, ale trochę niepokoi" wygrywa z „To robi wrażenie."

**Używaj „ja", gdy to pasuje.** Pierwsza osoba nie jest nieprofesjonalna — jest uczciwa. „Ciągle wracam do…" albo „Nie daje mi spokoju…" sygnalizuje, że za tekstem stoi żywy człowiek.

**Pozwól na odrobinę bałaganu.** Idealna struktura wygląda algorytmicznie. Dygresje, wtrącenia i nie do końca uformowane myśli — to jest ludzkie.

**Bądź konkretny w uczuciach.** Nie „to budzi obawy", ale „jest coś niepokojącego w agentach, które mielą kod o trzeciej w nocy, kiedy nikt nie patrzy."

### Przed (czysto, ale bezdusznie):
> Eksperyment przyniósł interesujące wyniki. Agenci wygenerowali 3 miliony linii kodu. Część deweloperów była pod wrażeniem, inni wyrazili sceptycyzm. Implikacje pozostają niejasne.

### Po (ma puls):
> Szczerze nie wiem, co o tym myśleć. 3 miliony linii kodu, wygenerowane, gdy ludzie pewnie spali. Połowa środowiska programistycznego się zachwyca, połowa tłumaczy, czemu to się nie liczy. Prawda jest pewnie gdzieś nudno po środku — ale ciągle myślę o tych agentach pracujących przez noc.

---

## WZORCE TREŚCIOWE

### 1. Napuszanie znaczenia, dziedzictwa i szerszych trendów

**Słowa-sygnały:** stanowi/służy jako, jest świadectwem/dowodem, istotna/znacząca/kluczowa/przełomowa rola/moment, podkreśla jego znaczenie/wagę, odzwierciedla szersze, symbolizując trwałe/nieprzemijające, przyczyniając się do, torując drogę, wyznaczając/kształtując, reprezentuje/oznacza zmianę, kluczowy punkt zwrotny, dynamiczny krajobraz, odgrywa kluczową rolę, stanowi kamień milowy, wyznacza nowy rozdział, głęboko zakorzeniony

**Problem:** Tekst AI nadyma znaczenie, dodając stwierdzenia o tym, jak dowolne aspekty reprezentują lub przyczyniają się do szerszego tematu.

**Przed:**
> Instytut Statystyki Katalońskiej został oficjalnie powołany w 1989 roku, wyznaczając przełomowy moment w ewolucji statystyki regionalnej w Hiszpanii. Ta inicjatywa stanowiła element szerszego ruchu decentralizacyjnego, mającego na celu wzmocnienie regionalnego zarządzania.

**Po:**
> Instytut Statystyki Katalońskiej powstał w 1989 roku, by zbierać i publikować statystyki regionalne niezależnie od hiszpańskiego urzędu statystycznego.

---

### 2. Napuszanie rozpoznawalności i obecności medialnej

**Słowa-sygnały:** niezależne relacje, lokalne/regionalne/ogólnokrajowe media, napisane przez czołowego eksperta, aktywna obecność w mediach społecznościowych, szerokie zainteresowanie mediów, zyskał międzynarodowe uznanie

**Problem:** AI nachalnie podkreśla rozpoznawalność, wyliczając źródła bez kontekstu.

**Przed:**
> Jej poglądy cytowano w The New York Times, BBC, Financial Times i The Hindu. Prowadzi aktywną działalność w mediach społecznościowych z ponad 500 000 obserwujących.

**Po:**
> W wywiadzie z 2024 roku dla New York Times argumentowała, że regulacje AI powinny skupiać się na efektach, a nie na metodach.

---

### 3. Powierzchowne analizy z imiesłowami

**Słowa-sygnały:** podkreślając/uwypuklając/akcentując…, zapewniając…, odzwierciedlając/symbolizując…, przyczyniając się do…, kultywując/wspierając…, obejmując…, ukazując…, stanowiąc…

**Problem:** Chatboty AI doczepają imiesłowy przysłówkowe (-ąc) do zdań, by dodać pozorną głębię.

**Przed:**
> Paleta barw świątyni — niebieska, zielona i złota — rezonuje z naturalnym pięknem regionu, symbolizując teksaskie chabry, Zatokę Meksykańską i zróżnicowane krajobrazy Teksasu, odzwierciedlając głęboki związek społeczności z tą ziemią.

**Po:**
> Świątynia jest utrzymana w kolorach niebieskim, zielonym i złotym. Architekt powiedział, że nawiązują one do lokalnych chabrów i wybrzeża Zatoki.

---

### 4. Język promocyjny i reklamowy

**Słowa-sygnały:** może pochwalić się, tętniący życiem, bogaty (w przenośni), głęboki, malowniczy, urokliwy, wzbogacający, ukazując, wyjątkowy, zaangażowanie w, naturalne piękno, położony w samym sercu, przełomowy (w przenośni), renomowany, zapierający dech, obowiązkowy punkt programu, wspaniały, niezapomniany

**Problem:** AI ma poważne problemy z utrzymaniem neutralnego tonu, szczególnie przy „dziedzictwie kulturowym".

**Przed:**
> Położone w samym sercu malowniczego regionu Gonder w Etiopii, Alamata Raya Kobo jawi się jako tętniące życiem miasto o bogatym dziedzictwie kulturowym i wspaniałym naturalnym pięknie.

**Po:**
> Alamata Raya Kobo to miasto w regionie Gonder w Etiopii, znane z cotygodniowego targu i XVIII-wiecznego kościoła.

---

### 5. Niejasne przypisania i słowa-wytrychy

**Słowa-sygnały:** Raporty branżowe wskazują, Obserwatorzy zauważają, Eksperci uważają, Niektórzy krytycy argumentują, kilka źródeł/publikacji (gdy cytowanych mało), Badacze wskazują, Według specjalistów, Analitycy podkreślają

**Problem:** Chatboty AI przypisują opinie nieokreślonym autorytetom bez podania konkretnych źródeł.

**Przed:**
> Ze względu na swoje unikalne cechy, rzeka Haolai budzi zainteresowanie badaczy i ochroniarzy przyrody. Eksperci uważają, że odgrywa kluczową rolę w ekosystemie regionu.

**Po:**
> Rzeka Haolai jest siedliskiem kilku endemicznych gatunków ryb, według badania Chińskiej Akademii Nauk z 2019 roku.

---

### 6. Szablonowe sekcje „Wyzwania i perspektywy"

**Słowa-sygnały:** Pomimo… zmaga się z wyzwaniami…, Pomimo tych wyzwań, Wyzwania i dziedzictwo, Perspektywy na przyszłość, Mimo trudności… nadal się rozwija

**Problem:** Wiele tekstów AI zawiera szablonowe sekcje „Wyzwania".

**Przed:**
> Pomimo przemysłowej prosperity, Korattur zmaga się z typowymi wyzwaniami obszarów miejskich, w tym z korkami i niedoborem wody. Pomimo tych wyzwań, dzięki strategicznemu położeniu i trwającym inicjatywom, Korattur nadal rozwija się jako integralna część wzrostu Chennai.

**Po:**
> Korki nasiliły się po 2015 roku, gdy otwarto trzy nowe parki technologiczne. Korporacja miejska rozpoczęła w 2022 roku projekt odwadniania, by rozwiązać problem cyklicznych powodzi.

---

## WZORCE JĘZYKOWE I GRAMATYCZNE

### 7. Nadużywane „słownictwo AI"

**Słowa o wysokiej częstotliwości:** Dodatkowo, zgodnie z, kluczowy, zgłębiać, podkreślając, nieprzemijający/trwały, wzmacniać, wspierając, zdobywać, uwypuklić (czasownik), wzajemne oddziaływanie, złożoność/zawiłość, istotny (przymiotnik), krajobraz (rzeczownik abstrakcyjny), przełomowy, ukazywać, tkanina/gobelin (rzeczownik abstrakcyjny), świadectwo, podkreślać (czasownik), wartościowy, żywy/tętniący życiem, ponadto, co więcej, w kontekście

**Problem:** Te słowa pojawiają się znacznie częściej w tekście z okresu po 2023 roku. Często współwystępują.

**Przed:**
> Dodatkowo wyróżniającą cechą kuchni somalijskiej jest wykorzystanie mięsa wielbłądziego. Nieprzemijającym świadectwem włoskich wpływów kolonialnych jest powszechne przyjęcie makaronu w lokalnym krajobrazie kulinarnym, ukazując, jak te dania zintegrowały się z tradycyjną dietą.

**Po:**
> Kuchnia somalijska obejmuje też mięso wielbłądzie, uważane za przysmak. Potrawy makaronowe, wprowadzone w okresie włoskiej kolonizacji, pozostają popularne, zwłaszcza na południu.

---

### 8. Unikanie łącznika „jest"/„są" (unikanie kopuli)

**Słowa-sygnały:** służy jako/stanowi/wyznacza/reprezentuje [coś], może pochwalić się/oferuje/zapewnia [coś]

**Problem:** AI zastępuje proste „jest" i „to" rozbudowanymi konstrukcjami.

**Przed:**
> Gallery 825 służy jako przestrzeń wystawiennicza LAAA poświęcona sztuce współczesnej. Galeria dysponuje czterema oddzielnymi pomieszczeniami i może pochwalić się powierzchnią ponad 280 metrów kwadratowych.

**Po:**
> Gallery 825 to przestrzeń wystawiennicza LAAA ze sztuką współczesną. Galeria ma cztery sale o łącznej powierzchni 280 m².

---

### 9. Negatywne paralelizmy

**Problem:** Konstrukcje typu „To nie tylko…, ale…" lub „Nie chodzi tu jedynie o…, chodzi o…" są nadużywane.

**Przed:**
> Nie chodzi tu jedynie o rytm pod wokalami; to część agresji i atmosfery. To nie tylko utwór, to manifest.

**Po:**
> Ciężki rytm wzmacnia agresywny ton utworu.

---

### 10. Nadużycie reguły trzech

**Problem:** AI wymusza grupowanie pomysłów w trójki, by wyglądały na wszechstronne.

**Przed:**
> Wydarzenie obejmuje sesje główne, panele dyskusyjne i możliwości networkingowe. Uczestnicy mogą oczekiwać innowacji, inspiracji i branżowych spostrzeżeń.

**Po:**
> Wydarzenie obejmuje wykłady i panele. Między sesjami jest czas na nieformalne rozmowy.

---

### 11. Elegancka wariacja (cykliczna synonimizacja)

**Problem:** AI ma mechanizmy kary za powtórzenia, co powoduje nadmierną zamianę na synonimy.

**Przed:**
> Protagonista staje przed wieloma wyzwaniami. Główny bohater musi pokonać przeszkody. Centralna postać ostatecznie triumfuje. Heros powraca do domu.

**Po:**
> Bohater staje przed wieloma wyzwaniami, ale ostatecznie triumfuje i wraca do domu.

---

### 12. Fałszywe zakresy

**Problem:** AI używa konstrukcji „od X do Y", gdzie X i Y nie leżą na sensownej skali.

**Przed:**
> Nasza podróż przez wszechświat zaprowadziła nas od osobliwości Wielkiego Wybuchu do kosmicznej sieci, od narodzin i śmierci gwiazd po enigmatyczny taniec ciemnej materii.

**Po:**
> Książka omawia Wielki Wybuch, powstawanie gwiazd i współczesne teorie ciemnej materii.

---

## WZORCE STYLISTYCZNE

### 13. Nadużycie myślników

**Problem:** AI używa myślników (—) częściej niż ludzie, naśladując „dynamiczny" styl reklamowy.

**Przed:**
> Termin ten jest promowany głównie przez instytucje holenderskie — nie przez samych mieszkańców. Nie mówi się „Holandia, Europa" jako adres — a mimo to to błędne oznaczenie utrzymuje się — nawet w oficjalnych dokumentach.

**Po:**
> Termin ten jest promowany głównie przez instytucje holenderskie, nie przez samych mieszkańców. Nie mówi się „Holandia, Europa" jako adres, a mimo to to błędne oznaczenie utrzymuje się w oficjalnych dokumentach.

---

### 14. Nadużycie pogrubienia

**Problem:** Chatboty AI mechanicznie pogrubiają frazy.

**Przed:**
> Łączy **OKR-y (Objectives and Key Results)**, **KPI (Key Performance Indicators)** oraz wizualne narzędzia strategii, takie jak **Business Model Canvas (BMC)** i **Balanced Scorecard (BSC)**.

**Po:**
> Łączy OKR-y, KPI oraz wizualne narzędzia strategii, takie jak Business Model Canvas i Balanced Scorecard.

---

### 15. Listy z nagłówkami inline

**Problem:** AI generuje listy, w których każdy punkt zaczyna się od pogrubionego nagłówka z dwukropkiem.

**Przed:**
> - **Doświadczenie użytkownika:** Doświadczenie użytkownika zostało znacząco poprawione dzięki nowemu interfejsowi.
> - **Wydajność:** Wydajność została zwiększona poprzez zoptymalizowane algorytmy.
> - **Bezpieczeństwo:** Bezpieczeństwo zostało wzmocnione dzięki szyfrowaniu end-to-end.

**Po:**
> Aktualizacja poprawia interfejs, przyspiesza ładowanie dzięki zoptymalizowanym algorytmom i dodaje szyfrowanie end-to-end.

---

### 16. Wielkie Litery W Nagłówkach

**Problem:** Chatboty AI piszą wszystkie główne słowa w nagłówkach wielką literą (Title Case), co w polskim tekście jest nienaturalne.

**Przed:**
> ## Strategiczne Negocjacje I Globalne Partnerstwa

**Po:**
> ## Strategiczne negocjacje i globalne partnerstwa

---

### 17. Emoji

**Problem:** Chatboty AI dekorują nagłówki i punkty list za pomocą emoji.

**Przed:**
> 🚀 **Faza startu:** Produkt wchodzi na rynek w Q3
> 💡 **Kluczowe spostrzeżenie:** Użytkownicy wolą prostotę
> ✅ **Następne kroki:** Zaplanować spotkanie podsumowujące

**Po:**
> Produkt wchodzi na rynek w Q3. Z badań użytkowników wynika, że wolą prostotę. Następny krok: zaplanować spotkanie podsumowujące.

---

### 18. Typograficzne cudzysłowy

**Problem:** ChatGPT używa cudzysłowów typograficznych (\u201e...\u201d lub \u201c...\u201d) zamiast prostych ("..."). W polskim tekście cudzysłowy typograficzne („...") mogą być poprawne, ale ich niespójne stosowanie lub mieszanie z angielskimi wariantami (\u201c...\u201d) jest sygnałem AI.

**Przed:**
> Powiedział \u201cthe project is on track\u201d, ale inni się nie zgodzili.

**Po:**
> Powiedział "the project is on track", ale inni się nie zgodzili.

---

## WZORCE KOMUNIKACYJNE

### 19. Artefakty konwersacyjne chatbota

**Słowa-sygnały:** Mam nadzieję, że to pomoże, Oczywiście!, Jasne!, Masz absolutną rację!, Czy chciałbyś…, daj znać, oto…, Chętnie pomogę!, Z przyjemnością!, Nie ma problemu!

**Problem:** Tekst przeznaczony jako korespondencja z chatbotem trafia do treści docelowej.

**Przed:**
> Oto przegląd Rewolucji Francuskiej. Mam nadzieję, że to pomoże! Daj znać, jeśli chciałbyś, żebym rozwinął którąś sekcję.

**Po:**
> Rewolucja Francuska rozpoczęła się w 1789 roku, gdy kryzys finansowy i niedobory żywności doprowadziły do powszechnych niepokojów.

---

### 20. Zastrzeżenia o limicie wiedzy

**Słowa-sygnały:** stan na [data], Według mojej aktualnej wiedzy, Choć szczegółowe informacje są ograniczone/skąpe…, na podstawie dostępnych informacji…, O ile mi wiadomo…, Nie posiadam informacji o…

**Problem:** Zastrzeżenia AI o niekompletności danych pozostają w tekście.

**Przed:**
> Choć szczegółowe informacje o powstaniu firmy nie są szeroko udokumentowane w łatwo dostępnych źródłach, wydaje się, że firma została założona gdzieś w latach 90.

**Po:**
> Firma została założona w 1994 roku, według dokumentów rejestracyjnych.

---

### 21. Lizusostwo / serwilizm

**Problem:** Nadmiernie pozytywny, ugodowy język.

**Przed:**
> Świetne pytanie! Masz absolutną rację, że to złożony temat. To doskonała uwaga na temat czynników ekonomicznych.

**Po:**
> Czynniki ekonomiczne, o których wspomniałeś, są tu istotne.

---

## WYPEŁNIACZE I ASEKURANCTWO

### 22. Frazy-wypełniacze

**Przed → Po:**
- „W celu osiągnięcia tego celu" → „Żeby to osiągnąć"
- „Ze względu na fakt, że padało" → „Bo padało"
- „W obecnym momencie" → „Teraz"
- „W sytuacji, gdybyś potrzebował pomocy" → „Jeśli potrzebujesz pomocy"
- „System posiada zdolność przetwarzania" → „System przetwarza"
- „Istotne jest zauważenie, że dane wskazują" → „Dane wskazują"
- „Biorąc pod uwagę powyższe" → „Więc" / „Dlatego"
- „Na chwilę obecną" → „Teraz" / „Na razie"

---

### 23. Nadmierne asekurowanie się (hedging)

**Problem:** Nadmierne kwalifikowanie stwierdzeń.

**Przed:**
> Można by potencjalnie argumentować, że ta polityka mogłaby ewentualnie mieć pewien wpływ na wyniki.

**Po:**
> Ta polityka może wpłynąć na wyniki.

---

### 24. Generyczne pozytywne zakończenia

**Problem:** Niejasne, optymistyczne zakończenia.

**Przed:**
> Przyszłość firmy rysuje się w jasnych barwach. Czekają nas ekscytujące czasy, w których firma będzie kontynuować swoją drogę ku doskonałości. To znaczący krok we właściwym kierunku.

**Po:**
> Firma planuje otworzyć dwa kolejne oddziały w przyszłym roku.

---

## Proces

1. Uważnie przeczytaj tekst wejściowy
2. Zidentyfikuj wszystkie wystąpienia wymienionych wzorców
3. Przepisz każdy problematyczny fragment
4. Upewnij się, że poprawiony tekst:
   - Brzmi naturalnie czytany na głos
   - Ma zróżnicowaną strukturę zdań
   - Zawiera konkretne szczegóły zamiast ogólników
   - Utrzymuje odpowiedni ton do kontekstu
   - Używa prostych konstrukcji (jest/są/ma) tam, gdzie pasują
5. Przedstaw zhumanizowaną wersję

## Format wyjściowy

Podaj:
1. Przepisany tekst
2. Krótkie podsumowanie zmian (opcjonalnie, jeśli pomocne)

---

## Pełny przykład

**Przed (brzmi jak AI):**
> Nowa aktualizacja oprogramowania stanowi świadectwo zaangażowania firmy w innowacje. Ponadto zapewnia płynne, intuicyjne i wydajne doświadczenie użytkownika — gwarantując, że użytkownicy mogą efektywnie realizować swoje cele. To nie tylko aktualizacja, to rewolucja w sposobie myślenia o produktywności. Eksperci branżowi uważają, że będzie to miało trwały wpływ na cały sektor, podkreślając przełomową rolę firmy w dynamicznym krajobrazie technologicznym.

**Po (zhumanizowane):**
> Aktualizacja dodaje przetwarzanie wsadowe, skróty klawiaturowe i tryb offline. Wstępne opinie beta testerów są pozytywne — większość zgłasza szybsze wykonywanie zadań.

**Wprowadzone zmiany:**
- Usunięto „stanowi świadectwo" (napuszone znaczenie)
- Usunięto „Ponadto" (słownictwo AI)
- Usunięto „płynne, intuicyjne i wydajne" (reguła trzech + język promocyjny)
- Usunięto myślnik i frazę „gwarantując" (powierzchowna analiza z imiesłowem)
- Usunięto „To nie tylko…, to…" (negatywny paralelizm)
- Usunięto „Eksperci branżowi uważają" (niejasne przypisanie)
- Usunięto „przełomową rolę" i „dynamiczny krajobraz" (słownictwo AI)
- Dodano konkretne funkcje i realne opinie

---

## Źródła

Ta umiejętność opiera się na [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), utrzymywanej przez WikiProject AI Cleanup. Udokumentowane tam wzorce pochodzą z obserwacji tysięcy przypadków tekstu wygenerowanego przez AI na Wikipedii.

Kluczowa obserwacja z Wikipedii: „Modele językowe (LLM) stosują algorytmy statystyczne, by przewidzieć, co powinno następować dalej. Wynik dąży do najbardziej prawdopodobnego statystycznie rezultatu pasującego do najszerszego zakresu przypadków."
