# Role, grupy i uprawnienia {#roles-groups-and-permissions}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Nie każdy, kto pomaga prowadzić stowarzyszenie, musi widzieć wszystko.
Osoba odczytująca liczniki wody nie potrzebuje danych bankowych, a
skarbnik nie musi planować prac społecznych. Parcella pozwala dać każdej
osobie dokładnie taki dostęp, jakiego wymaga jej zadanie.

!!! info "Kto może z tego korzystać"
    Ta strona wyjaśnia dostęp dla wszystkich. Tylko **administratorzy**
    mogą zmieniać, kto ma jaki dostęp, w częściach
    [Użytkownicy i zaproszenia](../administration/users.md) oraz
    [Grupy](../administration/groups.md).

## Trzy poziomy dostępu {#the-three-levels-of-access}

Każde konto należy do jednego z trzech poziomów.

| Poziom | Widzi i zmienia | Otwiera obszar **Administracja** | Jak go uzyskać |
|---|---|---|---|
| **Administrator** | Wszystko w każdym włączonym module | Tak | Grupa z **Dostęp do panelu administracyjnego** albo starsza rola **Administrator** |
| **Pełny dostęp** (zwykle zarząd) | Wszystko w każdym włączonym module | Nie | Grupa z **Pełny dostęp do każdego modułu** albo starsza rola **Zarząd** |
| **Ograniczony** | To, na co pozwalają jego grupy, moduł po module; co najmniej odczyt członków i działek | Nie | Członkostwo w jednej lub kilku grupach bez zaznaczonych tych dwóch pól |

Obszar **Administracja** -- użytkownicy, grupy, ustawienia
stowarzyszenia, integracje, kopie zapasowe -- jest celowo oddzielony od
pełnego dostępu. Członkostwo w zarządzie nie czyni automatycznie kogoś
osobą opiekującą się instalacją i odwrotnie. Administratorzy zawsze mają
też pełny dostęp do modułów.

## Grupy {#groups}

**Grupa** to nazwany zestaw uprawnień, np. „Zespół wodny”, „Skarbnik”
albo „Zarząd”. Administratorzy tworzą grupy i dodają do nich konta.
Jedna osoba może należeć do kilku grup.

Grupa nadaje albo:

- **Pełny dostęp do każdego modułu**, albo
- **Dostęp do panelu administracyjnego** (co obejmuje pełny dostęp),
  albo
- **Odczyt**, **Zapis** i **Usuwanie** dla każdego modułu, zaznaczane
  osobno.

### Co oznaczają Odczyt, Zapis i Usuwanie {#what-read-write-and-delete-mean}

| Uprawnienie | Pozwala |
|---|---|
| **Odczyt** | Otworzyć moduł, oglądać jego listy i strony szczegółów oraz pobierać jego eksporty i raporty. Bez tego moduł nie pojawia się na pasku bocznym. |
| **Zapis** | Tworzyć nowe rekordy i zmieniać istniejące -- dodać odczyt licznika, edytować członka, zapisać płatność faktury. |
| **Usuwanie** | Usuwać rekordy, o ile moduł w ogóle pozwala na usuwanie. |

!!! tip "Zaznacz też Odczyt"
    Zapis i Usuwanie działają jako dodatek do Odczytu. Osoba, która nie
    może czytać modułu, nie widzi go na pasku bocznym i nie może otworzyć
    jego stron, więc sam Zapis nic jej nie daje. Każdy rozdział modułu
    mówi, które działania wymagają którego uprawnienia.

### Moduły, które grupa może nadać {#the-modules-a-group-can-grant}

| Moduł w formularzu grupy | Obejmuje |
|---|---|
| **Członkowie i działki** | [Członkowie](../modules/members.md) i [Działki](../modules/parcels.md) |
| **Prace społeczne** | [Prace społeczne](../modules/work-hours.md) |
| **Woda** | Część „woda” w [Wodzie i prądzie](../modules/metering.md) |
| **Prąd** | Część „prąd” w [Wodzie i prądzie](../modules/metering.md) |
| **Ubezpieczenia** | [Ubezpieczenia](../modules/insurance.md) |
| **Wnioski zakupowe** | [Wnioski zakupowe](../modules/purchase-requests.md) |
| **Kalendarz** | [Kalendarz](../modules/calendar.md) |
| **Inwentarz** | [Inwentarz](../modules/inventory.md) |
| **Finanse** | [Finanse](../modules/finances/index.md) |
| **Wsparcie (helpdesk)** | [Wsparcie](../modules/support.md) |
| **Kandydaci** | [Kandydaci](../modules/applicants.md) |
| **Kontakty zewnętrzne** | [Kontakty zewnętrzne](../modules/external-contacts.md) |
| **Raporty** | [Raporty](../modules/reporting.md) |
| **Notatki** | [Notatki](../modules/notes.md) |
| **Procesy** | [Procesy](../modules/processes.md) |

### Kilka grup: wygrywa najszersza {#several-groups-the-most-generous-wins}

Jeśli osoba należy do kilku grup, jej uprawnienia się sumują. Dla
każdego modułu i każdego poziomu wystarczy jedna grupa, która go nadaje.
Przykład: grupa „Zespół wodny” nadaje Wodę z odczytem i zapisem, grupa
„Kalendarz” nadaje odczyt Kalendarza. Ktoś w obu grupach może czytać i
zmieniać dane wody oraz czytać kalendarz.

### Każdy może sprawdzić członków i działki {#everybody-can-look-up-members-and-parcels}

Każde konto, nawet niebędące w żadnej grupie, może **czytać** członków
i działki. Każdy, kto pomaga prowadzić stowarzyszenie, musi wiedzieć,
kto jest kim i która działka jest czyja. Do ich zmiany potrzebny jest
**Zapis** w **Członkowie i działki**.

## Co może tylko pełny dostęp {#things-only-full-access-can-do}

Kilku obszarów nie da się nadać dla pojedynczego modułu. Są zawsze
zarezerwowane dla osób z pełnym dostępem (zarząd, administratorzy lub
grupa z **Pełny dostęp do każdego modułu**):

- [Tablica zadań](../modules/tasks.md),
- [Ogłoszenia](../modules/announcements.md),
- zatwierdzanie lub odrzucanie [wniosku zakupowego](../modules/purchase-requests.md)
  -- oba wymagane zatwierdzenia muszą pochodzić od osób z pełnym
  dostępem,
- tworzenie i edytowanie kalendarzy w **Własne kalendarze** w
  [Kalendarzu](../modules/calendar.md),
- folder w chmurze działki (przeglądanie, przesyłanie, pobieranie) oraz
  pobieranie załącznika faktury przychodzącej,
- tworzenie zadania z rozmowy wsparcia lub łączenie jej z zadaniem.

## Starsze role: Administrator, Zarząd, Skarbnik, Tylko odczyt {#the-older-roles-administrator-board-treasurer-read-only}

Wcześniejsze wersje Parcelli dawały każdemu kontu stałą **rolę**.
Konta utworzone wtedy mogą ją nadal mieć:

| Rola | Działanie dziś |
|---|---|
| **Administrator** | Pełny dostęp oraz obszar administracji, bez potrzeby grupy. Pierwsze konto nowej instalacji ma tę rolę. |
| **Zarząd** | Pełny dostęp, bez potrzeby grupy. |
| **Skarbnik** | Nic poza podstawowym odczytem członków i działek. Więcej nadaje się grupą. |
| **Tylko odczyt (podgląd)** | Tak samo jak Skarbnik: tylko podstawowy dostęp, wszystko inne pochodzi z grup. |

Nowe konta dostają nieaktywną rolę **Tylko odczyt**; ich rzeczywisty
dostęp pochodzi wyłącznie z grup. Administrator może przełączyć konto
Administratora lub Zarządu na grupy przyciskiem **Usuń starą rolę** (zob.
[Użytkownicy i zaproszenia](../administration/users.md)). Najpierw
dodaj konto do właściwej grupy, inaczej spadnie do podstawowego dostępu.

Stopka paska bocznego pokazuje grupy, do których należysz. Bez grupy
pokazuje **Administrator** lub **Zarząd**, jeśli masz tę rolę, w
przeciwnym razie kreskę.

## Zabezpieczenie: ostatni administrator {#safety-net-the-last-administrator}

Parcella odrzuca każdą zmianę, po której **nie zostałoby żadne aktywne
konto mogące otworzyć obszar administracji**. Dostajesz komunikat
**Nie można odebrać uprawnień administratora ostatniemu pozostałemu
kontu Administratora/Zarządu**, gdy próbujesz dezaktywować, usunąć,
zdegradować lub usunąć z grupy ostatnie takie konto albo usunąć lub
odznaczyć ostatnią grupę, która je nadaje. Bez co najmniej jednego
administratora nikt nie mógłby już naprawić problemów z dostępem.

## REST API i tokeny API {#the-rest-api-and-api-tokens}

Programy komunikujące się z Parcellą przez jej interfejs programistyczny
używają [tokenu API](../administration/api-tokens.md). Token osobisty
działa z uprawnieniami konta, do którego należy.
<!-- TODO(verify): several REST API endpoints still check only the old role (Administrator/Board) rather than group permissions, so a group-based full-access account may be refused some API writes. Confirm before stating this to users. -->

## Powiązane {#related}

- [Grupy](../administration/groups.md) -- tworzenie grup i zaznaczanie uprawnień
- [Użytkownicy i zaproszenia](../administration/users.md) -- dodawanie osób do grup
- [Orientacja w aplikacji](navigation.md#why-entries-appear-and-disappear)
