# Roczne fakturowanie {#running-the-annual-invoices}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Raz w roku stowarzyszenie wystawia faktury za każdą działkę: dzierżawa,
woda, prąd, ubezpieczenie, nieodpracowane godziny, może składka
członkowska albo jednorazowa [składka ogólna](../glossary.md#general-levy).
W Parcelli jest to [seria faktur](../glossary.md#invoice-run):
definiujesz pozycje raz, sprawdzasz podgląd każdej pojedynczej faktury,
zatwierdzasz, aby nadać numery faktur, a następnie je wysyłasz --
e-mailem, na papierze albo do folderu każdej działki w chmurze. Potem
zapisujesz płatności i wysyłasz [upomnienia](../glossary.md#dunning).

!!! info "Kto może to zrobić"
    Wszystko tutaj wymaga uprawnienia do **zapisu** w **Finanse**. Moduł
    **Finanse** jest w nowej instalacji **wyłączony**; włącz go w
    **Administracja → Ustawienia → Moduły funkcjonalne** (zob.
    [Włączanie i wyłączanie modułów](../administration/modules.md)).

!!! warning "Zatwierdzenia nie można cofnąć"
    Dopóki nie zatwierdzisz, nic nie jest zapisywane jako faktura i nic
    nie jest wysyłane -- zmieniaj pozycje, ile chcesz. Zatwierdzenie
    nadaje trwałe numery faktur i blokuje serię. Najpierw pobierz kopię
    zapasową (**Administracja → Użytkownicy → Pobierz kopię
    zapasową**).

## 1. Sprawdź ustawienia finansowe (jednorazowo) {#1-check-the-finance-settings-once}

1. Otwórz **Administracja → Ustawienia** i znajdź **Ustawienia
   finansowe**.
2. Wpisz dane bankowe stowarzyszenia: **Nazwa banku**, **IBAN**,
   **BIC**, **Posiadacz konta**. Pojawiają się w stopce każdej faktury.
3. Sprawdź **Format numeru faktury**. Domyślnie to rok i kolejny numer;
   możesz użyć własnego, na przykład `R-{year}-{number}`. `{number}`
   jest wymagane.
4. Zostaw **Następny numer faktury (nadpisanie)** puste, chyba że
   pierwsza seria faktur w Parcelli musi kontynuować wcześniej używaną
   numerację. Jest używane raz, a potem czyszczone.
5. Upewnij się, że **E-mail (SMTP)** jest skonfigurowany, jeśli chcesz
   wysyłać faktury e-mailem.
6. Kliknij **Zapisz ustawienia**.

## 2. Przygotuj katalog pozycji (raz, potem używaj ponownie) {#2-prepare-the-item-catalog-once-then-reuse}

Katalog pozycji przechowuje pozycje, które fakturujesz co roku, więc nie
musisz ich definiować od nowa dla każdej serii.

1. Otwórz **Finanse → Przegląd** i kliknij **Katalog pozycji**.
2. W **Nowy szablon pozycji** wypełnij **Kolejność** (miejsce na
   fakturze), **Nazwa**, **Opis**, **Sposób naliczania**, **Cena
   jednostkowa** i opcjonalnie **Kategoria**.
3. Wybierz, kogo dotyczy (zob. niżej), i kliknij przycisk **+**.

| Sposób naliczania | Co fakturuje |
|---|---|
| **Kwota stała za działkę** | Cenę jednostkową raz na działkę -- np. dzierżawę. |
| **Kwota stała za osobę** | Cenę jednostkową raz na *członka* -- np. składkę członkowską, także dla członków bez działki. |
| **Za dzierżaw. m²** | Cena jednostkowa × powierzchnia działki. |
| **Udział w dzierżawie powierzchni wspólnej** | Powierzchnia wspólna (Powierzchnia B), podzielona równo na fakturowane działki, × cena jednostkowa. |
| **Obciążenia publiczne (własna powierzchnia + udział w powierzchni wspólnej)** | Własna powierzchnia działki plus jej udział w powierzchni wspólnej, × cena jednostkowa. |
| **Ogólna składka (podzielona równo na wszystkie działki)** | Cena jednostkowa to kwota *łączna*, dzielona równo na wszystkie fakturowane działki. |
| **Zużycie wody (z modułu)** | Zużycie wody na działce × cena wody na dany rok. |
| **Zużycie energii (z modułu)** | Zużycie prądu na działce × cena prądu na dany rok. |
| **Koszt ubezpieczenia (z modułu)** | Ubezpieczenie działki, jeden wiersz na rodzaj ubezpieczenia. |
| **Niedobór godzin pracy (z modułu)** | Brakujące [obowiązkowe godziny](../glossary.md#mandatory-hours) × stawka godzinowa. |

**Kogo dotyczy pozycja.** Pozycje oparte na działkach mają **Dotyczy
każdej działki**; odznacz to, aby wybrać pojedyncze **Działki**.
**Kwota stała za osobę** ma zamiast tego **Dotyczy każdego członka** i
wybór **Członkowie**. Cztery pozycje „z modułu” same wybierają działki
-- zamiast wyboru pokazane jest **Automatycznie (...)** -- a ich cena
jednostkowa jest **Obliczane automatycznie**.

Więcej: [Serie faktur](../modules/finances/invoice-runs.md).

## 3. Sprawdź liczby, z których korzystają pozycje automatyczne {#3-check-the-numbers-the-automatic-items-use}

Pozycje „z modułu” biorą swoje liczby z innych modułów. Sprawdź je dla
fakturowanego roku **przed** zatwierdzeniem.

**Woda i prąd**

1. Otwórz **Woda → Konfiguracja** i sprawdź, czy dla roku istnieje cena
   (**Cena za m³**) (w **Historia cen**). Jeśli nie, wpisz **Rok** i
   cenę w **Nowa/aktualizacja ceny** i kliknij **Zapisz**. To samo zrób
   w **Prąd → Konfiguracja**.
2. Otwórz **Woda → Przegląd**. Jeśli pokazuje, że niektóre punkty
   pomiarowe nie mają jeszcze odczytu za dany rok, najpierw je zbierz
   -- zob. [Zbieranie odczytów liczników](meter-readings.md). Działka
   bez odczytu za dany rok nie dostaje w ogóle pozycji za wodę.
3. Otwórz **Woda → Rozliczenie** za dany rok i poszukaj działek z
   **brak odczytu** lub z nieprawdopodobnym zużyciem.

**Godziny pracy**

1. Otwórz **Prace społeczne → Wpisy i przegląd** i sprawdź
   **Konfiguracja godzin** na dany rok: wymagane godziny i **Stawka
   godzinowa**.
2. Otwórz **Prace społeczne → Rozliczenie roczne** za dany rok. Sprawdź
   kolumny **Pozostało** i **Zaległość** -- to zostanie zafakturowane.
   Brakuje obecności, patronatów lub zwolnień? Popraw je teraz (zob.
   [Organizacja terminu prac](work-session.md)).

**Ubezpieczenia**

1. Otwórz **Ubezpieczenia → Konfiguracja** i **Ubezpieczenia → Działki**
   i sprawdź ceny na dany rok oraz ubezpieczenie każdej działki.

!!! tip "Kto dostaje fakturę"
    Faktura za działkę trafia do obecnych dzierżawców działki
    oznaczonych **Użyj jako adresu do faktury**. Działki bez takiego
    dzierżawcy nie dostają faktury. Sprawdź to na stronach działek
    przed zatwierdzeniem -- zwłaszcza po przekazaniu działki.

## 4. Utwórz serię faktur {#4-create-the-invoice-run}

1. Otwórz **Finanse → Faktury wychodzące** (strona nazywa się **Faktury
   roczne**).
2. Kliknij **Nowa seria faktur**.
3. Wpisz fakturowany **Rok**, **Temat** (np. „Faktura roczna 2026”),
   **Data wystawienia** i **Termin płatności**.
4. Opcjonalnie napisz **Tekst stopki**. Może zawierać
   `{invoice_number}`, `{parcel_number}`, `{invoice_address}` i
   `{due_date}`, które są uzupełniane dla każdej faktury.
5. Kliknij **Utwórz**.

Seria jest **Wersja robocza**. Otwórz ją przyciskiem **Otwórz**.

## 5. Dodaj pozycje {#5-add-the-line-items}

1. Na stronie serii, w **Dodaj z katalogu pozycji**, zaznacz pozycje z
   katalogu na ten rok i kliknij **Dodaj zaznaczone pozycje**.
2. Dla wszystkiego, co jest fakturowane tylko w tym roku, wypełnij
   **Dodaj pozycję** na dole, tak samo jak w katalogu.
3. Sprawdź tabelę **Definicje pozycji**: kolejność, ceny, kogo dotyczy
   każda pozycja. Dopóki seria jest wersją roboczą, możesz jeszcze
   edytować lub usuwać pozycje.

## 6. Podgląd {#6-preview}

1. Kliknij **Podgląd** u góry strony serii.
2. Strona pokazuje, ile faktur zostałoby utworzonych, i wymienia je w
   **Obliczone faktury**, z odbiorcą i sumą częściową.
3. Otwórz kilka przyciskiem **PDF** i sprawdź je: adres, pozycje,
   kwoty, stopka.
4. Aby coś poprawić, przejdź **Powrót do serii faktur**, zmień pozycje
   i ponownie otwórz podgląd. Nic jeszcze nie zostało zapisane ani
   wysłane.

Jeśli strona mówi *„Nie zostałaby utworzona żadna faktura”*, sprawdź
zakres działek w pozycjach i znacznik **Użyj jako adresu do faktury**
u dzierżawców.

## 7. Zatwierdź {#7-finalize}

1. Na stronie podglądu kliknij **Zakończ i nadaj numery faktur** i
   potwierdź.
2. Parcella tworzy faktury z trwałymi numerami. Strona serii pokazuje
   teraz, że jest zatwierdzona, i wymienia **Faktury**.

Imiona, nazwiska i adresy odbiorców są zapisywane na każdej fakturze w
stanie z tej chwili. Późniejsze zmiany adresu nie zmieniają
zatwierdzonych faktur.

## 8. Wyślij faktury {#8-send-the-invoices}

1. Na stronie zatwierdzonej serii znajdź kartę **Doręczenie**.
2. Kliknij **Wyślij e-maile i prześlij do chmury**.
    - Faktury są wysyłane e-mailem (z załączonym PDF) do odbiorców
      faktur, którzy mają **Może otrzymywać informacje e-mailem** i
      adres e-mail.
    - Jeśli działka ma folder dokumentów w chmurze, faktura jest tam
      również przesyłana.
    - Ponowne kliknięcie wysyła tylko to, czego jeszcze nie wysłano.
3. Kliknij **Pobierz pakiet do druku**. Zawiera on list dla każdego
   dzierżawcy, który nie dostaje faktur e-mailem, jako jeden PDF do
   wydruku i wysłania: jeden list na adres, wymieniający osoby pod tym
   adresem bez e-maila. Dotyczy to też kogoś, kogo współlokator dostał
   e-mail. Są one następnie oznaczane jako uwzględnione w pakiecie do
   druku.

Kolumna **Doręczenie** pokazuje dla każdej faktury, czy została
**Wysłano e-mailem**, **Uwzględniono w pakiecie do druku** czy
**Przesłano do chmury**. Aby wysłać pojedynczą fakturę ponownie, otwórz
ją i kliknij **Wyślij e-mail ponownie**.

Więcej: [Faktury, płatności i upomnienia](../modules/finances/invoices.md).

## 9. Zapisz płatności {#9-record-payments}

**Ręcznie**

1. Otwórz serię (albo **Wszystkie faktury** w **Faktury roczne**, aby
   szukać we wszystkich seriach po numerze faktury, odbiorcy lub
   kwocie).
2. Kliknij **Płatność** w wierszu faktury.
3. Wpisz **Kwota**, **Zapłacono dnia**, opcjonalnie **Notatka** i
   **Konto**, na które wpłynęły pieniądze, i kliknij **Dodaj
   płatność**.

Płatności częściowe są w porządku; status zmienia się sam z **Otwarta**
na **Częściowo opłacona** i na **Opłacona**.

**Z wyciągu bankowego**

1. Jednorazowo: otwórz **Finanse → Przegląd → Konta** i dodaj swoje
   konto bankowe w **Nowe konto**.
2. Kliknij **Księgowania** obok konta, a następnie **Importuj CSV**.
3. Prześlij wyciąg wyeksportowany z bankowości internetowej. Na ekranie
   **Mapowanie kolumn CSV** przypisz co najmniej **Data** i **Kwota**;
   **Opis**, **Nadawca / odbiorca** i **IBAN** pomagają w
   dopasowaniu.
4. Na ekranie **Dopasuj wiersze do faktur** Parcella proponuje dla
   każdej wpłaty otwarte faktury o tej samej kwocie. Wybierz właściwą,
   aby zapisać wpłatę jako płatność na tej fakturze, albo wybierz
   **Zarejestruj jako zwykłe księgowanie**.
5. Kliknij **Importuj CSV** na dole strony, aby utworzyć księgowania i
   płatności.

Więcej: [Rachunki bankowe i księgowania](../modules/finances/bank-accounts.md).

## 10. Wyślij upomnienia {#10-send-reminders}

1. Po terminie płatności otwórz **Finanse → Upomnienia**. **Zaległe
   faktury** wymienia każdą niezapłaconą fakturę po terminie, z tym,
   jak długo jest zaległa i ile upomnień wysłano.
2. Kliknij **Otwórz** obok faktury.
3. Opcjonalnie wpisz **Opłata (opcjonalnie)** i **Wiadomość
   (opcjonalnie)**.
4. Kliknij **Wyślij upomnienie**.

Parcella tworzy kolejne upomnienie jako PDF (**Upomnienie nr 1**,
**nr 2**, …), dolicza opłatę do należnej kwoty i wysyła je e-mailem,
jeśli członek zgodził się na e-mail; w przeciwnym razie jest oznaczane
**Do druku/wysyłki pocztowej**, abyś je wydrukował i wysłał. Nie ma
stałych stopni upomnień -- to Ty decydujesz, kiedy wysłać następne.

## Powiązane {#related}

- [Finanse](../modules/finances/index.md)
- [Serie faktur](../modules/finances/invoice-runs.md)
- [Faktury, płatności i upomnienia](../modules/finances/invoices.md)
- [Rachunki bankowe i księgowania](../modules/finances/bank-accounts.md)
- [Kategorie, budżet i zestawienie](../modules/finances/bookkeeping.md)
- [Woda i prąd](../modules/metering.md)
- [Prace społeczne](../modules/work-hours.md)
- [Ubezpieczenia](../modules/insurance.md)
- [Zbieranie odczytów liczników](meter-readings.md)
