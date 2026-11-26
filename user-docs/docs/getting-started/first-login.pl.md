# Pierwsze logowanie i Twoje konto {#first-login-and-your-account}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Ta strona opisuje wszystko o Twoim własnym koncie: jak je dostajesz, jak
się logujesz oraz jak zmieniasz hasło i zdjęcie.

!!! info "Kto może z tego korzystać"
    Każdy, kto ma konto w Parcelli. Nie ma publicznej rejestracji: konto
    istnieje dopiero wtedy, gdy zaprosi Cię administrator.

## Jak dostać konto: zaproszenie {#getting-an-account-the-invitation}

Administrator Twojej instalacji zaprasza Cię e-mailem (zob.
[Użytkownicy i zaproszenia](../administration/users.md)). Dostajesz
e-mail z tematem **Zaproszenie do Parcella** i przyciskiem
**Przyjmij zaproszenie**. Link w nim jest ważny przez **7 dni**.

!!! tip "Nie przyszedł żaden e-mail?"
    Najpierw zajrzyj do folderu spamu. Jeśli go tam nie ma, poproś
    administratora, aby sprawdził [Dziennik e-maili](../administration/email-log.md)
    i w razie potrzeby wysłał zaproszenie ponownie. Ponowne wysłanie
    przedłuża ważność linku o kolejne 7 dni; link z pierwszego e-maila
    nadal działa.

### Przyjęcie zaproszenia {#accept-invitation}

<!-- TODO(verify): no screenshot of "Set up your account" -- it needs a valid invitation link, which the screenshot tool can't produce from the sample data. -->

Kliknięcie linku otwiera stronę **Utwórz konto**. Pod nagłówkiem widzisz
adres, na który wysłano zaproszenie (**Zaproszenie dla** ...). Ten adres
staje się Twoim loginem; nie możesz go tu zmienić.

| Pole / przycisk | Do czego służy |
|---|---|
| **Imię i nazwisko** | Twoje imię i nazwisko. Inni członkowie zarządu widzą je na listach, przy zadaniach, zatwierdzeniach i w historii zmian. |
| **Hasło** | Co najmniej 8 znaków. |
| **Powtórz hasło** | Wpisz to samo hasło jeszcze raz. Jeśli się nie zgadzają, zobaczysz **Hasła nie są zgodne.** |
| **Utwórz konto** | Tworzy konto i od razu Cię loguje. Trafiasz na [Panel główny](dashboard.md). |

To, co zobaczysz później, zależy od grup, które administrator wybrał
przy zapraszaniu. Jeśli nie wybrał żadnej, możesz tylko przeglądać
członków i działki -- poproś o dodanie do grupy. Zob.
[Role, grupy i uprawnienia](roles-and-permissions.md).

### Zaproszenie wygasło {#invitation-expired}

![Zaproszenie wygasło](../assets/screenshots/getting-started/invitation-expired.png)

Widzisz **Zaproszenie wygasło** -- *Ten link zaproszenia jest już
nieważny lub został wykorzystany.* -- gdy:

- od wysłania (lub ostatniego ponownego wysłania) zaproszenia minęło
  ponad 7 dni,
- konto zostało już utworzone za pomocą tego linku, albo
- administrator usunął zaproszenie lub zaprosił ten sam adres ponownie
  (działa tylko najnowsze zaproszenie).

Poproś administratora o ponowne zaproszenie. **Do logowania** prowadzi
na stronę logowania, co pomoże tylko wtedy, gdy masz już konto.

## Logowanie {#signing-in}

![Strona logowania](../assets/screenshots/getting-started/login.png)

Otwórz adres Parcelli swojego stowarzyszenia w przeglądarce. Strona
logowania pokazuje logo i nazwę stowarzyszenia (oba ustawia
administrator w [Ustawieniach stowarzyszenia](../administration/settings.md)).

| Pole / przycisk | Do czego służy |
|---|---|
| **E-mail** | Adres, na który wysłano zaproszenie. Wielkość liter nie ma znaczenia. |
| **Hasło** | Twoje hasło. |
| **Zaloguj się** | Loguje Cię i otwiera [Panel główny](dashboard.md). |

Komunikaty, które możesz zobaczyć:

| Komunikat | Znaczenie |
|---|---|
| **Nieprawidłowy e-mail lub hasło.** | Jedno z dwojga jest błędne. Dla Twojego bezpieczeństwa Parcella nie mówi, które. |
| **Twoje konto jest dezaktywowane.** | Administrator wyłączył Twoje konto. Twoje dane nadal istnieją; poproś o ponowną aktywację. |
| **Zbyt wiele nieudanych prób logowania. Odczekaj kilka minut i spróbuj ponownie.** | Po wielokrotnym podaniu błędnego hasła Parcella wstrzymuje próby logowania na to konto na około 15 minut. |

Pozostajesz zalogowany przez **8 godzin** (chyba że osoba hostująca
Twoją instalację to zmieniła). Potem Parcella prosi o ponowne
zalogowanie, nawet jeśli cały czas pracowałeś.

Aby się wylogować, kliknij **Wyloguj** na dole paska bocznego. Rób to
na każdym współdzielonym lub publicznym komputerze.

!!! note "Nie pamiętasz hasła?"
    Celowo nie ma linku „Nie pamiętam hasła”. Zwróć się do
    administratora: może zresetować Twoje hasło i dać Ci tymczasowe (zob.
    [Użytkownicy i zaproszenia](../administration/users.md#reset-password)).
    Przy następnym logowaniu musisz wtedy ustawić nowe hasło.

## Pierwsze logowanie po instalacji {#the-very-first-login-after-installation}

Gdy Parcella uruchamia się po raz pierwszy, sama tworzy jedno konto
administratora:

- **E-mail:** `admin@parcella.local`
- **Hasło:** `admin1234`

Te dane są opublikowane w instrukcji instalacji Parcelli i są takie same
w każdej nowej instalacji, więc każdy mógłby ich użyć. Dlatego to konto
jest zablokowane, dopóki hasło nie zostanie zmienione: po zalogowaniu
trafiasz od razu na **Zmień hasło**, z komunikatem

> To konto nadal używa domyślnego hasła z pierwszej konfiguracji. Ustaw
> nowe -- do tego czasu reszta aplikacji pozostaje zablokowana.

Każda inna strona odsyła Cię tutaj, dopóki nie zapiszesz nowego hasła.

!!! warning "Zrób to przed wszystkim innym"
    Zmień hasło natychmiast, nawet w instalacji testowej dostępnej z
    internetu. Następnie w części
    [Użytkownicy i zaproszenia](../administration/users.md) zmień nazwę
    i adres e-mail konta na dane prawdziwej osoby albo zaproś
    prawdziwych administratorów i pracuj na ich własnych kontach.

Ta sama wymuszona zmiana następuje po zresetowaniu hasła przez
administratora: tymczasowe hasło prowadzi tylko na stronę **Zmień
hasło**.

## Zmiana hasła {#change-password}

![Zmień hasło](../assets/screenshots/getting-started/change-password.png)

Otwierasz ją przyciskiem **Zmień hasło** na dole paska bocznego. Ta
strona to Twój profil: jest tu też Twój awatar i link do Twoich tokenów
API.

### Awatar {#avatar}

Awatar to małe okrągłe zdjęcie obok Twojego imienia na pasku bocznym, na
listach użytkowników i przy zadaniach. Bez niego Parcella pokazuje
zwykłą ikonę osoby.

| Pole / przycisk | Do czego służy |
|---|---|
| Pole pliku | Wybierz zdjęcie: PNG, JPEG lub WebP, najwyżej 2 MB. |
| **Prześlij** | Zapisuje zdjęcie. Widzisz **Awatar został pomyślnie przesłany.** Zły typ pliku lub zbyt duży plik są odrzucane z komunikatem. |
| **Usuń awatar** | Widoczne tylko, gdy masz awatar. Usuwa go. |

### Tokeny API dla integracji {#api-tokens-for-integrations}

**Zarządzaj** otwiera **Moje tokeny API**. Potrzebujesz tego tylko
wtedy, gdy chcesz podłączyć do Parcelli inny program (np. asystenta
AI). Zob. [Tokeny API](../administration/api-tokens.md).

### Zmiana hasła {#changing-the-password}

| Pole / przycisk | Do czego służy |
|---|---|
| **Bieżące hasło** | Twoje obecne hasło, aby nikt nie mógł go zmienić na komputerze, na którym zostawiłeś otwartą sesję. |
| **Nowe hasło** | Co najmniej 8 znaków i inne niż obecne. |
| **Potwierdź nowe hasło** | Nowe hasło jeszcze raz. |
| **Zmień hasło** | Zapisuje nowe hasło. Widzisz **Hasło zostało pomyślnie zmienione.** |

Możliwe błędy: **Bieżące hasło jest nieprawidłowe.**, **Hasła nie są
zgodne.**, **Hasło musi mieć co najmniej 8 znaków.** oraz **Nowe hasło
musi różnić się od obecnego.**

Co się dzieje po zapisaniu:

- W tej przeglądarce pozostajesz zalogowany.
- **Wszystkie inne miejsca, w których byłeś zalogowany, zostają
  wylogowane** -- inny komputer, Twój telefon albo przeglądarka, w
  której ktoś inny używa Twojego konta. Skorzystaj z tego, jeśli
  podejrzewasz, że ktoś zna Twoje hasło.
- Wszystkie Twoje **tokeny API przestają działać** (są oznaczone jako
  **zakończony**). Utwórz nowe, jeśli nadal ich potrzebujesz.

## Język {#language}

Parcella pokazuje wszystkim w stowarzyszeniu ten sam język. Nie ma
przełącznika języka dla poszczególnych użytkowników. Administrator
wybiera język w [Ustawieniach stowarzyszenia](../administration/settings.md#language)
-- English, Deutsch, Polski, Čeština, Slovenčina, Français lub
Nederlands. Strona logowania i strony zaproszeń też używają tego języka.

Formaty liczb, dat i walut to osobne ustawienie (**Region** i
**Waluta**), więc stowarzyszenie może np. używać angielskich menu z
niemieckimi formatami liczb.

## Powiązane {#related}

- [Orientacja w aplikacji](navigation.md)
- [Role, grupy i uprawnienia](roles-and-permissions.md)
- [Użytkownicy i zaproszenia](../administration/users.md) -- dla administratorów
