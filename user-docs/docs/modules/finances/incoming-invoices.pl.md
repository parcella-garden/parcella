# Faktury przychodzące {#incoming-invoices}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Faktury przychodzące to rachunki, które otrzymuje stowarzyszenie:
dostawca wody, ubezpieczyciel, sklep budowlany. Zapisywanie ich tutaj,
podzielonych na pozycje z kategorią księgową każda, i notowanie, kiedy
zostały zapłacone, daje stronę wydatków w
[zestawieniu księgowym](bookkeeping.md#accounting-statement).

!!! info "Kto może z tego korzystać"
    Część modułu **Finanse** (domyślnie wyłączonego). Oglądanie wymaga
    prawa odczytu **Finanse**; rejestrowanie faktur, łączenie kontaktów i
    dodawanie płatności wymaga prawa zapisu; usunięcie faktury lub
    płatności wymaga prawa usuwania. Przesyłanie i pobieranie
    zeskanowanego rachunku (załącznika) jest możliwe tylko dla członków
    zarządu i administratorów, i tylko gdy moduł **Magazyn w chmurze**
    jest włączony, a folder faktur przychodzących skonfigurowany. Zob.
    [Finanse](index.md).

## Lista faktur przychodzących {#incoming-invoices-list}

![Faktury przychodzące](../../assets/screenshots/finances/incoming-invoice-list.png)

Otwierasz ją przez **Finanse → Faktury przychodzące** albo kartę
**Faktury przychodzące** na panelu. Lista jest posortowana według daty
faktury, od najnowszych.

**Górny pasek**

| Przycisk | Do czego służy |
|---|---|
| **Zarejestruj fakturę przychodzącą** | Otwiera formularz nowej faktury przychodzącej (zob. niżej). Wymaga prawa zapisu. |
| **Powrót do Finansów** | Powrót do panelu finansów. |

**Filtr**

| Filtr | Do czego służy |
|---|---|
| **Nr faktury** | Faktury, których numer zawiera ten tekst. |
| **Nadawca** | Faktury, których nadawca zawiera ten tekst. |
| **Kwota od** / **Kwota do** | Suma faktury co najmniej / najwyżej tyle. |
| **Status płatności** | **Wszystkie**, **Otwarta**, **Częściowo opłacona** lub **Opłacona**. |
| **Filtruj** / **Wyczyść** | Stosuje filtr / czyści go. |

**Tabela**

| Kolumna / przycisk | Co pokazuje |
|---|---|
| **Data** | Data faktury. |
| **Nadawca** | Kto wystawił rachunek; kliknij, aby otworzyć [fakturę przychodzącą](#incoming-invoice). |
| **Nr faktury** | Numer faktury dostawcy, jeśli wpisany. |
| **Kategorie** | Jeden wiersz na pozycję: jej kategoria (lub „Bez kategorii”) i opis. |
| **Kwota** | Suma faktury (suma wszystkich pozycji). |
| **Status płatności** | **Otwarta**, **Częściowo opłacona** lub **Opłacona**, według zapisanych płatności. |
| Ikona pobierania | Pobiera załączony rachunek. Widoczna tylko, gdy jest załącznik i możesz korzystać z magazynu w chmurze. |
| Ikona kosza | Po potwierdzeniu usuwa fakturę przychodzącą wraz z pozycjami i płatnościami. Wymaga prawa usuwania. |

Jeśli nic jeszcze nie zarejestrowano: „Nie zarejestrowano jeszcze
żadnych faktur przychodzących.”

!!! note "Usunięcie zachowuje załącznik"
    „Czy na pewno usunąć tę fakturę przychodzącą? Załącznik nie zostanie
    usunięty z folderu w chmurze.” Zeskanowany rachunek zostaje we
    wspólnym folderze; w razie potrzeby usuń go tam ręcznie.

## Rejestrowanie faktury przychodzącej {#record-incoming-invoice}

Kliknij **Zarejestruj fakturę przychodzącą**. Otwiera się okno:

| Pole | Do czego służy |
|---|---|
| **Kontakt** | Opcjonalne. Widoczne tylko, gdy moduł [Kontakty zewnętrzne](../external-contacts.md) jest włączony i możesz czytać kontakty. Wybór dostawcy z kontaktów wypełnia za Ciebie **Nadawca** („Wybór kontaktu wypełnia pole nadawcy.”), chyba że już coś wpisałeś. **— brak —** nie łączy żadnego kontaktu. |
| **Nadawca** | Wymagane. Nazwa dostawcy tak, jak ma się pojawiać na listach, w dopasowaniu bankowym i w zestawieniu księgowym. |
| **Nr faktury** | Opcjonalne. Numer faktury dostawcy. |
| **Data faktury** | Wymagana, wstępnie wypełniona dzisiejszą datą. |
| **Notatka** | Opcjonalna. |
| **Pozycje** | Jeden wiersz na pozycję kosztową (zob. niżej). |
| **Dodaj pozycję** | Dodaje kolejny wiersz pozycji. Każdy wiersz poza pierwszym ma przycisk usuwania. |
| **Załącznik** | Opcjonalny. Zeskanowany lub sfotografowany rachunek. „Przesyłany do współdzielonego folderu w chmurze powyżej.” Widoczny tylko dla członków zarządu i administratorów, gdy magazyn w chmurze i folder faktur przychodzących są skonfigurowane. |
| **Zapisz** | Zapisuje fakturę. Widzisz „Zapisano.”. |
| **Anuluj** | Zamyka okno bez zapisywania. |

Każda pozycja ma trzy pola:

| Pole | Do czego służy |
|---|---|
| Kategoria | Opcjonalna [kategoria księgowa](bookkeeping.md#bookkeeping-categories). „—” oznacza brak; pozycja jest wtedy pokazywana jako „Bez kategorii”. |
| **Opis (co zakupiono)** | Opcjonalny dowolny tekst, np. „Serwis kosiarki”. Kilka pozycji może mieć tę samą kategorię, ale opisywać różne zakupy. |
| Kwota | Kwota pozycji, np. `249,90`. Pozycja bez prawidłowej kwoty jest pomijana. |

!!! warning "Sprawdź przed zapisaniem"
    Nadawcy, daty, pozycji i kwot nie można edytować po zapisaniu;
    później można zmienić tylko powiązany kontakt i płatności. Jeśli coś
    jest nie tak, usuń fakturę przychodzącą i zarejestruj ją ponownie.

Jeśli nie uda się przesłać załącznika, faktura i tak zostaje zapisana,
a błąd magazynu w chmurze jest pokazywany na górze listy. Nazwa pliku
załącznika w folderze w chmurze zaczyna się od numeru wewnętrznego,
więc dwa rachunki o tej samej nazwie pliku nigdy się nie nadpisują.
Sam folder ustawia się w **Integracje** → **Folder faktur
przychodzących**, zob. [Integracje](../../administration/integrations.md).

## Faktura przychodząca {#incoming-invoice}

![Faktura przychodząca](../../assets/screenshots/finances/incoming-invoice-detail.png)

Otwiera się po kliknięciu nadawcy na liście. Tytuł to „Faktura
przychodząca — *nadawca*”.

**Górny pasek**

| Przycisk | Do czego służy |
|---|---|
| **Pobierz załącznik** | Pobiera załączony rachunek z folderu w chmurze. Widoczny tylko, gdy jest załącznik i możesz korzystać z magazynu w chmurze. |
| **Powrót do faktur przychodzących** | Powrót do listy. |

Karta **Faktura**

| Pole | Co pokazuje |
|---|---|
| **Nadawca** | Nadawca tak, jak go wpisano. |
| **Kontakt** | Powiązany kontakt zewnętrzny, jako link do kontaktu, jeśli możesz oglądać kontakty („usunięty”, jeśli kontakt został później usunięty). Z prawem zapisu lista rozwijana i **Zapisz** pozwalają powiązać inny kontakt albo żaden. Zmiana kontaktu **nie** zmienia tekstu **Nadawca**. |
| **Nr faktury** | Numer faktury dostawcy. |
| **Data** | Data faktury. |
| **Notatka** | Notatka. |
| **Kwota** | Suma faktury. |
| **Status płatności** | **Otwarta**, **Częściowo opłacona** lub **Opłacona**. |

Karta **Pozycje**: każda pozycja z kategorią („kod · nazwa” lub „Bez
kategorii”), opisem i kwotą oraz **Suma**.

Karta **Płatności**: każda płatność zapisana dla tego rachunku z datą,
kwotą, kontem i notatką. Ikona kosza usuwa płatność (wymaga prawa
usuwania, pyta „Usunąć tę płatność?”). Jeśli nie ma żadnych: „Nie
zarejestrowano jeszcze żadnych płatności.”

Aby zapisać płatność (prawo zapisu):

| Pole | Do czego służy |
|---|---|
| **Kwota** | Wymagana. Ile stowarzyszenie zapłaciło, jako liczba dodatnia. Płatności częściowe są w porządku. |
| **Zapłacono dnia** | Wymagane, wstępnie wypełnione dzisiejszą datą. Ta data decyduje, w którym roku wydatek liczy się w zestawieniu księgowym. |
| **Notatka** | Opcjonalna. |
| **Konto** | Opcjonalne. [Konto](bank-accounts.md#accounts), z którego wyszły pieniądze; proponowane są tylko aktywne konta. Płatność pojawia się wtedy, jako kwota ujemna, w księgowaniach tego konta. |
| **Dodaj płatność** | Zapisuje płatność. |

Status zmienia się na **Opłacona**, gdy płatności osiągną sumę faktury.
Faktury przychodzące nie mają upomnień ani opłat.

!!! tip "Płatność z wyciągu bankowego"
    Zamiast wpisywać płatność tutaj, możesz zaimportować wyciąg bankowy
    na stronie księgowań konta: ujemne księgowanie o tej samej kwocie co
    otwarta faktura przychodząca jest proponowane jako dopasowanie i
    zapisywane jako jej płatność. Zob.
    [Rachunki bankowe i księgowania](bank-accounts.md#possible-matching-invoices).

!!! note "Liczą się tylko zapłacone rachunki"
    Zestawienie księgowe i plan budżetu liczą wydatek w dniu zapłaty.
    Faktura przychodząca bez płatności w ogóle się tam nie pojawia.

## Powiązane {#related}

- [Kontakty zewnętrzne](../external-contacts.md) -- strona kontaktu
  dostawcy pokazuje powiązane z nim faktury przychodzące.
- [Wnioski zakupowe](../purchase-requests.md) -- tam zatwierdza się
  zakup; wynikający z niego rachunek rejestruje się tutaj ręcznie.
  <!-- TODO(verify): there is no link between a purchase request and an incoming invoice in the code; confirm this is the intended workflow. -->
- [Kategorie, budżet i zestawienie](bookkeeping.md)
- [Integracje](../../administration/integrations.md) -- wspólny folder
  w chmurze na załączniki.
