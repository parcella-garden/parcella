# Moduły {#modules}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Parcella składa się z modułów: po jednym na każdy obszar pracy
stowarzyszenia. Twoje stowarzyszenie włącza tylko te, których potrzebuje;
pozostałe znikają z nawigacji dla wszystkich. Wyłączenie modułu nigdy nie
usuwa jego danych -- włącz go ponownie i wszystko wraca.

Moduły włącza i wyłącza administrator, zob.
[Włączanie i wyłączanie modułów](../administration/modules.md). Kto może
korzystać z włączonego modułu, ustala się za pomocą
[grup](../administration/groups.md).

## Przegląd {#overview}

| Moduł | Do czego służy | Włączony po instalacji? |
|---|---|---|
| [Członkowie](members.md) | Wszyscy, którzy należą do stowarzyszenia: dane kontaktowe, daty członkostwa, role, historia. | Zawsze włączony |
| [Działki](parcels.md) | Działki ogrodowe, ich dzierżawy i dzierżawcy, dawni i obecni. | Zawsze włączony |
| [Kandydaci](applicants.md) | Osoby, które ubiegały się o wolną działkę, ich status i notatki zarządu. | Tak |
| [Prace społeczne](work-hours.md) | Terminy prac, zgłoszenia i obecność, patronaty, przekazywanie godzin oraz roczne rozliczenie wymaganych godzin. | Tak |
| [Woda i prąd](metering.md) | Liczniki, odczyty i zestawienia zużycia. Woda i prąd włącza się osobno. | Tak |
| [Ubezpieczenia](insurance.md) | Ubezpieczenie mienia i od następstw nieszczęśliwych wypadków dla każdej działki i roku, z rocznym zestawieniem. | Tak |
| [Finanse](finances/index.md) | Roczne faktury dla każdej działki, płatności, upomnienia, rachunki bankowe, faktury przychodzące i księgowość. | Nie |
| [Wnioski zakupowe](purchase-requests.md) | Wydatki stowarzyszenia zatwierdzane przez dwóch członków zarządu, zanim zostaną wydane pieniądze. | Tak |
| [Kalendarz](calendar.md) | Kalendarz stowarzyszenia, urodziny, obecność i nieobecność zarządu, własne kalendarze -- każdy także jako subskrybowany kanał kalendarza. | Tak |
| [Ogłoszenia](announcements.md) | Napisz wiadomość stowarzyszenia raz i wyślij ją na stronę internetową, e-mailem i jako ogłoszenie do wydruku. | Nie |
| [Tablica zadań](tasks.md) | Tablica Do zrobienia / W toku / Gotowe dla spraw stowarzyszenia. Tylko dla zarządu i administratorów. | Tak |
| [Inwentarz](inventory.md) | Wszystko, co należy do stowarzyszenia (oraz rzeczy członków przechowywane na terenie stowarzyszenia), z wypożyczaniem. | Tak |
| [Notatki](notes.md) | Protokoły z zebrań i inne notatki, z kategoriami i tagami, opcjonalnie przechowywane jako pliki w chmurze. | Tak |
| [Procesy](processes.md) | Własne procedury krok po kroku, np. przekazanie działki, prowadzone dla działki, członka lub kandydata. | Tak |
| [Kontakty zewnętrzne](external-contacts.md) | Dostawcy, rzemieślnicy i urzędy, powiązani z fakturami i wnioskami zakupowymi. | Tak |
| [Wsparcie](support.md) | Rozmowy z helpdesku stowarzyszenia, powiązane z członkami, działkami i zadaniami. | Nie |
| [Raporty](reporting.md) | Dane stowarzyszenia na przestrzeni lat w formie wykresów. Tylko do odczytu. | Tak |

## Dlaczego niektóre moduły są na początku wyłączone {#why-some-modules-start-switched-off}

Moduły wyłączone po instalacji robią coś, o czym stowarzyszenie powinno
zdecydować świadomie:

- **Finanse** obsługują pieniądze członków i wysyłają faktury hurtowo.
- **Ogłoszenia** mogą wysłać e-mail do każdego członka i publikować na
  Twojej stronie internetowej.
- **Wsparcie** łączy się z zewnętrznym helpdeskiem i potrzebuje danych
  dostępowych.

To samo dotyczy dodatków na liście modułów, które nie mają własnego
rozdziału: **Magazyn w chmurze**, **Synchronizacja Nextcloud Deck**,
**Konektor MCP dla klientów AI** oraz trzech publicznych formularzy na
stronę internetową (**Publiczne API zgłoszeń**, **Publiczne API
formularza kontaktowego**, **Publiczne API formularza zgłoszeń**). Albo
przechowują hasła do usług zewnętrznych, albo otwierają formularz dla
publicznego internetu. Zob.
[Włączanie i wyłączanie modułów](../administration/modules.md) oraz
[Integracje](../administration/integrations.md).

## Powiązane {#related}

- [Role, grupy i uprawnienia](../getting-started/roles-and-permissions.md)
- [Orientacja w aplikacji](../getting-started/navigation.md)
