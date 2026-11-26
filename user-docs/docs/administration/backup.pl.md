# Kopia zapasowa i przywracanie {#backup-and-restore}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Kopia zapasowa to pełna kopia danych Twojego stowarzyszenia w Parcelli,
w jednym pliku. Dzięki niej odzyskasz wszystko po awarii serwera,
pomyłce albo przeprowadzce na nowy serwer. Twórz kopie regularnie i
przechowuj je gdzie indziej niż na serwerze Parcelli.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Wszystko zaczyna się w **Administracja →
    System**.

## Co zawiera kopia zapasowa {#what-a-backup-contains}

Jeden plik `.zip` zawierający:

- całą bazę danych -- każdego członka, działkę, odczyt, fakturę,
  ustawienie i konto użytkownika,
- przesłane pliki przechowywane w Parcelli: logo, obrazy ogłoszeń,
  awatary i pliki procesów,
- klucz, którym Parcella szyfruje zapisane hasła (serwer pocztowy,
  strona internetowa, magazyn w chmurze, helpdesk).

!!! warning "Traktuj kopię zapasową jak hasło"
    Ponieważ zawiera ten klucz i wszystkie dane osobowe członków, każdy,
    kto ma plik, może przeczytać wszystko. Przechowuj go tam, gdzie
    dostęp ma tylko zarząd.

Pliki przechowywane w Twoim magazynie w chmurze (foldery działek,
załączniki faktur, pliki notatek) **nie** są częścią kopii zapasowej --
już są w chmurze, która ma własną kopię zapasową.

## Pobieranie kopii zapasowej {#download-a-backup}

W **Administracja → System** karta **Kopia zapasowa** ma przycisk
**Pobierz kopię zapasową**. Przeglądarka od razu pobiera plik zip. Nic
nie jest przechowywane na serwerze, więc ten plik jest jedyną kopią:
zapisz go w bezpiecznym miejscu.

Jeśli coś pójdzie nie tak, zobaczysz **Kopia zapasowa nie powiodła się:**
i przyczynę.

## Przywracanie z kopii zapasowej {#restore-from-backup}

![Przywróć z kopii zapasowej](../assets/screenshots/administration/backup-restore.png)

Otwierasz je przyciskiem **Przywróć z kopii zapasowej** na stronie
System.

!!! danger "To nadpisuje wszystkie obecne dane"
    Przywracanie zastępuje **całą** bazę danych i wszystkie przesłane
    pliki zawartością kopii zapasowej. Wszystko, co wprowadzono od czasu
    tej kopii, znika, łącznie z kontami użytkowników i hasłami
    utworzonymi później. Tego nie można cofnąć. Jeśli możesz chcieć
    wrócić, najpierw **pobierz kopię zapasową obecnego stanu**.

| Pole / przycisk | Do czego służy |
|---|---|
| **Plik kopii zapasowej (.zip)** | Wybierz plik kopii zapasowej pobrany z Parcelli (najwyżej 200 MB). |
| **Wpisz RESTORE, aby potwierdzić** | Wpisz słowo `RESTORE` wielkimi literami. Chroni to przed przypadkowym przywróceniem. |
| **Anuluj** | Powrót do strony System. |
| **Przywróć** | Pyta jeszcze raz, potem przywraca. Może to chwilę potrwać. |

Potem widzisz **Przywracanie zakończone pomyślnie.** Wszyscy -- łącznie
z Tobą -- pracują teraz na danych w stanie z chwili utworzenia kopii;
może być konieczne ponowne zalogowanie hasłem obowiązującym wtedy.

Możliwe komunikaty:

| Komunikat | Znaczenie |
|---|---|
| **Fraza potwierdzająca nie zgadza się -- nic nie zostało zmienione.** | Słowo nie brzmiało dokładnie `RESTORE`. |
| **Plik jest zbyt duży.** | Ponad 200 MB. |
| **Plik kopii zapasowej ma nieoczekiwaną strukturę: ...** | To nie jest kopia zapasowa Parcelli albo plik jest uszkodzony. Nic nie zostało zmienione. |
| **Przywracanie nie powiodło się, nic nie zostało zmienione: ...** | Przywracanie bazy danych się nie udało, a Twoje dane są jak przedtem. |
| **Baza danych została pomyślnie przywrócona, ale przywracanie przesłanych plików nie powiodło się: ...** | Dane są przywrócone, ale część plików nie. Ponowne uruchomienie przywracania jest bezpieczne. |

Kopie zapasowe ze starszej wersji Parcelli można przywrócić do nowszej;
osoba opiekująca się serwerem może potem musieć uruchomić aktualizację
bazy danych.
<!-- TODO(verify): whether the app applies pending database migrations by itself after a restore of an older backup, or whether the server admin must always run them (developer docs say a restore doesn't run them). -->

## Kopie zapasowe w chmurze {#cloud-backups}

![Kopie zapasowe w chmurze](../assets/screenshots/administration/backup-cloud.png)

Otwierasz je przyciskiem **Kopie zapasowe w chmurze** na stronie
System. Parcella może automatycznie tworzyć tę samą kopię zapasową i
przesyłać ją do Twojego magazynu w chmurze.

Wymaga to włączonego modułu **Magazyn w chmurze** i magazynu
skonfigurowanego w [Integracjach](integrations.md#cloud-storage). W
przeciwnym razie strona mówi, czego brakuje, z linkiem.

### Harmonogram {#schedule}

| Pole / przycisk | Do czego służy |
|---|---|
| **Automatycznie twórz kopie zapasowe w chmurze** | Włącza lub wyłącza automatyczne kopie zapasowe. |
| **Folder docelowy** | Folder w magazynie w chmurze, np. `backups/parcella`. Zostanie utworzony, jeśli nie istnieje. Wybierz folder, który może otworzyć tylko zarząd -- każda kopia zawiera klucz do zapisanych haseł. |
| **Częstotliwość** | **Co godzinę**, **Codziennie** (domyślnie), **Co tydzień** lub **Co miesiąc**. |
| **Przechowuj tyle kopii zapasowych** | Ile kopii zachować, co najmniej 1 (domyślnie 10). Po dodaniu nowej najstarsze ponad tę liczbę są usuwane. Dotyczy to tylko własnych plików kopii zapasowych Parcelli. |
| **Zapisz** | Zapisuje harmonogram (**Zapisano.**). |
| **Utwórz kopię zapasową w chmurze teraz** | Od razu tworzy i przesyła kopię zapasową, niezależnie od tego, czy automatyczne kopie są włączone. |

Pod polami widzisz wynik ostatniego uruchomienia: **Ostatnia kopia
zapasowa w chmurze: ... (sukces).**, **... -- nieudana:** z przyczyną
albo **Żadna kopia zapasowa w chmurze jeszcze się nie wykonała.**
Sprawdzaj to od czasu do czasu -- kopia, która po cichu nie działa od
tygodni, nie jest kopią.

### Kopie zapasowe w chmurze {#backups-in-the-cloud}

Lista kopii zapasowych w folderze docelowym, od najnowszych, z
kolumnami **Nazwa**, **Rozmiar** i **Ostatnia modyfikacja**. **W tym
folderze nie ma jeszcze żadnych kopii zapasowych.**, jeśli nie ma
żadnych.

Aby przywrócić jedną z nich, wpisz `RESTORE` w pole w jej wierszu i
kliknij **Przywróć**. Obowiązuje to samo ostrzeżenie co wyżej: nadpisuje
to wszystkie obecne dane.

## Dobre praktyki {#good-practice}

- Pobierz kopię zapasową przed dużymi zmianami: aktualizacją, dużym
  importem, fakturowaniem.
- Trzymaj co najmniej jedną kopię także poza magazynem w chmurze, np.
  na zaszyfrowanym pendrivie w sejfie stowarzyszenia.
- Od czasu do czasu sprawdź kopię, przywracając ją na zapasowej
  instalacji testowej. Kopia, której nigdy nie przywrócono, to tylko
  nadzieja.

## Powiązane {#related}

- [Informacje o systemie i aktualizacje](system.md)
- [Integracje](integrations.md#cloud-storage)
