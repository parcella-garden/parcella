# Inwentarz {#inventory}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Inwentarz to rejestr majątku stowarzyszenia: wszystko, co należy do
stowarzyszenia, oraz rzeczy, które członkowie mają prywatnie, ale
przechowują na terenie stowarzyszenia. Przedmioty są pogrupowane w
kategorie, które definiujesz sam, mają cenę zakupu, bieżącą wartość i
koszt wymiany i mogą być wypożyczane członkom za pomocą prostego systemu
wypożyczeń i zwrotów.

!!! info "Kto może z tego korzystać"
    Członkowie zarządu i administratorzy zawsze mają pełny dostęp. Inni
    użytkownicy potrzebują grupy, która nadaje uprawnienia do
    **Inwentarz** (zob. [Grupy](../administration/groups.md)):

    - **Odczyt** -- oglądanie listy przedmiotów, stron przedmiotów i
      aktywnych wypożyczeń.
    - **Zapis** -- tworzenie, edycja i wycofywanie przedmiotów,
      zarządzanie kategoriami, wypożyczanie przedmiotów i oznaczanie ich
      jako zwrócone.
    - **Usuwanie** -- trwałe usuwanie przedmiotów i kategorii.

    Moduł włącza się przełącznikiem **Inwentarz** w
    [Włączaniu i wyłączaniu modułów](../administration/modules.md).
    Domyślnie jest włączony.

## Lista inwentarza {#inventory-list}

![Lista inwentarza](../assets/screenshots/inventory/list.png)

**Inwentarz** w nawigacji pokazuje wszystkie przedmioty, pogrupowane w
jedną kartę na kategorię w kolejności alfabetycznej. Przedmioty bez
kategorii są na końcu w **Bez kategorii**. W obrębie karty przedmioty
są posortowane według nazwy.

| Pole / przycisk | Do czego służy |
|---|---|
| **Aktywne wypożyczenia** | Otwiera [listę wszystkiego, co jest obecnie wypożyczone](#active-loans). |
| **Zarządzaj kategoriami** | Otwiera [kategorie](#inventory-categories). Widoczny tylko z prawem zapisu. |
| **Nowy przedmiot** | Otwiera pusty [formularz przedmiotu](#item-form). Widoczny tylko z prawem zapisu. |
| **Wszystkie kategorie** / kategoria | Pokazuje tylko przedmioty jednej kategorii. |
| **Uwzględnij wycofane przedmioty** | Pokazuje też [wycofane](#retiring-and-deleting) przedmioty, na szaro z oznaczeniem **Wycofany**. Domyślnie wyłączone. |

| Kolumna | Co pokazuje |
|---|---|
| **Nazwa** | Przedmiot, z linkiem do jego strony. Oznaczenia: **Wycofany**, **Do wypożyczenia**. |
| **Właściciel** | **Własność klubu** lub **Własność członka**. |
| **Miejsce przechowywania** | Miejsce przechowywania. |
| **Ilość** | Dla przedmiotów do wypożyczenia: dostępne / posiadane (np. **1 / 2**, gdy jeden z dwóch jest wypożyczony); w przeciwnym razie posiadana ilość. |
| **Wartość** | Bieżąca wartość, jeśli wpisano. |
| Przycisk oka | Otwiera przedmiot. |

## Strona przedmiotu {#item-page}

![Strona przedmiotu](../assets/screenshots/inventory/detail.png)

Kliknij nazwę przedmiotu, aby otworzyć jego stronę.

### Przyciski {#buttons}

| Przycisk | Do czego służy |
|---|---|
| **Edytuj** | Otwiera [formularz przedmiotu](#item-form). Wymaga prawa zapisu. |
| **Wycofaj** | Po potwierdzeniu oznacza przedmiot jako już nieposiadany lub nieużywany. Wymaga prawa zapisu; niewidoczny, gdy przedmiot jest już wycofany. Zob. [Wycofywanie i usuwanie](#retiring-and-deleting). |
| **Usuń** | Po potwierdzeniu trwale usuwa przedmiot i całą jego historię wypożyczeń. Wymaga prawa usuwania. |
| **Wstecz** | Wraca na listę inwentarza. |

Wycofany przedmiot pokazuje na górze notkę „Ten przedmiot jest wycofany
-- już nie w posiadaniu/użyciu.”

### Przegląd {#overview}

| Pole | Co pokazuje |
|---|---|
| **Kategoria** | Kategoria albo **Bez kategorii**. |
| **Właściciel** | **Własność klubu** albo imię i nazwisko członka, do którego należy. |
| **Miejsce przechowywania** | Gdzie przedmiot jest przechowywany, albo „-”. |
| **Ilość** | Dla przedmiotów do wypożyczenia „dostępne / posiadane **dostępne**”, w przeciwnym razie posiadana ilość. |
| **Opis**, **Notatki** | Widoczne tylko, jeśli wypełnione. |

### Finanse {#financials}

| Pole | Co pokazuje |
|---|---|
| **Data zakupu** | Kiedy został kupiony. |
| **Cena zakupu** | Ile kosztował. |
| **Bieżąca wartość** | Bieżąca ocena zarządu, z „stan na” i datą ostatniego sprawdzenia, jeśli wpisano. |
| **Koszt wymiany** | Ile kosztowałaby wymiana. |

Puste pola pokazują „-”.

### Wypożycz {#check-out}

Widoczne tylko dla przedmiotów oznaczonych jako do wypożyczenia. Jeśli
nic nie jest dostępne, pokazuje **Obecnie nic nie jest dostępne do
wypożyczenia.** Formularz wymaga prawa zapisu.

| Pole / przycisk | Do czego służy |
|---|---|
| **Członek** | Kto wypożycza przedmiot. Pokazuje obecnych członków. Wymagane. |
| **Ilość** | Ile sztuk. Co najmniej 1, najwyżej liczba obecnie dostępna. Domyślnie 1. |
| **Data** | Dzień wypożyczenia. Domyślnie dziś. |
| **Opłata** | Opcjonalna. Tylko liczba, np. `5` lub `2,50` -- bez znaku waluty ani tekstu. Jeśli pole jest puste, naliczana jest **Sugerowana opłata za wypożyczenie** przedmiotu (pokazuje ją podpowiedź pod polem). |
| **Notatka** | Opcjonalny dowolny tekst, np. „zwrot do niedzieli”. |
| **Wypożycz** | Zapisuje wypożyczenie. Dostępna ilość odpowiednio się zmniejsza. |

Jeśli coś jest nie tak -- nie wybrano członka, więcej sztuk niż
dostępnych („Dostępne jest tylko 1 z 2 w tej chwili.”), opłata z
tekstem, nieprawidłowa data -- strona pokazuje komunikat nad
formularzem i zachowuje to, co wpisałeś.

!!! note "Opłaty są zapisywane, nie fakturowane"
    Opłata jest zapisywana przy wypożyczeniu, aby zarząd wiedział, co
    uzgodniono. Parcella nie tworzy dla niej faktury ani księgowania.

### Historia wypożyczeń {#loan-history}

Każde wypożyczenie tego przedmiotu, od najnowszych.

| Kolumna | Co pokazuje |
|---|---|
| **Członek** | Kto go wypożyczył. |
| **Ilość** | Ile sztuk. |
| **Wypożyczono** | Data wypożyczenia. |
| **Zwrócono** | Data zwrotu albo oznaczenie **Niezwrócone**, dopóki przedmiot jest wypożyczony. |
| **Opłata** | Naliczona opłata albo „-”. |
| **Oznacz jako zwrócone** | Zapisuje zwrot z dzisiejszą datą. Widoczne przy niezwróconych wypożyczeniach z prawem zapisu. |

## Formularz przedmiotu {#item-form}

![Nowy przedmiot](../assets/screenshots/inventory/form-new.png)

Ten sam formularz służy do **Nowy przedmiot** i **Edytuj**, z tytułem
**Przedmiot inwentarza**.

### Ogólne {#general}

| Pole | Do czego służy |
|---|---|
| **Nazwa** | Czym jest przedmiot. Wymagana. |
| **Kategoria** | Jedna z Twoich [kategorii](#inventory-categories) albo **Bez kategorii**. |
| **Opis** | Opcjonalny dłuższy opis. |
| **Miejsce przechowywania** | Gdzie jest przechowywany, np. „Szopa na narzędzia”. |

### Własność {#ownership}

| Pole | Do czego służy |
|---|---|
| **Własność klubu** | Ustawienie domyślne. |
| **Własność osobista członka** | Dla rzeczy, które członkowie przechowują na terenie stowarzyszenia, ale które należą do nich -- warto je zapisać ze względu na ubezpieczenie i odpowiedzialność. Pokazuje **Członek-właściciel**. |
| **Członek-właściciel** | Członek, do którego należy przedmiot. Wymagany, gdy przedmiot jest własnością członka; pokazuje obecnych członków. |

### Finanse {#financials_1}

Bieżącą wartość wpisuje się ręcznie za każdym razem, gdy ktoś ją
sprawdzi. Parcella niczego nie amortyzuje automatycznie.

| Pole | Do czego służy |
|---|---|
| **Data zakupu** | Opcjonalna. |
| **Cena zakupu** | Opcjonalna. |
| **Bieżąca wartość** | Opcjonalna. Twoja aktualna najlepsza ocena. |
| **Koszt wymiany** | Opcjonalny. |
| **Wartość ostatnio sprawdzona** | Opcjonalna data, aby każdy widział, jak aktualna jest bieżąca wartość. |

Kwoty to tylko liczby: `5`, `2,50` lub `2.50`. Tekst, znak waluty lub
kwota ujemna są odrzucane z komunikatem.

### Wypożyczanie {#lending}

| Pole | Do czego służy |
|---|---|
| **Posiadana ilość** | Ile identycznych sztuk oznacza ten wpis -- trzy taczki mogą być jednym przedmiotem z ilością 3. Liczba całkowita 1 lub większa; domyślnie 1. |
| **Członkowie mogą to wypożyczyć** | Włącza wypożyczanie i zwroty dla tego przedmiotu. Pokazuje **Sugerowana opłata za wypożyczenie**. |
| **Sugerowana opłata za wypożyczenie** | Opcjonalna. Używana jako opłata, gdy wypożyczenie jest zapisywane bez opłaty; można ją zmienić dla każdego wypożyczenia. |

### Notatki {#notes}

Dowolny tekst na wszystko inne.

Kliknij **Zapisz**, aby zapisać przedmiot i otworzyć jego stronę, albo
**Anuluj**.

!!! tip "Jeden wpis na rodzaj rzeczy"
    Identyczne rzeczy zapisuj jako jeden przedmiot z ilością, a nie jako
    osobne przedmioty. Wypożyczanie pokazuje wtedy „Dostępne 2 z 3”, a
    zmianę ceny wprowadza się raz.

## Wycofywanie i usuwanie {#retiring-and-deleting}

- **Wycofaj** przedmiot, który naprawdę istniał, a teraz został
  sprzedany, zezłomowany lub zgubiony. Pozostaje w rejestrze z cenami i
  historią wypożyczeń, ale jest ukryty na liście, chyba że zaznaczysz
  **Uwzględnij wycofane przedmioty**. Nie ma przycisku do cofnięcia
  wycofania.
- **Usuń** tylko prawdziwą pomyłkę, np. przedmiot wpisany dwa razy.
  Usuwa przedmiot i wszystkie jego wypożyczenia na zawsze.
<!-- TODO(verify): a retired borrowable item still shows the Check out form and can still be lent; and there is no way in the web UI to un-retire an item. Confirm both are intended. -->

## Kategorie inwentarza {#inventory-categories}

![Kategorie inwentarza](../assets/screenshots/inventory/categories.png)

**Zarządzaj kategoriami** na liście inwentarza otwiera tę stronę.
Wymaga prawa zapisu. **Wstecz** wraca do listy.

| Pole / przycisk | Do czego służy |
|---|---|
| Nazwa (np. „Plac zabaw, Ogrodzenia, Zamki i klucze”) | Nazwa nowej kategorii. Wymagana; nie może jeszcze istnieć („Kategoria o tej nazwie już istnieje.”). |
| **Opcjonalny opis** | Krótki opis. |
| **Dodaj** | Tworzy kategorię. |
| Kolumny **Nazwa**, **Opis** | Istniejące kategorie. |
| Przycisk kosza | Po potwierdzeniu usuwa kategorię. Jej przedmioty **nie** są usuwane -- stają się **Bez kategorii**. Wymaga prawa usuwania. |

Na tej stronie nie można zmieniać nazw kategorii. Aby zmienić nazwę,
utwórz nową kategorię, przenieś do niej przedmioty, edytując je, i usuń
starą.

## Aktywne wypożyczenia {#active-loans}

![Aktywne wypożyczenia](../assets/screenshots/inventory/active-loans.png)

**Aktywne wypożyczenia** na liście inwentarza pokazuje wszystko, co jest
obecnie wypożyczone, ze wszystkich przedmiotów, od najstarszego
wypożyczenia. Użyj tego, aby zobaczyć, kto co ma, przed terminem prac
lub na koniec sezonu.

| Kolumna / przycisk | Co pokazuje |
|---|---|
| **Przedmiot** | Przedmiot, z linkiem do jego strony. |
| **Członek** | Kto go ma. |
| **Ilość** | Ile sztuk. |
| **Od** | Data wypożyczenia. |
| **Opłata** | Naliczona opłata albo „-”. |
| **Oznacz jako zwrócone** | Zapisuje zwrot z dzisiejszą datą i otwiera stronę przedmiotu. Wymaga prawa zapisu. |

Jeśli nic nie jest wypożyczone, strona mówi **Obecnie nic nie jest
wypożyczone.**

!!! tip "Dostępność w kalendarzu"
    Jeśli moduł kalendarza jest włączony, **Kalendarz → Własne kalendarze
    → Zasoby** pokazuje przedmioty stowarzyszenia do wypożyczenia (bez
    wycofanych) z ich statusem -- **Dostępny**, **Wypożyczony** lub
    „Dostępne 1 z 2” -- oraz kto je ma i od kiedy. Wymaga też prawa
    odczytu inwentarza. Zob. [Kalendarz](calendar.md).

## Powiązane {#related}

- [Członkowie](members.md) -- wypożyczający i właściciele przedmiotów
  należących do członków
- [Wnioski zakupowe](purchase-requests.md) -- uzyskanie zgody przed
  zakupem czegoś nowego
- [Grupy](../administration/groups.md) -- nadanie komuś dostępu do
  inwentarza bez pełnych praw zarządu
