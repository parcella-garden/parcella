# Włączanie i wyłączanie modułów {#turning-modules-on-and-off}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Nie każde stowarzyszenie korzysta z każdej części Parcelli.
Stowarzyszenie bez własnego wodociągu nie potrzebuje odczytów liczników;
stowarzyszenie, które nie wymaga prac społecznych, nie potrzebuje
terminów prac. Ty decydujesz, z których modułów korzysta Twoje
stowarzyszenie.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → Ustawienia** i
    rozwiń kartę **Moduły funkcjonalne**.

Każdy moduł ma przełącznik, nazwę i krótki opis. Przestaw przełączniki,
które chcesz zmienić, i kliknij **Zapisz ustawienia**.

## Co się dzieje po wyłączeniu modułu {#what-happens-when-you-switch-a-module-off}

- **Znika z paska bocznego i z panelu głównego** dla wszystkich, łącznie
  z administratorami. (Wyjątek: kafelek *Urodziny w tym tygodniu*
  zostaje na panelu głównym nawet przy wyłączonym Kalendarzu.)
- Jego stron nie można już otworzyć, nawet z zakładki.
- **Nic nie zostaje usunięte.** Wszystkie dane zostają w bazie danych i
  wracają bez zmian, gdy tylko ponownie włączysz moduł.
- Uprawnienia grup dla modułu pozostają bez zmian, więc po ponownym
  włączeniu dostęp mają znowu te same osoby.

Włączenie modułu od razu udostępnia go wszystkim z pełnym dostępem.
Pozostałe osoby widzą go na pasku bocznym dopiero wtedy, gdy grupa nada
im dla niego **Odczyt** -- zob. [Grupy](groups.md).

## Przełączniki {#the-switches}

Pojawiają się na karcie w tej kolejności.

| Przełącznik | Do czego służy | Domyślnie włączony |
|---|---|---|
| **Zarządzanie pracami społecznymi** | Terminy prac, patronaty, role w stowarzyszeniu i roczne zestawienie godzin pracy. Zob. [Prace społeczne](../modules/work-hours.md). | Tak |
| **Zarządzanie wodą** | Liczniki wody, odczyty i zestawienia zużycia. Zob. [Woda i prąd](../modules/metering.md). | Tak |
| **Zarządzanie prądem** | Liczniki prądu, odczyty i zestawienia zużycia. | Tak |
| **Zarządzanie ubezpieczeniami** | Ubezpieczenie mienia i NNW dla każdej działki, z rocznym zestawieniem. Zob. [Ubezpieczenia](../modules/insurance.md). | Tak |
| **Wsparcie (helpdesk)** | Łączy rozmowy z Twojego helpdesku z członkami i tablicą zadań. Najpierw wybierz helpdesk w [Integracjach](integrations.md#support-helpdesk). Zob. [Wsparcie](../modules/support.md). | Nie |
| **Wnioski zakupowe** | Wydatki stowarzyszenia z zatwierdzaniem przez dwie osoby. Zob. [Wnioski zakupowe](../modules/purchase-requests.md). | Tak |
| **Kalendarz** | Kalendarz stowarzyszenia, urodziny, obecność i nieobecność zarządu, każdy z kanałem kalendarza. Zob. [Kalendarz](../modules/calendar.md). | Tak |
| **Inwentarz** | Wszystko, co należy do stowarzyszenia, z kategoriami i wypożyczaniem. Zob. [Inwentarz](../modules/inventory.md). | Tak |
| **Tablica zadań** | Tablica Do zrobienia / W toku / Gotowe dla spraw stowarzyszenia. Tylko dla użytkowników z pełnym dostępem (zarząd, administratorzy i grupy z pełnym dostępem). Zob. [Tablica zadań](../modules/tasks.md). | Tak |
| **Kandydaci** | Osoby, które ubiegały się o wolną działkę. Zob. [Kandydaci](../modules/applicants.md). | Tak |
| **Kontakty zewnętrzne** | Dostawcy, rzemieślnicy, urzędy. Zob. [Kontakty zewnętrzne](../modules/external-contacts.md). | Tak |
| **Raporty** | Dane stowarzyszenia w czasie jako wykresy, tylko do odczytu. Zob. [Raporty](../modules/reporting.md). | Tak |
| **Notatki** | Notatki z kategoriami i tagami, opcjonalnie przechowywane jako pliki w chmurze. Zob. [Notatki](../modules/notes.md). | Tak |
| **Procesy** | Twoje własne procesy krok po kroku. Zob. [Procesy](../modules/processes.md). | Tak |
| **Konektor MCP dla klientów AI** | Pozwala asystentowi AI (Claude, ChatGPT, ...) przeszukiwać, czytać i zapisywać **tylko te notatki, które udostępniłeś dla AI**, nic więcej. Wymaga [tokenu API](api-tokens.md) rodzaju **Tylko konektor MCP (dla klienta AI)**. | Nie |
| **Publiczne API zgłoszeń** | Pozwala formularzowi na stronie stowarzyszenia zapisywać działkowców na terminy prac bez logowania. Zob. [Integracje](integrations.md#public-signup-api) i [Dla działkowców](../gardeners/index.md). | Nie |
| **Publiczne API formularza kontaktowego** | Pozwala formularzowi kontaktowemu na stronie stowarzyszenia tworzyć nowe zgłoszenie w Twoim helpdesku zamiast wysyłać e-mail. | Nie |
| **Publiczne API formularza zgłoszeń** | Pozwala formularzowi zgłoszeń o działkę na stronie stowarzyszenia od razu tworzyć kandydatów. Z modułu **Kandydaci** można korzystać bez niego, dla zgłoszeń wprowadzanych ręcznie. | Nie |
| **Ogłoszenia** | Napisz wiadomość stowarzyszenia raz i przygotuj ją na stronę internetową, e-mail do członków i ogłoszenie do wydruku. Zob. [Ogłoszenia](../modules/announcements.md). | Nie |
| **Magazyn w chmurze** | Folder w chmurze dla każdej działki na umowy dzierżawy i dokumenty; potrzebny też do załączników faktur przychodzących, dokumentów kontaktów, plików notatek i kopii zapasowych w chmurze. Najpierw wybierz magazyn w [Integracjach](integrations.md#cloud-storage). | Nie |
| **Finanse** | Roczne faktury dla każdej działki, płatności i księgowość. Najpierw wypełnij [ustawienia finansowe](settings.md#finance-settings). Zob. [Finanse](../modules/finances/index.md). | Nie |
| **Synchronizacja Nextcloud Deck** | Kopiuje karty jednej tablicy Nextcloud Deck na tablicę zadań i automatycznie je aktualizuje. Najpierw skonfiguruj połączenie w [Integracjach](integrations.md#nextcloud-deck). | Nie |

**Członkowie** i **Działki** nie mają przełącznika: są rdzeniem Parcelli
i zawsze są włączone.

## Dlaczego niektóre przełączniki są na początku wyłączone {#why-some-switches-start-off}

Przełączniki wyłączone w nowej instalacji robią jedną z tych rzeczy:

- **Otwierają drzwi do publicznego internetu.** Trzy przełączniki
  *Publiczne API ...* pozwalają każdemu, kto odwiedza Twoją stronę
  internetową, wysyłać dane do Parcelli. Włącz jeden z nich tylko
  wtedy, gdy Twoja strona naprawdę ma odpowiedni formularz, i tylko ten,
  którego potrzebujesz.
- **Przechowują hasła do innych usług** albo pozwalają Parcelli w nich
  działać: magazyn w chmurze, helpdesk, Nextcloud Deck, połączenie
  ogłoszeń ze stroną internetową.
- **Obsługują pieniądze albo docierają naraz do każdego członka:**
  finanse i ogłoszenia.
- **Przekazują dane zewnętrznej firmie:** konektor MCP daje usłudze AI
  dostęp do notatek, które udostępnisz.

Nic się nie zepsuje, jeśli zostawisz je wyłączone. Włączaj je
świadomie, gdy wiesz, że ich potrzebujesz.

## Powiązane {#related}

- [Moduły](../modules/index.md) -- co robi każdy moduł
- [Grupy](groups.md) -- kto może korzystać z włączonego modułu
- [Integracje](integrations.md) -- połączenia potrzebne kilku modułom
