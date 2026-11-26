# Informacje o systemie i aktualizacje {#system-information-and-updates}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Strona System pokazuje, której wersji Parcelli używasz, czy dostępna
jest nowsza, i jest punktem wyjścia do kopii zapasowych.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → System**.

![System](../assets/screenshots/administration/system.png)

## Powiadomienie o aktualizacji {#update-notice}

Parcella regularnie pyta GitHub, gdzie jest publikowana, czy wydano
nowszą wersję. Nie są wysyłane żadne dane o Twoim stowarzyszeniu. Możesz
to wyłączyć w [Ustawieniach stowarzyszenia → Aktualizacje](settings.md#updates);
wtedy powiadomienie o aktualizacji znika z tej strony.

**Gdy masz aktualną wersję**, widzisz

> Wersja v1.2.3 -- aktualna (ostatnio sprawdzono: 18.11.2026 14:05)

albo **... jeszcze nie sprawdzono aktualizacji** zaraz po instalacji.

**Gdy istnieje nowsza wersja**, wyróżnione pole pokazuje **Dostępna
aktualizacja:** z numerem nowej wersji, wersją, której używasz, oraz
czterema poleceniami, które instalują aktualizację na serwerze.

| Przycisk | Do czego służy |
|---|---|
| **Sprawdź teraz** | Pyta GitHub od razu, zamiast czekać na następne automatyczne sprawdzenie (co sześć godzin). |

!!! note "Aktualizacja odbywa się na serwerze"
    Sama aktualizacja nie jest przyciskiem w Parcelli. Osoba prowadząca
    serwer wpisuje polecenia pokazane w polu. Przekaż je dalej, jeśli to
    nie Ty. Najpierw pobierz [kopię zapasową](backup.md).

    Pole ostrzega też, że pierwsze polecenie zastępuje plik konfiguracyjny
    serwera aktualnym. Zmiany, które administrator serwera wprowadził w
    tym pliku, zostaną utracone, chyba że trzyma je w osobnym pliku
    nadpisującym, jak wyjaśnia instrukcja instalacji.

Przed aktualizacją przeczytaj informacje o wydaniu na GitHubie, aby
zobaczyć, co się zmieniło.

## Kopia zapasowa {#backup}

Karta **Kopia zapasowa** ma trzy przyciski:

| Przycisk | Do czego służy |
|---|---|
| **Kopie zapasowe w chmurze** | Otwiera harmonogram automatycznych kopii zapasowych w Twoim magazynie w chmurze. |
| **Przywróć z kopii zapasowej** | Otwiera stronę przywracania. |
| **Pobierz kopię zapasową** | Od razu pobiera pełną kopię zapasową. |

Wszystkie trzy opisuje strona [Kopia zapasowa i przywracanie](backup.md).

## Powiązane {#related}

- [Kopia zapasowa i przywracanie](backup.md)
- [Ustawienia stowarzyszenia](settings.md#updates)
