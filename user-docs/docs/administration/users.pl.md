# Użytkownicy i zaproszenia {#users-and-invitations}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Tutaj decydujesz, kto może logować się do Parcelli. Nowe osoby są
zapraszane e-mailem i same ustawiają hasło; Ty wybierasz, do których
grup należą.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → Użytkownicy**.

*Użytkownik* to konto logowania -- członek zarządu, skarbnik, osoba
odczytująca liczniki. To nie to samo co *członek* stowarzyszenia:
większość działkowców to członkowie, którzy nigdy nie dostają konta
użytkownika.

## Zarządzanie użytkownikami {#user-management}

![Zarządzanie użytkownikami](../assets/screenshots/administration/users.png)

Strona ma po lewej formularz zaproszenia, a po prawej listę kont.
Komunikaty o tym, co właśnie zrobiłeś, pojawiają się na górze.

### Zaproś użytkownika {#invite-user}

| Pole / przycisk | Do czego służy |
|---|---|
| **Adres e-mail** | Adres e-mail nowej osoby. Staje się jej loginem. |
| **Grupy** | Zaznacz grupy, do których ma należeć osoba. Jej dostęp pochodzi wyłącznie z tych grup -- zob. [Grupy](groups.md). Jeśli nie ma jeszcze grup, widzisz **Nie ma jeszcze żadnych grup.** z linkiem **Utwórz jedną**. |
| **Wyślij zaproszenie** | Wysyła e-mail z osobistym linkiem. Link jest ważny przez **7 dni**. |

Co się dzieje:

- Osoba dostaje e-mail **Zaproszenie do Parcella** z przyciskiem
  **Przyjmij zaproszenie**. Sama wybiera imię i hasło (zob.
  [Pierwsze logowanie](../getting-started/first-login.md#getting-an-account-the-invitation))
  i zostaje dodana do zaznaczonych grup.
- Jeśli adres należy już do konta, widzisz **Adres e-mail już
  zarejestrowany**.
- Jeśli dla adresu istnieje już oczekujące zaproszenie, stare przestaje
  działać i liczy się tylko nowe.
- Jeśli nie zaznaczysz żadnej grupy, osoba po przyjęciu może tylko
  przeglądać członków i działki. Grupy możesz dodać później.

!!! warning "E-mail musi działać"
    Zaproszenia wymagają działającego serwera pocztowego (zob.
    [Ustawienia stowarzyszenia](settings.md#email-smtp)). Jeśli serwer
    pocztowy odrzuci e-mail, strona mówi o tym zamiast **Zaproszenie
    wysłane**: „Zaproszenie dla … zostało zapisane, ale nie udało się
    wysłać e-maila. Sprawdź ustawienia e-mail i Dziennik e-maili, a
    następnie wyślij zaproszenie ponownie.” Zaproszenie zostaje w
    **Oczekujące zaproszenia**; gdy ustawienia poczty zaczną działać,
    użyj **Wyślij zaproszenie ponownie**. [Dziennik e-maili](email-log.md)
    pokazuje przyczynę podaną przez serwer pocztowy.

### Oczekujące zaproszenia {#pending-invitations}

Widoczne pod formularzem, dopóki zaproszenia czekają na przyjęcie. Każdy
wiersz pokazuje adres, zaznaczone grupy (albo **Nie wybrano żadnych
grup**), **Ważne do** z datą oraz oznaczenie **oczekujące**.

| Przycisk | Do czego służy |
|---|---|
| **Wyślij zaproszenie ponownie** (okrągłe strzałki) | Wysyła e-mail jeszcze raz i daje linkowi kolejne 7 dni od dziś. Link z pierwszego e-maila nadal działa. Widzisz **Zaproszenie wysłane ponownie**. |
| **Usuń zaproszenie** (kosz) | Po potwierdzeniu zaproszenie zostaje usunięte, a jego link przestaje działać. |

Przyjęte zaproszenia znikają z listy; osoba pojawia się wtedy w
**Zarejestrowani użytkownicy**.

### Zarejestrowani użytkownicy {#registered-users}

| Kolumna / przycisk | Co pokazuje lub robi |
|---|---|
| **Imię i nazwisko** | Awatar i imię. |
| **E-mail** | Adres logowania. |
| **Grupy** | Grupy, do których należy konto. Starsze konta bez grup pokazują swoją rolę, **Administrator** lub **Zarząd**; w przeciwnym razie **–**. |
| **Status** | **aktywny** lub **nieaktywny**. |
| **Edytuj** (ołówek) | Otwiera [Edytuj użytkownika](#edit-user). |
| **Dezaktywuj** / **Aktywuj** (przełącznik) | Jednym kliknięciem wyłącza lub ponownie włącza konto. Nie jest pokazywany dla Twojego własnego konta, które zamiast tego jest oznaczone **Ja**. |

**Dezaktywacja** konta od razu odcina tej osobie dostęp -- także na
każdym komputerze, na którym jest właśnie zalogowana. Wszystko, co
utworzyła lub zatwierdziła, zostaje, z jej nazwiskiem. Aktywuj konto
ponownie, a będzie mogła zalogować się starym hasłem.

Nie możesz dezaktywować samego siebie ani ostatniego konta, które może
otworzyć obszar administracji.

## Edytuj użytkownika {#edit-user}

![Edytuj użytkownika](../assets/screenshots/administration/user-edit.png)

**Anuluj** na górze wraca do listy bez zapisywania.

### Awatar {#avatar}

Tak samo jak we własnym profilu użytkownika: wybierz plik PNG, JPEG lub
WebP o rozmiarze najwyżej 2 MB i kliknij **Prześlij** albo **Usuń
awatar**, aby go usunąć. Przydatne dla osób, które same nie przesyłają
zdjęcia.

### Edytuj użytkownika {#edit-user_1}

| Pole / przycisk | Do czego służy |
|---|---|
| **Imię i nazwisko** | Wymagane. |
| **Adres e-mail** | Wymagany; to login, więc powiedz osobie, gdy go zmienisz. Nie może należeć do innego konta (**Adres e-mail już zarejestrowany**). |
| **Rola** | Widoczna tylko dla starszych kont, które nadal mają rolę **Administrator** lub **Zarząd**, z notką *Dostęp tego konta wynika z jego roli, a nie z przynależności do grupy.* Nie można jej tu edytować. |
| **Zapisz zmiany** | Zapisuje imię i e-mail. Na liście widzisz **Użytkownik zaktualizowany**. |

### Usuń starą rolę {#remove-legacy-role}

Tylko dla kont z rolą **Administrator** lub **Zarząd**. **Usuń starą
rolę** odbiera rolę; od tej chwili dostęp konta pochodzi wyłącznie z
jego grup, jak w każdym nowszym koncie.

!!! warning "Najpierw dodaj grupy"
    Bez grupy konto w chwili kliknięcia spada do podstawowego dostępu
    (odczyt członków i działek). Byłego **Administratora** najpierw dodaj
    do grupy z **Dostęp do panelu administracyjnego**; **Zarząd** do
    grupy z **Pełny dostęp do każdego modułu**. Parcella odmawia
    odebrania roli ostatniemu administratorowi.

### Grupy {#groups}

Pokazuje każdą grupę. **Dodaj** dodaje konto do tej grupy, **Usuń**
usuwa je z niej. Zmiana działa od razu -- nie trzeba klikać **Zapisz
zmiany**.

### Strefa zagrożenia {#danger-zone}

Nie jest pokazywana, gdy edytujesz własne konto.

| Przycisk | Do czego służy |
|---|---|
| **Dezaktywuj** / **Aktywuj** | Jak na liście: od razu odcina dostęp, nic nie jest usuwane. |
| <a id="reset-password"></a>**Resetuj hasło** | Dla kogoś, kto zapomniał hasła. Po potwierdzeniu Parcella tworzy **hasło tymczasowe** i pokazuje je **raz**, z przyciskiem **Kopiuj**. Przekaż je osobie (telefonicznie, osobiście). Jej stare hasło przestaje działać, zostaje wylogowana wszędzie, a przy następnym logowaniu musi ustawić nowe hasło. Jeśli konto jest dezaktywowane, zostaniesz przypomniany, aby je aktywować. |
| **Usuń trwale** | Po potwierdzeniu całkowicie usuwa konto. Możliwe tylko dla kont, które nigdzie nie zostawiły śladu -- zwykle konta utworzonego przez pomyłkę i nigdy nieużywanego. |

Do zmiany własnego hasła użyj zamiast tego **Zmień hasło** na pasku
bocznym.

Gdy osoba zrobiła w Parcelli cokolwiek -- utworzyła rekord, zatwierdziła
wniosek, wpisała odczyt licznika -- konta nie można już usunąć i
widzisz *Ten użytkownik ma historię aktywności ... Zamiast tego
dezaktywuj konto.* Dzięki temu dokumentacja stowarzyszenia pozostaje
kompletna: nawet po latach widać, kto co zrobił.

## Powiązane {#related}

- [Grupy](groups.md)
- [Role, grupy i uprawnienia](../getting-started/roles-and-permissions.md)
- [Pierwsze logowanie i Twoje konto](../getting-started/first-login.md)
- [Tokeny API](api-tokens.md)
