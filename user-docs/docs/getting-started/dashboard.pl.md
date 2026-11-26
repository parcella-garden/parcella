# Panel główny {#dashboard}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Panel główny to strona startowa, którą widzisz po zalogowaniu. Pokazuje
najważniejsze dane stowarzyszenia w jednym miejscu i wskazuje sprawy
wymagające uwagi. Kliknij **Panel główny** na górze paska bocznego, aby
do niego wrócić.

!!! info "Kto może z tego korzystać"
    Każdy zalogowany. Niektóre kafelki pojawiają się tylko wtedy, gdy ich
    moduł jest włączony, a kilka wymaga też prawa odczytu tego modułu
    (opisano niżej).

![Panel główny](../assets/screenshots/getting-started/dashboard.png)

Wszystkie liczby są obliczane na nowo przy każdym otwarciu strony.

## Kafelki {#the-tiles}

Kafelki na górze mają stałą kolejność. Pierwsze cztery są zawsze
widoczne; pozostałe pojawiają się w zależności od modułów
stowarzyszenia.

| Kafelek | Co liczy | Kiedy się pojawia | Przycisk |
|---|---|---|---|
| **Członkowie** | Duża liczba: obecni członkowie -- nieusunięci, z niezakończonym członkostwem i albo już rozpoczętym, albo bez daty **Członek od**. Pod spodem: **... aktywnych** -- ci z nich, którzy mają datę **Członek od**. Jeśli co najmniej jeden obecny członek ma zapisaną datę urodzenia: **Średni wiek ... lat**, liczony tylko z tych członków. | Zawsze | **Pokaż** otwiera listę członków przefiltrowaną do aktywnych. |
| **Działki aktywne** | Działki ze statusem *aktywna*. Pod spodem, na pomarańczowo: **... wolnych** -- aktywne działki bez obecnego ani przyszłego dzierżawcy (działka, której ostatnia dzierżawa się zakończyła, liczy się jako wolna; działka, której dzierżawca złożył wypowiedzenie lub której nowy dzierżawca zaczyna później, już nie); albo **wszystkie zajęte**, jeśli takich nie ma. | Zawsze | **Pokaż wszystkie** otwiera listę działek. |
| **Wypowiedziane** | Działki ze statusem *wypowiedziana*. | Zawsze | **Pokaż** otwiera listę działek przefiltrowaną do wypowiedzianych. |
| **Powierzchnia całkowita (m²)** | Suma powierzchni wszystkich działek, aktywnych i wypowiedzianych. Usunięte działki i tereny wspólne się nie liczą. To ta sama liczba co **Powierzchnia A (działki, m²)** w [ustawieniach stowarzyszenia](../administration/settings.md#areas-sqm). | Zawsze | -- |
| **Otwarte wnioski zakupowe** | Wnioski, które wciąż **oczekuje na zatwierdzenie**. | Moduł **Wnioski zakupowe** włączony i możesz czytać wnioski zakupowe | **Pokaż wszystkie** |
| **Nowe zgłoszenia** | Zgłoszenia ze statusem *nowe*, czyli **jeszcze nierozpatrzone**. | Moduł **Kandydaci** włączony i możesz czytać kandydatów | **Pokaż wszystkie** otwiera listę kandydatów przefiltrowaną do nowych. |
| **Otwarte procesy** | Procesy **w toku**. | Moduł **Procesy** włączony i możesz czytać procesy | **Pokaż wszystkie** otwiera otwarte procesy. |
| **Otwarte rozmowy wsparcia** | **Aktywne lub oczekujące rozmowy** w helpdesku stowarzyszenia. | Moduł **Wsparcie (helpdesk)** włączony i możesz go czytać | **Pokaż wszystkie** |
| **Zaległe zadania** | Zadania na tablicy zadań, których termin minął i które nie są zakończone. | Moduł **Tablica zadań** włączony i masz pełny dostęp (tablica zadań jest tylko dla użytkowników z pełnym dostępem) | **Pokaż wszystkie** otwiera tablicę zadań z samymi zaległymi zadaniami. |
| **Nowe zgłoszenia** | Zgłoszenia **do prac społecznych** z ostatnich 14 dni, na regularne terminy, które jeszcze się nie odbyły. Zgłoszenia na termin oznaczony przez kogoś jako przejrzany przestają się liczyć. | Moduł **Zarządzanie pracami społecznymi** włączony i możesz czytać prace społeczne | **Pokaż wszystkie** otwiera **Wpisy i przegląd**. |

Liczby na kafelkach **Otwarte wnioski zakupowe**, **Nowe zgłoszenia**
(kandydaci i prace społeczne), **Otwarte rozmowy wsparcia** i **Zaległe
zadania** są takie same jak czerwone oznaczenia na pasku bocznym (zob.
[Orientacja w aplikacji](navigation.md#badges-things-that-need-attention)).
Tak jak oznaczenia, zmniejszają się same, gdy sprawa zostanie
załatwiona.

## Urodziny w tym tygodniu {#birthdays-this-week}

Ta karta pojawia się tylko wtedy, gdy co najmniej jeden obecny członek
ma urodziny w ciągu najbliższych siedmiu dni, łącznie z dzisiejszym.
Pokazuje tych członków, od najbliższych urodzin:

- imię i nazwisko członka z linkiem do jego strony,
- **dziś kończy ...** przy urodzinach dzisiaj, w przeciwnym razie data i
  **kończy ...**,
- wyróżnione oznaczenie **Okrągłe** przy okrągłych urodzinach (30, 40,
  50, ...).

Członkowie bez zapisanej daty urodzenia nie są pokazywani. Karta jest
widoczna nawet przy wyłączonym module **Kalendarz**; jej przycisk
**Pokaż wszystkie** prowadzi do pełnej listy urodzin w kalendarzu, która
wymaga modułu kalendarza i uprawnienia.

## Najnowsi członkowie {#recent-members}

Pięciu obecnych członków, którzy zostali najpóźniej **wpisani do
Parcelli**, z datą **Członek od** po prawej (– jeśli nie jest ustawiona).
Kliknij nazwisko, aby otworzyć członka. Na świeżej instalacji pojawia
się **Nie utworzono jeszcze żadnych członków.**

**Nowy członek** otwiera formularz nowego członka.

## Szybki dostęp {#quick-access}

Skróty do częstych zadań:

| Przycisk | Do czego służy |
|---|---|
| **Utwórz nowego członka** | Otwiera formularz nowego członka. |
| **Utwórz nową działkę** | Otwiera formularz nowej działki. |
| **Eksportuj członków jako CSV** | Pobiera listę członków jako plik CSV, np. do arkusza kalkulacyjnego. |
| **Eksportuj działki jako CSV** | Pobiera listę działek jako plik CSV. |

Tworzenie członków i działek wymaga prawa **Zapis** w **Członkowie i
działki**. Bez niego formularz odpowiada komunikatem **Nie masz
uprawnień, aby to zrobić**.

## Powiązane {#related}

- [Członkowie](../modules/members.md) i [Działki](../modules/parcels.md)
- [Orientacja w aplikacji](navigation.md)
- [Włączanie i wyłączanie modułów](../administration/modules.md)
