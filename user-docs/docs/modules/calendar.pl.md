# Kalendarz {#calendar}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Moduł kalendarza trzyma w jednym miejscu daty ważne dla Twojego
stowarzyszenia: zebrania i kontrole, urodziny członków, kiedy członkowie
zarządu są na miejscu i kiedy ktoś jest nieobecny. Każdy kalendarz można
subskrybować w aplikacji kalendarza na telefonie lub komputerze.

!!! info "Kto może z tego korzystać"
    - Przełącznik modułu to **Kalendarz** w **Administracja → Włączanie
      i wyłączanie modułów**. Domyślnie jest **włączony**.
    - Role **Zarząd** i **Administrator** oraz członkowie grupy z
      **Pełny dostęp do każdego modułu** mogą wszystko.
    - Wszyscy pozostali potrzebują uprawnienia **Kalendarz** w jednej ze
      swoich [grup](../administration/groups.md): *odczyt*, aby widzieć
      kalendarze, *zapis*, aby dodawać wpisy, *usuwanie*, aby je usuwać.
    - **Nieobecność zarządu** jest wyjątkiem: każdy, kto jest zalogowany
      i może otworzyć kalendarz, może wpisać nieobecność.
    - Tworzenie i edycja własnych kalendarzy w **Własne kalendarze**
      wymaga pełnego dostępu (Zarząd, Administrator lub grupa z pełnym
      dostępem).

Celowo nie ma siatki miesięcznej. Każdy kalendarz to prosta lista tego,
co nadchodzi, zaczynając od dziś. Minione wpisy automatycznie znikają z
listy (i z kanałów subskrypcji).

Wszystkie kalendarze znajdziesz na pasku bocznym pod **Kalendarz**:
**Kalendarz stowarzyszenia**, **Urodziny**, **Obecność zarządu**,
**Nieobecność zarządu** i **Własne kalendarze**. Otwarcie samego adresu
kalendarza prowadzi do **Kalendarz stowarzyszenia**.

## Kalendarz stowarzyszenia {#community-calendar}

![Kalendarz stowarzyszenia](../assets/screenshots/calendar/community.png)

Kalendarz całego stowarzyszenia: zebrania członków, kontrole działek i
inne wydarzenia stowarzyszenia, razem z zaplanowanymi terminami prac z
modułu [Prace społeczne](work-hours.md). To kalendarz, który możesz
pokazać na publicznej stronie internetowej.

### Nowy wpis {#new-entry}

Karta **Nowy wpis** po lewej jest widoczna tylko z prawem *zapisu* w
kalendarzu.

| Pole / przycisk | Do czego służy |
|---|---|
| **Typ** | **Zebranie członków**, **Kontrola działki** lub **Inne** (domyślnie). Zmienia tylko kolorowe oznaczenie na liście. |
| **Tytuł** | Wymagany. Nazwa wydarzenia, np. „Walne zebranie”. |
| **Data** | Wymagana. (Pierwszy) dzień wydarzenia. |
| **Godzina** | Opcjonalna godzina rozpoczęcia. Zostaw puste dla wpisu całodniowego. |
| **Data końcowa** | Opcjonalna. Tylko dla wpisów wielodniowych -- zostaw puste dla jednego dnia. |
| **Godzina końcowa** | Opcjonalna godzina zakończenia. |
| **Miejsce** | Opcjonalne. Pokazywane ze znacznikiem pod tytułem. |
| **Opis** | Opcjonalny dowolny tekst. Nie jest pokazywany na liście, ale trafia do kanału subskrypcji i widżetu na stronie. |
| **Dodaj wpis** | Zapisuje wpis i pokazuje go na liście. |

### Nadchodzące {#upcoming}

| Kolumna | Co pokazuje |
|---|---|
| **Data** | Data, plus przedział godzin, jeśli go wpisano. |
| **Tytuł** | Tytuł i miejsce. Dla terminu prac tytuł prowadzi do tego terminu w module prac społecznych. |
| **Typ** | Oznaczenie: **Zebranie członków**, **Kontrola działki**, **Inne** lub **Wpis prac**. |
| Ikona kosza | Usuwa wpis po potwierdzeniu (**Czy na pewno usunąć ten wpis?**). Widoczna tylko z prawem *usuwania* i tylko dla wpisów dodanych tutaj -- terminy prac zmienia się w module prac społecznych. |

Jeśli nic nie jest zaplanowane, lista mówi **Brak nadchodzących
wpisów.**

!!! note "Które terminy prac się pojawiają"
    Pojawiają się tu tylko regularne, zaplanowane terminy prac.
    Spontaniczne terminy „specjalne” (np. „dziś malujemy ławkę”) są
    pomijane, bo członkowie nie mogą się do nich przygotować. Terminy
    prac są odczytywane bezpośrednio z modułu prac społecznych, więc
    przesunięcie terminu tam zmienia go także tutaj -- nie ma czego
    synchronizować.

### Subskrybuj (ICS) {#subscribe-ics}

Przycisk **Subskrybuj (ICS)** u góry po prawej pokazuje **Publiczny link
ICS (można osadzić na publicznej stronie):**. Kliknij w pole, aby
zaznaczyć adres, i skopiuj go.

Ten kanał nie wymaga logowania ani hasła. Zawiera tylko to, co już jest
publiczne: wpisy powyżej i zaplanowane terminy prac. Możesz dodać go do
aplikacji kalendarza albo pokazać na stronie stowarzyszenia (zob.
[Subskrypcja w aplikacji kalendarza](#subscribing-in-a-calendar-app)
niżej).

<!-- TODO(verify): the WordPress connector plugin renders this calendar with a [parcella_calendar] shortcode. Link to the integrations page once it documents the plugin side. -->

## Urodziny {#birthdays}

![Urodziny](../assets/screenshots/calendar/birthdays.png)

Nadchodzące urodziny aktywnych członków. Dla tej listy nic nie jest
zapisywane: za każdym razem jest wyliczana z daty urodzenia każdego
członka. Popraw datę urodzenia u [członka](members.md), a lista od razu
jest poprawna. Członkowie bez daty urodzenia się nie pojawiają.

### Wybór zakresu czasu i kolejności {#choosing-the-time-range-and-order}

Nagłówek karty **Nadchodzące urodziny** pokazuje objęte daty (np.
„01.12.2026 – 28.02.2027”) i dwie listy rozwijane. Lista przeładowuje
się, gdy tylko którąś zmienisz.

| Pole | Do czego służy |
|---|---|
| Zakres czasu | **Następny miesiąc**, **Następne 3 miesiące** (domyślnie) lub **Następne 12 miesięcy**, zawsze licząc od dziś. **Następne 12 miesięcy** pokazuje każdego członka z datą urodzenia. |
| Sortowanie | **Sortuj według urodzin** (domyślnie), **Sortuj według nazwiska** lub **Sortuj według numeru działki**. Sortowanie według działki używa najniższego obecnego numeru działki członka, a członków bez działki umieszcza na końcu. |

### Nadchodzące urodziny {#upcoming-birthdays}

| Kolumna | Co pokazuje |
|---|---|
| **Data** | Data najbliższych urodzin. |
| **Imię i nazwisko** | Członek, z linkiem do jego rekordu. Okrągłe urodziny (30, 40, 50 ...) dostają oznaczenie **Okrągłe**, a cały wiersz jest wyróżniony. |
| **Kończy** | Wiek, który członek kończy. |
| **Tagi** | Tagi członka. Kliknij jeden, aby otworzyć listę członków przefiltrowaną po tym tagu. |
| **Prezent** | **Bez prezentu**, jeśli członek powiedział, że nie chce prezentu urodzinowego (ustawiane w rekordzie członka). |

Jeśli nikt nie ma urodzin w wybranym zakresie, lista mówi **Brak
nadchodzących urodzin w systemie.**

### Drukuj PDF {#print-pdf}

**Drukuj PDF** tworzy listę do druku dla osoby, która rozdaje prezenty.
Używa dokładnie zakresu czasu i kolejności wybranych na stronie.

PDF jest w formacie A4 poziomo, z nagłówkiem stowarzyszenia, i ma więcej
kolumn niż strona: działka, imię i nazwisko, urodziny, kończony wiek
(okrągłe urodziny wyróżnione), tagi, „bez prezentu”, adres pocztowy,
główny adres e-mail i główny numer telefonu. Przy sortowaniu według
działki członkowie są pogrupowani pod numerem działki; członek z kilkoma
działkami pojawia się pod każdą z nich, a członkowie bez działki są na
końcu w grupie „bez działki”.

!!! warning "Dane osobowe"
    Wydruk zawiera adresy i numery telefonów. Odpowiednio obchodź się z
    papierowymi kopiami.

### Subskrybuj (ICS) {#subscribe-ics_1}

Przycisk **Subskrybuj (ICS)** pokazuje **Prywatny link ICS (nie
udostępniaj -- każdy z tym linkiem może go zobaczyć):**. Kanał zawiera
urodziny każdego aktywnego członka jako powtarzający się co roku wpis
całodniowy.

## Obecność zarządu {#council-presence}

![Obecność zarządu](../assets/screenshots/calendar/council-presence.png)

Planuj, kiedy członkowie zarządu są na miejscu, np. dyżury w
świetlicy. Członkowie widzą wtedy, kiedy ktoś z zarządu jest obecny.

### Nowy termin obecności {#new-presence-slot}

Widoczny tylko z prawem *zapisu* w kalendarzu.

| Pole / przycisk | Do czego służy |
|---|---|
| **Członek(owie) zarządu** | Wymagane. Zaznacz jedno lub więcej kont użytkowników. Wybierz więcej niż jedno, jeśli kilku członków obsługuje ten termin razem -- każdy z nich dostaje własny wpis na ten sam termin. Jeśli nikogo nie zaznaczysz, formularz pokazuje **Wybierz co najmniej jednego członka zarządu** i nie zapisuje. |
| **Data** | Wymagana. |
| **Od** / **Do** | Opcjonalne godziny. Bez godziny termin liczy się jako całodniowy. |
| **Notatka** | Opcjonalna, np. „Otwarty dyżur dla członków”. |
| **Dodaj** | Zapisuje termin. |

Lista osób pokazuje tylko aktywne konta użytkowników, nie każdego
członka: członek zarządu potrzebuje loginu do Parcelli, aby pojawić się
na liście.

### Nadchodzące {#upcoming_1}

Wpisy są pogrupowane pod jednym nagłówkiem na dzień.

| Kolumna | Co pokazuje |
|---|---|
| **Członek** | Zdjęcie i imię użytkownika. |
| **Godzina** | Od -- do albo kreska, jeśli nie podano godziny. |
| **Notatka** | Notatka, jeśli jest. |
| Ikona kosza | Usuwa ten jeden wpis (jedna osoba, jeden termin) po potwierdzeniu. Wymaga prawa *usuwania*. |

Gdy nic nie jest zaplanowane: **Brak zaplanowanych terminów obecności.**

Przycisk **Subskrybuj (ICS)** pokazuje prywatny link, jak przy
urodzinach. Terminy z godziną pojawiają się w aplikacjach kalendarza
jako spotkania z godziną.

## Nieobecność zarządu {#council-absence}

![Nieobecność zarządu](../assets/screenshots/calendar/council-absence.png)

Urlopy i inne nieobecności, aby zarząd wiedział, kto jest niedostępny.
Każdy zalogowany może korzystać z tej strony -- nie potrzebujesz
żadnego dodatkowego uprawnienia.

### Wpisz nieobecność {#log-absence}

| Pole / przycisk | Do czego służy |
|---|---|
| **Członek(-owie)** | Domyślnie Ty; wybierz też innych, jeśli wpisujesz to w ich imieniu. Możesz odznaczyć siebie, aby wpisać nieobecność tylko dla kogoś innego. Jeśli odznaczysz wszystkich, nieobecność zostanie wpisana dla Ciebie. |
| **Od** | Wymagane. Pierwszy dzień nieobecności. |
| **Do** | Wymagane. Ostatni dzień nieobecności. |
| **Notatka** | Opcjonalna, np. „Urlop”. Sam decydujesz, czy i co wyjaśnić. |
| **Dodaj** | Zapisuje jedną nieobecność na każdą zaznaczoną osobę. |

### Nadchodzące nieobecności {#upcoming-absences}

Nieobecności zostają na liście, dopóki nie minie ich ostatni dzień.

| Kolumna | Co pokazuje |
|---|---|
| **Kto** | Zdjęcie i imię użytkownika. |
| **Okres** | Od -- do. |
| **Notatka** | Notatka, jeśli jest. |
| Ikona kosza | Usuwa wpis po potwierdzeniu. Widzisz ją przy własnych wpisach; zarząd i użytkownicy z pełnym dostępem widzą ją przy każdym wpisie, aby porządkować pomyłki. |

Gdy nikogo nie ma: **Brak wpisanych nieobecności.**

Przycisk **Subskrybuj (ICS)** pokazuje prywatny link, jak przy
urodzinach. Nieobecności to wpisy całodniowe.

## Własne kalendarze {#my-calendars}

![Własne kalendarze](../assets/screenshots/calendar/custom-index.png)

Dodatkowe kalendarze Twojego stowarzyszenia, na wszystko, co nie należy
do publicznego kalendarza stowarzyszenia: rezerwacje świetlicy, terminy
zarządu, grafik koszenia. Żaden z tych kalendarzy nigdy nie jest
publiczny.

Lista **Kalendarze** pokazuje:

- **Zasoby** na górze, jeśli moduł [Inwentarz](inventory.md) jest
  włączony i możesz go czytać -- zob. [Zasoby](#resources) niżej.
- Każdy kalendarz z kolorową kropką, nazwą i opisem. Kliknij nazwę, aby
  go otworzyć.
- **Tylko zarząd** przy kalendarzach, które widzą tylko zarząd i
  użytkownicy z pełnym dostępem. Inni użytkownicy w ogóle ich nie widzą.
- **Zarchiwizowany** przy zarchiwizowanych kalendarzach. Zarchiwizowane
  kalendarze widzą tylko zarząd i użytkownicy z pełnym dostępem.

Jeśli nie ma jeszcze kalendarzy, lista mówi **Brak kalendarzy.**

### Nowy kalendarz {#new-calendar}

Widoczny tylko dla zarządu i użytkowników z pełnym dostępem.

| Pole / przycisk | Do czego służy |
|---|---|
| **Nazwa** | Wymagana, do 100 znaków, np. „Rezerwacje świetlicy”. |
| **Kolor** | Kolor kropki obok nazwy. Domyślnie zielony. |
| **Opis** | Opcjonalny. Pokazywany pod nazwą i na stronie kalendarza. |
| **Widoczny tylko dla zarządu i użytkowników z pełnym dostępem** | Czyni z niego kalendarz **Tylko zarząd**. |
| **Utwórz kalendarz** | Tworzy kalendarz. |

### Edycja kalendarza {#editing-a-calendar}

Otwórz **Edytuj** pod nazwą kalendarza (tylko zarząd i użytkownicy z
pełnym dostępem).

| Pole / przycisk | Do czego służy |
|---|---|
| **Nazwa**, **Kolor**, **Opis** | Jak wyżej. |
| **Widoczny tylko dla zarządu i użytkowników z pełnym dostępem** | Przełącza kalendarz między widocznym dla wszystkich a tylko dla zarządu. Zmiana tworzy też nowy link subskrypcji, więc osoby, które subskrybowały wcześniej, tracą dostęp. |
| **Aktywny (odznacz, aby zarchiwizować)** | Odznacz, aby zarchiwizować kalendarz. Jego wpisy zostają, ale nie można dodawać nowych, a link subskrypcji przestaje działać. Zaznacz ponownie, aby przywrócić kalendarz. |
| **Nowy adres subskrypcji (stare przestaną działać)** | Zaznacz, gdy ktoś, kto miał link, nie powinien już widzieć kalendarza, np. po odejściu z zarządu. |
| **Zapisz** | Zapisuje zmiany. |

Kalendarza nie da się usunąć. Zamiast tego zarchiwizuj go, aby jego
historia została.

## Strona kalendarza {#a-calendars-page}

![Strona kalendarza](../assets/screenshots/calendar/custom-detail.png)

Otwarcie kalendarza z **Własne kalendarze** pokazuje jego kolor i nazwę
jako tytuł strony, opis i nadchodzące wpisy. **Wstecz** wraca do
**Własne kalendarze**.

Karta **Nowy wpis** działa jak ta w
[Kalendarzu stowarzyszenia](#new-entry), bez pola **Typ**. Jest widoczna
tylko z prawem *zapisu* i tylko, dopóki kalendarz jest aktywny. Tytuł i
miejsce mogą mieć do 255 znaków; godziny muszą być prawidłowe (gg:mm),
inaczej są ignorowane.

Lista **Nadchodzące** pokazuje **Data** (z datą końcową i godzinami),
**Tytuł** (z miejscem i opisem) oraz ikonę kosza do usunięcia wpisu
(wymaga prawa *usuwania*).

Zarchiwizowany kalendarz pokazuje **Ten kalendarz jest zarchiwizowany:
wpisy pozostają, ale nie można dodawać nowych.**

Przycisk **Subskrybuj (ICS)** (tylko aktywne kalendarze) pokazuje
**Prywatny adres subskrypcji (nie udostępniaj)**. Każdy z Twoich
własnych kalendarzy ma własny tajny link, oddzielny od wspólnego linku
używanego przez kalendarz urodzin i kalendarze zarządu.

## Zasoby {#resources}

![Zasoby](../assets/screenshots/calendar/resources.png)

Przegląd tylko do odczytu przedmiotów stowarzyszenia, które członkowie
mogą wypożyczać, i tego, kto je teraz ma. Dostępny z **Własne
kalendarze** i działa tylko wtedy, gdy moduł inwentarza jest włączony i
masz prawo jego odczytu, bo pokazuje, kto co wypożyczył. **Wstecz**
wraca do **Własne kalendarze**.

Lista obejmuje każdy przedmiot stowarzyszenia oznaczony jako do
wypożyczenia, który nie został wycofany. Przedmiotami zarządza się i
wypożycza je w module [Inwentarz](inventory.md), nie tutaj.

| Kolumna | Co pokazuje |
|---|---|
| **Przedmiot** | Nazwa przedmiotu (z linkiem do niego w inwentarzu) i jego kategoria. |
| **Status** | Dostępność: **Dostępny**, **Wypożyczony** (nic nie zostało) albo, dla przedmiotów, których masz kilka, np. „Dostępne 2 z 5”. |
| **Obecnie wypożyczone** | Jeden wiersz na otwarte wypożyczenie: „od 03.11.2026: Jan Kowalski (1×)” albo kreska, jeśli nikt go nie ma. |


Wypożyczenia w Parcelli nie mają planowanej daty zwrotu, więc ta strona
pokazuje tylko bieżącą sytuację, a nie harmonogram na przyszłość.

Jeśli nie ma przedmiotów do wypożyczenia: **Brak przedmiotów
stowarzyszenia do wypożyczenia.**

## Subskrypcja w aplikacji kalendarza {#subscribing-in-a-calendar-app}

Każdy kalendarz ma przycisk **Subskrybuj (ICS)** z adresem („link
ICS”). W większości aplikacji kalendarza dodajesz go opcją w rodzaju
„Subskrybuj kalendarz”, „Dodaj kalendarz z adresu URL” lub „Z
internetu”. Aplikacja regularnie sprawdza adres, więc nowe wpisy
pojawiają się same. Jak często sprawdza, zależy od aplikacji.

| Kalendarz | Link | Kto może go mieć |
|---|---|---|
| Kalendarz stowarzyszenia | Publiczny | Każdy. Bezpieczny dla strony stowarzyszenia. |
| Urodziny | Prywatny, wspólny sekret | Tylko osoby, które powinny widzieć urodziny członków. |
| Obecność zarządu | Prywatny, wspólny sekret | Zarząd i pomocnicy. |
| Nieobecność zarządu | Prywatny, wspólny sekret | Zarząd i pomocnicy. |
| Każdy z **Własne kalendarze** | Prywatny, jeden sekret na kalendarz | Ten, kto powinien widzieć ten kalendarz. |

Linki do urodzin, obecności zarządu i nieobecności zarządu używają tego
**samego** sekretu dla całej Twojej instalacji. Każdy, kto ma jeden z
tych linków, może czytać wszystkie trzy kanały bez logowania. Przekazuj
je tylko osobom, którym ufasz.

!!! warning "Jeśli prywatny link wycieknie"
    Dla **Własne kalendarze** zaznacz w kalendarzu **Nowy adres
    subskrypcji (stare przestaną działać)** i zapisz. Dla linków do
    urodzin i zarządu nie ma tu przycisku do zmiany wspólnego sekretu.
    <!-- TODO(verify): there is no UI to rotate the shared ICS token (stored as a club setting); confirm whether an administrator can reset it somewhere, e.g. via the API club settings. -->

## Powiązane {#related}

- [Prace społeczne](work-hours.md) -- skąd pochodzą terminy prac w
  kalendarzu stowarzyszenia.
- [Członkowie](members.md) -- daty urodzenia, tagi i ustawienie „bez
  prezentu”.
- [Inwentarz](inventory.md) -- przedmioty do wypożyczenia i
  wypożyczenia.
- [Grupy](../administration/groups.md) -- nadanie komuś uprawnień do
  kalendarza.
- [Włączanie i wyłączanie modułów](../administration/modules.md)
