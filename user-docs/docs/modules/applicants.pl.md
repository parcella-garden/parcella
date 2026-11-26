# Kandydaci {#applicants}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Lista kandydatów to lista oczekujących Twojego stowarzyszenia na wolne
działki ogrodowe. Zgłoszenia z formularza na Twojej stronie trafiają tu
same; możesz też wpisać zgłoszenia, które przyszły telefonicznie lub na
papierze. Śledzisz, z kim się skontaktowałeś i komu zaproponowałeś
działkę, a gdy działka się zwolni, przekazujesz ją -- kandydat staje się
członkiem i nowym dzierżawcą w jednym kroku.

Kandydaci są celowo oddzieleni od listy członków. Większość kandydatów
nigdy nie dostaje działki, więc ich dane nie mogą trafić do liczby
członków, faktur, prac społecznych ani korespondencji.

!!! info "Kto może z tego korzystać"
    Moduł **Kandydaci** jest domyślnie włączony. Można go wyłączyć w
    [Włączaniu i wyłączaniu modułów](../administration/modules.md).

    - **Oglądanie** listy i zgłoszeń wymaga prawa *odczytu* w
      **Kandydaci**.
    - **Dodawanie** kandydata, **edycja** danych kontaktowych, statusu i
      notatki zarządu oraz **kontakt** z nowym kandydatem wymaga prawa
      *zapisu*.
    - **Trwałe usunięcie** kandydata wymaga prawa *usuwania*.
    - **Przydziel działkę** wymaga prawa *zapisu* zarówno w
      **Kandydaci**, jak i w **Członkowie i działki**.

    Członkowie zarządu i administratorzy mają wszystkie te prawa. Grupa
    może nadać je innym, np. osobie zajmującej się przydziałem działek
    (zob. [Grupy](../administration/groups.md)).

    Zgłoszenia z Twojej strony internetowej trafiają tu tylko wtedy, gdy
    włączony jest osobny moduł **Publiczne API formularza zgłoszeń**.
    Domyślnie jest wyłączony, bo pozwala osobom spoza stowarzyszenia
    zapisywać dane w Parcelli. Zob.
    [Zgłoszenia z Twojej strony internetowej](#applications-from-your-website).

## Gdzie zauważysz nowe zgłoszenia {#where-you-notice-new-applications}

- Pozycja **Kandydaci** w menu głównym pokazuje czerwoną liczbę:
  zgłoszenia, których nikt jeszcze nie przejrzał (status **Nowe**).
  Znika, gdy każde nowe zgłoszenie zostanie przeniesione do innego
  statusu.
- [Panel główny](../getting-started/dashboard.md) ma kartę **Nowe
  zgłoszenia** z tą samą liczbą, „jeszcze nierozpatrzone”. Otwiera
  listę przefiltrowaną do nowych zgłoszeń.

Parcella nie wysyła zarządowi e-maila o nowym zgłoszeniu -- sygnałem
jest liczba w menu i na panelu.

## Statusy {#statuses}

Każde zgłoszenie przechodzi przez te statusy. Ustawiasz je na
[stronie zgłoszenia](#application-page); tylko **Zamknięte (działka
przydzielona)** ustawia sama Parcella.

| Status | Znaczenie |
|---|---|
| **Nowe** | Właśnie przyszło; nikt go jeszcze nie przejrzał. |
| **Skontaktowano** | Zarząd się odezwał -- np. wysłał pierwszy e-mail. Kandydat jest na liście oczekujących. |
| **Działka zaproponowana** | Zaproponowano działkę. |
| **Przyjęte** | Kandydat chce zaproponowanej działki; przekazanie jest jeszcze organizowane. |
| **Odrzucone** | Stowarzyszenie odmówiło albo kandydat nie chce dalszych propozycji. |
| **Zamknięte (działka przydzielona)** | Kandydat dostał działkę przez **Przydziel działkę**. |

**Nowe**, **Skontaktowano**, **Działka zaproponowana** i **Przyjęte**
liczą się jako *otwarte*. Jeśli kandydat odrzuci propozycję, ale chce
zostać na liście oczekujących, ustaw go z powrotem na **Skontaktowano**.
Jeśli nie chce dalszych propozycji, ustaw **Odrzucone**.

## Lista kandydatów {#applicant-list}

![Lista kandydatów](../assets/screenshots/applicants/list.png)

Otwórz **Kandydaci** w menu głównym. Lista pokazuje zgłoszenia, od
najnowszej daty zgłoszenia.

### Filtr i wyszukiwanie {#filter-and-search}

| Pole / przycisk | Do czego służy |
|---|---|
| **Nowe** | Tylko zgłoszenia ze statusem **Nowe**. Widoczne tylko, gdy są nowe zgłoszenia -- i wtedy lista otwiera się z tym filtrem. |
| **Otwarte** | Zgłoszenia, które są **Nowe**, **Skontaktowano**, **Działka zaproponowana** lub **Przyjęte**. Lista otwiera się z tym filtrem, gdy nie ma nowych zgłoszeń. |
| **Zamknięte** | Zgłoszenia, które są **Zamknięte (działka przydzielona)** lub **Odrzucone**. |
| **Wszystkie** | Każde zgłoszenie. |
| **Imię i nazwisko, e-mail, telefon, wiadomość, notatki…** | Przeszukuje imię i nazwisko, adres e-mail, numer telefonu, wiadomość kandydata i notatkę zarządu. Łączy się z przyciskami filtrów. Ponieważ przeszukiwana jest notatka zarządu, numer zgłoszenia zapisany tam znajduje kandydata. |
| **Szukaj** | Stosuje wyszukiwanie. |
| **Wyczyść** | Czyści wyszukiwanie, zachowuje przycisk filtra. |

### Kolumny {#columns}

| Kolumna | Co pokazuje |
|---|---|
| Pole wyboru | Wybiera kandydata do **Napisz do zaznaczonych kandydatów** (zob. niżej). |
| **Imię i nazwisko** | Imię i nazwisko albo adres e-mail, jeśli nie podano nazwiska. Kliknij, aby otworzyć zgłoszenie. |
| **E-mail** | Kliknij, aby napisać z własnego programu pocztowego. |
| **Telefon** | |
| **Data zgłoszenia** | Data zgłoszenia. Decyduje o kolejności na liście oczekujących. |
| **Status** | Zob. [Statusy](#statuses). |
| Przycisk oka | Otwiera zgłoszenie. |

Obok nazwiska mogą pojawić się dwa rodzaje oznaczeń:

- **2×**, **3×** … -- z tego adresu e-mail zgłoszono się więcej niż raz.
  Parcella nie łączy powtórzonych zgłoszeń; każde zostaje osobnym
  wpisem, aby żadna wiadomość nie zginęła. Ty decydujesz, co z nimi
  zrobić. Strona zgłoszenia wymienia pozostałe.
- **Czerwona flaga** -- imię i nazwisko, adres e-mail lub numer telefonu
  kandydata pasuje do [kontaktu zewnętrznego](external-contacts.md) z
  tagiem czerwonej flagi Twojego stowarzyszenia. Najedź na oznaczenie,
  aby zobaczyć, który kontakt i które dane pasują. Przy wyłączonym
  module Kontakty zewnętrzne nie ma czerwonych flag.

### Pisanie do wybranych kandydatów {#writing-to-selected-applicants}

Gdy moduł **Ogłoszenia** jest włączony, członkowie zarządu i
administratorzy widzą pole wyboru w każdym wierszu.

| Przycisk | Do czego służy |
|---|---|
| **Zaznacz wszystkich** | Zaznacza każdego kandydata, którego pokazuje bieżący filtr i wyszukiwanie. |
| **Odznacz wszystkich** | Czyści wszystkie zaznaczenia. |
| **Zaznaczono: *N*** | Liczy zaznaczonych kandydatów. |
| **Napisz do zaznaczonych kandydatów** | Rozpoczyna nowe [ogłoszenie](announcements.md) do zaznaczonych kandydatów. Wychodzi tylko e-mailem, raz na adres -- ktoś, kto zgłosił się dwa razy, dostaje jeden e-mail. Nieaktywny, dopóki nikogo nie zaznaczysz. |

### Ręczne dodanie kandydata {#adding-an-applicant-by-hand}

**Nowy kandydat** (u góry po prawej, wymaga prawa zapisu) otwiera
formularz [Nowy kandydat](#new-applicant).

## Nowy kandydat {#new-applicant}

![Formularz nowego kandydata](../assets/screenshots/applicants/form-new.png)

Dla zgłoszeń, które nie przyszły przez stronę internetową --
telefonicznie, listownie albo ze starej papierowej listy oczekujących.
Zgłoszenia z formularza na stronie pojawiają się na liście same.

| Pole | Do czego służy |
|---|---|
| **Adres e-mail** \* | Wymagany -- jedyne wymagane pole. Musi być prawidłowym adresem e-mail, inaczej „Podaj prawidłowy adres e-mail.” |
| **Imię** / **Nazwisko** | Tutaj opcjonalne, ale potrzebne, zanim będzie można przydzielić działkę. |
| **Telefon** | |
| **Data zgłoszenia** | Data zgłoszenia. „Pozostaw puste, aby użyć dzisiejszej daty. Zmień ją, aby wprowadzić starsze zgłoszenie, np. z papierowej listy oczekujących -- decyduje o kolejności.” Data w przyszłości jest odrzucana. |
| **Wiadomość kandydata** | Co kandydat napisał lub Ci powiedział. |
| **Notatka zarządu** | „Wewnętrzna -- nigdy nie jest pokazywana kandydatowi.” |

Kliknij **Zapisz**. Zgłoszenie zaczyna ze statusem **Nowe**, jego
źródło to **Wprowadzone ręcznie** (z Twoim nazwiskiem) i nie ma daty
zgody na przetwarzanie danych -- jest ona zapisywana tylko dla zgłoszeń
ze strony internetowej. **Wstecz** wraca do listy bez zapisywania.

## Strona zgłoszenia {#application-page}

![Strona zgłoszenia](../assets/screenshots/applicants/detail.png)

Kliknij kandydata na liście, aby otworzyć jego zgłoszenie.

Jeśli kandydat pasuje do kontaktu zewnętrznego z czerwoną flagą,
czerwone pole **Czerwona flaga** na górze wymienia kontakt i pasujące
dane (imię i nazwisko, e-mail, telefon). Użytkownicy, którzy mogą
widzieć kontakty zewnętrzne, mogą przejść do kontaktu.

### Zgłoszenie {#application}

Lewa karta zawiera wszystko, co możesz edytować.

| Pole | Do czego służy |
|---|---|
| **Status** | Zob. [Statusy](#statuses). Każda zmiana jest zapisywana w **Historia statusu**. |
| **Adres e-mail** \*, **Imię**, **Nazwisko**, **Telefon** | Dane kontaktowe kandydata. |
| **Data zgłoszenia** | Data zgłoszenia. Zmień ją, aby przesunąć zgłoszenie na właściwe miejsce w kolejce, np. gdy wpisujesz stare zgłoszenie papierowe. Zmiana jest zapisywana w historii statusu, bo przesuwa kandydata w górę lub w dół. Daty w przyszłości są odrzucane. |
| **Wiadomość kandydata** | Tekst, który przysłał kandydat. |
| **Notatka zarządu** | Notatki wewnętrzne, nigdy niepokazywane kandydatowi -- np. „telefon 3 maja, woli małą działkę”. |

Kliknij **Zapisz**, aby zapisać zmiany. Bez prawa zapisu widzisz dane,
ale nie możesz zapisać. Zmiany danych kontaktowych i notatki zarządu
nie są zapisywane w historii.

### Przyciski na górze {#buttons-at-the-top}

| Przycisk | Do czego służy |
|---|---|
| **Wstecz** | Wraca do listy kandydatów. |
| **Usuń** | Po potwierdzeniu „Trwale usunąć tego kandydata? Tego nie można cofnąć.” usuwa zgłoszenie na zawsze. Jego historia statusu znika razem z nim. Wymaga prawa usuwania. |

!!! info "Dlaczego kandydatów można trwale usuwać"
    Prawie wszystko inne w Parcelli zachowuje swoją historię. Kandydaci
    są wyjątkiem: ich dane są przechowywane tylko na potrzeby
    zgłoszenia, więc musisz móc je całkowicie usunąć -- gdy ktoś o to
    poprosi albo gdy zgłoszenie się zakończy. Twoje stowarzyszenie może
    też automatycznie usuwać stare zgłoszenia; zob.
    [Automatyczne usuwanie](#automatic-deletion).

### Kontakt z kandydatem {#contact-applicant}

Widoczne tylko przy zgłoszeniu **Nowe**, dla użytkowników z prawem
zapisu. To pierwszy krok procesu: e-mail z podziękowaniem, który
potwierdza, że kandydat jest na liście oczekujących.

| Pole / przycisk | Do czego służy |
|---|---|
| **Do:** | Adres e-mail kandydata. |
| **Temat:** | „Dziękujemy za zapisanie się na naszą listę oczekujących!” (w języku, w którym używasz Parcelli). |
| Wiadomość | Tekst e-maila, gotowy do edycji. Imię kandydata i nazwa stowarzyszenia są już wpisane. |
| **Wyślij** | Po potwierdzeniu wysyła tekst kandydatowi e-mailem i ustawia status na **Skontaktowano**. |

Po wysłaniu zielona notka mówi „E-mail został wysłany, a status
ustawiony na „Skontaktowano”.” Pole wtedy znika, bo zgłoszenie nie jest
już nowe.

Jeśli e-maila nie da się wysłać, nic się nie zmienia: status zostaje
**Nowe**, Twój edytowany tekst zostaje w polu, a Ty widzisz „Nie udało
się wysłać e-maila – proszę sprawdzić ustawienia SMTP. Status nie został
zmieniony.” Popraw ustawienia poczty i spróbuj ponownie.

Tekst początkowy pochodzi z **Treść e-maila do nowych kandydatów** w
[Ustawieniach stowarzyszenia](../administration/settings.md) →
**Kandydaci**. Jeśli jest pusty, Parcella używa wbudowanego tekstu w
języku, w którym używasz Parcelli. Kandydaci nie mają własnego
ustawienia języka, więc jeśli stowarzyszenie pisze własny tekst, napisz
go w języku, którym mówią Twoi kandydaci.

!!! note
    Parcella nie zachowuje kopii e-maila. Tylko zmiana statusu na
    **Skontaktowano** pokazuje, że wyszedł.

### Przydziel działkę {#assign-a-parcel}

Widoczne tylko przy otwartym zgłoszeniu, dla użytkowników z prawem
zapisu zarówno w **Kandydaci**, jak i w **Członkowie i działki**.
**Przydziel działkę** przekazuje kandydatowi wypowiedzianą działkę --
zob. [Przydziel działkę](#assign-a-parcel_1) niżej.

### Szczegóły {#details}

| Wiersz | Co pokazuje |
|---|---|
| **Data zgłoszenia** | Data zgłoszenia. |
| **Źródło** | **Formularz na stronie** albo **Wprowadzone ręcznie** z nazwiskiem użytkownika, który je wpisał. |
| **Zgoda na przetwarzanie danych (kandydat)** | Kiedy kandydat zaznaczył pole ochrony danych w formularzu na stronie. Puste dla zgłoszeń wprowadzonych ręcznie. To zgoda kandydata -- nie zatwierdzenie przez zarząd. |
| **Zmiana statusu** | Kiedy status ostatnio się zmienił. |

Wszystkie daty są pokazywane bez godziny.

### Inne zgłoszenia z tego adresu {#other-applications-from-this-address}

Widoczne tylko, jeśli z tego samego adresu e-mail zgłoszono się więcej
niż raz. Wymienia pozostałe zgłoszenia z datą i statusem; kliknij datę,
aby je otworzyć.

### Procesy {#processes}

Jeśli moduł [Procesy](processes.md) jest włączony i możesz widzieć
procesy, karta **Procesy** pokazuje procesy dotyczące tego kandydata.
**Rozpocznij proces** uruchamia nowy.

### Historia statusu {#status-history}

Każda zmiana statusu i każda zmiana daty zgłoszenia, z datą, godziną i
użytkownikiem, który ją wprowadził -- od najnowszych. Zmiany dokonane
przez samą Parcellę (przekazanie) też się tu pojawiają.

## Przydziel działkę {#assign-a-parcel_1}

![Przydziel działkę](../assets/screenshots/applicants/assign-parcel.png)

Gdy działka się zwolni, ta strona przekazuje ją jednemu lub kilku
kandydatom w jednym kroku. Otwierasz ją przyciskiem **Przydziel
działkę** przy zgłoszeniu.

!!! info "Zanim zaczniesz"
    - Działka musi mieć status **wypowiedziana**. Najpierw ustaw go w
      [formularzu działki](parcels.md#new-parcel-and-edit-parcel). Jeśli
      żadna działka nie jest wypowiedziana, strona to mówi.
    - Każdy kandydat, który przejmuje działkę, potrzebuje w zgłoszeniu
      imienia i nazwiska.

### Krok 1: działka i data przekazania {#step-1-parcel-and-handover-date}

| Pole | Do czego służy |
|---|---|
| **Wypowiedziana działka** | Działka do przekazania. Proponowane są tylko wypowiedziane działki, każda z nazwiskami obecnych dzierżawców. |
| **Data przekazania** | Dzień, w którym nowi dzierżawcy przejmują działkę. Domyślnie dziś. Może leżeć w przyszłości: dotychczasowi dzierżawcy pozostają wtedy dzierżawcami, członkami i odbiorcami faktur do tego dnia, a nowi dzierżawcy są pokazywani na stronie działki jako przyszli. |
| **Kolejni kandydaci (współdzierżawcy)** | Opcjonalne: inni otwarci kandydaci, którzy przejmują działkę razem z tym, np. para, która zgłosiła się osobno. |
| **Folder dokumentów dla nowych dzierżawców** | Tylko dla członków zarządu i administratorów, gdy moduł **Magazyn w chmurze** jest włączony. Folder, który w dniu przekazania staje się folderem dokumentów działki. **Przeglądaj chmurę** pozwala przeklikać się przez magazyn i wybrać **Użyj tego folderu**. Folder utwórz i udostępnij w magazynie w chmurze sam. Opcjonalne -- możesz go też ustawić później na stronie działki. |
| **Podgląd** | Pokazuje, co się stanie. Jeszcze nic nie jest zmieniane. |

### Krok 2: sprawdź podgląd {#step-2-check-the-preview}

Karta podglądu, **Przekazanie działki *X* w dniu *data***, wymienia
dokładnie, co się stanie:

- **Dotychczasowi dzierżawcy** -- dzierżawa każdego obecnego dzierżawcy
  kończy się w dniu przekazania. Jeśli nie mają innej działki, ich
  członkostwo kończy się dzień wcześniej („członkostwo kończy się po
  *dacie*”). Jeśli mają jeszcze inną działkę, zachowują członkostwo;
  podgląd wymienia tę działkę.
- **Nowi dzierżawcy i odbiorcy faktur** -- każdy kandydat albo „zostaje
  nowym członkiem” (imię, e-mail i telefon są przejmowane ze
  zgłoszenia), albo, jeśli aktywny członek ma już adres e-mail
  kandydata, zostaje połączony z tym członkiem („już członek”).
- **Folder dokumentów** -- który folder zostanie wycofany w dniu
  przekazania i który go zastąpi. Jeśli sam nie możesz zarządzać
  folderami, notka mówi, że nowy folder ustawi później ktoś z pełnym
  dostępem.

Jeśli coś jest nie tak -- działka nie jest wypowiedziana, zgłoszenie
kandydata jest już zamknięte albo nie ma nazwiska -- komunikat o błędzie
to wyjaśnia i nic się nie dzieje.

Kliknij **Przekaż działkę** i potwierdź. Parcella wtedy za jednym
razem:

1. kończy stare dzierżawy w dniu przekazania (zostają w historii
   działki jako byli dzierżawcy),
2. kończy członkostwo dotychczasowych dzierżawców, którzy nie mają innej
   działki,
3. tworzy nowych członków -- ich **Członek od** to data przekazania --
   i czyni ich dzierżawcami i odbiorcami faktur działki,
4. ustawia działkę z powrotem jako **aktywna**,
5. ustawia zgłoszenia na **Zamknięte (działka przydzielona)**.

Potem trafiasz na stronę działki.


!!! tip "Uzupełnij potem dane nowego członka"
    Ze zgłoszenia kopiowane są tylko imię i nazwisko, adres e-mail i
    numer telefonu. Otwórz nowego członka i dodaj adres i IBAN. **Może
    otrzymywać informacje e-mailem** jest zaznaczone, jak u każdego
    nowego członka; odznacz, jeśli chce tylko papieru.

## Zgłoszenia z Twojej strony internetowej {#applications-from-your-website}

Większość zgłoszeń przychodzi przez formularz na stronie internetowej
stowarzyszenia. Po konfiguracji każdy wysłany formularz pojawia się na
liście kandydatów jako zgłoszenie **Nowe** ze źródłem **Formularz na
stronie** i datą, w której kandydat wyraził zgodę na przetwarzanie
danych.

O co pyta formularz: adres e-mail (wymagany), imię i nazwisko, telefon,
wiadomość oraz pole zgody na przetwarzanie danych, które musi być
zaznaczone. Parcella chroni formularz przed spamem: ukryte pola, które
wypełniają tylko boty, opcjonalna captcha i limit kilku zgłoszeń na
godzinę od tego samego odwiedzającego.

Konfiguracja:

1. Włącz moduł **Publiczne API formularza zgłoszeń** w
   [Włączaniu i wyłączaniu modułów](../administration/modules.md).
2. W [Integracjach](../administration/integrations.md) wpisz adres
   swojej strony, aby Parcella przyjmowała z niej formularze. Strona
   pokazuje też adresy, na które formularz wysyła dane.
3. Umieść formularz na swojej stronie:
    - **WordPress**: zainstaluj wtyczkę Parcella Connector i umieść
      shortcode `[parcella_applicant_form]` na stronie.
    - **Dowolna inna strona**: zwykły formularz HTML, który wysyła
      powyższe pola do Parcelli. Twój projektant stron znajdzie
      szczegóły w Integracjach.

Co widzą kandydaci, opisuje strona [Dla działkowców](../gardeners/index.md).

!!! note
    Parcella nie wysyła kandydatowi automatycznego potwierdzenia. Do
    pierwszej odpowiedzi użyj [Kontaktu z kandydatem](#contact-applicant).

## Automatyczne usuwanie {#automatic-deletion}

W [Ustawieniach stowarzyszenia](../administration/settings.md) →
**Kandydaci** pole **Usuwaj zgłoszenia po (miesiącach)** pozwala
Parcelli usuwać stare zgłoszenia za Ciebie. Każde zgłoszenie, którego
status nie zmienił się przez tyle miesięcy, zostaje usunięte na zawsze
-- **niezależnie od statusu** i bez powiadamiania kogokolwiek. Miesiące
liczą się od ostatniej zmiany statusu albo od daty zgłoszenia, jeśli
status nigdy się nie zmienił.

Zostaw pole puste lub z 0 (domyślnie), aby przechowywać zgłoszenia,
dopóki nie usuniesz ich ręcznie. Sprawdzenie działa w tle, gdy ludzie
korzystają z Parcelli, najwyżej raz na godzinę.

!!! warning
    Automatyczne usuwanie usuwa też otwarte zgłoszenia, które po prostu
    długo czekają. Jeśli Twoja lista oczekujących jest długa, wybierz
    okres dłuższy niż zwykły czas oczekiwania albo od czasu do czasu
    przesuwaj status długo czekających kandydatów.

## Powiązane {#related}

- [Działki](parcels.md) -- wypowiedzenie działki przed przekazaniem
- [Członkowie](members.md) -- uzupełnianie danych nowego członka
- [Przekazanie działki](../guides/parcel-handover.md)
- [Ogłoszenia](announcements.md) -- pisanie do wybranych kandydatów
- [Kontakty zewnętrzne](external-contacts.md) -- tag czerwonej flagi
- [Integracje](../administration/integrations.md) -- formularz na stronie
