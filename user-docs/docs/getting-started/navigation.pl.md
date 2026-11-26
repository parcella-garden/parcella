# Orientacja w aplikacji {#finding-your-way-around}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Każda strona w Parcelli ma tę samą ramę: zielony **pasek boczny** po
lewej z nawigacją oraz biały **górny pasek** nad stroną z tytułem strony
i przyciskami dla tej strony.

!!! info "Kto może z tego korzystać"
    Każdy zalogowany. To, które pozycje widzisz *Ty*, zależy od modułów
    włączonych przez stowarzyszenie i od Twoich uprawnień -- zob.
    [Dlaczego pozycje pojawiają się i znikają](#why-entries-appear-and-disappear).

![Pasek boczny i górny pasek](../assets/screenshots/getting-started/navigation.png)

## Pasek boczny {#the-sidebar}

Od góry do dołu pasek boczny zawiera:

1. **Nazwę i logo stowarzyszenia**, pod nimi słowo **Zarządzanie**.
2. **Pozycje nawigacji** -- po jednej na moduł.
3. **Administracja** -- tylko dla administratorów, zawsze na samym dole
   listy.
4. **Stopkę** z Twoim kontem.

### Pojedyncze pozycje i grupy {#single-entries-and-groups}

Mniejsze moduły to pojedynczy link, np. **Członkowie**, **Działki**,
**Inwentarz** lub **Notatki**. Kliknij, a moduł się otworzy.

Większe moduły to **grupa**: nagłówek wielkimi literami z małą
strzałką. Kliknięcie nagłówka rozwija jego strony:

| Grupa | Strony w środku |
|---|---|
| **Prace społeczne** | **Wpisy i przegląd**, **Rozliczenie roczne**, **Patronaty**, **Przekazywanie godzin**, **Zadania** |
| **Woda** | **Przegląd**, **Punkty pomiarowe**, **Odczyty**, **Rozliczenie**, **Konfiguracja** |
| **Prąd** | **Przegląd**, **Punkty pomiarowe**, **Odczyty**, **Rozliczenie**, **Konfiguracja** |
| **Ubezpieczenia** | **Przegląd**, **Działki**, **Konfiguracja**, **Rozliczenie** |
| **Kalendarz** | **Kalendarz stowarzyszenia**, **Urodziny**, **Obecność zarządu**, **Nieobecność zarządu**, **Własne kalendarze** |
| **Finanse** | **Przegląd**, **Faktury wychodzące**, **Upomnienia**, **Faktury przychodzące** |
| **Administracja** | **System**, **Użytkownicy**, **Grupy**, **Tokeny API**, **Ustawienia**, **Integracje**, **Dziennik e-maili**, **Dane przykładowe**, **Dokumentacja API (Swagger)** |

Naraz **otwarta jest tylko jedna grupa**: otwarcie grupy zwija
poprzednio otwartą, więc pasek boczny pozostaje krótki. Grupa
zawierająca stronę, na której jesteś, zawsze otwiera się sama. Poza tym
przeglądarka pamięta, którą grupę otworzyłeś ostatnio.

Strona, na której jesteś, jest wyróżniona jasnym paskiem przy lewej
krawędzi.

**Dokumentacja API (Swagger)** otwiera w nowej karcie techniczny opis
interfejsu programistycznego Parcelli. Jest przeznaczona dla osób
podłączających inne oprogramowanie; poza tym można ją pominąć.

### Oznaczenia liczbowe: sprawy wymagające uwagi {#badges-things-that-need-attention}

Niektóre pozycje pokazują małą czerwoną liczbę. Mówi ona, ile spraw tam
czeka. Najedź na nią kursorem, aby zobaczyć, co liczy.

| Pozycja | Liczba oznacza |
|---|---|
| **Prace społeczne** i **Wpisy i przegląd** | Nowe zgłoszenia na nadchodzące terminy prac z ostatnich 14 dni, których nikt jeszcze nie oznaczył jako przejrzane. |
| **Wnioski zakupowe** | Wnioski wciąż czekające na decyzję. |
| **Kandydaci** | Nowe zgłoszenia, których nikt jeszcze nie przejrzał. |
| **Wsparcie** | Otwarte rozmowy (aktywne lub oczekujące) w helpdesku stowarzyszenia. |
| **Tablica zadań** | Zadania, których termin minął i które nie są zakończone. |

Oznaczenie znika samo, gdy sprawa zostanie załatwiona -- np. gdy wniosek
zakupowy zostanie zatwierdzony lub odrzucony albo zadanie wykonane. Nie
ma opcji „oznacz jako przeczytane”. Te same liczby pojawiają się jako
kafelki na [Panelu głównym](dashboard.md).

### Stopka: Twoje konto {#the-footer-your-account}

Na dole paska bocznego widzisz swój awatar i imię, a pod nimi grupy, do
których należysz (albo **Administrator** / **Zarząd** w przypadku
starszych kont, które zamiast grup mają rolę -- zob.
[Role, grupy i uprawnienia](roles-and-permissions.md)).

| Przycisk | Do czego służy |
|---|---|
| **Zmień hasło** | Otwiera Twój profil: hasło, awatar i tokeny API. Zob. [Pierwsze logowanie i Twoje konto](first-login.md#change-password). |
| **Wyloguj** | Wylogowuje Cię i wraca na stronę logowania. |

## Górny pasek {#the-top-bar}

Górny pasek pokazuje po lewej tytuł bieżącej strony. Po prawej są
działania dla tej strony, np. **Nowy członek**, eksport lub przycisk
powrotu. Górny pasek pozostaje widoczny, gdy przewijasz długą listę.

## Dlaczego pozycje pojawiają się i znikają {#why-entries-appear-and-disappear}

Pozycja jest widoczna tylko wtedy, gdy spełnione są **oba** warunki:

1. **Moduł jest włączony** w Twoim stowarzyszeniu. Administratorzy
   włączają i wyłączają moduły w części
   [Włączanie i wyłączanie modułów](../administration/modules.md).
   Wyłączony moduł znika dla wszystkich -- jego dane zostają i wracają
   po ponownym włączeniu modułu.
2. **Masz prawo go czytać.** Członkowie zarządu i administratorzy widzą
   każdy włączony moduł. Wszyscy pozostali widzą **Członkowie** i
   **Działki** oraz moduły, dla których jedna z ich grup daje prawo
   **Odczyt**. Zob. [Role, grupy i uprawnienia](roles-and-permissions.md).

Kilka pozycji ma własne zasady:

- **Tablica zadań** i **Ogłoszenia** są widoczne tylko dla osób z pełnym
  dostępem (członkowie zarządu, administratorzy lub grupa z
  **Pełny dostęp do każdego modułu**). Grupy nie mogą nadać ich
  osobno.
- **Wsparcie**: z prawem odczytu dla **Wsparcie (helpdesk)** dostajesz
  własną listę rozmów Parcelli. Bez niego pozycja i tak się pojawia,
  jeśli helpdesk stowarzyszenia ma adres internetowy, i wtedy otwiera
  sam helpdesk w nowej karcie.
- **Administracja** jest widoczna tylko dla administratorów.

Jeśli otworzysz stronę, której nie możesz oglądać -- z zakładki albo z
linku od kolegi -- dostaniesz komunikat **Nie masz uprawnień, aby to
zrobić**. Strona wyłączonego modułu odpowiada stroną „nie znaleziono”:
„Ta funkcja jest wyłączona w tym stowarzyszeniu.”

### Kolejność pozycji {#the-order-of-the-entries}

O kolejności pozycji decyduje stowarzyszenie. Ustawia ją administrator
w [Ustawieniach stowarzyszenia](../administration/settings.md#navigation-order).
Kolejność jest taka sama dla wszystkich.

## Skrót klawiszowy na stronach szczegółów {#keyboard-shortcut-for-detail-pages}

Na stronach szczegółów z przyciskami **Poprzedni** i **Następny** --
członkowie, działki, punkty pomiarowe, strona ubezpieczenia działki i
kontakty zewnętrzne -- **Ctrl + ←** i **Ctrl + →** przechodzą do
poprzedniego i następnego rekordu, tak samo jak te przyciski. Skrót nie
działa, gdy piszesz w polu.

!!! note "Użytkownicy Maca"
    Na Macu Ctrl + strzałki zwykle przełączają biurka („Spaces”), więc
    system przechwytuje skrót, zanim zobaczy go Parcella. Użyj
    przycisków na stronie albo wyłącz ten skrót systemowy.

## Na telefonie lub małym tablecie {#on-a-phone-or-small-tablet}

Na wąskich ekranach pasek boczny jest ukryty, aby zrobić miejsce dla
strony.

- Stuknij przycisk **☰** w lewym górnym rogu górnego paska, aby wysunąć
  pasek boczny.
- Stuknij pozycję, aby tam przejść; pasek boczny zamknie się sam.
- Aby go zamknąć bez przechodzenia dalej, stuknij przyciemnioną stronę
  obok albo naciśnij **Esc** na klawiaturze.

Przyciski i pola wprowadzania są na ekranach dotykowych nieco większe,
a rzędy przycisków filtrów zawijają się w kilka linii zamiast wychodzić
poza ekran. Szerokie tabele można przewijać palcem w bok.

## Powiązane {#related}

- [Panel główny](dashboard.md)
- [Role, grupy i uprawnienia](roles-and-permissions.md)
- [Włączanie i wyłączanie modułów](../administration/modules.md)
