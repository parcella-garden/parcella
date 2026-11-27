# Administracja {#administration}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Obszar administracji to miejsce, w którym konfiguruje się i utrzymuje
Twoją instalację Parcelli: kto może się logować, co może robić, dane
podstawowe stowarzyszenia, połączenia z innymi usługami oraz kopie
zapasowe.

!!! info "Kto może z tego korzystać"
    Tylko **administratorzy**: konta ze starszą rolą **Administrator**
    albo w grupie z **Dostęp do panelu administracyjnego**. Członkowie
    zarządu z pełnym dostępem do modułów go nie widzą, chyba że są też
    administratorami. Zob.
    [Role, grupy i uprawnienia](../getting-started/roles-and-permissions.md).

Znajdziesz go na dole paska bocznego pod **Administracja**.

## Strony {#the-pages}

| Pozycja na pasku bocznym | Strona | Co tam robisz |
|---|---|---|
| **System** | [Informacje o systemie i aktualizacje](system.md) | Sprawdzasz swoją wersję i czy jest aktualizacja; pobierasz kopię zapasową. |
| | [Kopia zapasowa i przywracanie](backup.md) | Przywracasz z kopii zapasowej; planujesz automatyczne kopie zapasowe w chmurze. |
| **Użytkownicy** | [Użytkownicy i zaproszenia](users.md) | Zapraszasz osoby, edytujesz, dezaktywujesz i usuwasz konta, resetujesz hasła. |
| **Grupy** | [Grupy](groups.md) | Decydujesz, kto może czytać, zapisywać i usuwać co. |
| **Tokeny API** | [Tokeny API](api-tokens.md) | Oglądasz i unieważniasz tokeny wszystkich; tworzysz tokeny dla kont integracyjnych. |
| **Ustawienia** | [Ustawienia stowarzyszenia](settings.md) | Nazwa i adres stowarzyszenia, logo, język, region i waluta, serwer e-mail, dane finansowe, kolejność nawigacji i więcej. |
| | [Włączanie i wyłączanie modułów](modules.md) | Karta **Moduły funkcjonalne** na stronie ustawień. |
| **Własne pola** | [Własne pola](custom-fields.md) | Własne pola dla członków i działek, np. zawód członka albo basen na działce. |
| **Integracje** | [Integracje](integrations.md) | Formularze na stronie internetowej, szkice na stronę, magazyn w chmurze, helpdesk, Nextcloud Deck, linki do kanałów kalendarza. |
| **Dziennik e-maili** | [Dziennik e-maili](email-log.md) | Sprawdzasz, czy e-mail został wysłany. |
| **Dane przykładowe** | [Dane przykładowe](sample-data.md) | Wypełniasz nową instalację danymi demonstracyjnymi, aby coś wypróbować, i usuwasz je potem. |
| **Dokumentacja API (Swagger)** | -- | Techniczny opis interfejsu programistycznego, dla deweloperów. |

## Konfiguracja nowej instalacji {#setting-up-a-new-installation}

Rozsądna kolejność dla zupełnie nowej instalacji:

1. Zaloguj się wbudowanym kontem administratora i zmień jego hasło --
   zob. [Pierwsze logowanie](../getting-started/first-login.md#the-very-first-login-after-installation).
2. W [Ustawieniach stowarzyszenia](settings.md): język, region i waluta,
   dane stowarzyszenia, logo oraz serwer e-mail (bez niego Parcella nie
   może wysyłać zaproszeń).
3. W [Włączaniu i wyłączaniu modułów](modules.md): wyłącz to, czego nie
   potrzebujesz, włącz to, czego potrzebujesz.
4. Utwórz [grupy](groups.md) dla zadań w Twoim stowarzyszeniu.
5. [Zaproś](users.md) pozostałych członków zarządu do tych grup.
6. Skonfiguruj [kopie zapasowe](backup.md).

Instrukcja [Konfiguracja nowego stowarzyszenia](../guides/new-club-setup.md)
przeprowadza przez to razem z wprowadzaniem członków i działek.

Instalację samej Parcelli (serwer, Docker, adres internetowy) opisuje
[dokumentacja dla deweloperów](https://github.com/parcella-garden/parcella#install-self-hosting).
