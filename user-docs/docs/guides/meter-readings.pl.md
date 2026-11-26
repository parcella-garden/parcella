# Zbieranie odczytów liczników {#collecting-meter-readings}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Raz w roku ktoś obchodzi teren i odczytuje każdy licznik wody i prądu:
licznik główny stowarzyszenia, po jednym liczniku na działkę oraz
własne przyłącza stowarzyszenia (świetlica, myjnia). Ta instrukcja
opisuje wprowadzanie tych odczytów -- w telefonie podczas obchodu albo
później z listy -- a także wymianę licznika i sprawdzanie wyników.

Woda i prąd działają dokładnie tak samo; każde ma własne menu. Poniższe
kroki mówią o **Woda**; dla prądu użyj zamiast tego menu **Prąd**.

!!! info "Kto może to zrobić"
    Wprowadzanie odczytów wymaga uprawnienia do **zapisu** w module
    **Woda** (lub **Prąd**); usunięcie odczytu wymaga uprawnienia do
    **usuwania**. Oba moduły są domyślnie włączone. Stowarzyszenie może
    dać zespołowi odczytującemu grupę z dokładnie tymi uprawnieniami --
    zob. [Grupy](../administration/groups.md).

## Jak Parcella liczy zużycie {#how-parcella-counts-consumption}

- Na każdym **[punkcie pomiarowym](../glossary.md#metering-point)**
  (przyłącze działki, licznik główny, przyłącze stowarzyszenia) jest w
  danym momencie zainstalowany jeden **licznik**.
- Licznik ma **jeden odczyt na rok**. Zużycie w roku to ten odczyt minus
  odczyt z poprzedniego roku -- albo minus **Stan początkowy** licznika,
  jeśli to pierwszy odczyt.
- Wprowadzenie odczytu za rok, który już ma odczyt, **zastępuje** go.
- Odczyty wprowadza się dokładnie tak, jak pokazuje wyświetlacz. Niektóre
  liczniki prądu pokazują tylko część rzeczywistej wartości; ich punkt
  pomiarowy ma wtedy **Mnożnik** (np. 20), który rozliczenie uwzględnia.

## 1. Przed obchodem: sprawdź listę punktów pomiarowych {#1-before-the-round-check-the-list-of-metering-points}

1. Otwórz **Woda → Przegląd**. Kafelki pokazują, ile jest liczników
   głównych, przyłączy działek i przyłączy stowarzyszenia, oraz
   **Brakujące punkty pomiarowe**: działki bez przyłącza wody w Parcelli.
2. Kliknij **Pokaż** pod **Brakujące punkty pomiarowe**, aby zobaczyć te
   działki; każda prowadzi do **Nowy punkt pomiarowy** z już wybraną
   działką. Dodaj te, które naprawdę mają licznik.
3. Przyłącze przez jakiś czas bez dostaw (woda zakręcona na pustej
   działce)? Otwórz jego punkt pomiarowy, ustaw **Wyłącz od** i kliknij
   **Wyłącz**. Znika on z listy odczytów, dopóki nie klikniesz **Włącz
   ponownie**.

Jeśli Twoja lista liczników jest jeszcze w arkuszu kalkulacyjnym,
zaimportuj ją -- zob. [Import członków i
działek](csv-import.md#4-metering-points).

## 2. Możliwość A: wprowadzaj odczyty w telefonie podczas obchodu {#2-option-a-enter-readings-on-your-phone-while-you-walk}

1. Otwórz w telefonie **Woda → Odczyty**. Strona pokazuje bieżący rok;
   w razie potrzeby wybierz inny w liście lat u góry.
2. Strona wymienia **Licznik główny**, **Działki** (posortowane według
   numeru działki) i **Przyłącza stowarzyszenia**. Każdy wiersz pokazuje
   numer licznika i odczyt z **Poprzedni rok** do porównania.
3. Wpisz odczyt w pole wiersza i stuknij przycisk zapisu obok. Wiersz
   pokazuje wtedy wartość jako **zarejestrowano**.
4. Przejdź do następnego licznika. Wiersze bez wartości mówią **Jeszcze
   nie wprowadzono**.

Odczyty wprowadzone tutaj dostają dzisiejszą datę. Aby użyć innej daty
lub dodać notatkę, wprowadź odczyt na stronie punktu pomiarowego
(możliwość C).

## 3. Możliwość B: zbieraj na papierze lub w arkuszu, potem zaimportuj {#3-option-b-collect-on-paper-or-in-a-spreadsheet-then-import}

1. Otwórz **Woda → Odczyty**, wybierz rok i kliknij **Eksport CSV**.
   Dostaniesz plik z jednym wierszem na licznik: **Typ**, **Numer
   działki**, **Oznaczenie**, **Numer licznika**, **Rok** oraz puste
   kolumny **Data**, **Odczyt** i **Notatka**.
2. Wydrukuj go albo wypełnij na tablecie. Uzupełnij **Data** i
   **Odczyt** dla każdego odczytanego licznika.
3. Z powrotem na **Woda → Odczyty** kliknij **Import CSV**, wybierz plik
   i kliknij **Importuj**.
4. Na ekranie **Mapowanie kolumn CSV** sprawdź przypisanie kolumn. Jeśli
   Twój plik nie ma kolumny z rokiem, wpisz go w **Rok domyślny
   (opcjonalnie)**. Kliknij **Importuj**.
5. Przeczytaj podsumowanie na stronie odczytów: ile odczytów
   zarejestrowano, ile wierszy pominięto i dlaczego.

Wiersze bez odczytu są pomijane jako „nieprawidłowy wiersz” -- to
normalne dla liczników, których jeszcze nie odczytano. Szczegóły o
kolumnach i komunikatach błędów: [Import członków i
działek](csv-import.md#5-meter-readings).

## 4. Możliwość C: wprowadź pojedynczy odczyt z datą i notatką {#4-option-c-enter-a-single-reading-with-date-and-note}

1. Otwórz **Woda → Punkty pomiarowe** i kliknij punkt pomiarowy.
2. Na dole, pod **Odczyty**, wypełnij **Rok**, **Data**, **Stan
   licznika** i opcjonalnie **Notatka**.
3. Kliknij **Zarejestruj odczyt**.

Tabela **Odczyty** na tej samej stronie wymienia każdy rok z odczytem i
zużyciem. Błędny odczyt można tam usunąć.

## 5. Gdy odczyt wygląda na błędny {#5-when-a-reading-looks-wrong}

Odczyt niższy niż w poprzednim roku (albo wyższy niż już zarejestrowany
późniejszy) jest **mimo to zapisywany**, z ostrzeżeniem w rodzaju
*„Odczyt zapisany, ale proszę go sprawdzić: Stan licznika (…) jest
mniejszy niż poprzedni stan (…) tego samego licznika. Czy wcześniejszy
odczyt był szacowany? Proszę sprawdzić.”* Odczyt zachowuje znacznik
ostrzeżenia na stronie odczytów i na punkcie pomiarowym.

Częste przyczyny: literówka, źle odczytana cyfra, wcześniejszy odczyt
oszacowany zbyt wysoko albo licznik, który faktycznie wymieniono (krok
6). Popraw wartość, rejestrując odczyt ponownie za ten sam rok.

## 6. Wymiana licznika {#a-meter-is-replaced}

Gdy licznik zostaje fizycznie wymieniony -- na przykład dlatego, że
kończy się jego legalizacja:

1. Odczytaj stary licznik ostatni raz, jeśli jeszcze możesz, i wprowadź
   ten stan na stronie punktu pomiarowego jako odczyt za rok
   (możliwość C).
2. Na karcie **Aktualny licznik (woda)** (dla prądu **Aktualny licznik
   (prąd)**) otwórz **Wymień licznik**.
3. Wpisz **Stary licznik zdemontowano dnia**, **Nowy licznik
   zainstalowano dnia**, **Nowy numer**, **Legalizacja do** (rok) oraz
   **Stan początkowy** nowego licznika (zwykle to, co pokazuje jego
   wyświetlacz przy montażu).
4. Kliknij **Wymień** i potwierdź.

Stary licznik nie jest usuwany: trafia do **Poprzednie liczniki** z
datami montażu i demontażu oraz swoim **Ostatni stan**. Od teraz odczyty
trafiają do nowego licznika, którego zużycie liczy się od jego **Stan
początkowy**.

!!! tip "Zużycie w roku wymiany"
    Wypełnij w formularzu wymiany **Stan końcowy starego licznika** --
    to, co stary licznik pokazuje w dniu demontażu. Zużycie w roku
    sumuje wtedy oba liczniki (stary do wymiany, nowy od jego stanu
    początkowego) i ta suma trafia na fakturę roczną. Bez stanu
    końcowego część starego licznika od jego ostatniego odczytu nie
    zostanie rozliczona.

!!! tip "Literówka, a nie nowy licznik?"
    Jeśli tylko pomyliłeś się w numerze licznika lub stanie
    początkowym, użyj zamiast tego **Edytuj licznik**. **Wymień
    licznik** służy do rzeczywistej wymiany.

## 7. Sprawdź rok {#7-check-the-year}

1. Otwórz **Woda → Rozliczenie** i wybierz rok.
2. Kafelki porównują **Licznik główny** z **Działki razem** i
   **Stowarzyszenie razem**; tabele poniżej wymieniają każdy punkt
   pomiarowy z jego **Zużycie**. Punkty, którym brakuje odczytu,
   pokazują **brak odczytu**.
3. Jeśli działki i przyłącza stowarzyszenia razem zużyły więcej niż
   pokazuje licznik główny, Parcella wyświetla ostrzeżenie. To normalne,
   dopóki odczyty są jeszcze wprowadzane; gdy wszystkie są już w
   systemie, wskazuje to na źle odczytany licznik.
4. **Eksport CSV** pobiera rozliczenie do Twojej dokumentacji lub dla
   dostawcy mediów.

**Woda → Przegląd** pokazuje też, ile punktów pomiarowych nie ma jeszcze
odczytu za dany rok, z linkiem **Zarejestruj teraz →**.

## 8. Ustal cenę do rozliczenia {#8-set-the-price-for-billing}

Jeśli rozliczasz wodę i prąd fakturami rocznymi w Parcelli:

1. Otwórz **Woda → Konfiguracja**.
2. W **Nowa/aktualizacja ceny** wpisz **Rok** i **Cena za m³** oraz
   opcjonalnie **Notatka** (np. „zmiana stawki dostawcy”).
3. Kliknij **Zapisz**.

Bez ceny na dany rok seria faktur nie rozlicza wody za ten rok. Następnie
przejdź do [Roczne fakturowanie](annual-invoicing.md).

## Powiązane {#related}

- [Woda i prąd](../modules/metering.md)
- [Import członków i działek](csv-import.md)
- [Roczne fakturowanie](annual-invoicing.md)
- [Przekazanie działki](parcel-handover.md)
- Słownik: [punkt pomiarowy](../glossary.md#metering-point),
  [licznik](../glossary.md#meter)
