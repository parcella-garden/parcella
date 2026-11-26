# Integracje {#integrations}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Integracje łączą Parcellę z innymi systemami, których używa Twoje
stowarzyszenie: stroną internetową stowarzyszenia, magazynem w chmurze,
helpdeskiem, Nextcloud Deck i aplikacjami kalendarza.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → Integracje**.

![Integracje](../assets/screenshots/administration/integrations.png)

Strona to kolumna zwiniętych kart; kliknij nagłówek, aby otworzyć kartę.
Każda karta zapisuje się osobno własnym przyciskiem.

Większość integracji wymaga też modułu włączonego w
[Włączaniu i wyłączaniu modułów](modules.md). Karty mówią, gdy go
brakuje.

!!! note "Serwer e-mail jest gdzie indziej"
    Serwer poczty wychodzącej (SMTP) ustawia się w
    [Ustawieniach stowarzyszenia](settings.md#email-smtp), nie tutaj.

## Prywatne kanały kalendarza {#private-calendar-feeds}

Moduł kalendarza oferuje linki do subskrypcji (kanały kalendarza) dla
listy urodzin oraz obecności i nieobecności zarządu, aby członkowie
zarządu widzieli je w aplikacji kalendarza w telefonie. Te linki zawierają
jeden wspólny sekret i nigdy nie wygasają.

| Przycisk | Do czego służy |
|---|---|
| **Wygeneruj ponownie** | Po potwierdzeniu tworzy nowy sekret. **Każda istniejąca subskrypcja tych kanałów przestaje działać**; subskrybenci muszą skopiować nowy link ze stron kalendarza. Widzisz **Wygenerowano nowy token kanałów kalendarza. ...** |

Zrób to, gdy link mógł trafić w niepowołane ręce albo gdy ktoś, kto go
miał, odchodzi z zarządu. Zob. [Kalendarz](../modules/calendar.md).

## Publiczne API zgłoszeń {#public-signup-api}

Ta karta pozwala stronie internetowej stowarzyszenia rozmawiać z
Parcellą: działkowcy zapisują się na terminy prac, wysyłają wiadomość
kontaktową lub ubiegają się o działkę przez formularze na stronie, bez
logowania do Parcelli.

Jeśli moduł **Publiczne API zgłoszeń** jest wyłączony, mówi o tym
komunikat na górze strony z linkiem **Włącz w Ustawieniach**. Podobny
komunikat pojawia się w karcie, dopóki **Publiczne API formularza
kontaktowego** jest wyłączone. Formularz zgłoszenia o działkę wymaga
dodatkowo przełącznika **Publiczne API formularza zgłoszeń**.

Strona internetowa może wysyłać formularze na dwa sposoby; możesz
używać obu.

### Z tokenem API (wtyczka strony na serwerze) {#with-the-api-token-website-plugin-on-the-server}

Dla strony z wtyczką po stronie serwera -- „konektorem” -- która sama
wysyła dane formularza do Parcelli.

| Element | Do czego służy |
|---|---|
| **Token API** | Sekret, którego potrzebuje wtyczka. Kliknij w pole, aby go zaznaczyć, i skopiuj do ustawień wtyczki. |
| **Wygeneruj ponownie** | Po potwierdzeniu tworzy nowy token. **Każda wtyczka używająca jeszcze starego od razu przestaje działać**; wpisz nowy wszędzie. Widzisz *Wygenerowano nowy token API. ...* |
| **Punkty końcowe** | Tabela adresów internetowych używanych przez wtyczki, każdy z kolumnami **Metoda**, **URL** i **Uwierzytelnianie** (**Brak (publiczny odczyt)**, token API albo **Dozwolone adresy stron**). Potrzebuje tego osoba techniczna od Twojej strony; Ty nie. |

Karta kończy się informacją, że gotowa wtyczka WordPress jest częścią
projektu Parcella.

### Formularze na stronie (czysty HTML, wtyczka WordPress) {#website-forms-plain-html-wordpress-plugin}

Dla stron, których formularze wysyłają dane prosto z przeglądarki
odwiedzającego do Parcelli: zwykłe strony HTML w dowolnym systemie
stron oraz wtyczka WordPress od wersji 3.0. Nie ma tu tokenu, więc
Parcella przyjmuje tylko formularze pochodzące ze stron, które tu
wymienisz. Dopóki lista jest pusta, te formularze są zamknięte.

| Pole / przycisk | Do czego służy |
|---|---|
| **Dozwolone adresy stron** | Jeden adres w wierszu, tylko schemat i host, np. `https://example.org`. Wymień każdy adres, pod którym dostępna jest strona stowarzyszenia, łącznie z własnym adresem strony WordPress. Wpisy, które nie są adresami internetowymi, są pomijane i wymieniane w ostrzeżeniu. |
| **Wymagaj ALTCHA (zadanie obliczeniowe przeciw botom spamującym)** | Przeglądarka odwiedzającego musi rozwiązać małą zagadkę, zanim formularz zostanie przyjęty -- bez ciasteczek, bez zewnętrznej firmy, bez klikania. Dotyczy to **każdego** sposobu wysyłania, także wtyczek z tokenem API. Zaznacz to dopiero, gdy wszystkie formularze na Twojej stronie zawierają widżet ALTCHA, inaczej każde zgłoszenie zostanie odrzucone. |
| **Zapisz adresy** | Zapisuje oba. Widzisz **Dozwolone adresy stron zostały zapisane.** |

Co widzą i dostają działkowcy, opisuje strona
[Dla działkowców](../gardeners/index.md).

## Strona internetowa (szkice z ogłoszeń) {#website-drafts-from-announcements}

Pozwala modułowi [Ogłoszenia](../modules/announcements.md) jednym
kliknięciem utworzyć szkic wpisu na stronie stowarzyszenia. Parcella
tworzy zawsze tylko **szkice**; publikacja pozostaje Twoją decyzją w
systemie strony.

| Pole / przycisk | Do czego służy |
|---|---|
| **Typ strony** | **Brak (bez szkiców na stronie)**, **WordPress**, **Folder Markdown (chmura)** lub **Wtyczka Parcella (TYPO3, Contao, Drupal, Joomla, ...)**. Wybór pokazuje jego pola. Naraz aktywny jest tylko jeden typ; zmiana zachowuje ustawienia drugiego typu na później. |
| **Zapisz** | Zapisuje typ i jego pola. Widzisz **Ustawienia strony zapisane** albo błąd wyjaśniający, czego brakuje. |
| **Testuj połączenie** | Próbuje połączenia z tym, co jest teraz w formularzu, bez zapisywania. Pokazuje **Połączenie udane** albo błąd. |

Pola oznaczone * są wymagane. Pola haseł pokazują, czy coś jest
zapisane; zostaw je puste, aby to zachować.

**WordPress**

| Pole | Co wpisać |
|---|---|
| **Adres strony WordPress** * | Adres Twojej strony. |
| **Nazwa użytkownika WordPress** * | Użytkownik WordPress, jako który tworzone są szkice. |
| **Hasło aplikacji** * | Nie zwykłe hasło WordPress: utwórz hasło aplikacji w WordPressie w *Użytkownicy → Profil → Hasła aplikacji*. |

**Folder Markdown (chmura)** -- dla stron budowanych z plików
tekstowych (Hugo, Jekyll, Eleventy, Astro i podobne). Każdy szkic staje
się plikiem oznaczonym jako szkic w folderze w Twoim
[magazynie w chmurze](#cloud-storage); usunięcie wiersza szkicu go
publikuje.

| Pole | Co wpisać |
|---|---|
| **Folder wpisów** * | Folder w magazynie w chmurze na wpisy, np. `website/content/posts`. Musi już istnieć. |
| **Folder obrazów** | Gdzie trafiają obrazy, w podfolderach według roku i miesiąca. Pusty: wpisy bez obrazów. |
| **Ścieżka www folderu obrazów** | Jak strona adresuje folder obrazów, np. `/media`. |
| **Adres strony** | Używany do kodu QR na drukowanym ogłoszeniu, gdy wpis zostanie opublikowany. |
| **Wzór nazwy pliku** | `{date}` zamienia się na RRRRMMDD, `{slug}` na tytuł bez znaków diakrytycznych i spacji. |
| **Wzór adresu wpisu** | Adres internetowy wpisu, zapisywany w pliku. Zostaw puste, jeśli Twoja strona sama go ustala. |
| **Autor** | Zapisywany w każdym wpisie. |
| **Kategorie** | Rozdzielone przecinkami, tak jak nazywa je Twoja strona. |

**Wtyczka Parcella** -- dla TYPO3, Contao, Drupala, Joomli i innych
systemów z zainstalowaną wtyczką Parcella. Własne ustawienia wtyczki
pokazują obie wartości.

| Pole | Co wpisać |
|---|---|
| **Adres wtyczki** * | Np. `https://example.org/parcella/v1`. |
| **Wspólny klucz** * | Generowany przez wtyczkę. |

## Magazyn w chmurze {#cloud-storage}

Nagłówek brzmi **Chmura (dokumenty działek, faktury, kopie zapasowe)**.
Decyduje, gdzie Parcella przechowuje pliki: folder dla każdej działki
(umowy dzierżawy, dokumenty), faktury przychodzące, dokumenty kontaktów,
notatki, pliki procesów, kopie zapasowe i stronę Markdown. Kto jeszcze
widzi dany folder, ustala się w samym magazynie, nie w Parcelli.

| Pole / przycisk | Do czego służy |
|---|---|
| **Typ chmury** | **Brak (bez chmury)**, **Nextcloud**, **WebDAV (ownCloud, Seafile, HiDrive, Storage Box, ...)** lub **Zgodna z S3 (AWS, Hetzner, MinIO, Wasabi, ...)**. Naraz aktywny jest tylko jeden. Ścieżki folderów wpisane w innych miejscach Parcelli są względne wobec wybranego magazynu. |
| **Zapisz**, **Testuj połączenie** | Jak w karcie strony internetowej. |

| Magazyn | Pola |
|---|---|
| **Nextcloud** | **Adres Nextcloud** *, **Nazwa użytkownika Nextcloud** *, **Hasło aplikacji** * -- utwórz hasło aplikacji w Nextcloud w *Ustawienia → Bezpieczeństwo → Urządzenia i sesje*; nie używaj zwykłego hasła. |
| **WebDAV** | **Adres WebDAV** * (pełny adres folderu, w którym ma pracować Parcella, tak jak dokumentuje go Twój dostawca), **Nazwa użytkownika** *, **Hasło** *. |
| **Zgodna z S3** | **Endpoint** *, **Region** * (zostaw `us-east-1`, jeśli Twój dostawca nie ma regionów), **Bucket** *, **ID klucza dostępu** *, **Tajny klucz dostępu** *, **Ścieżka w buckecie** (opcjonalny podfolder na wszystkie pliki Parcelli). |

Magazyn jest używany dopiero po włączeniu modułu **Magazyn w chmurze**.
Wtedy karta pokazuje też poniższe foldery. Każdy ma pole ścieżki
(względnej wobec magazynu) i przycisk **Zapisz**; zostaw ścieżkę pustą,
aby wyłączyć dane zastosowanie.

| Folder | Do czego służy |
|---|---|
| **Folder faktur przychodzących** | Załączniki [faktur przychodzących](../modules/finances/incoming-invoices.md) trafiają do tego jednego wspólnego folderu. |
| **Folder na dokumenty kontaktów zewnętrznych** | Folder bazowy z jednym podfolderem na każdy [kontakt zewnętrzny](../modules/external-contacts.md), utworzonym przez Ciebie w magazynie. Każdy kontakt wybiera potem swój podfolder. Pusty: sekcja dokumentów jest ukryta. |
| **Folder na drukowane ogłoszenia** | Każdy PDF do druku [ogłoszenia](../modules/announcements.md) jest też zapisywany tutaj. **Przeglądaj…** pozwala przeklikać się przez magazyn i **użyć** folderu. Pusty: tylko pobieranie. |
| **Folder notatek** | [Notatki](../modules/notes.md) są tu przechowywane jako pliki tekstowe, a zmiany tych plików w chmurze pojawiają się w Parcelli. Podfoldery stają się kategoriami notatek. Pusty: notatki istnieją tylko w Parcelli. |
| **Folder na pliki procesów** | Pliki przesłane do [procesu](../modules/processes.md), jeden podfolder na proces. Pusty: przechowywane w Parcelli. Pliki już przesłane zostają tam, gdzie są. |

Folder automatycznych kopii zapasowych ustawia się na stronie
[Kopie zapasowe w chmurze](backup.md#cloud-backups).

## Wsparcie / helpdesk {#support-helpdesk}

Podłącza helpdesk, w którym stowarzyszenie odpowiada na zgłoszenia.
Parcella łączy wtedy jego rozmowy z członkami, działkami i tablicą
zadań (zob. [Wsparcie](../modules/support.md)), a formularz kontaktowy
na stronie tworzy tam nowe zgłoszenia.

| Pole / przycisk | Do czego służy |
|---|---|
| **Helpdesk** | **Brak (bez helpdesku)**, **FreeScout**, **Zammad**, **Znuny / OTRS**, **osTicket**, **Zendesk** lub **Freshdesk**. Naraz aktywny jest tylko jeden; jeśli później do niego wrócisz, wrócą też jego rozmowy. Każdy wybór pokazuje krótką notkę o tym, co z nim działa. |
| **Zapisz**, **Testuj połączenie** | Jak w karcie strony internetowej. |

| Helpdesk | Pola | Uwagi |
|---|---|---|
| **FreeScout** | **Adres FreeScout** *, **Klucz API** *, **ID skrzynki** (domyślnie 1) | Wszystko działa. Wymaga modułu FreeScout *API & Webhooks*. |
| **Zammad** | **Adres Zammad** *, **Token dostępu** *, **Grupa dla nowych zgłoszeń** * | Wszystko działa. |
| **Znuny / OTRS** | **Adres usługi sieciowej** *, **Login agenta** *, **Hasło** *, **Kolejka dla nowych zgłoszeń** *, **Adres interfejsu agenta** | Bez zmiany nazw klientów. Usługę sieciową Parcelli trzeba raz zaimportować do Znuny. |
| **osTicket** | **Adres osTicket** *, **Klucz API** * | Działa tylko formularz kontaktowy na stronie; czytanie i odpowiadanie odbywa się w osTicket. |
| **Zendesk** | **Adres Zendesk** *, **Adres e-mail agenta** *, **Token API** * | Wszystko działa. |
| **Freshdesk** | **Adres Freshdesk** *, **Klucz API** * | Wszystko działa. |

Podpowiedź pod każdym polem mówi, gdzie w helpdesku znaleźć klucz lub
token. Włącz też moduł **Wsparcie (helpdesk)**.

## Nextcloud Deck {#nextcloud-deck}

Kopiuje karty jednej tablicy Nextcloud Deck na
[tablicę zadań](../modules/tasks.md) Parcelli -- tylko w jedną stronę,
tylko do odczytu, automatycznie aktualizowane. To osobne połączenie od
magazynu w chmurze powyżej, nawet gdy oba używają tego samego
Nextcloud.

| Pole / przycisk | Do czego służy |
|---|---|
| **URL serwera Nextcloud** | Np. `https://cloud.example.com`. |
| **Nazwa użytkownika Nextcloud** | |
| **Hasło aplikacji Nextcloud** | Utwórz je w Nextcloud w *Ustawienia osobiste → Bezpieczeństwo*. Zostaw puste, aby zachować zapisane. |
| **ID tablicy Deck** | Liczba na końcu adresu tablicy (`.../apps/deck/board/3` → `3`). Wklejenie całego adresu też działa. |
| **Zapisz** | Zapisuje połączenie (**Zapisano ustawienia Deck**). |
| **Testuj połączenie** | Sprawdza połączenie z tym, co jest w formularzu. |
| **Synchronizuj teraz** | Widoczne po zapisaniu ID tablicy. Kopiuje karty od razu zamiast czekać. Obok: ile zadań zsynchronizowano i kiedy, albo **Jeszcze nie zsynchronizowano**. |

Włącz też moduł **Synchronizacja Nextcloud Deck**.

## Powiązane {#related}

- [Włączanie i wyłączanie modułów](modules.md)
- [Kopia zapasowa i przywracanie](backup.md)
- [Dla działkowców](../gardeners/index.md) -- jak formularze na stronie wyglądają z drugiej strony
