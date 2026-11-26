# Import członków i działek {#importing-members-and-parcels}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Jeśli Twoje stowarzyszenie prowadzi już listę członków, działek lub
liczników w arkuszu kalkulacyjnym, nie musisz wszystkiego wpisywać od
nowa. Zapisz arkusz jako plik CSV, prześlij go, wskaż Parcelli, która
kolumna jest która, i zaimportuj.

Działa to tak samo dla **działek**, **członków**, **punktów
pomiarowych**, **odczytów liczników** i **kontaktów zewnętrznych**. Ta
instrukcja omawia je w kolejności sensownej dla nowej instalacji.

!!! info "Kto może to zrobić"
    Import członków i działek wymaga uprawnienia do **zapisu** w
    **Członkowie i działki**; punkty pomiarowe i odczyty wymagają zapisu
    w **Woda** lub **Prąd**; kontakty zewnętrzne wymagają zapisu w
    **Kontakty zewnętrzne**. Członkowie zarządu i administratorzy mają
    wszystkie te uprawnienia.

!!! warning "Najpierw pobierz kopię zapasową"
    Import zapisuje wiele rekordów naraz i nie ma „cofnij”. Zanim
    zaczniesz, otwórz **Administracja → Użytkownicy** i kliknij **Pobierz
    kopię zapasową**. Zob. [Kopia zapasowa i
    przywracanie](../administration/backup.md).

## Jak działa każdy import {#how-every-import-works}

Wszystkie pięć importów ma te same dwa kroki.

1. **Prześlij.** Na stronie listy kliknij **Import CSV**, wybierz plik i
   kliknij **Importuj**. Nic nie jest jeszcze zapisywane.
2. **Mapowanie kolumn CSV.** Parcella pokazuje tabelę: jedna kolumna na
   każdą kolumnę Twojego pliku, z Twoim nagłówkiem u góry i pierwszymi
   pięcioma wierszami danych pod spodem. Nad każdą kolumną jest lista
   wyboru. Parcella już odgadła pasujące pole na podstawie nagłówka
   (działają nagłówki angielskie i niemieckie, na przykład „Nachname”
   lub „Last name”). Sprawdź każdą listę, popraw błędne, a kolumny,
   których nie chcesz, ustaw na **— Ignoruj —**. Potem kliknij
   **Importuj**.

Następnie wracasz na stronę listy z krótkim podsumowaniem: ile wierszy
utworzono, zaktualizowano lub pominięto, oraz powody dla pierwszych
kilku pominiętych wierszy.

### Jak powinien wyglądać plik {#what-your-file-should-look-like}

- **Pierwszy wiersz zawiera nagłówki kolumn.** Każdy wiersz poniżej to
  jeden rekord. Nagłówki nie muszą pasować dokładnie -- przypiszesz je
  w kroku 2.
- **Średnik lub przecinek** między kolumnami: Parcella sama wykrywa,
  którego używa plik.
- **Najlepiej UTF-8.** Większość programów arkuszowych oferuje przy
  zapisie „CSV UTF-8”. Zwykły „CSV” z Excela (Windows/ANSI) też
  działa: polskie znaki i inne akcenty przechodzą w obu przypadkach.
- **Daty** jako `2026-03-15` albo `15.03.2026` (także `15.03.26`).
- **Liczby dziesiętne** z przecinkiem lub kropką: działa zarówno
  `312,5`, jak i `312.5`. Kwoty bankowe i stany liczników mogą też
  mieć separatory tysięcy, po niemiecku lub po angielsku: `12.345,6` i
  `12,345.6`.
- **Kilka wartości w jednej komórce** (adresy e-mail, numery telefonów,
  tagi) oddziela się średnikiem. Program arkuszowy przy zapisie
  otoczy taką komórkę cudzysłowem -- to w porządku.

!!! tip "Zacznij od eksportu"
    Najprostszym wzorem jest eksport z samej Parcelli. Każda lista z
    importem ma też **Eksport CSV**. Wyeksportuj (jeszcze pustą lub
    wypełnioną danymi przykładowymi) listę, uzupełnij plik w programie
    arkuszowym i zaimportuj go z powrotem: nagłówki pasują wtedy bez
    żadnego przypisywania.

## 1. Działki {#1-parcels}

Najpierw zaimportuj działki. Członkowie, punkty pomiarowe i odczyty
odwołują się do działek po ich numerze.

1. Otwórz **Działki** i kliknij **Import CSV**.
2. Wybierz plik i kliknij **Importuj**.
3. Na ekranie **Mapowanie kolumn CSV** przypisz co najmniej **Numer
   działki**. Pozostałe pola są opcjonalne.
4. Kliknij **Importuj**. Podsumowanie brzmi np. *„24 zaimportowanych, 0
   pominiętych”*.

| Pole | Czego oczekuje Parcella |
|---|---|
| **Numer działki** | Wymagane. Zapisywane wielkimi literami („g12” staje się „G12”). |
| **Powierzchnia (m²)** | Liczba, z przecinkiem lub kropką jako separatorem dziesiętnym. Cokolwiek innego pozostaje puste. |
| **Szerokość geograficzna** / **Długość geograficzna** | Opcjonalna pozycja GPS, w stopniach dziesiętnych (np. `51,339695`). |
| **Status** | `ACTIVE`, `TERMINATED`, `COMMUNAL` lub `DELETED` (wielkimi lub małymi literami). Puste lub cokolwiek innego oznacza aktywna. |
| **Notatki** | Dowolny tekst. |

!!! warning "Istniejące działki są pomijane, a nie aktualizowane"
    Jeśli numer działki już istnieje w Parcelli, ten wiersz jest
    **pomijany**, a istniejąca działka pozostaje dokładnie taka, jaka
    jest. Aby zmienić istniejące działki, edytuj je ręcznie. Wiersze bez
    numeru działki są ignorowane i liczone osobno w podsumowaniu.

Import działek **nie** przypisuje dzierżawców. Eksport działek ma
kolumnę z imionami i nazwiskami dzierżawców, ale import ją ignoruje --
zob. krok 3 poniżej.

## 2. Członkowie {#2-members}

1. Otwórz **Członkowie** i kliknij **Import CSV**.
2. Wybierz plik i kliknij **Importuj**.
3. Na ekranie **Mapowanie kolumn CSV** przypisz co najmniej **Imię** i
   **Nazwisko**. Bez obu import zatrzymuje się z komunikatem *„Przed
   importem przypisz kolumny imienia i nazwiska.”*
4. Kliknij **Importuj**. Podsumowanie brzmi np. *„80 nowo
   zaimportowanych, 0 zaktualizowanych”*.

| Pole | Czego oczekuje Parcella |
|---|---|
| **Imię**, **Nazwisko** | Wymagane. Wiersz z jednym z nich pustym jest pomijany. |
| **Ulica**, **Kod pocztowy**, **Miejscowość** | Dowolny tekst. |
| **Data urodzenia** | Data (zob. wyżej). Służy też do rozróżnienia dwóch członków o tym samym imieniu i nazwisku. |
| **IBAN** | Dowolny tekst, niesprawdzany. |
| **Członek od**, **Członek do** | Daty. Puste **Członek do** oznacza aktywnego członka. |
| **Powiadomienia e-mail** | „No”, „Nein”, „false” lub „0” oznacza, że członek **nie** chce informacji od stowarzyszenia e-mailem; cokolwiek innego wypełnionego oznacza tak. Pusta komórka lub nieprzypisana kolumna oznacza tak dla nowego członka i „bez zmian” dla istniejącego. |
| **Adresy e-mail** | Jeden lub więcej, oddzielone średnikami. Pierwszy staje się adresem głównym. |
| **Numery telefonów** | Jeden lub więcej, oddzielone średnikami. Pierwszy staje się numerem głównym. |
| **Notatki** | Dowolny tekst. |

**Dopasowanie istniejących członków.** Dla każdego wiersza Parcella
szuka istniejącego członka o tym samym imieniu i nazwisku -- a jeśli
wiersz ma datę urodzenia, także o tej samej dacie urodzenia. Jeśli
znajdzie dokładnie jednego, **aktualizuje** tego członka zamiast
tworzyć drugiego. Jeśli kilku członków ma to imię i nazwisko, właściwego
wskazują adresy e-mail i numery telefonów z wiersza; jeśli wiersz
nadal pasuje do więcej niż jednego, jest pomijany i wymieniony w
podsumowaniu. Sam e-mail lub telefon nigdy nie dopasowuje członka o
innym imieniu i nazwisku.

Aktualizacja zmienia tylko to, co zawiera wiersz: kolumna ustawiona na
**— Ignoruj —** albo pusta komórka zostawia zapisaną wartość bez
zmian. Możesz więc zaktualizować same adresy plikiem, który zawiera
tylko imiona, nazwiska i adresy. Adresy e-mail i numery telefonów nigdy
nie są zmieniane przy aktualizacji; są dodawane tylko dla nowych
członków.

Tagi, przypisania działek i ustawienie **Nie chce prezentów
urodzinowych** nie są częścią importu. Eksport zawiera kolumny
**Działki** i **Tagi**, ale import je ignoruje.

## 3. Przypisz członków do ich działek {#3-assign-members-to-their-parcels}

Nie ma importu dzierżaw. Gdy członkowie i działki już istnieją,
przypisz je ręcznie:

1. Otwórz działkę w **Działki**.
2. W **Obecni dzierżawcy** zacznij wpisywać imię i nazwisko członka w
   **Wybierz członka…** i wybierz go z listy.
3. Opcjonalnie wpisz datę rozpoczęcia dzierżawy.
4. Zostaw zaznaczone **Użyj jako adresu do faktury** u dzierżawcy, który
   ma dostawać faktury za działkę.
5. Kliknij **Przypisz**.

Przy wielu działkach przycisk **Następny** u góry strony działki
prowadzi prosto do następnej.

Więcej: [Działki](../modules/parcels.md).

## 4. Punkty pomiarowe {#4-metering-points}

Punkty pomiarowe to przyłącza wody i prądu (licznik główny, po jednym
na działkę, przyłącza stowarzyszenia). Wodę i prąd importuje się
osobno, każde we własnym menu.

1. Otwórz **Woda → Punkty pomiarowe** (albo **Prąd → Punkty
   pomiarowe**) i kliknij **Import CSV**.
2. Wybierz plik i kliknij **Importuj**.
3. Przypisz kolumny i kliknij **Importuj**. Co najmniej jedna kolumna
   musi być przypisana.

| Pole | Czego oczekuje Parcella |
|---|---|
| **Typ** | `PARCEL`, `MAIN_METER` lub `CLUB`. Jeśli w ogóle nie przypiszesz tej kolumny, każdy wiersz liczy się jako przyłącze działki. Jeśli ją przypiszesz, wiersz z pustym lub nieznanym typem jest pomijany („nieprawidłowy typ”). |
| **Numer działki** | Wymagane dla przyłączy działek; musi pasować do istniejącego numeru działki, w przeciwnym razie wiersz jest pomijany („nie znaleziono działki”). |
| **Oznaczenie** | Nazwa licznika głównego lub przyłącza stowarzyszenia, np. „Świetlica”. |
| **Numer licznika** | Numer wydrukowany na liczniku. |
| **Data montażu** | Data. |
| **Legalizacja do** | Tylko **rok**, np. `2031`. |
| **Stan początkowy** | Stan przy montażu licznika. Puste oznacza 0. |
| **Mnożnik** | Zwykle puste (= 1). Dla liczników, które pokazują tylko część rzeczywistej wartości, np. `20`. Musi być większy od 0. |

Import tylko **tworzy** punkty pomiarowe. Działka, która ma już punkt
pomiarowy dla tego medium, albo licznik główny lub przyłącze
stowarzyszenia o tym samym oznaczeniu, jest pomijana jako „już
istnieje” -- więc dwukrotny import tego samego eksportu nie szkodzi.
Nowe punkty pomiarowe zawsze zaczynają jako włączone.

!!! note
    **Legalizacja do** to rok. Data w tej kolumnie (`30.06.2027`,
    `2027-06`, `06/2027`) też jest w porządku: Parcella bierze z niej
    rok. Wiersz, którego wartość nie zawiera czterocyfrowego roku
    (`06/27`, `wkrótce`), jest pomijany z komunikatem „„Legalizacja do”
    nie jest rokiem”; pozostałe wiersze są importowane.

Więcej: [Woda i prąd](../modules/metering.md).

## 5. Odczyty liczników {#5-meter-readings}

Odczyty są dołączane do już istniejących punktów pomiarowych; import
nigdy nie tworzy punktu pomiarowego.

1. Otwórz **Woda → Odczyty** (albo **Prąd → Odczyty**) i kliknij
   **Import CSV**.
2. Wybierz plik i kliknij **Importuj**.
3. Przypisz kolumny. Jeśli plik nie ma kolumny z rokiem albo niektóre
   wiersze zostawiają ją pustą, wpisz rok w **Rok domyślny
   (opcjonalnie)**.
4. Kliknij **Importuj**.

| Pole | Czego oczekuje Parcella |
|---|---|
| **Typ** | Jak przy punktach pomiarowych. Nieprzypisane = każdy wiersz to przyłącze działki. |
| **Numer działki** / **Oznaczenie** | Wskazują punkt pomiarowy, tak samo jak wyżej. |
| **Numer licznika** | Opcjonalna kontrola. Jeśli nie zgadza się z obecnie zainstalowanym licznikiem, wiersz jest pomijany („niezgodny numer licznika”) -- prawdopodobnie należy do licznika, który został już wymieniony. |
| **Rok** | Rok, do którego należy odczyt. Ma pierwszeństwo przed **Rok domyślny (opcjonalnie)**. |
| **Data** | Dzień odczytu licznika. Wymagane. |
| **Odczyt** | Wartość z wyświetlacza. Wymagane. |
| **Notatka** | Dowolny tekst. |

Parcella nigdy nie zgaduje roku na podstawie daty. Odczyt wykonany w
styczniu może nadal należeć do rozliczenia poprzedniego roku, więc to
Ty określasz, który to rok.

Jeden plik może zawierać kilka lat. Jeśli punkt pomiarowy ma już odczyt
za dany rok, import go **zastępuje**.

Odczyt, który wygląda nieprawdopodobnie -- na przykład niższy niż
poprzedni -- jest mimo to zapisywany. Podsumowanie pokazuje wtedy
osobne ostrzeżenie z danymi wierszami, abyś mógł je sprawdzić.

Więcej: [Zbieranie odczytów liczników](meter-readings.md).

## 6. Kontakty zewnętrzne {#6-external-contacts}

Dostawcy, rzemieślnicy i urzędy, jeśli korzystasz z modułu **Kontakty
zewnętrzne**.

1. Otwórz **Kontakty zewnętrzne** i kliknij **Import CSV**.
2. Wybierz plik i kliknij **Importuj**.
3. Na ekranie **Przypisz kolumny** przypisz kolumny. Żadne pole nie jest
   wymagane; całkowicie puste wiersze są pomijane.
4. Kliknij **Importuj**.

| Pole | Czego oczekuje Parcella |
|---|---|
| **Typ (firma/osoba)** | „Firma”, „Company” lub „Unternehmen” dla firmy; „Person” dla osoby. Bez tego wiersz z imieniem lub nazwiskiem jest osobą, w przeciwnym razie firmą. |
| **Nazwa firmy** | Dla firmy: jej nazwa. Dla osoby: firma, do której należy -- tworzona, jeśli jeszcze nie istnieje. |
| **Imię**, **Nazwisko**, **Stanowisko** | Dla osób. |
| **Ulica**, **Kod pocztowy**, **Miejscowość**, **IBAN** | Adres i dane bankowe. U osoby w firmie uzupełniają puste pola firmy. |
| **Adresy e-mail**, **Numery telefonów**, **Tagi** | Kilka wartości oddzielonych średnikami. |
| **Notatki** | Dowolny tekst. |

Firma, która już istnieje (ta sama nazwa, bez względu na wielkość
liter), albo osoba o tym samym imieniu i nazwisku jest **aktualizowana**
z niepustych komórek wiersza. Brakujące numery telefonów, e-maile i tagi
są dodawane. Inaczej niż przy imporcie członków nic nigdy nie jest
czyszczone ani usuwane.

Więcej: [Kontakty zewnętrzne](../modules/external-contacts.md).

## Częste problemy {#common-problems}

| Co widzisz | Dlaczego i co zrobić |
|---|---|
| *„Ten plik CSV wydaje się być pusty.”* | Plik nie ma żadnych wierszy. Sprawdź, czy zapisałeś właściwy arkusz. |
| Wszystkie dane trafiają do jednej kolumny na ekranie przypisywania | Parcella nie rozpoznała separatora. Zapisz plik ponownie jako „CSV (rozdzielany średnikami)” lub „CSV (rozdzielany przecinkami)”. |
| Dziwne znaki zamiast polskich liter | Plik używa nietypowego kodowania (ani UTF-8, ani Windows/ANSI, np. ze starego Maca). Zapisz go ponownie jako „CSV UTF-8”. |
| Członkowie pominięci z komunikatem „brak imienia lub nazwiska” | Te wiersze mają pustą komórkę z imieniem lub nazwiskiem albo kolumna nie została przypisana. |
| Członek pojawia się dwa razy | Dwa wiersze różnią się pisownią lub datą urodzenia, więc Parcella traktuje je jak różne osoby. Usuń duplikat ręcznie. |
| Adres istniejącego członka nagle pusty | Członek został zaktualizowany z wiersza lub pliku bez tej kolumny. Zob. ostrzeżenie w kroku 2; w razie potrzeby przywróć dane z kopii zapasowej. |
| Działki „pominięte” | Numer działki już istnieje. Edytuj istniejące działki ręcznie. |
| Punkty pomiarowe „nie znaleziono działki” | Numer działki z pliku nie istnieje w Parcelli -- najpierw zaimportuj działki i sprawdź pisownię („G12” a „G 12”). |
| Odczyty „nie znaleziono punktu pomiarowego” | Najpierw zaimportuj lub utwórz punkty pomiarowe. Jeśli przypisałeś **Typ**, sprawdź jego wartość. |
| Odczyty „nieprawidłowy wiersz” | **Data** lub **Odczyt** jest puste lub niezrozumiałe albo brakuje roku (ani kolumny **Rok**, ani **Rok domyślny (opcjonalnie)**). |
| Odczyty „brak aktywnego licznika” | Na punkcie pomiarowym nie ma zainstalowanego licznika. Dodaj go na stronie punktu pomiarowego. |
| `'` na początku wyeksportowanych numerów telefonów | Parcella dodaje go do komórek zaczynających się od `+`, `-`, `=` lub `@`, aby programy arkuszowe nie traktowały ich jak formuł. Usuń go przed importem członków albo zostaw -- import kontaktów zewnętrznych usuwa go za Ciebie. |

## Powiązane {#related}

- [Członkowie](../modules/members.md)
- [Działki](../modules/parcels.md)
- [Woda i prąd](../modules/metering.md)
- [Kontakty zewnętrzne](../modules/external-contacts.md)
- [Konfiguracja nowego stowarzyszenia](new-club-setup.md)
- [Zbieranie odczytów liczników](meter-readings.md)
