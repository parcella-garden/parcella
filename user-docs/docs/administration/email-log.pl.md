# Dziennik e-maili {#e-mail-log}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Dziennik e-maili pokazuje każdy e-mail, który Parcella próbowała wysłać
-- zaproszenia, powiadomienia, ogłoszenia, faktury, potwierdzenia
zgłoszeń -- oraz odpowiedź serwera pocztowego. Zajrzyj tu, gdy ktoś
mówi „nigdy nie dostałem tego e-maila”.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → Dziennik e-maili**.

![Dziennik e-maili](../assets/screenshots/administration/email-log.png)

## Czytanie dziennika {#reading-the-log}

Na górze krótka notka wyjaśnia stronę i ile dni przechowywane są wpisy,
z linkiem **Zmień** do [ustawienia](settings.md#email-log).

Karta **Wychodzące e-maile** pokazuje liczbę znalezionych wpisów i
tabelę, od najnowszych, po 50 na stronę:

| Kolumna | Co pokazuje |
|---|---|
| **Data/godzina** | Kiedy Parcella przekazała e-mail serwerowi pocztowemu, w strefie czasowej stowarzyszenia. |
| **Odbiorca** | Adres, na który poszedł. |
| **Temat** | Wiersz tematu. Spinacz oznacza załączniki; najedź na niego, aby zobaczyć ile. |
| **Status** | **Wysłano** lub **Błąd**. Pod **Błąd** widzisz komunikat błędu serwera pocztowego. |

**Nowsze** i **Starsze** na dole przewijają dziennik (**Strona ... z
...**).

### Co oznaczają „Wysłano” i „Błąd” {#what-sent-and-failed-mean}

- **Wysłano** oznacza, że Twój serwer pocztowy **przyjął** e-mail. Nie
  dowodzi to, że dotarł: jeśli skrzynka jest pełna albo adres już nie
  istnieje, wiadomość zwrotna trafia do skrzynki nadawczej
  stowarzyszenia, a nie do tego dziennika.
- **Błąd** oznacza, że serwer pocztowy od razu go odrzucił albo był
  nieosiągalny -- np. złe hasło, nieznany odbiorca albo w ogóle brak
  skonfigurowanego serwera pocztowego.

Jeśli wiele e-maili kończy się tym samym błędem, sprawdź ustawienia
serwera pocztowego w [Ustawieniach stowarzyszenia](settings.md#email-smtp).

## Wyszukiwanie i filtrowanie {#searching-and-filtering}

| Element | Do czego służy |
|---|---|
| **Szukaj odbiorcy…** | Pokazuje tylko e-maile, których adres odbiorcy zawiera wpisany tekst. |
| Lista statusów | **Wszystkie statusy**, **Wysłano** lub **Błąd**. Zmiana filtruje od razu. |
| **Filtruj** | Stosuje wyszukiwanie. |
| **Resetuj** | Pojawia się, gdy filtr jest aktywny; pokazuje znowu wszystko. |

**Brak zarejestrowanych e-maili.** pojawia się, gdy nic nie pasuje.

## Jak długo przechowywane są wpisy {#how-long-entries-are-kept}

Adresy odbiorców to dane osobowe, więc wpisy są automatycznie usuwane po
liczbie dni ustawionej w
[Ustawieniach stowarzyszenia → Dziennik e-maili](settings.md#email-log)
-- 90 dni, jeśli tego nie zmienisz. Dziennik zapisuje tylko odbiorcę,
temat, status, błąd i liczbę załączników -- nie treść e-maila.

## Powiązane {#related}

- [Ustawienia stowarzyszenia](settings.md#email-smtp)
- [Użytkownicy i zaproszenia](users.md)
