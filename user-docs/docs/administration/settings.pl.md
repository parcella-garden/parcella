# Ustawienia stowarzyszenia {#club-settings}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Strona ustawień zawiera dane podstawowe stowarzyszenia i przełączniki
obowiązujące w całej instalacji: język, logo, serwer e-mail, dane
finansowe i więcej.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → Ustawienia**.

![Ustawienia stowarzyszenia](../assets/screenshots/administration/settings.png)

## Jak działa strona {#how-the-page-works}

Strona to kolumna kart. Każda karta jest zwinięta; kliknij jej
nagłówek, aby ją otworzyć. Otwarcie jednej karty zwija pozostałe.

| Element | Do czego służy |
|---|---|
| **Szukaj ustawień...** | Wpisz słowo, np. „logo” albo „IBAN”. Karty, które je zawierają, otwierają się, a słowo jest wyróżnione; wszystkie inne karty są ukryte. Jeśli nic nie pasuje, widzisz **Żadne ustawienia nie pasują do wyszukiwania.** |
| **Zapisz ustawienia** | Na górze i na dole strony. Zapisuje **wszystkie karty naraz**, niezależnie od tego, którą zmieniłeś. Widzisz **Ustawienia zapisane.** |

!!! warning "Jeden przycisk zapisu dla wszystkiego"
    Zmiany są zapisywane dopiero po kliknięciu **Zapisz ustawienia**.
    Jeśli wcześniej opuścisz stronę, przepadną.

Karty od góry do dołu:

## Język {#language}

Język całej instalacji: menu, przyciski, komunikaty, strona logowania
oraz e-maile i pliki PDF tworzone przez Parcellę. Wszyscy widzą ten sam
język; nie ma osobistego ustawienia języka.

Do wyboru: **Deutsch**, **English**, **Polski**, **Čeština**,
**Slovenčina**, **Français** i **Nederlands**. Nowa instalacja startuje
po angielsku.

Tam, gdzie tekst nie został jeszcze przetłumaczony na wybrany język,
Parcella pokazuje tekst angielski.

Język nie zmienia wyglądu liczb, dat i kwot -- za to odpowiada karta
**Region i waluta**.

## Branding {#branding}

| Pole | Do czego służy |
|---|---|
| **Logo stowarzyszenia** | Pokazuje obecne logo (albo ikonę Parcelli). Wybierz nowy plik -- PNG, JPEG, WebP lub SVG, najwyżej 2 MB -- aby je zastąpić. Logo pojawia się na stronie logowania, na górze paska bocznego i w nagłówku generowanych plików PDF. |
| **Usuń logo (powrót do domyślnej ikony)** | Widoczne tylko, gdy logo jest przesłane. Zaznacz i zapisz, aby wrócić do ikony Parcelli. |

Zły typ pliku lub zbyt duży plik jest odrzucany z komunikatem; reszta
strony i tak zostaje zapisana.

## Region i waluta {#region-currency}

| Pole | Do czego służy |
|---|---|
| **Region** | Jak zapisywane są liczby i adresy -- separator tysięcy, przecinek lub kropka dziesiętna, czy kod pocztowy stoi przed miejscowością, czy po niej. Decyduje też o strefie czasowej kanałów kalendarza. Do wyboru: Niemcy, Wielka Brytania, Francja, Holandia, Polska, Czechy, Słowacja. Domyślnie: Niemcy. |
| **Waluta** | Symbol waluty i jego położenie („19,99 €” lub „£19.99”). Do wyboru: euro (€), funt brytyjski (£), złoty polski (zł), korona czeska (Kč). Domyślnie: euro. |

Oba są niezależne od języka: stowarzyszenie mówiące po niderlandzku może
mieć niderlandzkie menu z kwotami w euro, a instalacja po angielsku może
używać niemieckich formatów liczb.

## Moduły funkcjonalne {#feature-areas}

Przełączniki włączające i wyłączające moduły. Szczegółowo opisane w
[Włączaniu i wyłączaniu modułów](modules.md).

## Kolejność nawigacji {#navigation-order}

Decyduje o kolejności pozycji na pasku bocznym wszystkich osób. Każda
pozycja ma pole liczbowe: **Panel główny**, **Członkowie**, **Działki**,
**Wsparcie**, **Wnioski zakupowe**, **Prace społeczne**, **Woda**,
**Prąd**, **Ubezpieczenia**, **Kalendarz**, **Ogłoszenia**,
**Inwentarz**, **Tablica zadań**, **Finanse**, **Kandydaci**,
**Kontakty zewnętrzne**, **Raporty**, **Notatki**, **Procesy**.

Niższe liczby są pierwsze. Fabrycznie liczby to 100, 200, 300 ... w
kolejności jak wyżej, więc możesz przesunąć pozycję między dwie inne,
dając jej np. 150. Puste pola wracają do liczby domyślnej; wszystko, co
nie jest liczbą całkowitą, jest ignorowane.

**Administracja** nie ma na liście: jest zawsze ostatnia.

## Aktualizacje {#updates}

| Pole | Do czego służy |
|---|---|
| **Automatycznie sprawdzaj dostępność aktualizacji** | Domyślnie włączone. Parcella pyta wtedy co kilka godzin GitHub, czy wydano nowszą wersję, i pokazuje powiadomienie na stronie [System](system.md). Nie są wysyłane żadne dane o stowarzyszeniu. Wyłącz, jeśli Twój serwer nie może łączyć się z internetem; strona System nie pokazuje wtedy żadnych informacji o aktualizacjach. |

## Kandydaci {#applicants}

Istotne tylko, gdy korzystasz z modułu [Kandydaci](../modules/applicants.md).

| Pole | Do czego służy |
|---|---|
| **Usuwaj zgłoszenia po (miesiącach)** | Każde zgłoszenie, którego status nie zmienił się przez tyle miesięcy, zostaje **usunięte na zawsze**, niezależnie od statusu, bez powiadamiania kogokolwiek. Liczone od ostatniej zmiany statusu albo od daty zgłoszenia, jeśli status nigdy się nie zmienił. Zostaw puste lub wpisz 0, aby przechowywać zgłoszenia, dopóki nie usuniesz ich ręcznie. Przydatne ze względu na ochronę danych. |
| **Treść e-maila do nowych kandydatów** | Tekst używany przez **Skontaktuj się z kandydatem** przy nowym zgłoszeniu; przed każdym wysłaniem można go jeszcze zmienić. `{name}` zastępowane jest imieniem kandydata, `{club}` nazwą stowarzyszenia. Zostaw puste, aby użyć wbudowanego tekstu, pokazanego na szaro. |

## Dziennik e-maili {#email-log}

| Pole | Do czego służy |
|---|---|
| **Przechowuj wpisy dziennika e-maili (dni)** | Jak długo [Dziennik e-maili](email-log.md) przechowuje wpisy. Starsze są usuwane automatycznie, bo adresy odbiorców to dane osobowe. Domyślnie 90 dni, możliwe od 1 do 3650. |

## Dane stowarzyszenia {#club-data}

| Pole | Do czego służy |
|---|---|
| **Nazwa stowarzyszenia** | Pokazywana na górze paska bocznego, na stronie logowania i na drukowanych dokumentach. Pusta: „Parcella”. |
| **Ulica**, **Kod pocztowy**, **Miejscowość** | Adres stowarzyszenia w stopce generowanych plików PDF (faktury, ogłoszenia, listy). |
| **Numer stowarzyszenia**, **Sąd rejestrowy** | Też drukowane w stopkach PDF, bo stowarzyszenia zarejestrowane w Niemczech muszą je podawać. |

## Członkowie zarządu {#board-members}

Którzy członkowie są obecnie w zarządzie. Ich nazwiska są drukowane w
stopce generowanych dokumentów.

| Element | Do czego służy |
|---|---|
| **Członkowie zarządu** / **Pokaż listę** | Rozwija listę wszystkich obecnych członków, każdy z polem wyboru. **Ukryj listę** zwija ją z powrotem. |
| **Szukaj…** | Zawęża listę do pasujących nazwisk. **Brak wyników**, jeśli żadne nie pasuje. |
| **Zaznacz wszystkich** / **Odznacz wszystkich** | Zaznacza lub odznacza każdego widocznego członka. |

Członek, który opuszcza stowarzyszenie, automatycznie znika z
drukowanej listy.

## Powierzchnie (m²) {#areas-sqm}

Teren stowarzyszenia, podzielony tak, jak zwykle raportują go niemieckie
stowarzyszenia ogrodów działkowych.

| Pole | Do czego służy |
|---|---|
| **Powierzchnia całkowita (m²)** | Cały teren stowarzyszenia. Wpisz ją sam. |
| **Powierzchnia A (działki, m²)** | Obliczana, nie można jej edytować: suma powierzchni wszystkich działek, wydzierżawionych lub wypowiedzianych. Usunięte działki i tereny wspólne się nie liczą. Ta sama liczba co **Powierzchnia całkowita (m²)** na [Panelu głównym](../getting-started/dashboard.md). |
| **Powierzchnia B (wspólna, m²)** | Obliczana: powierzchnia całkowita minus powierzchnia A minus powierzchnia C. |
| **Powierzchnia C (miejska, m²)** | Wpisz ją sam. |

Te liczby są używane, gdy [fakturowanie](../modules/finances/invoice-runs.md)
dzieli koszty według udziału każdej działki w powierzchni wspólnej.

## Ustawienia finansowe {#finance-settings}

Używane przez moduł [Finanse](../modules/finances/index.md).

| Pole | Do czego służy |
|---|---|
| **Nazwa banku**, **IBAN**, **BIC**, **Posiadacz konta** | Drukowane w stopce każdej faktury, aby członkowie wiedzieli, dokąd płacić. |
| **Następny numer faktury (nadpisanie)** | Zwykle puste: numery po prostu się kontynuują. Wpisz liczbę, aby najbliższe fakturowanie -- w dowolnym roku -- zaczęło się od niej. Parcella sprawdza tylko, czy numer nie jest zajęty, gdy to fakturowanie zostaje sfinalizowane. Pole opróżnia się samo po użyciu. |
| **Format numeru faktury** | Jak wyglądają numery faktur. `{number}` jest wymagane, `{year}` opcjonalne; każdy inny tekst jest używany dosłownie, np. `R-{year}-{number}`. Pod polem widzisz **Obecnie używany:** z przykładem; **(domyślny, nic własnego nie zapisano)** oznacza, że obowiązuje domyślny `{year}/{number}`. Pole podpowiada kilka przykładów. |

Format dotyczy tylko faktur tworzonych od teraz. Numery już nadane nigdy
się nie zmieniają. Nieprawidłowy format nie jest zapisywany; widzisz
**Nieprawidłowy format numeru faktury -- musi zawierać dokładnie jeden
{number} (opcjonalnie także {year}), żadnych innych symboli
zastępczych.**

## E-mail (SMTP) {#email-smtp}

Każdy e-mail wysyłany przez Parcellę -- zaproszenia, powiadomienia,
ogłoszenia, faktury -- wychodzi przez ten serwer pocztowy. Parcella nie
czyta żadnej skrzynki.

| Pole | Do czego służy |
|---|---|
| **Serwer SMTP** | Adres serwera pocztowego od Twojego dostawcy poczty. |
| **Port SMTP** | Zwykle 587 (albo to, co podaje dostawca). |
| **Użytkownik SMTP** | Login do serwera pocztowego, często adres e-mail. |
| **Hasło SMTP** | Pokazywane jako **Jeszcze nie ustawione** lub **•••••••• (ustawione – wpisz ponownie, aby zmienić)**. Zostaw puste, aby zachować zapisane hasło; wpisz nowe, aby je zastąpić. Przechowywane w postaci zaszyfrowanej. |
| **E-mail nadawcy** | Adres, z którego przychodzą e-maile. |

!!! tip "Sprawdź, czy działa"
    Po zapisaniu zaproś siebie na drugi adres albo wyślij dowolny
    e-mail, a potem zajrzyj do [Dziennika e-maili](email-log.md).
    **Błąd** z komunikatem mówi, co nie spodobało się serwerowi
    pocztowemu.

Jeśli te pola są puste, Parcella używa ustawień poczty, które osoba
instalująca mogła wpisać do konfiguracji serwera.

Parcella szyfruje połączenie z serwerem pocztowym za pomocą STARTTLS,
metody zwykle używanej na porcie 587. Na stronie ustawień nie ma na to
przełącznika; można to zmienić tylko w konfiguracji serwera.
<!-- TODO(verify): whether mail servers that only offer implicit TLS on port 465 work at all. -->

## Powiązane {#related}

- [Włączanie i wyłączanie modułów](modules.md)
- [Integracje](integrations.md)
- [Konfiguracja nowego stowarzyszenia](../guides/new-club-setup.md)
