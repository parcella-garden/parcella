# Przekazanie działki {#handing-over-a-parcel}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Dzierżawca wypowiada umowę, działka zostaje obejrzana i wyceniona,
zaproponowana osobom z listy oczekujących, a na koniec nowy dzierżawca
podpisuje umowę i dostaje klucze. Trwa to tygodnie lub miesiące i
angażuje kilku członków zarządu. Ta instrukcja pokazuje, co Parcella
zapisuje po drodze i jak [proces](../glossary.md#process) pilnuje
kroków, których sama nie zapisuje.

## Co Parcella śledzi -- a czego nie {#what-parcella-does-and-doesnt-track}

| Część przekazania | W Parcelli |
|---|---|
| Wypowiedzenie | Status działki **wypowiedziana**, z datą zapisywaną automatycznie i opcjonalną **Notatka o wypowiedzeniu**. |
| Dotychczasowi i nowi dzierżawcy | Zakończenie dotychczasowej [dzierżawy](../glossary.md#tenancy) zachowuje ją jako historię; nowa dzierżawa zaczyna się w dniu przekazania. **Przydziel działkę** przy zgłoszeniu robi oba kroki naraz. |
| Członkostwo dotychczasowego dzierżawcy | Kończy się automatycznie przy **Przydziel działkę**, jeśli nie ma on innej działki. |
| Folder dokumentów | Folder w chmurze dotychczasowych dzierżawców jest wycofywany w dniu przekazania; zastępuje go nowy. |
| Oględziny, [wycena](../glossary.md#valuation), oferta, oglądanie, umowa, klucze | Nie są wbudowane. Śledź je **procesem** (krok 1). |
| [Kaucja](../glossary.md#deposit) | Brak funkcji kaucji. Zanotuj kwotę i datę w procesie; pieniądze zaksięguj w **Finanse**, jeśli z nich korzystasz (krok 7). |
| Końcowe stany liczników | Parcella przechowuje **jeden odczyt na licznik na rok**. Stany z przekazania zanotuj w procesie (krok 6). |
| Cena między dotychczasowym a nowym dzierżawcą | **Celowo nieśledzona.** To, ile nowy dzierżawca płaci dotychczasowemu za altanę i nasadzenia, jest prywatną sprawą między nimi. Parcella nie ma na to pola -- nie dodawaj go też do swojego szablonu procesu. |

!!! info "Kto może to zrobić"
    Zmiany działek i dzierżaw wymagają **zapisu** w **Członkowie i
    działki**; **Przydziel działkę** wymaga też **zapisu** w
    **Kandydaci**. Szablony procesów wymagają pełnego dostępu (zarząd
    lub administrator); praca nad procesem wymaga **zapisu** w
    **Procesy**.

## 1. Przygotuj szablon procesu przekazania (jednorazowo) {#1-prepare-a-handover-process-template-once}

Moduł **Procesy** zawiera przykładowy szablon **Przekazanie działki**.
Zacznij od niego i dopasuj go do kolejności kroków w Twoim
stowarzyszeniu.

1. Otwórz **Procesy → Szablony** (strona nazywa się **Szablony
   procesów**).
2. W **Zacznij od przykładu** kliknij **Użyj** obok **Przekazanie
   działki**. Parcella tworzy zwykły szablon, który możesz dowolnie
   zmieniać. Dotyczy on **Działka**, więc każdy proces należy do jednej
   działki i pojawia się na jej stronie.
3. Przykład ma sześć etapów: **Oględziny**, **Wycena**, **Ogłoszenie**,
   **Nowy dzierżawca**, **Umowa i kaucja** oraz **Przekazanie**. Aby
   odpowiadał zwykłej kolejności poniżej, dodaj etapy i zmień ich nazwy
   w edytorze (wpisz **Nazwa etapu** i kliknij **Dodaj**; przeciągnij
   etapy, aby zmienić kolejność; pola dodasz, wpisując etykietę i
   naciskając Enter):

| Etap | Przykładowe pola | Typ pola |
|---|---|---|
| Wypowiedzenie *(nowy, pierwszy)* | Wypowiedzenie otrzymano dnia (wymagane) · Pismo z wypowiedzeniem | Data · Pliki (PDF, zdjęcia) |
| **Oględziny** | **Data oględzin** · **Stwierdzone usterki** · **Zdjęcia usterek** · **Wszystkie usterki usunięte** | z przykładu |
| **Wycena** | **Rzeczoznawca** · **Data wyceny** · **Protokół wyceny** | z przykładu |
| **Ogłoszenie** → zmień nazwę na „Oferta dla listy oczekujących” | **Treść ogłoszenia** · **Opublikowano** | z przykładu |
| Oglądanie *(nowy)* | Data oglądania · Zainteresowani kandydaci (notatki) | Data · Długi tekst |
| **Nowy dzierżawca** | **Nowy dzierżawca** (kandydat) · **Nawiązano kontakt** · **Wysłano dokumenty** | z przykładu |
| **Umowa i kaucja** | **Umowa kupna potwierdzona** · **Kaucja** · **Kaucja wpłynęła** | z przykładu |
| **Przekazanie** → podziel na „Podpisanie” i „Lista końcowa” | Podpisanie: **Podpisane przez nowego dzierżawcę**, **Kontrasygnowane przez zarząd**. Lista końcowa: **Klucze przekazane**, **Liczniki odczytane**, **Protokół przekazania** | z przykładu |

4. W etapie „Lista końcowa” dodaj pola typu **Liczba** na stany
   liczników przy przekazaniu, np. „Stan licznika wody przy
   przekazaniu” i „Stan licznika prądu przy przekazaniu” (zob. krok 6).

Oznacz pole jako **Wymagane**, jeśli proces nie może bez niego pójść
dalej. Zmiany w szablonie dotyczą tylko procesów rozpoczętych później.

!!! tip
    **Umowa kupna potwierdzona** to tylko pole wyboru: zarząd
    potwierdza, że dotychczasowy i nowy dzierżawca się porozumieli. Sama
    cena pozostaje sprawą między nimi dwoma.

Więcej: [Procesy](../modules/processes.md).

## 2. Zapisz wypowiedzenie {#2-record-the-notice}

Gdy wpłynie wypowiedzenie dzierżawcy:

1. Otwórz działkę w **Działki** i kliknij **Edytuj**.
2. Ustaw **Status** na **wypowiedziana**. Parcella zapisuje czas zmiany
   statusu; strona działki pokazuje wtedy **Wypowiedziana dnia**.
3. Opcjonalnie dodaj **Notatka o wypowiedzeniu** (powód, data
   wypowiedzenia, uwagi).
4. Kliknij **Zapisz zmiany**.

Dzierżawca pozostaje obecnym dzierżawcą -- i nadal dostaje faktury za
działkę -- do faktycznego zakończenia dzierżawy. Nie kończ dzierżawy
teraz; **Przydziel działkę** zrobi to w dniu przekazania (krok 5).

## 3. Rozpocznij proces {#3-start-the-process}

1. Na stronie działki, na karcie **Procesy**, kliknij **Rozpocznij
   proces**.
2. Wybierz swój **Szablon** przekazania. Opcjonalnie nadaj procesowi
   **Tytuł**.
3. Kliknij **Rozpocznij**.
4. Wypełnij pola pierwszego etapu i kliknij **Zapisz**. Gdy etap jest
   ukończony, kliknij **Gotowe -- następny etap**.

Proces pojawia się na stronie działki z bieżącym etapem oraz w
**Procesy** dla wszystkich, którzy nad nim pracują. Przesłane pliki
(pisma, zdjęcia, protokół wyceny) trafiają do folderu działki w
chmurze, jeśli jest ustawiony, a w przeciwnym razie do własnego
magazynu Parcelli.

Aby wrócić do wcześniejszego etapu, kliknij **Cofnij**, wybierz etap i
podaj **Powód**. Jeśli przekazanie nie dojdzie do skutku, użyj
**Przerwij proces** z podaniem powodu.

## 4. Oględziny, wycena, oferta, oglądanie {#4-inspection-valuation-offer-viewing}

Przechodź przez te etapy procesu w miarę, jak się odbywają. Protokół
[wyceny](../glossary.md#valuation) trafia do **Protokół wyceny**; treść
oferty do **Treść ogłoszenia**.

Aby znaleźć zainteresowanych, otwórz **Kandydaci** z filtrem
**Otwarte** -- lista jest posortowana według daty zgłoszenia. Osobom,
którym proponujesz działkę, ustaw **Działka zaproponowana**, a tej,
która ją bierze, **Przyjęte**. Przy włączonym module **Ogłoszenia**
zaznacz kilku kandydatów i kliknij **Napisz do zaznaczonych
kandydatów**, aby wysłać ofertę e-mailem.

Więcej: [Kandydaci](../modules/applicants.md).

## 5. Przekaż działkę nowemu dzierżawcy {#5-hand-the-parcel-over-to-the-new-tenant}

Gdy umowa jest podpisana -- albo, z datą w przyszłości, gdy tylko
termin jest ustalony:

1. Otwórz zgłoszenie nowego dzierżawcy i kliknij **Przydziel działkę**.
2. Wybierz tę działkę w **Wypowiedziana działka** i ustaw **Data
   przekazania**.
3. Dodaj partnera w **Kolejni kandydaci (współdzierżawcy)**, jeśli
   przejmują działkę razem.
4. Jeśli korzystasz z chmury, wpisz **Folder dokumentów dla nowych
   dzierżawców**. Folder dotychczasowych dzierżawców i tak zostanie
   wycofany w dniu przekazania.
5. Kliknij **Podgląd**, sprawdź dotychczasowych i nowych dzierżawców, a
   potem kliknij **Przekaż działkę** i potwierdź.

W dniu przekazania:

- dotychczasowa dzierżawa się kończy i przechodzi do **Byli
  dzierżawcy** na stronie działki;
- dotychczasowy dzierżawca bez innej działki odchodzi ze
  stowarzyszenia (**Członek do** to dzień przed datą przekazania);
- kandydaci zostają członkami, dzierżawcami i odbiorcami faktur;
- działka jest znowu **aktywna**.

Szczegóły oraz uzupełnianie kartoteki nowego członka opisuje
[Przyjęcie nowego członka](new-member.md), kroki 5 i 6.

### Jeśli nowy dzierżawca nie jest kandydatem {#if-the-new-tenant-isnt-an-applicant}

Na przykład gdy działkę przejmuje członek rodziny. Zrób to ręcznie:

1. Na stronie działki, w **Obecni dzierżawcy**, kliknij ikonę ołówka
   obok dotychczasowego dzierżawcy (**Edytuj dzierżawę**), ustaw
   **Dzierżawca do** na ostatni dzień i kliknij **Zapisz zmiany**. Albo,
   aby zakończyć ją dzisiaj, kliknij ikonę **Zakończ dzierżawę** i
   potwierdź *„Zakończyć dzierżawę? (historia zostaje zachowana)”*.
2. Jeśli dotychczasowy dzierżawca odchodzi ze stowarzyszenia, otwórz
   jego stronę członka, kliknij **Edytuj**, ustaw **Członek do** i
   kliknij **Zapisz zmiany**. Nie usuwaj go -- zob. ostrzeżenie poniżej.
3. Przypisz nowego dzierżawcę: **Wybierz członka…**, data początkowa,
   **Użyj jako adresu do faktury**, **Przypisz**. W razie potrzeby
   najpierw utwórz go w **Członkowie → Nowy członek**.
4. Edytuj działkę i ustaw **Status** z powrotem na **aktywna**.

!!! tip "Zapisywanie wypowiedzenia"
    Dzierżawca, który wypowiedział umowę, pozostaje adresem do faktury
    aż do odejścia: ustaw jego **Dzierżawca do** w **Edytuj dzierżawę**
    i zostaw zaznaczone **Użyj jako adresu do faktury**. Gdy ten dzień
    minie, pole odznacza się samo -- zadbaj, aby do tego czasu adresem
    do faktury był nowy dzierżawca.

!!! warning "Kończ, nie usuwaj"
    Zakończenie dzierżawy lub członkostwa zachowuje historię: kto miał
    którą działkę i kiedy oraz czyje były które godziny i faktury.
    Usunięcie członka usuwa go z każdego rozliczenia, łącznie z
    godzinami pracy z lat, w których był dzierżawcą.

## 6. Końcowe stany liczników {#6-final-meter-readings}

Parcella przechowuje jeden odczyt na licznik i rok, i to na nim opiera
się faktura roczna. Nie ma osobnego „odczytu przy przekazaniu”.

- Zapisz stany z dnia przekazania w procesie (etap „Lista końcowa” z
  kroku 1) i zaznacz **Liczniki odczytane**.
- Nie wprowadzaj ich jako odczytu rocznego na punkcie pomiarowym, chyba
  że naprawdę tego chcesz: roczny odczyt później w roku je
  **zastąpi**.
- Roczna faktura za wodę i prąd dla działki trafia do tego, kto jest
  odbiorcą faktury w chwili zatwierdzenia [serii
  faktur](../glossary.md#invoice-run) -- po przekazaniu do nowego
  dzierżawcy -- za zużycie z całego roku. Jak dotychczasowy i nowy
  dzierżawca się tym podzielą, zależy od nich i od zasad Twojego
  stowarzyszenia; rozlicz to poza Parcellą, korzystając ze stanów
  zapisanych w procesie.

Jeśli przy przekazaniu wymieniany jest licznik, zob. [Zbieranie
odczytów liczników](meter-readings.md#a-meter-is-replaced).

## 7. Kaucja i pieniądze {#7-deposit-and-money}

Parcella nie ma pola kaucji przy działce ani przy członku. Do
dokumentacji użyj procesu: **Kaucja** (kwota) i **Kaucja wpłynęła** w
etapie **Umowa i kaucja**.

Jeśli korzystasz z modułu **Finanse**, zaksięguj też same pieniądze:

- **Otrzymana kaucja**: otwórz **Finanse → Przegląd → Konta**, kliknij
  **Księgowania** obok konta, na które wpłynęły pieniądze, i użyj
  **Dodaj księgowanie** (albo **Importuj CSV** z wyciągiem bankowym).
- **Zwrot kaucji dotychczasowemu dzierżawcy**: tak samo, jako kwota
  ujemna.

<!-- TODO(verify): confirm with the treasurer whether a deposit should rather be billed as a one-off invoice run (a "Fixed amount per parcel" item scoped to this parcel) so it gets an invoice number. -->

**Godziny pracy.** Dzierżawca, który odchodzi w ciągu roku, nadal jest
winien [obowiązkowe godziny](../glossary.md#mandatory-hours) za ten
rok. Przy rozliczaniu na działkę jego godziny liczą się razem z
godzinami nowego dzierżawcy, a niedobór jest fakturowany odbiorcy
faktury działki w chwili serii faktur -- czyli nowemu dzierżawcy. Jeśli
Twoje stowarzyszenie chce inaczej, rozlicz to ręcznie. Zob. [Roczne
fakturowanie](annual-invoicing.md).

**Otwarte faktury** dotychczasowego dzierżawcy pozostają bez zmian;
numer faktury, odbiorca i adres są zapisane na każdej fakturze, więc
nadal możesz ściągać należności i wysyłać upomnienia.

## 8. Zakończ proces {#8-close-the-process}

Gdy ostatni etap jest gotowy, kliknij **Zakończ proces**. Zakończony
proces jest tylko do odczytu i pozostaje na stronie działki z pełną
**Historia**.

## Powiązane {#related}

- [Działki](../modules/parcels.md)
- [Kandydaci](../modules/applicants.md)
- [Członkowie](../modules/members.md)
- [Procesy](../modules/processes.md)
- [Woda i prąd](../modules/metering.md)
- [Rachunki bankowe i księgowania](../modules/finances/bank-accounts.md)
- [Przyjęcie nowego członka](new-member.md)
- Słownik: [kaucja](../glossary.md#deposit),
  [wycena](../glossary.md#valuation),
  [wypowiedzenie](../glossary.md#notice-of-termination),
  [dzierżawa](../glossary.md#tenancy)
