# Słowniczek {#glossary}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Pojęcia stowarzyszenia i pojęcia Parcelli, w kolejności alfabetycznej.

Rozdziały odsyłają bezpośrednio do hasła, np. `glossary.md#deposit`.

## Adres do faktury { #invoice-address }

Dzierżawca działki, na którego adres trafiają faktury działki --
**Użyj jako adresu do faktury** przy dzierżawie. Może go mieć kilku
dzierżawców jednej działki; działka i tak dostaje jedną fakturę.
Działka bez adresu do faktury nie dostaje faktury.

## Aktywna, wypowiedziana, wspólna, usunięta { #parcel-status }

Cztery statusy [działki](#parcel):

- **aktywna** -- zwykła działka, zwykle komuś wydzierżawiona.
- **wypowiedziana** -- dzierżawca złożył [wypowiedzenie](#notice-of-termination)
  i działka czeka na nowego dzierżawcę. Tylko wypowiedziane działki
  można przekazać [kandydatowi](#applicant).
- **wspólna** -- teren stowarzyszenia prowadzony jako działka (ścieżki,
  plac zabaw), nigdy niewydzierżawiany. Nie wlicza się do powierzchni
  wydzierżawionej.
- **usunięta** -- już nieużywana, ale zachowana wraz z historią.

## Były, obecny i przyszły dzierżawca { #former-tenant }

[Dzierżawa](#tenancy) jest **obecna**, dopóki trwa, **przyszła**, jeśli
zaczyna się w przyszłości (po przekazaniu z datą w przyszłości), i
**była**, gdy się zakończy. Byli dzierżawcy pozostają na stronie działki
w sekcji **Byli dzierżawcy**; tylko obecni (i przyszli) dzierżawcy mogą
być [adresem do faktury](#invoice-address).

## Członek { #member }

Osoba należąca do stowarzyszenia. Zwykle też
[dzierżawca](#tenant), ale niekoniecznie (członkowie wspierający lub
honorowi). Członek liczy się jako aktywny do swojej daty **Członek do**.

## Dane przykładowe { #sample-data }

Zmyśleni członkowie, działki i inne rekordy, które możesz dodać do nowej
instalacji, aby wypróbować Parcellę, i usunąć jednym kliknięciem. Zob.
[Dane przykładowe](administration/sample-data.md).

## Działka { #parcel }

Jedna działka ogrodowa, identyfikowana przez **Numer działki**.

## Dzierżawa { #tenancy }

Dzierżawa działki przez członka, od daty początkowej do opcjonalnej
daty końcowej. Zakończenie dzierżawy zachowuje ją jako historię; jedną
działkę może dzielić kilku członków. Zob. też
[były dzierżawca](#former-tenant).

## Dzierżawca { #tenant }

Członek, który ma [dzierżawę](#tenancy) działki.

## Grupa { #group }

Zestaw [uprawnień](#permission) w Parcelli -- odczyt, zapis lub
usuwanie dla każdego [modułu](#module) albo pełny dostęp -- który
nadajesz kontom użytkowników. Nowi użytkownicy dostają dostęp wyłącznie
przez grupy. Zob. [Grupy](administration/groups.md).

## Kandydat { #applicant }

Ktoś, kto ubiegał się o ogród i jest na
[liście oczekujących](#waiting-list). Kandydaci są oddzieleni od
[członków](#member): członkami stają się dopiero, gdy rzeczywiście
dostaną działkę. Zob. [Kandydaci](modules/applicants.md).

## Katalog pozycji { #item-catalog }

Twoja lista pozycji faktur wielokrotnego użytku (dzierżawa, woda,
ubezpieczenie, ...), wybieranych do [serii faktur](#invoice-run) w
każdym roku. Znajdziesz ją w **Finanse → Przegląd → Katalog pozycji**.

## Kaucja { #deposit }

Kwota, którą nowy dzierżawca płaci przy przejęciu działki, a którą
stowarzyszenie przechowuje i zwraca -- albo zatrzymuje jej część -- gdy
dzierżawca odchodzi. Parcella nie ma osobnej funkcji kaucji: zapisz
kwotę i datę w [procesie](#process) przekazania, a pieniądze w
**Finanse**. Zob.
[Przekazanie działki](guides/parcel-handover.md#7-deposit-and-money).

## Kontakt zewnętrzny { #external-contact }

Dostawca, rzemieślnik, urząd lub inna organizacja, z którą
stowarzyszenie ma do czynienia -- firma i/lub osoba kontaktowa. Nie jest
członkiem. Zob. [Kontakty zewnętrzne](modules/external-contacts.md).

## Legalizacja { #calibration }

Liczniki wody i prądu mogą służyć do rozliczeń tylko do wygaśnięcia
legalizacji. Parcella zapisuje rok jako **Legalizacja do** i oznacza
liczniki po terminie jako **Legalizacja wygasła**. Zwykle rozwiązaniem
jest [wymiana licznika](guides/meter-readings.md#a-meter-is-replaced).

## Licznik { #meter }

Fizyczny licznik wody lub prądu, z numerem, rokiem legalizacji i
odczytem początkowym. [Punkt pomiarowy](#metering-point) ma naraz jeden
licznik; po wymianie stary jest zachowywany jako dawny licznik.

## Licznik główny { #main-meter }

Licznik, w którym stowarzyszenie przejmuje wodę lub prąd od dostawcy.
Jego zużycie powinno mniej więcej równać się sumie wszystkich liczników
działek i stowarzyszenia; Parcella ostrzega, jeśli działki razem zużyły
więcej.

## Lista oczekujących { #waiting-list }

[Kandydaci](#applicant) czekający na działkę, w kolejności zgłoszeń. W
Parcelli: **Kandydaci** z filtrem **Otwarte**.

## Mnożnik { #factor }

Mnożnik w [punkcie pomiarowym](#metering-point) dla liczników, które
pokazują tylko ułamek rzeczywistej wartości (np. 20 dla licznika prądu
z przekładnikami prądowymi). Odczyty wpisuje się tak, jak są
wyświetlane; rozliczenie mnoży je przez mnożnik. Zwykle 1.

## Moduł { #module }

Obszar funkcji Parcelli -- Prace społeczne, Woda, Finanse, Procesy itd.
-- który można włączyć lub wyłączyć dla stowarzyszenia w **Administracja
→ Ustawienia → Moduły funkcjonalne**. Wyłączenie go ukrywa; jego dane
zostają. Zob. [Włączanie i wyłączanie modułów](administration/modules.md).

## Obciążenia publiczne { #public-burdens }

Opłaty, które właściciel gruntu przenosi na stowarzyszenie -- podatek od
nieruchomości, oczyszczanie ulic i podobne opłaty gminne -- zwykle za
metr kwadratowy. Stowarzyszenie przenosi je na działki, łącznie z
udziałem za teren wspólny. W aplikacji: **Obciążenia publiczne (własna
powierzchnia + udział w powierzchni wspólnej)**: własna powierzchnia
działki plus jej równy udział w [powierzchni B](#areas), razy wpisana
stawka.

## Obowiązkowe godziny { #mandatory-hours }

Godziny prac społecznych, które działka lub członek jest winien
stowarzyszeniu każdego roku, zgodnie z uchwałą walnego zebrania.
Nieprzepracowane godziny opłaca się według stawki godzinowej. Parcella
zalicza do nich odbyte [terminy prac](#work-session),
[patronaty](#sponsorship) i [przekazania godzin](#hours-transfer), a
brakujące godziny można zafakturować w rocznej
[serii faktur](#invoice-run). Zob. [Prace społeczne](modules/work-hours.md).

## Odbiór działki { #inspection }

Obejście działki przez zarząd, gdy dzierżawca odchodzi, aby zanotować
usterki przed [wyceną](#valuation). Śledzone w [procesie](#process)
przekazania.

## Odczyt { #reading }

Wartość na wyświetlaczu licznika. Parcella przechowuje jeden odczyt na
[licznik](#meter) i rok; zużycie w roku to ten odczyt minus poprzedni.

## Ogólna składka { #general-levy }

Jednorazowa kwota, którą stowarzyszenie musi zebrać od wszystkich
działek razem -- rachunek prawnika, naprawa, wzrost składki
ubezpieczeniowej -- dzielona równo. W aplikacji: **Ogólna składka
(podzielona równo na wszystkie działki)**. Jako cenę jednostkową
wpisujesz kwotę *całkowitą*; Parcella dzieli ją przez liczbę
fakturowanych działek i umieszcza każdy udział na fakturze działki.

## Pakiet do druku { #print-bundle }

Jeden PDF z każdą fakturą z serii faktur, której odbiorca nie jest
osiągalny e-mailem, gotowy do wydruku i wysłania pocztą.

## Patronat { #sponsorship }

Członek opiekuje się przez rok częścią terenu stowarzyszenia --
żywopłotem, placem zabaw -- i dostaje za to stałą liczbę
zaliczonych [obowiązkowych godzin](#mandatory-hours). Zob.
**Prace społeczne → Patronaty**.

## Powierzchnia A, B i C { #areas }

Całkowita powierzchnia stowarzyszenia podzielona na trzy części,
ustawiane w **Administracja → Ustawienia → Powierzchnie (m²)**:

- **Powierzchnia A (działki, m²)** -- suma powierzchni wszystkich
  działek, obliczana przez Parcellę.
- **Powierzchnia B (wspólna, m²)** -- ścieżki, tereny zielone i inny
  wspólny teren stowarzyszenia: całość minus A i C, obliczana przez
  Parcellę.
- **Powierzchnia C (miejska, m²)** -- teren, którym stowarzyszenie
  zarządza, ale który należy do gminy, wpisywany ręcznie.

Na powierzchni B opierają się [udział w powierzchni
wspólnej](#communal-area-share) i [obciążenia publiczne](#public-burdens).

## Proces { #process }

Lista kontrolna krok po kroku, którą projektujesz sam -- np. przekazanie
działki albo przyjęcie członka -- prowadzona dla jednej działki, członka
lub kandydata. Każdy etap ma pola do wypełnienia; pola wymagane muszą
być wypełnione przed przejściem dalej. Zob. [Procesy](modules/processes.md).

## Przekazanie działki { #handover }

Zmiana starego dzierżawcy na nowego na działce. W Parcelli **Przydziel
działkę** przy zgłoszeniu kończy starą [dzierżawę](#tenancy), czyni
kandydata członkiem i dzierżawcą oraz ustawia działkę z powrotem jako
aktywną. Zob. [Przekazanie działki](guides/parcel-handover.md).

## Przekazanie godzin { #hours-transfer }

Członek, który przepracował więcej [obowiązkowych godzin](#mandatory-hours)
niż wymagano, oddaje część nadwyżki innemu członkowi za ten sam rok.
Zob. **Prace społeczne → Przekazywanie godzin**.

## Punkt pomiarowy { #metering-point }

Miejsce, w którym mierzy się wodę lub prąd: przyłącze działki,
[licznik główny](#main-meter) albo przyłącze stowarzyszenia (świetlica,
myjnia). Punkt pomiarowy zostaje; zainstalowany w nim [licznik](#meter)
może się zmieniać.

## Rola { #role }

Starsze konta mają stałą rolę (**Administrator**, **Zarząd**,
**Skarbnik**, **Tylko odczyt**). Nowe konta dostają dostęp zamiast tego
z [grup](#group). To nie to samo co [rola klubowa](#club-role).

## Rola klubowa { #club-role }

Funkcja w stowarzyszeniu -- prezes, skarbnik, opiekun wodociągu -- którą
członek pełni przez rok. Rola klubowa może [zwolnić](#exemption) jej
posiadacza z [obowiązkowych godzin](#mandatory-hours). Ustawia się ją w
**Prace społeczne → Wpisy i przegląd → Role klubowe**. Nie mylić z
[rolą](#role) w Parcelli.

## Seria faktur { #invoice-run }

Jedna partia faktur, zwykle roczne faktury za dany rok. Dodajesz
pozycje, sprawdzasz podgląd, potem je **finalizujesz** -- co nadaje
stałe numery faktur -- i wysyłasz. Zob.
[Roczne fakturowanie](guides/annual-invoicing.md).

## Skarbnik { #treasurer }

Członek zarządu odpowiedzialny za pieniądze stowarzyszenia. W Parcelli
daj skarbnikowi [grupę](#group) z pełnymi prawami do **Finanse**.

## Tag { #tag }

Dowolna etykieta przy członku, np. „zespół żywopłotu” albo „odpowiedzialny
za wodę”, aby znajdować i filtrować osoby. Tagi istnieją też dla
kontaktów zewnętrznych.

## Termin prac społecznych { #work-session }

Dzień, w którym członkowie wykonują prace społeczne dla
stowarzyszenia, zaliczane do ich [obowiązkowych godzin](#mandatory-hours).
Terminy **Standardowy** są planowane i mogą być publikowane na stronie
stowarzyszenia; terminy **Specjalny** są spontaniczne i wewnętrzne. Zob.
[Organizacja terminu prac](guides/work-session.md).

## Udział w powierzchni wspólnej { #communal-area-share }

Pozycja faktury rozliczająca dzierżawę wspólnego terenu stowarzyszenia
([powierzchnia B](#areas)), dzielona równo na działki, których dotyczy.
W aplikacji: **Udział w dzierżawie powierzchni wspólnej**.

## Upominanie { #dunning }

Przypominanie członkowi o niezapłaconej fakturze. W Parcelli **Wyślij
upomnienie** przy zaległej fakturze tworzy **Upomnienie nr 1**, **nr
2** itd., z opcjonalną opłatą. Nie ma stałych poziomów upomnień; zarząd
decyduje, kiedy wysłać następne. Zob.
[Faktury, płatności i upomnienia](modules/finances/invoices.md).

## Uprawnienie { #permission }

Co użytkownik może robić w [module](#module): **Odczyt** (oglądać),
**Zapis** (dodawać i zmieniać) lub **Usuwanie**. Każdy, kto może się
zalogować, może przeglądać członków i działki. Zob.
[Role, grupy i uprawnienia](getting-started/roles-and-permissions.md).

## Wniosek zakupowy { #purchase-request }

Wniosek o wydanie pieniędzy stowarzyszenia, który przed zakupem wymaga
[zatwierdzenia przez dwie osoby](#two-person-approval). Zob.
[Wnioski zakupowe](modules/purchase-requests.md).

## Wycena { #valuation }

Ocena rzeczoznawcy, ile warte są altana, rośliny i wyposażenie działki,
gdy dzierżawca odchodzi. Parcella jej nie oblicza; raport przechowujesz
w [procesie](#process) przekazania.

## Wypowiedzenie { #notice-of-termination }

Zawiadomienie dzierżawcy (lub stowarzyszenia), że dzierżawa się kończy.
W Parcelli ustawiasz status działki na **wypowiedziana**; data jest
zapisywana automatycznie.

## Zarząd { #board }

Wybrany zarząd stowarzyszenia. W Parcelli członkowie zarządu zwykle mają
pełny dostęp do każdego modułu. Obecny zarząd wpisujesz w
**Administracja → Ustawienia → Członkowie zarządu**; ich dostęp pochodzi
z [grupy](#group) z **Pełny dostęp do każdego modułu** (albo, w
starszych kontach, z roli **Zarząd**).

## Zatwierdzenie przez dwie osoby { #two-person-approval }

[Wniosek zakupowy](#purchase-request) jest zatwierdzony dopiero wtedy,
gdy zatwierdzi go dwóch różnych członków zarządu -- i żaden z nich nie
może być osobą, która o niego wnioskowała. Jeden członek zarządu może go
odrzucić.

## Zwolnienie { #exemption }

Członek, który w danym roku nie musi odpracowywać
[obowiązkowych godzin](#mandatory-hours) -- zwykle z powodu
[roli klubowej](#club-role), zdrowia lub wieku. Jeśli zwolniony jest
jeden dzierżawca działki, zwolniona jest cała działka, a zwolnienie
zawsze obowiązuje przez cały rok kalendarzowy.
