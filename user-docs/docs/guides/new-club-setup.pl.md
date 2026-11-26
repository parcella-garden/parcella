# Konfiguracja nowego stowarzyszenia {#setting-up-a-new-club}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Parcella jest zainstalowana i działa. Ta instrukcja prowadzi od
pierwszego logowania do instalacji, z którą może pracować cały zarząd:
bezpieczne hasło administratora, dane i logo stowarzyszenia, właściwy
język, tylko potrzebne moduły, konta dla pozostałych członków zarządu i
-- jeśli chcesz -- najpierw próbna runda z danymi przykładowymi.

Zaplanuj około godziny. Potrzebujesz konta administratora, które
powstało przy instalacji.

!!! info "Kto może to zrobić"
    Wszystko tutaj odbywa się w **Administracja**, którą mogą otworzyć
    tylko administratorzy (i grupy z **Dostęp do panelu
    administracyjnego**). Zob.
    [Role, grupy i uprawnienia](../getting-started/roles-and-permissions.md).

## 1. Zaloguj się i zmień hasło administratora {#1-log-in-and-change-the-admin-password}

1. Otwórz Parcellę w przeglądarce i zaloguj się kontem administratora z
   instalacji.
   <!-- TODO(verify): the default login (admin@parcella.local / admin1234) is documented for developers; confirm whether self-hosters get the same default or set their own during installation before naming it here. -->
2. Jeśli konto nadal używa domyślnego hasła z konfiguracji, Parcella od
   razu otwiera **Zmień hasło** i pokazuje: *„To konto nadal używa
   domyślnego hasła z pierwszej konfiguracji. Ustaw nowe -- do tego
   czasu reszta aplikacji pozostaje zablokowana.”*
3. Wpisz **Bieżące hasło**, potem **Nowe hasło** i **Potwierdź nowe
   hasło**, i kliknij **Zmień hasło**.

Hasło możesz zmienić ponownie w każdej chwili w menu użytkownika na dole
menu bocznego: **Zmień hasło**.

!!! warning
    Nie pomijaj tego w instalacji dostępnej z internetu. Każdy, kto zna
    domyślne hasło, mógłby się inaczej zalogować jako administrator.

Więcej: [Pierwsze logowanie i Twoje konto](../getting-started/first-login.md).

## 2. Wpisz dane stowarzyszenia {#2-enter-your-clubs-details}

1. W menu bocznym otwórz **Administracja → Ustawienia**. Strona nazywa
   się **Ustawienia stowarzyszenia**.
2. Na karcie **Dane stowarzyszenia** wypełnij **Nazwa stowarzyszenia**,
   **Ulica**, **Kod pocztowy**, **Miejscowość**, **Numer
   stowarzyszenia** i **Sąd rejestrowy**. Nazwa pojawia się w tytułach
   stron; reszta trafia do stopki pism i faktur.
3. W **Członkowie zarządu** wyszukaj i zaznacz członków, którzy obecnie
   zasiadają w zarządzie. Możesz wybrać tylko osoby, które już istnieją
   jako członkowie -- wróć do tego po kroku 9 albo po
   [imporcie](csv-import.md).
4. W **Powierzchnie (m²)** wpisz **Powierzchnia całkowita (m²)** terenu
   i **Powierzchnia C (miejska, m²)**, jeśli ją masz. **Powierzchnia A
   (działki, m²)** i **Powierzchnia B (wspólna, m²)** Parcella oblicza
   sama na podstawie działek.
5. Kliknij **Zapisz ustawienia**. Zobaczysz *„Ustawienia zapisane.”*

!!! tip
    Strona ustawień jest długa. Użyj pola **Szukaj ustawień...** u góry,
    aby przejść do pola po nazwie.

## 3. Dodaj logo {#3-add-your-logo}

1. Nadal w **Administracja → Ustawienia** znajdź kartę **Branding**.
2. W **Logo stowarzyszenia** wybierz plik PNG, JPEG, WebP lub SVG o
   rozmiarze co najwyżej 2 MB.
3. Kliknij **Zapisz ustawienia**.

Logo zastępuje logo Parcelli na stronie logowania i w menu bocznym. Aby
wrócić do domyślnego, zaznacz **Usuń logo (powrót do domyślnej ikony)**
i zapisz.

## 4. Wybierz język, region i walutę {#4-choose-language-region-and-currency}

To celowo trzy osobne ustawienia: stowarzyszenie może na przykład używać
angielskiego interfejsu, ale niemieckiego formatu liczb i adresów.

1. **Język** -- język całej instalacji. Każdy użytkownik widzi ten sam.
2. **Region** -- format liczb i adresów (separator tysięcy, kolejność
   kodu pocztowego i miejscowości).
3. **Waluta** -- symbol i jego położenie („19,99 €” albo „£19.99”).
4. Kliknij **Zapisz ustawienia**.

## 5. Skonfiguruj wysyłanie e-maili {#5-set-up-outgoing-email}

Parcella wysyła e-mailem zaproszenia, powiadomienia, ogłoszenia i
faktury. Bez serwera pocztowego zaproszenia z kroku 9 nie mogą zostać
wysłane.

1. W **Administracja → Ustawienia** znajdź kartę **E-mail (SMTP)**.
2. Wypełnij **Serwer SMTP**, **Port SMTP**, **Użytkownik SMTP**,
   **Hasło SMTP** i **E-mail nadawcy** -- te wartości poda Ci Twój
   dostawca poczty.
3. Kliknij **Zapisz ustawienia**.

Po zapisaniu pole hasła pokazuje tylko, że hasło jest ustawione; aby je
zmienić, wpisz nowe.

## 6. Włącz i wyłącz moduły {#6-turn-modules-on-and-off}

Nie każde stowarzyszenie korzysta z każdego obszaru funkcji. Wyłączenie
modułu ukrywa go w nawigacji; jego dane zostają i wracają po ponownym
włączeniu.

1. W **Administracja → Ustawienia** znajdź kartę **Moduły
   funkcjonalne**.
2. Zaznacz moduły, z których korzysta Twoje stowarzyszenie, a pozostałe
   odznacz. Pod każdym jest krótki opis.
3. Kliknij **Zapisz ustawienia**.

Kilka modułów jest w nowej instalacji **wyłączonych**, bo wysyłają dane
na zewnątrz lub otwierają coś publicznie: **Finanse**, **Ogłoszenia**,
**Magazyn w chmurze**, **Wsparcie (helpdesk)**, **Synchronizacja
Nextcloud Deck**, **Konektor MCP dla klientów AI** oraz trzy publiczne
API dla strony internetowej. Włącz je dopiero, gdy będą potrzebne.

Więcej: [Włączanie i wyłączanie modułów](../administration/modules.md).

## 7. Wypróbuj na danych przykładowych (opcjonalnie) {#7-try-things-out-with-sample-data-optional}

Zanim wprowadzisz prawdziwe dane, możesz wypełnić pustą instalację
zmyślonymi członkami, działkami, licznikami, terminami prac i nie
tylko, poklikać i wszystko to znowu usunąć.

1. Otwórz **Administracja → Dane przykładowe**.
2. Przeczytaj **Co zostanie dodane**, potem kliknij **Dodaj dane
   przykładowe** i potwierdź.
3. Poznaj moduły. Wypróbuj serię faktur, zapisz odczyt licznika,
   przekaż działkę.
4. Gdy skończysz, wróć do **Administracja → Dane przykładowe** i kliknij
   **Usuń wszystkie dane przykładowe**, a potem potwierdź.

!!! warning "Usuń dane przykładowe, zanim zaczniesz na poważnie"
    - Dane przykładowe można **dodać** tylko do świeżej instalacji. Gdy
      tylko istnieje jeden prawdziwy członek lub działka, przycisk jest
      zablokowany.
    - **Usuń wszystkie dane przykładowe** usuwa dokładnie to, co
      utworzył generator, i nic, co wpisałeś sam. Wszystko, co podczas
      ćwiczeń dołączysz *do* przykładowego rekordu (odczyt na
      przykładowym liczniku, płatność na przykładowej fakturze), może
      nie zostać czysto usunięte. Najpierw usuń dane przykładowe, potem
      wprowadź prawdziwe.
      <!-- TODO(verify): what happens on removal if a real record references a sample record (e.g. a finalized invoice run built from sample parcels)? -->
    - Dane przykładowe nie tworzą ani nie zmieniają kont użytkowników.

Więcej: [Dane przykładowe](../administration/sample-data.md).

## 8. Utwórz grupy {#8-create-groups}

Nowe konta użytkowników dostają dostęp przez **grupy**, a nie przez
stałą rolę. Najpierw utwórz grupy, potem zaproś do nich ludzi.

1. Otwórz **Administracja → Grupy**.
2. W **Utwórz grupę** wpisz **Nazwa** (na przykład „Zarząd”) i **Opis**.
3. Dla zarządu zaznacz **Pełny dostęp do każdego modułu**. **Dostęp do
   panelu administracyjnego** zaznacz tylko dla osób, które mają też
   zarządzać użytkownikami i ustawieniami.
4. Kliknij **Utwórz grupę**.
5. Do węższych zadań utwórz kolejne grupy i w tabeli uprawnień zaznacz
   **Odczyt**, **Zapis** i **Usuwanie** dla każdego **Moduł** -- na
   przykład „Zespół wodny” z odczytem i zapisem w **Woda** albo
   „Skarbnik” z pełnymi prawami w **Finanse**. Kliknij **Zapisz**.

!!! tip
    Każdy, kto może się zalogować, zawsze może *przeglądać* członków i
    działki. Grupy rozszerzają dostęp od tego miejsca; nigdy go nie
    odbierają.

Więcej: [Grupy](../administration/groups.md) i
[Role, grupy i uprawnienia](../getting-started/roles-and-permissions.md).

## 9. Zaproś pozostałych członków zarządu {#9-invite-the-other-board-members}

1. Otwórz **Administracja → Użytkownicy** (strona nazywa się
   **Zarządzanie użytkownikami**).
2. W **Zaproś użytkownika** wpisz **Adres e-mail** osoby i zaznacz jej
   **Grupy**.
3. Kliknij **Wyślij zaproszenie**.
4. Osoba dostaje e-mail z linkiem. Na stronie **Utwórz konto** wpisuje
   swoje **Imię i nazwisko** i **Hasło** (co najmniej 8 znaków) i klika
   **Utwórz konto**.

Zaproszenie jest ważne przez 7 dni i do przyjęcia widnieje w
**Oczekujące zaproszenia**. Stamtąd możesz **Wyślij zaproszenie
ponownie** (co je też przedłuża) albo **Usuń zaproszenie**.

!!! warning
    Zaproszenie wychodzi e-mailem, więc najpierw skonfiguruj **E-mail
    (SMTP)** (krok 5). Jeśli nie da się go wysłać, strona to pokaże;
    popraw ustawienia poczty i użyj **Wyślij zaproszenie ponownie**.

Więcej: [Użytkownicy i zaproszenia](../administration/users.md).

## 10. Podłącz chmurę (opcjonalnie) {#10-connect-cloud-storage-optional}

Jeśli Twoje stowarzyszenie trzyma umowy dzierżawy i inne dokumenty w
Nextcloud (lub w innym obsługiwanym magazynie), Parcella może pokazywać
folder dokumentów na stronie każdej działki.

1. Otwórz **Administracja → Integracje** i znajdź **Chmura (dokumenty
   działek, faktury, kopie zapasowe)**.
2. Wybierz **Typ chmury** i wpisz dane połączenia, o które prosi.
   Kliknij **Zapisz**, a potem **Testuj połączenie**.
3. Opcjonalnie ustaw wspólne foldery niżej: **Folder faktur
   przychodzących**, **Folder na dokumenty kontaktów zewnętrznych**,
   **Folder notatek**, **Folder na pliki procesów**, **Folder na
   drukowane ogłoszenia**.
4. Przejdź do **Administracja → Ustawienia → Moduły funkcjonalne**,
   zaznacz **Magazyn w chmurze** i kliknij **Zapisz ustawienia**.
5. Na stronie każdej działki ustaw **Ścieżka folderu** w **Dokumenty
   (chmura)** -- wpisz ją albo użyj **Przeglądaj…** -- i kliknij
   **Zapisz**.

Ścieżki są zawsze względne wobec wybranego magazynu. Parcella nie
tworzy ani nie udostępnia folderów za Ciebie; zrób to najpierw w swojej
chmurze.

Więcej: [Integracje](../administration/integrations.md).

## 11. Wprowadź lub zaimportuj prawdziwe dane {#11-enter-or-import-your-real-data}

Teraz dodaj działki i członków -- ręcznie w **Działki → Nowa działka**
i **Członkowie → Nowy członek** albo za jednym razem z arkusza
kalkulacyjnego: zob. [Import członków i działek](csv-import.md).
Następnie przypisz każdego członka do jego działki (zob. [Przyjęcie
nowego członka](new-member.md), krok 6).

## 12. Zrób pierwszą kopię zapasową {#12-make-your-first-backup}

1. Otwórz **Administracja → Użytkownicy** i znajdź kartę **Kopia
   zapasowa**.
2. Kliknij **Pobierz kopię zapasową** i przechowuj plik zip w
   bezpiecznym miejscu.

Kopia zapasowa zawiera bazę danych, przesłane pliki i klucz
szyfrowania. Traktuj ją jak samą listę członków.

Więcej: [Kopia zapasowa i przywracanie](../administration/backup.md).

## Powiązane {#related}

- [Ustawienia stowarzyszenia](../administration/settings.md)
- [Włączanie i wyłączanie modułów](../administration/modules.md)
- [Użytkownicy i zaproszenia](../administration/users.md)
- [Grupy](../administration/groups.md)
- [Integracje](../administration/integrations.md)
- [Dane przykładowe](../administration/sample-data.md)
- [Kopia zapasowa i przywracanie](../administration/backup.md)
- [Import członków i działek](csv-import.md)
