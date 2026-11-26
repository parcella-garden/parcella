# Faktury, płatności i upomnienia {#invoices-payments-and-reminders}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Gdy seria faktur zostanie zakończona, jej faktury żyją dalej. Ten
rozdział opisuje wyszukiwanie faktury, ponowne jej wysłanie, zapisywanie
wpłat i upominanie członków, którzy nie zapłacili w terminie.

!!! info "Kto może z tego korzystać"
    Część modułu **Finanse** (domyślnie wyłączonego). Oglądanie faktur,
    plików PDF i listy upomnień wymaga prawa odczytu **Finanse**.
    Zapisywanie płatności, ponowne wysyłanie e-maili i wysyłanie upomnień
    wymaga prawa zapisu; usunięcie płatności wymaga prawa usuwania.
    Członkowie zarządu i administratorzy mogą wszystko. Zob.
    [Finanse](index.md).

Faktury powstają wyłącznie przez [zakończenie serii faktur](invoice-runs.md#what-finalizing-does).
Nie można ręcznie utworzyć, edytować ani usunąć pojedynczej faktury i
nie ma funkcji anulowania ani faktury korygującej.
<!-- TODO(verify): no cancel/credit-note feature exists in the code; if a finalized invoice is wrong, the club has to handle the correction outside Parcella (e.g. record a payment with a note). Confirm the recommended workaround with the maintainers. -->

## Faktury (wszystkie serie) {#invoices-all-runs}

![Faktury](../../assets/screenshots/finances/invoice-list.png)

Otwierasz ją przyciskiem **Wszystkie faktury** na stronie
[Faktury roczne](invoice-runs.md#annual-invoices-list-of-runs). Pokazuje
każdą fakturę z każdej zakończonej serii, od najwyższego numeru
faktury. **Powrót do serii faktur** na górnym pasku prowadzi z powrotem.

**Filtr**

| Filtr | Do czego służy |
|---|---|
| **Działka** | Faktury, których numer działki zawiera ten tekst. |
| **Nr faktury** | Faktury, których numer zawiera ten tekst, np. `2026/` dla całego 2026. |
| **Odbiorca** | Faktury, których nazwy odbiorców zawierają ten tekst. |
| **Kwota od** / **Kwota do** | Kwota faktury (suma, bez opłat za upomnienia) co najmniej / najwyżej tyle. |
| **Status** | **Wszystkie**, **Otwarta**, **Częściowo opłacona** lub **Opłacona**. |
| **Filtruj** / **Wyczyść** | Stosuje filtr / czyści wszystkie filtry. |

**Tabela**

| Kolumna | Co pokazuje |
|---|---|
| **Nr faktury** | Numer faktury; kliknij, aby otworzyć [fakturę](#invoice). |
| **Działka** | Numer działki albo **Brak działki (członek)** dla faktury wystawionej bezpośrednio członkowi. |
| **Odbiorca** | Nazwy, na które wystawiono fakturę w chwili jej wystawienia. |
| **Suma** | Kwota faktury. |
| **Zapłacono** | Suma wszystkich dotychczas zapisanych płatności. |
| **Status** | **Otwarta** (na czerwono), **Częściowo opłacona** (na żółto) lub **Opłacona** (na zielono), zob. [Status płatności](#payment-status). |
| **Zapłacono dnia** | Daty wszystkich płatności, rozdzielone przecinkami. |

Jeśli nic nie pasuje: „Żadna faktura nie pasuje do tych filtrów.”

Ta sama lista, ograniczona do jednej serii i z przyciskami płatności i
PDF, jest na [stronie zakończonej serii](invoice-runs.md#invoice-run-finalized).

## Faktura {#invoice}

![Faktura](../../assets/screenshots/finances/invoice-detail.png)

Otwiera się po kliknięciu numeru faktury. Tytuł to „Faktura *numer*”.

**Górny pasek**

| Przycisk | Do czego służy |
|---|---|
| **PDF** | Otwiera PDF faktury w nowej karcie. |
| **Wyślij e-mail ponownie** | Ponownie wysyła PDF faktury e-mailem, nawet jeśli wysłano go wcześniej. Wymaga prawa zapisu. Jeśli nikt nie jest osiągalny, widzisz „Nie znaleziono dostępnego członka z adresem do faktur dla tej faktury (powiadomienia e-mail + zapisany adres e-mail).” |
| **Powrót do faktur** | Powrót do listy wszystkich faktur. |

Karta **Faktura**

| Pole | Co pokazuje |
|---|---|
| **Działka** | Numer działki albo **Brak działki (członek)**. |
| **Odbiorca** | Nazwy i adres tak, jak wydrukowano je na fakturze. Zostały ustalone przy finalizacji serii; późniejsze zmiany adresu ich nie zmieniają. Jeśli dzierżawcy mieszkają pod różnymi adresami, widzisz „Liczba egzemplarzy: *n* (po jednym na adres)” oraz nazwy i adres każdego egzemplarza. |
| **Suma** | Kwota faktury. |
| **Termin płatności** | Termin płatności serii faktur. |
| **Status** | Status płatności, a po nim „zapłacono dotychczas / razem należne”. Razem należne obejmuje opłaty za upomnienia. |

Karta **Upomnienia**: upomnienia wysłane dla tej faktury i formularz
wysłania następnego, zob. [Wysyłanie upomnienia](#sending-a-reminder).

!!! note "Gdzie są płatności?"
    Płatności zapisuje się w oknie płatności na liście faktur serii, zob.
    [Płatności](#payments). Strona faktury pokazuje wynik w wierszu
    **Status**.

### PDF faktury {#the-invoice-pdf}

PDF jest ułożony jak niemiecki list handlowy do kopert z okienkiem: logo
i nazwa stowarzyszenia na górze, adres odbiorcy tam, gdzie pokazuje go
okienko koperty, potem numer faktury, data, termin płatności i działka,
tabela pozycji (**Opis**, **Ilość**, **Cena jednostkowa**, **Razem**),
**Suma**, tekst stopki serii oraz dane stowarzyszenia (adres, bank) w
stopce strony. Te dane stowarzyszenia pochodzą z
[Ustawień stowarzyszenia](../../administration/settings.md).

Układ odpowiada normie **DIN 5008 formularz B**: adres znajduje się w
okienku koperty DL lub C6/5, a krótkie znaczniki przy lewej krawędzi
pokazują, gdzie zgiąć (na jednej trzeciej i dwóch trzecich strony) i
gdzie dziurkować. Upomnienia i listy z ogłoszeniami używają tego samego
układu.

Nazwa pliku zaczyna się od daty wystawienia i numeru działki (lub
nazwiska członka), a po nich numer faktury. Faktura z jednym egzemplarzem
na adres ma w swoim PDF wszystkie egzemplarze, każdy na osobnych
stronach.

## Płatności {#payments}

Płatność to pieniądze otrzymane za fakturę. Możesz ją zapisać na dwa
sposoby:

- **Ręcznie:** na [stronie zakończonej serii](invoice-runs.md#payment-dialog)
  kliknij **Płatność** obok faktury, wpisz **Kwota**, **Zapłacono
  dnia**, opcjonalnie **Notatka** i **Konto**, i kliknij **Dodaj
  płatność**.
- **Z wyciągu bankowego:** na [stronie księgowań konta](bank-accounts.md#bookings-of-an-account)
  dodaj księgowanie lub zaimportuj plik CSV i wybierz pasującą otwartą
  fakturę. Parcella zapisze wtedy płatność za Ciebie, z już ustawionym
  kontem.

Faktura może mieć dowolną liczbę płatności, więc płatności częściowe i
raty nie stanowią problemu. Aby poprawić błędną płatność, usuń ją (ikona
kosza w oknie płatności, wymaga prawa usuwania) i wpisz ją ponownie.

!!! tip "Zapłacono dnia decyduje o roku"
    [Zestawienie księgowe](bookkeeping.md#accounting-statement) liczy
    przychód według daty **Zapłacono dnia**, nie daty faktury. Faktura z
    2026 zapłacona w styczniu 2027 to przychód 2027.

### Status płatności {#payment-status}

Status jest za każdym razem obliczany z płatności, więc nigdy nie jest
nieaktualny:

| Status | Kiedy |
|---|---|
| **Otwarta** | Jeszcze nic nie zapłacono. |
| **Częściowo opłacona** | Coś zapłacono, ale mniej niż kwota faktury plus wszystkie opłaty za upomnienia. |
| **Opłacona** | Płatności osiągają kwotę faktury plus wszystkie opłaty za upomnienia (lub więcej). |

Nadpłaty są przyjmowane i po prostu pokazywane jako **Opłacona**;
Parcella nie prowadzi salda nadpłat.

## Upomnienia {#reminders}

![Upomnienia](../../assets/screenshots/finances/reminders.png)

Otwierasz je przez **Finanse → Upomnienia** albo kartę **Upomnienia** na
panelu. Lista **Zaległe faktury** pokazuje każdą fakturę, która nie jest
w pełni zapłacona i której termin płatności serii minął, od najdłużej
zaległych. To lista robocza skarbnika: otwórz każdą fakturę i zdecyduj,
czy wysłać upomnienie.

| Kolumna / przycisk | Co pokazuje |
|---|---|
| **Działka** | Numer działki. Pusta dla faktury członkowskiej. |
| **Odbiorca** | Nazwy odbiorców. |
| **Nr faktury** | Numer faktury. |
| **Termin płatności** | Termin płatności serii. |
| **Zaległość** | Ile dni minęło od terminu, np. „14 dni”. |
| **Kwota do zapłaty** | Co jest jeszcze należne: kwota faktury plus opłaty za upomnienia minus płatności. |
| **Wysłane upomnienia** | Ile upomnień wysłano, z datą ostatniego, albo „Jeszcze nie wysłano”. |
| **Otwórz** | Otwiera fakturę, z której wysyłasz upomnienie. |

Jeśli nic nie jest zaległe: „Brak zaległych faktur — nic do
przypomnienia.”

Faktura znika z tej listy, gdy tylko zostanie w pełni zapłacona.

### Wysyłanie upomnienia {#sending-a-reminder}

Na stronie [faktury](#invoice) karta **Upomnienia** pokazuje każde już
wysłane upomnienie:

| Kolumna | Co pokazuje |
|---|---|
| „Upomnienie nr *n*” | Poziom upomnienia: pierwsze upomnienie to nr 1, następne nr 2 itd. |
| Data | Kiedy zostało utworzone. |
| Doręczenie | „Wysłano e-mailem”, „Do druku/wysyłki pocztowej”, jeśli nie dało się wysłać e-mailem, albo „Wysłano e-mailem, a do tego egzemplarze do druku/wysyłki pocztowej”, jeśli niektóre adresy dostały je e-mailem, a inne potrzebują listu. |
| Opłata | Opłata naliczona z tym upomnieniem, jeśli jest. |
| Ikona PDF | Otwiera PDF upomnienia w nowej karcie -- stąd wydrukujesz je do wysyłki pocztowej. Zawiera listy do wysłania pocztą, po jednym na adres dla osób bez e-maila (wszystkie egzemplarze, jeśli każdy dostał e-mail). |

Jeśli żadnego jeszcze nie wysłano: „Nie wysłano jeszcze żadnych
upomnień.”

Pod listą, dopóki faktura nie jest w pełni zapłacona i masz prawo
zapisu:

| Pole | Do czego służy |
|---|---|
| **Opłata (opcjonalnie)** | Opłata za upomnienie, np. `5,00`. Doliczana do kwoty należnej z faktury. Zostaw puste, jeśli bez opłaty. |
| **Wiadomość (opcjonalnie)** | Krótki tekst drukowany na dole upomnienia. |
| **Wyślij upomnienie** | Tworzy następne upomnienie i je doręcza. |

Co robi **Wyślij upomnienie**: „Generuje kolejne przypomnienie jako PDF
-- opłata (jeśli podana) zostaje doliczona do kwoty należnej. Wysyła je
e-mailem, jeśli członek wyraził zgodę i ma zapisany adres, w przeciwnym
razie przygotowuje je do druku/wysyłki pocztowej.”

- Upomnienie ma zawsze poziom o jeden wyższy niż poprzednie. Nie ma
  stałych etapów upominania; Twoje stowarzyszenie decyduje, ile upomnień
  wysłać i kiedy.
- E-mail trafia do tej samej osoby, do której trafiłaby faktura (zob.
  [kto dostaje e-mail](invoice-runs.md#delivery)), z tematem
  „Upomnienie nr *n* dotyczące faktury *numer* — *nazwa
  stowarzyszenia*” i załączonym PDF.
- Jeśli e-maila nie da się wysłać, upomnienie zostaje zachowane i
  oznaczone „Do druku/wysyłki pocztowej”. Wydrukuj je przez ikonę PDF.

PDF upomnienia ma nagłówek „Upomnienie o zapłatę nr *n*”, odnosi się do
faktury i jej daty oraz wymienia **Kwota pierwotna**, **Dotychczas
zapłacono**, **Poprzednie opłaty za upomnienia** i **Opłata za to
upomnienie** (wiersze opłat tylko wtedy, gdy jest opłata), kwotę teraz
należną, Twoją wiadomość i zdanie końcowe z prośbą o zapłatę.

!!! warning "Opłat nie można usunąć"
    Upomnienia i jego opłaty nie można usunąć ani zmienić po wysłaniu.
    Sprawdź opłatę dwa razy, zanim klikniesz **Wyślij upomnienie**.
    Jeśli w **Opłata (opcjonalnie)** wpiszesz coś, co nie jest liczbą,
    upomnienie zostanie wysłane bez opłaty.

## Powiązane {#related}

- [Serie faktur](invoice-runs.md) -- skąd pochodzą faktury.
- [Rachunki bankowe i księgowania](bank-accounts.md) -- zapisywanie
  płatności z wyciągu bankowego.
- [Roczne fakturowanie](../../guides/annual-invoicing.md)
- [Dziennik e-maili](../../administration/email-log.md) -- sprawdź, czy
  serwer pocztowy przyjął e-mail z fakturą lub upomnieniem.
