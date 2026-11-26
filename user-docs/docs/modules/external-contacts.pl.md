# Kontakty zewnętrzne {#external-contacts}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Kontakty zewnętrzne to książka adresowa stowarzyszenia dla wszystkich,
którzy nie są członkami: dostawców, rzemieślników, wodociągów, urzędu
miasta. Kontakt to albo **firma**, albo **osoba**, a osoba może pracować
w firmie. Kontakty możesz łączyć z fakturami przychodzącymi i
wnioskami zakupowymi, oznaczać tagami i przechowywać ich dokumenty w
chmurze stowarzyszenia.

!!! info "Kto może z tego korzystać"
    Członkowie zarządu i administratorzy zawsze mają pełny dostęp.
    Wszyscy pozostali nie widzą niczego z tego modułu, dopóki grupa nie
    nada uprawnień do **Kontakty zewnętrzne** (zob.
    [Grupy](../administration/groups.md)):

    - **Odczyt** -- oglądanie listy i stron kontaktów, eksport CSV,
      strona tagów, pobieranie dokumentów.
    - **Zapis** -- tworzenie i edycja kontaktów, dodawanie numerów
      telefonów, adresów e-mail i tagów, zmiana nazw tagów, import CSV,
      wybór folderu dokumentów kontaktu i przesyłanie dokumentów.
    - **Usuwanie** -- usuwanie kontaktów, numerów telefonów, adresów
      e-mail i tagów oraz łączenie firm.

    Moduł włącza się przełącznikiem **Kontakty zewnętrzne** w
    [Włączaniu i wyłączaniu modułów](../administration/modules.md).
    Domyślnie jest włączony.

## Firmy i osoby {#companies-and-people}

- **Firma** ma nazwę firmy, adres, IBAN oraz własne numery telefonów i
  adresy e-mail.
- **Osoba** ma imię i nazwisko, stanowisko (np. „Urzędnik”,
  „Właściciel”) i opcjonalnie firmę. Jeśli osoba nie ma własnego adresu
  ani IBAN, jej strona pokazuje dane firmy.
- To, czy kontakt jest firmą, czy osobą, ustala się przy tworzeniu i
  nie można tego później zmienić.
- Nazwa firmy może wystąpić tylko raz, tak samo imię i nazwisko osoby
  (wielkość liter nie ma znaczenia). Członkowie się nie liczą -- kontakt
  może mieć to samo imię i nazwisko co członek.
- Każde pole jest opcjonalne. Kontakt bez żadnej nazwy jest pokazywany
  jako **Kontakt bez nazwy**.

## Lista kontaktów {#contact-list}

![Kontakty zewnętrzne](../assets/screenshots/external-contacts/list.png)

**Kontakty zewnętrzne** w nawigacji pokazuje każdą firmę z jej osobami
wciętymi pod nią oraz każdą osobę, która nie należy do firmy. Lista
jest posortowana alfabetycznie według nazwy firmy albo, dla osób bez
firmy, według nazwiska.

| Pole / przycisk | Do czego służy |
|---|---|
| **Import CSV** | Otwiera [okno importu](#csv-import). Wymaga prawa zapisu. |
| **Eksport CSV** | Pobiera listę jako plik CSV (zob. [Eksport CSV](#csv-export)). Uwzględnia bieżące wyszukiwanie i filtr tagów. |
| **Zarządzaj tagami** | Otwiera [stronę tagów](#contact-tags). |
| **Nowy kontakt** | Otwiera [formularz kontaktu](#contact-form). Wymaga prawa zapisu. |
| Pole wyszukiwania | Przeszukuje nazwę firmy, imię i nazwisko, stanowisko, ulicę, kod pocztowy, miejscowość, IBAN, notatki, numery telefonów i adresy e-mail. Kliknij **Szukaj**, aby zastosować. |
| **Wszystkie tagi** / tag | Pokazuje tylko kontakty z tym tagiem. Widoczne, gdy istnieją tagi. |
| **Wyczyść** | Czyści wyszukiwanie i filtr tagów. Widoczny tylko, gdy filtr jest aktywny. |

| Kolumna | Co pokazuje |
|---|---|
| **Nazwa** | Ikona budynku dla firm, ikona osoby dla osób; nazwa prowadzi do strony kontaktu. Osoby pokazują po nazwisku swoje stanowisko. |
| **Tagi** | Tagi kontaktu. Kliknij tag, aby przefiltrować po nim listę. |
| **Telefon** | Pierwszy numer telefonu. |
| **E-mail** | Pierwszy adres e-mail, jako link pocztowy. |
| Przycisk oka | Otwiera kontakt. |

Gdy wyszukiwanie lub tag pasuje do osoby, wymieniana jest też jej
firma, a pasująca osoba jest wyróżniona pod nią. Stopka pokazuje, ile
wpisów (firm i osób bez firmy) jest na liście.

## Formularz kontaktu {#contact-form}

![Nowy kontakt zewnętrzny](../assets/screenshots/external-contacts/form-new.png)

**Nowy kontakt** otwiera pusty formularz, **Edytuj** na stronie kontaktu
formularz wypełniony. **Dodaj osobę** na stronie firmy otwiera go jako
nową osobę z już wpisaną firmą.

Przy nowym kontakcie najpierw wybierz na górze **Firma** lub **Osoba**.
Formularz pokazuje wtedy tylko pola dla tego rodzaju.

### Firma / Osoba {#company-person}

| Pole | Widoczne dla | Do czego służy |
|---|---|---|
| **Imię**, **Nazwisko** | Osoba | Imię i nazwisko osoby. Wystarczy jedna część. |
| **Nazwa firmy** | Firma | Nazwa firmy. |
| **Firma (opcjonalnie)** | Osoba | Firma, w której osoba pracuje. Podczas pisania podpowiada istniejące firmy. Istniejąca firma jest łączona; nowa nazwa tworzy tę firmę. Zostaw puste dla osoby niezwiązanej z firmą. Przy **Edytuj** wyczyszczenie usuwa osobę z firmy. |
| **Stanowisko** | Osoba | Np. „Urzędnik, właściciel”. |
| **E-mail**, **Telefon** | Nowe kontakty | Pierwszy adres e-mail i numer telefonu. Kolejne dodasz później na stronie kontaktu. |

Notka „Wszystkie pola są opcjonalne. Nazwa firmy i imię i nazwisko
osoby mogą wystąpić tylko raz.” przypomina o [zasadach powyżej](#companies-and-people).

### Adres i dane bankowe {#address-bank-details}

| Pole | Do czego służy |
|---|---|
| **Ulica**, **Kod pocztowy**, **Miejscowość** | Adres pocztowy. |
| **IBAN** | Rachunek bankowy, np. do opłacania faktur dostawcy. Do 34 znaków. |

Dla osoby w firmie: „Pozostaw puste, aby użyć danych firmy. Wpisany
razem z nową firmą staje się adresem firmy.” Jeśli firma nie ma jeszcze
adresu ani IBAN, to, co wpiszesz, zostaje zapisane przy firmie; jeśli
jest takie samo jak dane firmy, nie jest zapisywane dwa razy. Przy
osobie zostaje tylko adres lub IBAN, który naprawdę się różni.

### Notatki i tagi {#notes-and-tags}

| Pole | Do czego służy |
|---|---|
| **Notatki** | Dowolny tekst -- godziny otwarcia, numer klienta, numer zgłoszenia. Wyszukiwanie na liście go znajduje. |
| Pola wyboru tagów | Zaznacz istniejące tagi. |
| **Nowe tagi, oddzielone przecinkami** | Wpisz nowe tagi; zostaną utworzone i dodane. |

Kliknij **Utwórz kontakt** (nowy) lub **Zapisz zmiany** (edycja) albo
**Anuluj**. Jeśli firma lub osoba o tej samej nazwie już istnieje,
formularz wraca z komunikatem, np. „Firma … już istnieje.”, i zachowuje
to, co wpisałeś.

## Strona kontaktu {#contact-page}

<!-- TODO(verify): no screenshot -- the sample data contains no external contacts, so the screenshot tool has no contact page to open. Add one once sample data seeds contacts. -->

### Przyciski {#buttons}

| Przycisk | Do czego służy |
|---|---|
| **Edytuj** | Otwiera formularz kontaktu. Wymaga prawa zapisu. |
| **Poprzedni** / **Następny** | Poprzedni lub następny wpis listy, z zachowaniem wyszukiwania i filtra tagów. Klawiatura: ++ctrl+left++ i ++ctrl+right++. |
| **Do listy** | Wraca do listy z tym samym filtrem. |

### Firma / Osoba {#company-person_1}

| Pole | Co pokazuje |
|---|---|
| **Firma** (firma) | Nazwa firmy. |
| **Imię i nazwisko**, **Stanowisko**, **Firma** (osoba) | Imię i nazwisko osoby, stanowisko i link do jej firmy. Usunięta firma jest odpowiednio oznaczona. |
| **Adres** | Adres kontaktu. Dla osoby bez adresu adres firmy, oznaczony **Adres firmy**. |
| **IBAN** | IBAN kontaktu. Dla osoby bez IBAN IBAN firmy, oznaczony **IBAN firmy**. |

### Osoby {#people}

Tylko na stronie firmy: każda osoba w firmie, ze stanowiskiem,
numerami telefonów i adresami e-mail. **Dodaj osobę** tworzy nową osobę
w tej firmie (prawo zapisu). „Brak osób w tej firmie.”, jeśli nie ma
żadnych.

### Tagi {#tags}

Tagi kontaktu; kliknij jeden, aby zobaczyć wszystkie kontakty z nim. Z
prawem zapisu **x** przy tagu usuwa go z tego kontaktu, a pole **Dodaj
tag…** dodaje istniejący lub nowy tag (do 100 znaków). **Zarządzaj
tagami** otwiera [stronę tagów](#contact-tags).

### Numery telefonów i adresy e-mail {#phone-numbers-and-email-addresses}

| Pole / przycisk | Do czego służy |
|---|---|
| Numer / adres | Kliknij, aby zadzwonić lub napisać e-mail. Opis jest pokazywany w nawiasie. |
| Pole numeru / adresu, **Opis (opcjonalnie)**, **+** | Dodaje kolejny numer lub adres, np. z opisem „Biuro” lub „Faktury”. Wymaga prawa zapisu. |
| Przycisk kosza | Usuwa numer lub adres. Wymaga prawa usuwania. |

### Faktury przychodzące i wnioski zakupowe {#incoming-invoices-and-purchase-requests}

Pokazuje [faktury przychodzące](finances/incoming-invoices.md) i
[wnioski zakupowe](purchase-requests.md) powiązane z tym kontaktem --
na stronie firmy także te powiązane z jej osobami, z nazwiskiem osoby po
wpisie. Każda karta jest widoczna tylko, gdy dany moduł jest włączony i
możesz go czytać.

| Karta | Kolumny |
|---|---|
| **Faktury przychodzące** | Data faktury, numer faktury (lub nadawca), kwota całkowita. |
| **Wnioski zakupowe** | Data utworzenia, tytuł, szacowany koszt. |

### Dokumenty {#documents}

Widoczne, gdy moduł magazynu w chmurze jest włączony. Pisma, oferty i
umowy nie są przechowywane w Parcelli, lecz w folderze w chmurze
stowarzyszenia; ta karta pokazuje ten folder.

- Administrator najpierw ustawia folder bazowy w
  [Integracjach](../administration/integrations.md) (**Folder na
  dokumenty kontaktów zewnętrznych**). Do tego czasu karta o tym mówi.
- Folder dla każdego kontaktu tworzy się ręcznie w chmurze, wewnątrz
  folderu bazowego. Na stronie kontaktu ktoś z prawem zapisu wybiera go
  potem z listy **Folder** i klika **Zapisz folder**. **Zmień folder**
  wybiera inny; **— brak folderu —** odłącza go (pliki zostają w
  chmurze).
- Gdy folder jest wybrany, karta pokazuje jego pliki i podfoldery.
  Kliknij podfolder, aby go otworzyć, plik, aby go pobrać. Ścieżka nad
  listą prowadzi z powrotem w górę.
- Z prawem zapisu **Prześlij** umieszcza plik w obecnie pokazywanym
  folderze.
- Usuwanie, zmiana nazw i przenoszenie plików odbywa się w samej
  chmurze.

Dokumenty należą do firmy: strona osoby linkuje zamiast tego do
dokumentów firmy („Dokumenty są przechowywane przy firmie:”).

!!! warning
    Jeśli zmienisz nazwę folderu kontaktu w chmurze, Parcella go gubi.
    Wybierz go ponownie na stronie kontaktu.

### Notatki {#notes}

Notatki, jeśli są.

### Strefa zagrożenia {#danger-zone}

Widoczna z prawem usuwania.

| Pole / przycisk | Do czego służy |
|---|---|
| **Połącz z** + **Połącz** | Tylko na stronie firmy. Dla dwóch wpisów tej samej firmy (np. „Müller GmbH” i „Mueller GmbH”): wybierz firmę, którą chcesz zachować, kliknij **Połącz** i potwierdź. Osoby, numery telefonów, adresy e-mail, tagi oraz powiązane faktury i wnioski zakupowe przechodzą do wybranej firmy. Jej adres, IBAN i folder dokumentów są uzupełniane z tej firmy tam, gdzie ich nie ma; notatki są dopisywane do jej notatek. Ta firma jest potem usuwana, a otwiera się zachowana. |
| **Usuń kontakt** | Po potwierdzeniu usuwa kontakt. Znika z listy i z list wyboru, ale powiązane faktury i wnioski zakupowe nadal go pokazują (oznaczonego jako usunięty tam, gdzie go pokazują). Jego nazwa znów jest wolna. Firmy, która ma jeszcze osoby, nie można usunąć: „Ta firma ma jeszcze osoby. Najpierw je przenieś lub usuń.” |

## Tagi kontaktów {#contact-tags}

![Tagi kontaktów](../assets/screenshots/external-contacts/tags.png)

**Zarządzaj tagami** otwiera **Tagi kontaktów**. Tagi kontaktów są
oddzielone od tagów członków. **Wróć do kontaktów** wraca do listy.

| Pole / przycisk | Do czego służy |
|---|---|
| **Oznacza kandydatów:** | Wybierz jeden tag (lub **— brak —**) i kliknij **Zapisz**. Kandydaci, których imię i nazwisko, adres e-mail lub numer telefonu pasuje do kontaktu z tym tagiem, dostają czerwoną flagę na liście kandydatów i ostrzeżenie na swojej stronie -- przydatne dla tagu „nie wydzierżawiać”. Oznaczona tagiem firma oznacza też swoje osoby. Widoczne tylko, gdy moduł kandydatów jest włączony i istnieją tagi; zmiana wymaga prawa zapisu. Zob. [Kandydaci](applicants.md). |
| Nazwa tagu + przycisk haczyka | Zmienia nazwę tagu we wszystkich kontaktach. Wymaga prawa zapisu. Istniejąca już nazwa jest odrzucana. |
| **Kontakty: {count}** | Otwiera listę przefiltrowaną po tym tagu. |
| Przycisk kosza | Po potwierdzeniu usuwa tag ze wszystkich kontaktów. Wymaga prawa usuwania. |
| **Tłumaczenia** | Otwiera jedno pole na każdy język. Nazwa tagu może być pokazywana w każdym języku inaczej; puste pola pokazują własną nazwę tagu. **Zapisz tłumaczenia** je zapisuje (prawo zapisu). |

Nowe tagi tworzy się przy kontakcie lub w formularzu kontaktu, nie na
tej stronie.

## Eksport CSV {#csv-export}

**Eksport CSV** pobiera `external-contacts.csv`: rozdzielany
średnikami, jeden wiersz na firmę lub osobę, z kolumnami Typ, Firma,
Vorname, Nachname, Position, Strasse, PLZ, Ort, IBAN, E-Mail-Adressen,
Telefonnummern, Tags, Notizen (typ, firma, imię, nazwisko, stanowisko,
ulica, kod pocztowy, miejscowość, IBAN, adresy e-mail, numery telefonów,
tagi, notatki). „Typ” to „Firma” lub „Person”. Najpierw każda firma, a
po niej jej osoby. Kilka adresów e-mail, numerów lub tagów dzieli jedną
komórkę, rozdzielone średnikami.

Plik można zaimportować z powrotem bez zmian.

## Import CSV {#csv-import}

Import ma dwa kroki i wymaga prawa zapisu.

### Krok 1: wybór pliku {#step-1-choose-the-file}

**Import CSV** na liście otwiera **Import kontaktów z CSV**. Wybierz
plik `.csv` (rozdzielany średnikami lub przecinkami, z wierszem
nagłówka) i kliknij **Importuj**. Jeszcze nic nie jest zapisywane.

### Krok 2: import kontaktów {#step-2-import-contacts}

<!-- TODO(verify): no screenshot -- this screen is only reachable by uploading a file, which the screenshot tool can't do from a URL. -->

Karta **Przypisz kolumny** pokazuje każdą kolumnę pliku z nagłówkiem i
pierwszymi pięcioma wierszami. Dla każdej kolumny wybierz pole, do
którego trafia, albo **— pomiń —**:

**Typ (firma/osoba)**, **Nazwa firmy**, **Imię**, **Nazwisko**,
**Stanowisko**, **Ulica**, **Kod pocztowy**, **Miejscowość**, **IBAN**,
**Adresy e-mail**, **Numery telefonów**, **Tagi**, **Notatki**.

Parcella wybiera pole wstępnie dla typowych nagłówków niemieckich i
angielskich i w pełni mapuje swój własny eksport. Żadne pole nie jest
wymagane. Kliknij **Importuj**, aby uruchomić import; **Wstecz**
anuluje.

Jak obsługiwany jest każdy wiersz:

- **Firma czy osoba:** kolumna typu zawiera „Firma”/„Company” lub
  „Person”. Bez niej wiersz z imieniem lub nazwiskiem to osoba, w
  przeciwnym razie firma.
- **Istniejące kontakty są aktualizowane:** firma jest dopasowywana po
  nazwie, osoba po imieniu i nazwisku (wielkość liter nie ma znaczenia).
  Dopasowany kontakt dostaje każde pole wypełnione w pliku; numery
  telefonów, adresy e-mail i tagi, których jeszcze nie ma, są dodawane.
  Nic nigdy nie jest usuwane ani opróżniane.
- **Nowe kontakty** są tworzone dla wierszy bez dopasowania.
- **Firma osoby:** kolumna firmy łączy osobę z firmą o tej nazwie,
  tworzoną w razie potrzeby. Adres i IBAN z wiersza uzupełniają to,
  czego brakuje tej firmie, a przy osobie zostają tylko tam, gdzie się
  różnią.
- Całkowicie puste wiersze są pomijane.

Potem lista pokazuje podsumowanie, np. „Utworzono kontakty: 3,
zaktualizowano: 1.”, oraz pierwsze problemy, jeśli pominięto wiersze
(np. zduplikowana nazwa).

## Gdzie kontakty wybiera się w innych miejscach {#where-contacts-are-picked-elsewhere}

Gdy ten moduł jest włączony i możesz czytać kontakty, inne moduły
oferują wybór kontaktu. Firmy pojawiają się jako grupa z osobami pod
nimi; usunięte kontakty nie są proponowane.

| Gdzie | Etykieta | Do czego służy |
|---|---|---|
| [Faktury przychodzące](finances/incoming-invoices.md) -- nowa faktura | **Kontakt** | Wybór kontaktu wypełnia nadawcę. Nadawca pozostaje polem tekstowym. |
| Strona faktury przychodzącej | **Kontakt** | Późniejsze ustawienie lub zmiana powiązanego kontaktu. |
| [Wnioski zakupowe](purchase-requests.md) -- nowy wniosek i strona wniosku | **Dostawca (kontakt)** | Dostawca dla zakupu. Można go zmienić w każdym statusie. |

## Powiązane {#related}

- [Kandydaci](applicants.md) -- czerwone flagi z oznaczonych kontaktów
- [Integracje](../administration/integrations.md) -- magazyn w chmurze i
  folder bazowy dokumentów
- [Grupy](../administration/groups.md) -- nadanie skarbnikowi dostępu
  do kontaktów
