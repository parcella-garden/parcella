# Organizacja terminu prac {#organising-a-work-session}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Większość stowarzyszeń oczekuje, że każda działka (albo każdy członek)
odpracuje w roku określoną liczbę [obowiązkowych
godzin](../glossary.md#mandatory-hours) prac społecznych -- przycinanie
żywopłotu, naprawa ścieżek, wiosenne sprzątanie. Ta instrukcja
prowadzi jeden [termin prac](../glossary.md#work-session) od
planowania aż po rozliczenie na koniec roku: utwórz go, pozwól członkom
zapisywać się na stronie stowarzyszenia, zapisz, kto naprawdę przyszedł,
i zobacz, kto jest jeszcze winien godziny.

!!! info "Kto może to zrobić"
    Tworzenie terminów i zapisywanie obecności wymaga uprawnienia do
    **zapisu** w **Prace społeczne**; usunięcie uczestnika lub
    przekazania wymaga uprawnienia do **usuwania**. Moduł
    (**Zarządzanie pracami społecznymi**) jest domyślnie włączony.
    Publikacja na stronie internetowej wymaga administratora do
    jednorazowej konfiguracji w kroku 3.

## 1. Ustal zasady na rok (raz w roku) {#1-set-the-years-rules-once-a-year}

1. Otwórz **Prace społeczne → Wpisy i przegląd**. Jeśli rok nie ma
   jeszcze zasad, strona mówi *„Brak konfiguracji prac społecznych dla
   ….”* -- kliknij **Utwórz teraz →** (albo **Konfiguracja godzin** na
   dole).
2. W **Utwórz / zaktualizuj rok** wpisz:
    - **Rok**;
    - **Łączna liczba wymaganych godzin** -- godziny należne w roku;
    - **Stawka godzinowa** -- ile kosztuje godzina nieodpracowana;
    - **Tryb rozliczenia** -- **Na dzierżawę / działkę** (wszyscy
      dzierżawcy działki odpracowują godziny razem) albo **Na członka**
      (każdy członek osobno);
    - opcjonalnie **Notatka**, np. uchwała walnego zebrania.
3. Kliknij **Zapisz**.

Na tej samej stronie karta **E-mail z potwierdzeniem zgłoszenia**
ustala wiadomość, którą członkowie dostają po zapisaniu się na stronie
internetowej (krok 3).

**Zwolnienia.** Członkowie zarządu, osoby ze względów zdrowotnych lub
powyżej pewnego wieku są często zwolnieni. Ustawisz to w **Wpisy i
przegląd → Role klubowe**: utwórz rolę z **Zwolniony z prac
społecznych** i **Powód zwolnienia**, a następnie przypisz do niej
członków na dany rok. Jeśli jeden dzierżawca działki jest zwolniony,
zwolniona jest cała działka; zwolnienie obowiązuje przez cały rok
kalendarzowy.

## 2. Utwórz termin {#2-create-the-session}

1. Otwórz **Prace społeczne → Wpisy i przegląd** i kliknij **Nowy
   wpis**.
2. Wypełnij:
    - **Nazwa**, np. „Wiosenne sprzątanie”;
    - **Rodzaj**: **Standardowy (planowany)** dla terminów, które
      ogłaszasz, albo **Specjalny (spontaniczny)** dla nieplanowanych --
      terminy specjalne nigdy nie pojawiają się na stronie internetowej;
    - **Data**, **Od** i **Do**;
    - **Maks. liczba uczestników** -- zostaw puste, jeśli bez limitu;
    - **Termin zamknięcia zapisów (dni wcześniej)** -- zapisy na stronie
      zamykają się tyle dni przed terminem (1 = dzień wcześniej); puste
      oznacza, że zamykają się po upływie terminu;
    - **Godziny na uczestnika** -- zaliczane każdemu obecnemu, później
      do zmiany dla każdej osoby;
    - **Opis** -- zadania, narzędzia, co zabrać.
3. Kliknij **Utwórz wpis**.

Termin pojawia się na liście **Wpisy prac …** swojego roku.

## 3. Opublikuj zapisy na stronie stowarzyszenia (jednorazowa konfiguracja) {#3-publish-the-sign-up-on-the-club-website-one-time-setup}

Członkowie zapisują się na stronie stowarzyszenia, podając **numer
działki** i opcjonalnie swoje imię i nazwisko -- bez logowania do
Parcelli. Strona nigdy nie pokazuje, którzy członkowie są na której
działce.

Administrator konfiguruje to raz:

1. **Administracja → Ustawienia → Moduły funkcjonalne**: zaznacz
   **Publiczne API zgłoszeń** i kliknij **Zapisz ustawienia**. Domyślnie
   jest wyłączone, bo otwiera publiczny formularz.
2. **Administracja → Integracje → Publiczne API zgłoszeń**: zanotuj
   **Token API** (dla łącznika po stronie serwera) i dodaj swoją stronę
   w **Dozwolone adresy stron** (np. `https://example.org`), a potem
   kliknij **Zapisz adresy**. Opcjonalnie zaznacz **Wymagaj ALTCHA**
   przeciw spamowi.
3. Na stronie internetowej dodaj formularz zapisów -- za pomocą wtyczki
   Parcella Connector dla WordPressa albo zwykłego formularza HTML dla
   każdej innej strony. Osoba zajmująca się Twoją stroną znajdzie
   szczegóły w dokumentacji dla programistów.
   <!-- TODO(verify): link to the gardeners/website-form instructions once that page exists. -->

Od tej chwili każdy nowy termin **Standardowy** sam pojawia się na
stronie, o ile jego data nie minęła, termin zapisów nie upłynął i nie
jest pełny.

**Co się dzieje przy zapisie.** Parcella sprawdza aktualnych
dzierżawców działki. Jeśli wpisane imię i nazwisko pasuje dokładnie do
jednego z nich, zapisywany jest tylko ten członek. Jeśli nie podano
imienia albo nie pasuje jednoznacznie, zapisywani są **wszyscy**
aktualni dzierżawcy działki, z notatką z prośbą do zarządu o
sprawdzenie -- usuń tych, którzy w rzeczywistości się nie zapisali.
Każdy nowo zapisany członek dostaje e-mail z potwierdzeniem na adres
zapisany w Parcelli (nie ten wpisany w formularzu).

Więcej: [Integracje](../administration/integrations.md) i [Dla
działkowców](../gardeners/index.md).

## 4. Pilnuj zapisów {#4-keep-an-eye-on-sign-ups}

- Nowe zapisy pokazują licznik obok **Prace społeczne** w menu bocznym
  i na pulpicie.
- Otwórz termin (kliknij go na liście w **Wpisy i przegląd**). Nowi
  uczestnicy mają oznaczenie **Nowy**. Gdy już ich przejrzysz, kliknij
  **Oznacz jako przejrzane**.
- Sprawdź kolumnę **Notatka**: zapisy ze strony zawierają tam uwagi i
  dane kontaktowe odwiedzającego oraz ostrzeżenie, jeśli zapisano całą
  działkę.
- Aby dodać kogoś ręcznie (zapis telefoniczny), użyj **Wybierz członka…**
  na dole tabeli uczestników, wybierz **Zgłoszony** i kliknij **Dodaj**.

**Zadania (opcjonalnie).** Jeśli prowadzisz listę prac w **Prace
społeczne → Zadania**, zaplanuj tam część z nich na ten termin. Na
stronie terminu możesz wtedy przydzielić każde uczestnikowi
(**Przypisano do**) i zobaczyć jego **Nakład pracy** (**Lekkie**,
**Umiarkowane**, **Wymagające**). **Zarządzaj zadaniami** prowadzi do
pełnej listy.

## 5. W dniu prac: wydrukuj listę uczestników {#5-on-the-day-print-the-attendee-sheet}

1. Otwórz termin i kliknij **Lista uczestników**.
2. Wydrukuj PDF. Wymienia on każdego zapisanego uczestnika z działką,
   imieniem i nazwiskiem, przewidywanymi godzinami, przydzielonym
   zadaniem i miejscem na podpis.

Popraw godziny na papierze w razie potrzeby; wpiszesz je później. Lista
niczego nie zmienia w Parcelli.

## 6. Po pracach: zapisz obecność {#6-afterwards-record-attendance}

1. Otwórz termin.
2. Dla każdego uczestnika wybierz **Obecny** albo **Nieobecny** z listy
   **Status**. Zapisuje się od razu.
3. Jeśli ktoś pracował dłużej lub krócej niż **Godziny na uczestnika**,
   wpisz rzeczywiste godziny w jego pole **Godziny** i kliknij przycisk
   ✓.
4. Osoby, które przyszły bez zapisu: **Wybierz członka…**, status
   **Obecny**, ich godziny, **Dodaj**.
5. Użyj pola wyszukiwania nad tabelą, aby znaleźć kogoś po nazwisku lub
   numerze działki.

Do godzin liczą się tylko udziały ze statusem **Obecny**.

## 7. Patronaty i przekazania godzin {#7-sponsorships-and-hours-transfers}

**[Patronaty](../glossary.md#sponsorship)** to obszary, którymi członek
opiekuje się przez cały rok (żywopłot, plac zabaw) zamiast przychodzić
na terminy prac albo dodatkowo.

1. Otwórz **Prace społeczne → Patronaty**.
2. W **Utwórz patronat / dodaj członka** wpisz **Obszar**, **Członek**
   (albo zostaw **– jeszcze nie przydzielono –**, aby najpierw ogłosić
   obszar), **Opis**, **Godziny zaliczane/rok** oraz **Obowiązuje od** /
   **Obowiązuje do**.
3. Kliknij **Zapisz**.

Patronat zalicza godziny dopiero wtedy, gdy ma datę **Obowiązuje od** i
członka. Kilku członków może dzielić obszar -- dodaj wiersz dla każdego
członka z tą samą nazwą obszaru; każdy dostaje pełne zaliczenie.

**[Przekazania godzin](../glossary.md#hours-transfer)**: członek, który
przepracował więcej, niż było wymagane, może oddać godziny komuś
innemu.

1. Otwórz **Prace społeczne → Przekazywanie godzin**.
2. W **Przekaż godziny** wybierz **Od (przekazuje)**, **Do
   (otrzymuje)**, **Godziny** i opcjonalnie **Notatka**.
3. Kliknij **Przekaż godziny**.

Przekazać można tylko nadwyżkę przekazującego za dany rok. Członkowie
bez działki i członkowie zwolnieni mogą przekazać wszystkie swoje
godziny.

## 8. Rozliczenie na koniec roku {#8-the-year-end-evaluation}

1. Otwórz **Prace społeczne → Rozliczenie roczne** i wybierz rok.
2. Każdy wiersz to działka (albo członek, zależnie od **Tryb
   rozliczenia**) z kolumnami **Wymagane**, **Wpisy prac**, **Patronat**,
   **Przekazania**, **Razem**, **Pozostało** i **Zaległość** oraz
   **Status**: **Zrealizowane**, **Otwarte** albo **Zwolniony**.
3. Kliknij strzałkę na początku wiersza (**Pokaż wpisy prac**), aby
   zobaczyć, z których terminów pochodzą godziny.
4. **Eksport CSV** pobiera rozliczenie.

Dzierżawcy, którzy odeszli w ciągu roku, nadal są winni godziny za ten
rok; ich wiersz ma oznaczenie „dzierżawa zakończona …”.

Aby rozliczyć brakujące godziny, dodaj do rocznej serii faktur pozycję
**Niedobór godzin pracy (z modułu)** -- zob. [Roczne
fakturowanie](annual-invoicing.md).

## Powiązane {#related}

- [Prace społeczne](../modules/work-hours.md)
- [Kalendarz](../modules/calendar.md)
- [Integracje](../administration/integrations.md)
- [Roczne fakturowanie](annual-invoicing.md)
- Słownik: [obowiązkowe godziny](../glossary.md#mandatory-hours),
  [zwolnienie](../glossary.md#exemption),
  [patronat](../glossary.md#sponsorship),
  [przekazanie godzin](../glossary.md#hours-transfer)
