# Wsparcie {#support}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Parcella nie ma własnego systemu zgłoszeń. Twoje stowarzyszenie
odpowiada na e-maile i zgłoszenia z formularza kontaktowego w
helpdesku -- FreeScout, Zammad, Znuny / OTRS, osTicket, Zendesk lub
Freshdesk -- a moduł wsparcia łączy ten helpdesk z Parcellą: widzisz,
która rozmowa należy do którego członka i której działki, czytasz
rozmowę i zamieniasz ją w kartę na tablicy zadań. Odpowiedzi pisze się
zawsze w samym helpdesku.

!!! info "Kto może z tego korzystać"
    - Moduł włącza się przełącznikiem **Wsparcie (helpdesk)** w
      [Włączaniu i wyłączaniu modułów](../administration/modules.md).
      Jest **domyślnie wyłączony**, bo przechowuje dane dostępowe do
      helpdesku. Sam helpdesk wybiera i łączy administrator w
      [Integracjach](../administration/integrations.md).
    - **Rozmowy wsparcia w Parcelli:** członkowie zarządu i
      administratorzy oraz użytkownicy, których grupa nadaje **Odczyt**
      dla **Wsparcie (helpdesk)** (zob. [Grupy](../administration/groups.md)).
      **Zapis** jest potrzebny, aby połączyć rozmowę z członkiem lub
      działką.
    - **Utwórz zadanie:** tylko członkowie zarządu i administratorzy (lub
      użytkownicy w grupie z pełnym dostępem), tak jak sama tablica
      zadań.
    - **Wszyscy pozostali** i tak dostają link **Wsparcie** w nawigacji,
      gdy moduł jest włączony, a helpdesk ma adres internetowy: otwiera
      on helpdesk bezpośrednio w nowej karcie.

## Skąd pochodzą rozmowy {#where-conversations-come-from}

Parcella mniej więcej co pięć minut sprawdza w helpdesku nowe i
zmienione rozmowy. Przechowuje tylko odnośnik -- temat, klienta,
status, liczbę wiadomości oraz powiązania z członkiem, działką i
zadaniem. Same wiadomości zostają w helpdesku i są pobierane na nowo
przy każdym otwarciu rozmowy.

**Dopasowanie członków:** gdy przychodzi rozmowa, Parcella szuka
członka, do którego należy:

1. Jeśli ten klient helpdesku był już wcześniej połączony z członkiem,
   używany jest ten członek.
2. W przeciwnym razie, jeśli **dokładnie jeden** członek ma adres e-mail
   klienta, ten członek jest łączony automatycznie.
3. Jeśli kilku członków dzieli adres (np. para z jedną skrzynką) albo
   nikt go nie ma (sąsiad, dostawca), rozmowa zostaje bez członka.
   Możesz połączyć go ręcznie.

Jeśli połączony członek ma dokładnie jedną obecną działkę, ta działka
też jest łączona. Rozmowa, która ma członka -- automatycznie lub
ustawionego przez Ciebie -- nigdy nie jest później dopasowywana na nowo.

Gdy nazwisko członka zmienia się w Parcelli, jego rekord klienta w
helpdesku też zmienia nazwę, jeśli helpdesk to obsługuje.

**Statusy:** każdy helpdesk nazywa swoje stany inaczej; Parcella
pokazuje je jako `active`, `pending`, `closed`, `spam` lub `deleted`.
Rozmowy zamknięte, spam i usunięte są ukrywane na liście, w oznaczeniu
liczbowym i na panelu. Jeśli rozmowa zostanie w helpdesku otwarta
ponownie, znów się pojawia, z zachowanym powiązaniem z członkiem.

### Co obsługuje każdy helpdesk {#what-each-helpdesk-supports}

| Helpdesk | Lista rozmów i oznaczenie liczbowe | Czytanie rozmów | Formularz kontaktowy tworzy rozmowę | Synchronizacja nazwisk klientów |
|---|---|---|---|---|
| FreeScout | tak | tak | tak | tak |
| Zammad | tak | tak | tak | tak |
| Znuny / OTRS | tak | tak | tak | nie |
| osTicket | nie | nie | tak | nie |
| Zendesk | tak | tak | tak | tak |
| Freshdesk | tak | tak | tak | tak |

Z osTicket Parcella może tylko przekazywać zgłoszenia z formularza
kontaktowego na stronie; pracujesz z nimi wyłącznie w osTicket.

Pokazywane są tylko wiadomości widoczne dla klienta -- notatki
wewnętrzne zostają w helpdesku. Załączniki nie są pokazywane; aby je
zobaczyć, otwórz rozmowę w helpdesku.

## Rozmowy wsparcia {#support-conversations}

![Rozmowy wsparcia](../assets/screenshots/support/list.png)

**Wsparcie** w nawigacji otwiera listę otwartych rozmów aktywnego
helpdesku, od ostatnio zaktualizowanych. Czerwone oznaczenie obok
**Wsparcie** -- i kafelek **Otwarte rozmowy wsparcia** na
[panelu głównym](../getting-started/dashboard.md) -- liczy te same
rozmowy, niezależnie od tego, czy mają członka.

| Pole / przycisk | Do czego służy |
|---|---|
| **Otwórz w {helpdesk}** | Otwiera helpdesk w nowej karcie. Widoczne tylko, jeśli ustawiono adres internetowy helpdesku. |
| **Temat** | Temat rozmowy. Kliknij gdziekolwiek w wierszu, aby otworzyć rozmowę. |
| **Klient** | Nazwisko nadawcy albo jego adres e-mail. |
| **Członek** | Połączony członek albo „—”. |
| **Status** | `active` lub `pending` (zamknięte nie są wymieniane). |
| **Wiadomości** | Liczba wiadomości, według ostatniego raportu helpdesku. |
| **Zaktualizowano** | Kiedy rozmowa ostatnio się zmieniła w helpdesku. |
| **Zadanie** | Ikona tablicy, jeśli rozmowa jest połączona z zadaniem. |

Zamiast listy możesz zobaczyć:

- „Helpdesk nie jest jeszcze skonfigurowany. …” -- administrator musi
  go jeszcze wybrać w [Integracjach](../administration/integrations.md).
- „{helpdesk} nie potrafi wyświetlać listy rozmów przez swój interfejs.
  …” -- helpdesk to osTicket.
- „Brak jeszcze rozmów wsparcia.” -- w tej chwili nic nie jest otwarte.

## Strona rozmowy {#conversation-page}

<!-- TODO(verify): no screenshot -- the list's rows open conversations by click, not by a link, so the screenshot tool can't follow one; without a connected helpdesk the transcript would only show an error anyway. -->

Pokazuje jedną rozmowę, z jej tematem jako tytułem.

| Przycisk | Do czego służy |
|---|---|
| **Wstecz** | Wraca do listy. |
| **Otwórz w {helpdesk}** | Otwiera tę rozmowę w helpdesku -- tam na nią odpowiadasz. |

### Rozmowa {#conversation}

Wiadomości, od najstarszych, każda z autorem i godziną. Jeśli nie da
się ich wczytać, notka wyjaśnia dlaczego -- helpdesk jest nieosiągalny,
nie potrafi pokazywać rozmów (osTicket) albo „Helpdesk tej rozmowy nie
jest (już) skonfigurowany.”, gdy stowarzyszenie przeszło w międzyczasie
na inny helpdesk. „Nie udało się wczytać wiadomości.” oznacza, że
helpdesk nie zwrócił żadnych.

### Członek {#member}

Pokazuje połączonego członka (z linkiem do jego strony) albo „Nie
przypisano żadnego członka.”.

Z prawem zapisu wybierz członka i kliknij **Zapisz**:

- Członkowie z adresem e-mail klienta są wymienieni na początku,
  oznaczeni jako **sugerowany**. Jeśli kilku członków dzieli adres,
  notka prosi o wybór właściwego.
- Pod nimi wszyscy obecni członkowie.
- **-- brak --** usuwa powiązanie.

Zapisanie członka resetuje też działkę: jeśli członek ma dokładnie jedną
obecną działkę, jest ona łączona; w przeciwnym razie żadna.

### Działka {#parcel}

Widoczna, gdy połączono członka. Z prawem zapisu wybierz jedną z
obecnych działek członka albo **-- brak --** i kliknij **Zapisz**.
<!-- TODO(verify): without write permission the Parcel card is empty -- the linked parcel isn't displayed at all for read-only users. -->

### Tablica zadań {#task-board}

| Pole / przycisk | Do czego służy |
|---|---|
| **Otwórz zadanie** | Widoczne, gdy rozmowa jest połączona z zadaniem; otwiera zadanie. |
| Lista + **Utwórz zadanie** | Tworzy nową kartę na wybranej liście [tablicy zadań](tasks.md) i łączy ją z rozmową. Tytuł karty to temat; jej opis wymienia helpdesk, numer rozmowy i, jeśli połączony, członka. Tylko członkowie zarządu i administratorzy. |

Jeśli tablica zadań nie ma jeszcze list, utworzenie zadania kończy się
komunikatem „Na tablicy zadań nie ma jeszcze żadnych list”.
<!-- TODO(verify): there is a route to link an existing task to a conversation, but no form on the page uses it. -->

!!! note "Odpowiadanie odbywa się w helpdesku"
    Parcella celowo nie ma pola odpowiedzi. Kliknij **Otwórz w
    {helpdesk}** i odpowiedz tam; nowa wiadomość pojawi się w Parcelli
    przy następnym otwarciu rozmowy.

## Formularz kontaktowy na stronie {#the-website-contact-form}

Jeśli strona internetowa Twojego stowarzyszenia ma formularz
kontaktowy, może on przez Parcellę tworzyć rozmowę bezpośrednio w
helpdesku. To osobny przełącznik, **Publiczne API formularza
kontaktowego**, też domyślnie wyłączony. Konfigurację opisują
[Integracje](../administration/integrations.md).

## Powiązane {#related}

- [Integracje](../administration/integrations.md) -- wybór i podłączenie
  helpdesku
- [Tablica zadań](tasks.md) -- dalsza praca nad rozmową
- [Członkowie](members.md) -- adresy e-mail używane do dopasowania
- [Panel główny](../getting-started/dashboard.md)
