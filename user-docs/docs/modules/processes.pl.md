# Procesy {#processes}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Wiele zadań stowarzyszenia przebiega za każdym razem tak samo:
przekazanie działki, przyjęcie nowego członka, rozpatrzenie skargi.
Dzięki procesom opisujesz takie zadanie raz jako **szablon** -- ciąg
**etapów**, każdy z **polami** do wypełnienia -- a potem uruchamiasz go
tak często, jak potrzebujesz, dla działki, członka lub kandydata.
Parcella śledzi, na jakim etapie jest każde uruchomienie, co wpisano i
kto co zrobił.

!!! info "Kto może z tego korzystać"
    - Przełącznik modułu to **Procesy** w **Administracja → Włączanie i
      wyłączanie modułów**. Domyślnie jest **włączony**.
    - Role **Zarząd** i **Administrator** oraz członkowie grupy z
      **Pełny dostęp do każdego modułu** mogą wszystko, łącznie z
      tworzeniem szablonów.
    - Wszyscy pozostali potrzebują uprawnienia **Procesy** w jednej ze
      swoich [grup](../administration/groups.md):
        - *odczyt*: oglądanie procesów, ich wartości, plików i historii;
        - *zapis*: rozpoczynanie procesów, wypełnianie pól, przesyłanie
          plików, przechodzenie do następnego etapu lub cofanie;
        - *usuwanie*: przerywanie lub usuwanie procesu.
    - **Szablony** można tworzyć i zmieniać tylko z pełnym dostępem.
    - Procesy dotyczące kandydatów i pola kandydatów wymagają też prawa
      odczytu modułu [Kandydaci](applicants.md). Bez niego widzisz
      „Widoczne tylko z dostępem do modułu kandydatów.”

## Jak to się łączy {#how-it-fits-together}

- **Szablon** mówi, czego dotyczy proces (działki, członka, kandydata
  lub niczego konkretnego), i wymienia po kolei jego etapy.
- Każdy **etap** ma dowolną liczbę **pól**. Pole może być **Wymagane**.
- Rozpoczęcie procesu tworzy kopię szablonu. Późniejsze zmiany szablonu
  nie wpływają na procesy, które już trwają.
- Proces zawsze jest na jednym **bieżącym etapie**. Przechodzisz dalej
  przyciskiem **Gotowe -- następny etap**, gdy wszystkie wymagane pola
  tego etapu są wypełnione. Po ostatnim etapie proces jest
  **Zakończony**.
- Możesz wrócić do wcześniejszego etapu (z powodem) albo przerwać proces
  (z powodem). Zakończonego ani przerwanego procesu nie można już
  zmieniać.

## Lista procesów {#process-list}

![Lista procesów](../assets/screenshots/processes/list.png)

Otwórz **Procesy** w menu.

| Pole / przycisk | Do czego służy |
|---|---|
| **Szablony** | Otwiera [Szablony procesów](#process-templates). Tylko z pełnym dostępem. |
| **Rozpocznij proces** | Otwiera [Rozpoczęcie procesu](#start-a-process). Wymaga *zapisu*. |
| **Status** | **W toku** (domyślnie), **Zamknięte** (zakończone lub przerwane) lub **Wszystkie**. |
| **Szablon** | **Wszystkie szablony** albo jeden szablon; zarchiwizowane szablony są oznaczone dopiskiem o archiwizacji. |
| **Filtruj** | Stosuje oba filtry. |

| Kolumna | Co pokazuje |
|---|---|
| **Proces** | Tytuł (z linkiem), a pod nim nazwa szablonu. |
| **Dotyczy** | Działka, członek lub kandydat, z linkiem do ich strony. „(usunięto)”, jeśli ten rekord został usunięty. |
| **Bieżący etap** | Etap, na którym jest proces, np. „Wycena (2/6)”. Kreska dla zamkniętych procesów. |
| **Rozpoczęto** | Data rozpoczęcia. |
| **Status** | **W toku**, **Zakończony** lub **Przerwany**. |

Jeśli lista jest pusta, mówi **Brak procesów.**, a gdy nie ma jeszcze
szablonów, proponuje **Najpierw utwórz szablon.**

!!! tip "Procesy na stronach działek, członków i kandydatów"
    Strona [działki](parcels.md), [członka](members.md) i
    [kandydata](applicants.md) ma kartę **Procesy** z ich procesami,
    bieżącym etapem i statusem. Jej przycisk **Rozpocznij proces**
    otwiera stronę rozpoczęcia z już wybraną działką, członkiem lub
    kandydatem i proponuje tylko pasujące szablony.

## Rozpoczęcie procesu {#start-a-process}

![Rozpoczęcie procesu](../assets/screenshots/processes/new.png)

1. Wybierz **Szablon**. Strona przeładowuje się i pokazuje opis szablonu
   oraz jego **Etapy**. Zarchiwizowane szablony nie są proponowane.
2. Jeśli szablon dotyczy działki, członka lub kandydata, wybierz go w
   polu **Działka**, **Członek** lub **Kandydat**. Jest to wymagane.
3. Opcjonalnie nadaj **Tytuł** -- jeśli zostanie pusty, użyta zostanie
   nazwa szablonu. Wskazówka: dodaj numer działki lub nazwisko, np.
   „Przekazanie działki 17”, aby odróżniać procesy na liście.
4. Kliknij **Rozpocznij**. Proces otwiera się na pierwszym etapie.

**Anuluj** wraca do listy. Jeśli nie ma jeszcze szablonu, strona mówi
**Nie ma jeszcze aktywnego szablonu.**

## Trwający proces {#a-running-process}

![Proces](../assets/screenshots/processes/detail.png)

Na górze widzisz status, szablon, czego dotyczy proces (z linkiem) i
„Rozpoczęty {date} przez {name}”. Poniżej rząd oznaczeń pokazuje
postęp: zielone z haczykiem dla ukończonych etapów, niebieskie dla
bieżącego etapu, szare dla etapów, które jeszcze nadejdą. Kliknij
oznaczenie, aby przejść do tego etapu.

Zakończony proces pokazuje **Zakończony {date}.**; przerwany pokazuje
**Przerwany**, datę i powód.

### Etapy {#the-stages}

Każdy etap to karta z numerem i nazwą.

- **Ukończone etapy** pokazują datę i kto je ukończył. Ich pola można
  nadal poprawiać, dopóki proces jest otwarty.
- **Bieżący etap** jest oznaczony **Bieżący etap** i obramowany na
  niebiesko.
- **Etapy jeszcze nieosiągnięte** są oznaczone **Jeszcze nieosiągnięty**
  i wymieniają tylko nazwy swoich pól.

W etapie, który możesz edytować, wypełnij pola i kliknij **Zapisz**.
Zapisuje to pola tego jednego etapu. Pliki są przesyłane osobno (zob.
niżej). Jeśli wartość jest nieprawidłowa, widzisz komunikat, np.
**Podaj prawidłową liczbę.** lub **Podaj prawidłową datę.**

### Przejście dalej {#moving-on}

Na dole bieżącego etapu:

- **Brakuje jeszcze przed przejściem dalej:** wymienia wymagane pola,
  które są jeszcze puste, każde z linkiem do pola. Dopóki coś jest
  wymienione, przycisk jest nieaktywny.
- **Gotowe -- następny etap** kończy etap i przesuwa proces dalej. Na
  ostatnim etapie przycisk to **Zakończ proces**.

Wymagane pole wyboru liczy się jako wypełnione, gdy jest zaznaczone;
wymagane pole pliku, gdy ma co najmniej jeden plik.

### Cofnij {#go-back}

Karta **Cofnij** (z *zapisem*, gdy proces jest za pierwszym etapem)
przywraca proces do wcześniejszego etapu, np. gdy trzeba powtórzyć
oględziny.

| Pole / przycisk | Do czego służy |
|---|---|
| **Powrót do etapu** | Do którego wcześniejszego etapu wrócić. Wstępnie wybrany jest poprzedni etap. |
| **Powód** | Wymagany. Trafia do historii. |
| **Cofnij** | Cofa proces. Wszystkie dotychczas wpisane wartości zostają. |

### Historia {#history}

Karta **Historia** pokazuje wszystko, co się wydarzyło, od najnowszych,
z godziną, etapem, notatką i użytkownikiem: **Rozpoczęto**, **Przejście
do**, **Powrót do**, **Zakończono**, **Przerwano**, **Zmieniono pole**
(ze starą i nową wartością), **Dodano plik** i **Usunięto plik**.

### Przerwanie lub usunięcie {#abort-or-delete}

Tylko z prawem *usuwania*:

| Pole / przycisk | Do czego służy |
|---|---|
| **Przerwij proces** + **Powód** + **Przerwij** | Na zawsze zatrzymuje otwarty proces po **Na pewno przerwać ten proces? Nie można go ponownie otworzyć.** Powód jest wymagany i pokazywany przy procesie. Proces zostaje na liście jako **Przerwany**. |
| **Usuń proces** | Całkowicie usuwa proces, ze wszystkimi wartościami i plikami, po **Na pewno usunąć ten proces wraz ze wszystkimi wartościami i plikami?** Tylko dla procesu rozpoczętego przez pomyłkę. Pliki w chmurze nie są usuwane. |

## Typy pól {#field-types}

| Typ | Co wpisujesz w procesie |
|---|---|
| **Tekst** | Jeden wiersz, do 1000 znaków. |
| **Długi tekst** | Kilka wierszy. |
| **Liczba** | Liczba. Przecinek i kropka działają jako separator dziesiętny („1.234,50” i „1,234.50”). |
| **Kwota** | Jak liczba, pokazywana z walutą stowarzyszenia. |
| **Data** | Data. |
| **Pole wyboru** | Zaznaczone lub nie, np. „Klucze przekazane”. |
| **Wybór z listy** | Jedna z opcji zdefiniowanych w szablonie. |
| **Pliki (PDF, zdjęcia)** | Jeden lub więcej przesłanych plików. |
| **Członek** | Członek stowarzyszenia. |
| **Kandydat** | Kandydat (wymaga dostępu do modułu kandydatów). |
| **Działka** | Działka. |

Pole może mieć tekst pomocy, pokazywany pod nim.

### Pliki {#files}

Pole pliku pokazuje swoje pliki z nazwą, rozmiarem, datą i osobą, która
je przesłała; ikona chmury oznacza **Zapisany w chmurze**. Kliknij nazwę,
aby otworzyć lub pobrać plik. Aby dodać plik, użyj **Wybierz plik** i
**Prześlij**; małe x usuwa plik po **Usunąć ten plik?** (dopóki etap
jest edytowalny).

Tylko PDF, JPEG, PNG lub WebP, do 20 MB. Pod przyciskiem przesyłania
Parcella mówi, dokąd trafi plik, w tej kolejności:

1. **Folder działki w chmurze**, w podfolderze dla tego procesu -- jeśli
   moduł magazynu w chmurze jest włączony, a proces dotyczy działki z
   folderem w chmurze albo członka z dokładnie jedną obecną działką,
   która go ma.
2. **Folder na pliki procesów**, jeśli administrator ustawił **Folder na
   pliki procesów** w **Administracja → Integracje**.
3. W przeciwnym razie **prywatny magazyn Parcelli**: „Przechowywane w
   prywatnym magazynie Parcelli (brak folderu w chmurze dla tej działki
   lub dla procesów).”

!!! warning "Foldery działek są często udostępniane dzierżawcom"
    Jeśli foldery działek w chmurze są udostępnione dzierżawcom działki,
    widzą oni też pliki procesów dotyczących ich działki. Jest to
    zamierzone -- oficjalne dokumenty dotyczące działki są jawne dla jej
    dzierżawców. Jeśli chcesz pliki tylko dla zarządu, nie ustawiaj
    folderu w chmurze dla działki i użyj zamiast tego folderu na pliki
    procesów.

Usunięcie pliku z procesu kasuje plik we własnym magazynie Parcelli, ale
plik w chmurze tylko odłącza; sam plik tam zostaje.

## Szablony procesów {#process-templates}

![Szablony procesów](../assets/screenshots/processes/templates.png)

**Szablony** na liście procesów (tylko pełny dostęp) otwiera **Szablony
procesów**. **Procesy** u góry po prawej prowadzi z powrotem.

Karta **Szablony** pokazuje każdy szablon z tym, czego dotyczy, liczbą
etapów, liczbą użyć i oznaczeniem **zarchiwizowany**, jeśli jest
zarchiwizowany. **Edytuj** otwiera [edytor szablonu](#the-template-editor).

### Nowy szablon {#new-template}

| Pole / przycisk | Do czego służy |
|---|---|
| **Nazwa** | Wymagana, do 200 znaków. |
| **Proces dotyczy** | **Działka**, **Członek**, **Kandydat** lub **Nieprzypisany**. Przy rozpoczynaniu procesu wybiera się działkę, członka lub kandydata, którego dotyczy, a proces jest pokazywany na jego stronie. |
| **Opis** | Opcjonalny. Pokazywany, gdy ktoś wybiera szablon, aby rozpocząć proces. |
| **Utwórz** | Tworzy szablon i otwiera edytor. |

### Zacznij od przykładu {#start-from-an-example}

Tworzy zwykły szablon w Twoim języku, który możesz potem dowolnie
zmieniać. Kliknij **Użyj** obok:

- **Przekazanie działki** -- wypowiedziana działka w drodze do kolejnego
  dzierżawcy: oględziny, wycena, ogłoszenie, nowy dzierżawca, umowa i
  przekazanie.
- **Przyjęcie nowego członka** -- powitanie nowego członka: pierwsze
  spotkanie, dokumenty i ostatnie szczegóły.

## Edytor szablonu {#the-template-editor}

![Edytor szablonu](../assets/screenshots/processes/template-edit.png)

Edytor ma nagłówek „Szablon: {name}”. Zmiany są zapisywane na bieżąco;
u góry po prawej pojawia się krótkie potwierdzenie.

Nagłówek pokazuje nazwę, czego dotyczy szablon, i notkę: „Zmiany
dotyczą procesów rozpoczętych od teraz. Już rozpoczęte procesy ({count})
zachowują swoje etapy i pola.”

| Przycisk | Do czego służy |
|---|---|
| **Szczegóły** | Otwiera nazwę, **Proces dotyczy** i opis do edycji; **Zapisz** je zapisuje. |
| **Archiwizuj** / **Przywróć** | Zarchiwizowanego szablonu nie można użyć do rozpoczęcia nowych procesów; trwające działają dalej. |
| **Usuń** | Tylko dopóki z szablonu nie rozpoczęto żadnego procesu, po **Na pewno usunąć ten szablon?** W przeciwnym razie zarchiwizuj go. |

### Etapy {#stages}

Lewa karta pokazuje **Etapy** po kolei, z liczbą pól. Kliknij etap, aby
go edytować. Przeciągnij etap za uchwyt, aby zmienić kolejność. Dodaj
etap, wpisując nazwę w **Nowy etap, np. „Oględziny”** i klikając
**Dodaj**.

Wybrany etap jest pokazywany po prawej:

- Jego **nazwę** i **Opis (opcjonalnie)** można edytować w miejscu.
  Opis jest pokazywany na górze etapu w trwającym procesie.
- Menu **⋮** (**Działania etapu**) ma **W górę**, **W dół** i **Usuń
  etap** (po **Usunąć ten etap ze wszystkimi polami?**).

### Pola {#fields}

Zakładka **Pola** pokazuje pola etapu z ich typem, opcjami, tekstem
pomocy i oznaczeniem **Wymagane**. Etap bez pól to prosty krok do
odhaczenia.

Aby dodać pole, wpisz jego etykietę w **Nowe pole: wpisz nazwę i naciśnij
Enter**, wybierz **Typ**, w razie potrzeby zaznacz **Wymagane** i
naciśnij Enter albo kliknij **Dodaj pole**. Dla **Wybór z listy** najpierw
otwiera się panel boczny, bo wybór potrzebuje opcji.

Przeciągaj pola za uchwyt, aby zmienić kolejność. Kliknij pole, aby
otworzyć panel **Edytuj pole**:

| Pole / przycisk | Do czego służy |
|---|---|
| **Etykieta** | Wymagana, do 200 znaków. |
| **Typ** | Jeden z [typów pól](#field-types). |
| **Opcje (tylko dla wyboru, jedna w wierszu)** | Wymagane dla **Wybór z listy**: co najmniej jedna opcja. |
| **Wymagane** | Proces może przejść dalej dopiero, gdy to pole jest wypełnione. |
| **Tekst pomocy (opcjonalnie)** | Pokazywany pod polem w trwającym procesie. |
| **Zapisz** / **Zamknij** | Zapisuje pole / zamyka panel. |
| **Przenieś do etapu** + przycisk strzałki | Przenosi pole na koniec innego etapu. |
| **W górę** / **W dół** | Zmienia kolejność, bez przeciągania. |
| **Duplikuj** | Dodaje kopię zaraz poniżej. |
| **Usuń pole** | Usuwa pole z szablonu. |

Zakładka **Podgląd** pokazuje, jak etap wygląda w trwającym procesie, z
nieaktywnymi polami.

## Przykład: przekazanie działki {#worked-example-a-plot-handover}

Dzierżawca wypowiedział działkę 17. Oto jak zarząd przeprowadza
przekazanie z przykładem **Przekazanie działki**.

**Raz: skonfiguruj szablon.** Otwórz **Procesy → Szablony**, kliknij
**Użyj** obok **Przekazanie działki**. Dostajesz szablon dotyczący
**Działka** z sześcioma etapami:

| # | Etap | Pola (* = wymagane) |
|---|---|---|
| 1 | Oględziny | Data oględzin*, Stwierdzone usterki, Zdjęcia usterek, Wszystkie usterki usunięte* |
| 2 | Wycena | Rzeczoznawca*, Data wyceny*, Protokół wyceny* (plik) |
| 3 | Ogłoszenie | Treść ogłoszenia*, Zdjęcia do ogłoszenia, Opublikowano* |
| 4 | Nowy dzierżawca | Nowy dzierżawca* (kandydat), Nawiązano kontakt*, Wysłano dokumenty* |
| 5 | Umowa i kaucja | Umowa kupna potwierdzona*, Kaucja (kwota), Kaucja wpłynęła |
| 6 | Przekazanie | Podpisane przez nowego dzierżawcę*, Kontrasygnowane przez zarząd*, Klucze przekazane*, Liczniki odczytane*, Protokół przekazania (plik) |

Dostosuj go do swojego stowarzyszenia: np. ustaw **Kaucja** jako
wymaganą albo dodaj pole **Wybór z listy** „Wynik wyceny” z opcjami
„Przejęcie według wyceny” i „Działkę należy oczyścić”.

**Za każdym razem: uruchom go.**

1. Otwórz działkę 17 i kliknij **Rozpocznij proces** w jej karcie
   **Procesy**. **Przekazanie działki** i działka są już wybrane. Wpisz
   tytuł „Przekazanie działki 17” i kliknij **Rozpocznij**.
2. **Oględziny**: po obchodzie wpisz datę, wypisz usterki, prześlij
   zdjęcia i kliknij **Zapisz**. Etapu nie można jeszcze ukończyć:
   wciąż brakuje **Wszystkie usterki usunięte**. Gdy dzierżawca wszystko
   naprawi, zaznacz to, **Zapisz**, potem **Gotowe -- następny etap**.
3. **Wycena**: wpisz rzeczoznawcę i datę, prześlij protokół jako PDF.
   Jeśli działka ma folder w chmurze, protokół trafia tam do podfolderu
   tego przekazania. **Gotowe -- następny etap**.
4. **Ogłoszenie** i **Nowy dzierżawca**: zapisz ogłoszenie, potem wybierz
   wybraną osobę z listy kandydatów i zaznacz oba pola wyboru.
5. **Umowa i kaucja**: potwierdź umowę, wpisz kaucję i dzień, w którym
   wpłynęła.
6. **Przekazanie**: zaznacz podpisy, klucze i odczyty liczników,
   prześlij protokół przekazania i kliknij **Zakończ proces**.

Jeśli nowy dzierżawca wycofa się na etapie 5, użyj **Cofnij**, aby
wrócić do **Ogłoszenie** z powodem „Kandydat zrezygnował”. Dotychczas
wpisane wartości zostają, a historia pokazuje, co się stało.

Sam proces tylko dokumentuje przekazanie. Zakończenie starej dzierżawy,
rozpoczęcie nowej i odczyt liczników w Parcelli wykonuje się w modułach
[Działki](parcels.md) i [Woda i prąd](metering.md) -- zob.
[instrukcję przekazania działki](../guides/parcel-handover.md).

## Powiązane {#related}

- [Przekazanie działki](../guides/parcel-handover.md)
- [Działki](parcels.md), [Członkowie](members.md),
  [Kandydaci](applicants.md) -- karta **Procesy** na ich stronach.
- [Integracje](../administration/integrations.md) -- folder na pliki
  procesów.
- [Grupy](../administration/groups.md) -- nadanie komuś uprawnień do
  procesów.
