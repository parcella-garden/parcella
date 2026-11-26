# Notatki {#notes}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Protokoły z walnych zebrań, posiedzeń zarządu, spotkań z osobami z
zewnątrz i wszystko inne, co warto zapisać. Notatki pisze się w
Markdownie, przypisuje do kategorii i tagów, a potem można je
przeszukiwać, filtrować i sortować. Jeśli Twoje stowarzyszenie korzysta
z magazynu w chmurze, każda notatka może tam istnieć jako plik `.md`,
który możesz otworzyć i edytować także w chmurze.

!!! info "Kto może z tego korzystać"
    - Przełącznik modułu to **Notatki** w **Administracja → Włączanie i
      wyłączanie modułów**. Domyślnie jest **włączony**.
    - Role **Zarząd** i **Administrator** oraz członkowie grupy z
      **Pełny dostęp do każdego modułu** mogą wszystko.
    - Wszyscy pozostali potrzebują uprawnienia **Notatki** w jednej ze
      swoich [grup](../administration/groups.md):
        - *odczyt*: oglądanie listy i notatek, pobieranie ich,
          uruchamianie **Synchronizuj**;
        - *zapis*: tworzenie i edycja notatek, import zakładek, dodawanie,
          zmiana nazw i tłumaczenie kategorii i tagów;
        - *usuwanie*: usuwanie notatek, kategorii i tagów.
    - Przechowywanie notatek w chmurze wymaga też modułu **Magazyn w
      chmurze** i folderu notatek, zob. [Notatki w chmurze](#notes-in-the-cloud).

## Lista notatek {#note-list}

![Lista notatek](../assets/screenshots/notes/list.png)

Otwórz **Notatki** w menu.

### Przyciski na górze {#buttons-at-the-top}

| Przycisk | Do czego służy |
|---|---|
| **Synchronizuj** | Widoczny tylko, gdy ustawiono folder notatek. Wczytuje teraz zmiany z folderu w chmurze (zob. [Notatki w chmurze](#notes-in-the-cloud)). |
| **Kategorie i tagi** | Otwiera [Kategorie i tagi](#categories-tags). |
| **Importuj zakładki** | Otwiera [Import zakładek](#import-bookmarks). Wymaga *zapisu*. |
| **Nowa notatka** | Otwiera pusty [formularz notatki](#writing-a-note). Wymaga *zapisu*. |

### Wyszukiwanie i filtry {#search-and-filters}

| Pole / przycisk | Do czego służy |
|---|---|
| **Szukaj** | Przeszukuje tytuł, tekst i nazwy tagów. Wielkość liter nie ma znaczenia. |
| **Kategoria** | **Wszystkie**, **Bez kategorii** albo jedna kategoria. |
| **Tagi** | **Wszystkie** albo jeden tag. |
| **Od** / **Do** | Tylko notatki, których data mieści się w tym zakresie. |
| **Sortuj według** | **Data, od najnowszych** (domyślnie), **Data, od najstarszych**, **Tytuł**, **Ostatnia zmiana**. |
| **Zastosuj** | Stosuje wyszukiwanie, filtry i sortowanie. |
| **Wyczyść** | Widoczny, gdy coś jest ustawione. Wraca do wszystkich notatek, od najnowszych. |

### Kolumny {#columns}

| Kolumna | Co pokazuje |
|---|---|
| **Data** | Dzień, którego dotyczy notatka (dla protokołów: dzień zebrania). |
| **Tytuł** | Link do notatki. Ikona strzałki otwiera link źródłowy notatki w nowej karcie (zakładki). Pomarańczowa ikona chmury oznacza **Jeszcze nie zapisano w chmurze**. |
| **Kategoria** | Kliknij, aby przefiltrować po niej listę. |
| **Tagi** | Kliknij jeden, aby przefiltrować po nim listę. |
| **Zmieniono** | Kiedy notatkę ostatnio zapisano (ukryte na małych ekranach). |

Gdy lista jest pusta, mówi **Brak notatek.**, albo **Żadna notatka nie
pasuje do tych filtrów.**, gdy ustawiono filtr.

## Czytanie notatki {#reading-a-note}

![Notatka](../assets/screenshots/notes/detail.png)

Kliknij tytuł notatki. Widzisz tytuł, datę, kategorię i tagi (każde
klikalne, aby przefiltrować listę), **Źródło (link)**, jeśli to zakładka,
oraz sformatowany tekst. Stopka pokazuje, kto utworzył i kto ostatnio
zmienił notatkę, a przy folderze w chmurze ścieżkę pliku notatki.

| Przycisk | Do czego służy |
|---|---|
| **Wszystkie notatki** | Powrót do listy. |
| **Pobierz .md** | Pobiera notatkę jako plik Markdown, z tytułem, datą, kategorią i tagami w nagłówku na górze. |
| **Pobierz PDF** | Pobiera notatkę jako PDF z nagłówkiem stowarzyszenia. Obrazy, które są tylko podlinkowane z sieci, są pomijane. |
| **Edytuj** | Otwiera formularz. Wymaga *zapisu*. |
| **Usuń notatkę** | Wymaga *usuwania*. Pyta **Usunąć tę notatkę? Jej plik w chmurze również zostanie usunięty.** |

Otwarcie notatki najpierw ponownie odczytuje jej plik z chmury, więc
zawsze widzisz aktualny tekst. Jeśli to się nie uda, strona pokazuje
**Nie udało się odczytać pliku z chmury, pokazano ostatnio
zsynchronizowaną wersję: ...** z przyczyną.

## Pisanie notatki {#writing-a-note}

![Formularz notatki](../assets/screenshots/notes/form.png)

**Nowa notatka** lub **Edytuj** otwiera formularz (**Nowa notatka** /
**Edytuj notatkę**).

| Pole / przycisk | Do czego służy |
|---|---|
| **Tytuł** | Wymagany, do 255 znaków. |
| **Data** | Wymagana. Dzień, którego dotyczy notatka, a nie dzień, w którym ją piszesz. |
| **Kategoria** | **Bez kategorii** albo jedna z kategorii stowarzyszenia. |
| **Tagi** | Zaznacz istniejące tagi. |
| **Nowe tagi, oddzielone przecinkami** | Wpisz nowe tagi, rozdzielone przecinkami. Zostaną utworzone przy zapisie i dodane do listy tagów stowarzyszenia. |
| **Źródło (link)** | Opcjonalne: strona internetowa, której dotyczy notatka. Notatka ze źródłem to zakładka. Musi zaczynać się od `http://` lub `https://`. |
| **Notatka** | Tekst, w Markdownie. Przy folderze w chmurze pole mówi, gdzie zapisywany jest plik. |
| **Zapisz** | Zapisuje notatkę. |
| **Anuluj** | Powrót bez zapisywania. |

Edytor ma pasek narzędzi do pogrubienia, kursywy, przekreślenia,
nagłówka, cytatu, list, kodu, linku, tabeli i linii poziomej. Ikona oka
pokazuje podgląd, ikona podziału pokazuje tekst i podgląd obok siebie,
strzałki przełączają na pełny ekran, a znak zapytania otwiera
przewodnik po Markdownie.

Możliwe komunikaty: **Podaj tytuł.**, **Podaj datę.**, **Źródło musi być
adresem internetowym zaczynającym się od http:// lub https://.**, **Ta
kategoria nie istnieje (już).**, **Ten tag nie istnieje (już).**

## Notatki w chmurze {#notes-in-the-cloud}

Gdy moduł **Magazyn w chmurze** jest włączony, a administrator ustawił
**Folder notatek** w **Administracja → Integracje → Chmura (dokumenty
działek, faktury, kopie zapasowe)**, tekst każdej notatki jest plikiem
Markdown w tym folderze.

!!! note "Plik jest wersją nadrzędną tekstu"
    Wygrywa tekst w pliku w chmurze. Ty i inni możecie otwierać i
    zmieniać te pliki dowolnym edytorem w chmurze (Nextcloud Text,
    Obsidian itd.); zmiany pojawiają się w Parcelli. Tytuł, data,
    kategoria, tagi i źródło istnieją tylko w Parcelli i nie są
    zapisywane w pliku.

Jak to działa w praktyce:

- **Zapisywanie** najpierw zapisuje plik. Jeśli pliku nie da się
  zapisać, notatka nie zostaje zapisana i widzisz **Nie zapisano, nie
  udało się zapisać pliku w chmurze: ...**, a Twój tekst zostaje w
  formularzu. Zmiana tylko tytułu, daty, tagów lub źródła w ogóle nie
  dotyka pliku.
- **Podfoldery to kategorie.** Notatka w folderze „Posiedzenie zarządu/”
  dostaje kategorię „Posiedzenie zarządu” (tworzoną w razie potrzeby).
  Zapisanie notatki z inną kategorią przenosi jej plik do folderu tej
  kategorii. Notatki bez kategorii leżą bezpośrednio w folderze notatek.
- **Nowe pliki** są nazywane od daty i tytułu, np.
  `20261108-posiedzenie-zarzadu.md`. Parcella nigdy później nie zmienia
  nazwy pliku.
- **Pliki utworzone w chmurze** stają się notatkami. Ich data jest
  brana z początku nazwy pliku (`2026-11-08`, `20261108` lub `202506`
  dla 1. dnia tego miesiąca), w przeciwnym razie z daty ostatniej zmiany
  pliku.
- **Synchronizuj**: otwarcie listy notatek wczytuje zmiany z chmury w
  tle, najwyżej raz na minutę; pojawiają się przy następnym otwarciu
  listy. **Synchronizuj** robi to od razu i podaje **Zsynchronizowano:
  {n} nowych, {n} zmienionych, {n} usuniętych, {n} przesłanych.** Plik
  usunięty w chmurze usuwa swoją notatkę z listy.
- **Usunięcie** notatki w Parcelli usuwa też jej plik. Jeśli to się nie
  uda, notatka nie zostaje usunięta: **Nie usunięto, nie udało się
  usunąć pliku w chmurze: ...**
- **Jeszcze bez folderu?** Notatki są przechowywane tylko w Parcelli i
  oznaczone **Jeszcze nie zapisano w chmurze**. Zostaną przesłane przy
  pierwszej synchronizacji po ustawieniu folderu.

### Gdy ktoś w tym samym czasie zmienił plik {#when-someone-changed-the-file-at-the-same-time}

Jeśli plik został zmieniony w chmurze, gdy edytowałeś, zapisywanie
zatrzymuje się z komunikatem **Nie zapisano: notatka została w
międzyczasie zmieniona w chmurze.** Żółta karta **W międzyczasie
zmieniono w chmurze** pokazuje wersję z chmury (z **Pokaż jako Markdown**
dla surowego tekstu), a Twój własny tekst zostaje w formularzu poniżej.
Przenieś, co potrzebujesz, i kliknij **Zapisz** jeszcze raz, aby
nadpisać wersję z chmury.

Jeśli notatka została zmieniona zarówno w Parcelli (gdy nie był
ustawiony folder), jak i w chmurze, synchronizacja zachowuje wersję z
chmury, a Twoją zapisuje jako osobną notatkę z dopiskiem „conflict
copy”. **Synchronizuj** mówi wtedy, ile takich kopii powstało. Nic nie
ginie.

## Kategorie i tagi {#categories-tags}

![Kategorie i tagi](../assets/screenshots/notes/taxonomy.png)

**Kategorie i tagi** pokazuje kategorie i tagi stowarzyszenia. Każda
notatka ma jedną kategorię i dowolną liczbę tagów. Te same kategorie i
tagi mają być używane także przez przyszłą bazę wiedzy. Nowe instalacje
zaczynają z czterema kategoriami: „General meeting”, „Board meeting”,
„Meeting with externals” i „Other”. **Notatki** (u góry po prawej)
prowadzi z powrotem.

Strona ma dwie karty, **Kategorie** i **Tagi**, które działają tak samo:

| Pole / przycisk | Do czego służy |
|---|---|
| Nazwa + przycisk haczyka | Zmienia nazwę kategorii lub tagu. Wymaga *zapisu*; w przeciwnym razie nazwa jest tylko pokazywana. Zmiana nazwy kategorii przenosi pliki jej notatek do folderu o nowej nazwie przy następnej synchronizacji; stary, pusty folder zostaje. |
| „Notatki: {count}” | Otwiera listę notatek przefiltrowaną po niej. |
| Przycisk tłumaczenia | Otwiera nazwy dla każdego języka. Z *zapisem* możesz wpisać nazwę dla każdego języka obsługiwanego przez Parcellę i kliknąć **Zapisz tłumaczenia**; puste pola pokazują nazwę główną. |
| Przycisk kosza | Usuwa kategorię lub tag po **Usunąć "{name}"? Notatki pozostaną, tylko bez tego wpisu.** Wymaga *usuwania*. |
| **Nowa kategoria** / **Nowy tag** + **Dodaj** | Dodaje jedno. Wymaga *zapisu*. |

## Import zakładek {#import-bookmarks}

![Import zakładek](../assets/screenshots/notes/import-bookmarks.png)

Jeśli Twoje stowarzyszenie zbiera przydatne linki (dostawcy, urzędy,
poradniki) w Nextcloud Bookmarks lub w przeglądarce, możesz za jednym
razem zamienić je w notatki. Każda zakładka staje się notatką z linkiem
jako źródłem.

1. Wyeksportuj zakładki jako plik HTML. Potrafią to Nextcloud Bookmarks
   i każda przeglądarka.
2. Kliknij **Importuj zakładki**, wybierz plik i kliknij **Pokaż
   podgląd**. Jeszcze nic nie jest zapisywane.
3. Podgląd mówi, ile jest „nowych”, ile „już jest notatką” (istnieje
   notatka z tym samym linkiem -- pomijane) i ile „nie link internetowy”
   (pomijane). Tabela pokazuje dla każdej zakładki **Data**, **Tytuł** (z
   linkiem i opisem), **Tagi** i **Status**.
4. Kliknij **Importuj zakładki ({count})** albo **Wybierz inny plik**.

Nowe notatki nie dostają kategorii; przy folderze w chmurze są
zapisywane w katalogu głównym folderu notatek. Foldery zakładki stają
się tagami, opis staje się tekstem, a data dodania zakładki datą
notatki. Parcella nigdy nie otwiera podlinkowanych stron.

Jeśli plik nie zawiera zakładek: **W tym pliku nie znaleziono
zakładek.**

## Notatki i asystenci AI {#notes-and-ai-assistants}

Administrator może włączyć moduł **Konektor MCP dla klientów AI**.
Asystent AI, taki jak Claude, może wtedy przeszukiwać, czytać i zapisywać
notatki -- ale tylko notatki z tagiem udostępnienia (domyślnie
`ki-freigegeben`). Każda inna notatka pozostaje dla niego niewidoczna.
Notatki zapisane przez AI są oznaczane tagiem (domyślnie `ki-erstellt`),
abyś wiedział, co sprawdzić. Domyślnie jest to wyłączone, bo przekazuje
notatki stowarzyszenia zewnętrznej usłudze.

<!-- TODO(verify): where the release and created tag names are configured in the UI (stored as club settings); and link to the API tokens page section on "MCP connector only" tokens. -->

## Powiązane {#related}

- [Integracje](../administration/integrations.md) -- magazyn w chmurze i
  folder notatek.
- [Tokeny API](../administration/api-tokens.md)
- [Grupy](../administration/groups.md) -- nadanie komuś uprawnień do
  notatek.
- [Włączanie i wyłączanie modułów](../administration/modules.md)
