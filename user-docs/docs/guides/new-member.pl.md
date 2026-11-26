# Przyjęcie nowego członka {#welcoming-a-new-member}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Ktoś ubiega się o ogród, dostaje propozycję działki, zgadza się -- i
zostaje członkiem oraz dzierżawcą. Ta instrukcja prowadzi tą drogą
przez Parcellę, od zgłoszenia aż po powitanie.

Członkiem można zrobić kogoś na dwa sposoby:

- **Ze zgłoszenia** (kroki 1-6): osoba jest na Twojej [liście
  oczekujących](../glossary.md#applicant) w **Kandydaci**.
  **Przydziel działkę** tworzy wtedy za jednym razem kartotekę członka,
  [dzierżawę](../glossary.md#tenancy) i adres do faktury. To zwykła
  droga.
- **Ręcznie** (krok 7): dla kogoś, kto nigdy nie był na liście
  oczekujących, albo dla działki, która nie jest wypowiedziana.

!!! info "Kto może to zrobić"
    Praca ze zgłoszeniami wymaga uprawnienia do **zapisu** w
    **Kandydaci**; przydzielenie działki wymaga też **zapisu** w
    **Członkowie i działki**. Członkowie zarządu i administratorzy mają
    oba. Moduł **Kandydaci** jest domyślnie włączony.

## 1. Wpływa zgłoszenie {#1-the-application-comes-in}

Zgłoszenia przychodzą na dwa sposoby:

- **Z Twojej strony internetowej**, jeśli stowarzyszenie ma tam
  formularz zgłoszeń i włączone jest **Publiczne API formularza
  zgłoszeń** (zob. [Integracje](../administration/integrations.md)).
  Pojawiają się same.
- **Ręcznie**, dla zgłoszeń telefonicznych, listownych lub osobistych:
  otwórz **Kandydaci**, kliknij **Dodaj kandydata**, wypełnij co
  najmniej **Adres e-mail** (jedyne pole wymagane), a do tego według
  uznania **Imię**, **Nazwisko**, **Telefon**, **Wiadomość kandydata** i
  **Notatka zarządu**, i kliknij **Zapisz**.

Aby wprowadzić stare zgłoszenie z papierowej listy oczekujących, ustaw
**Data zgłoszenia** na pierwotną datę. Data zgłoszenia decyduje o
kolejności na liście oczekujących.

Nowe zgłoszenia pokazują licznik obok **Kandydaci** w menu bocznym i na
pulpicie, dopóki ktoś się nimi nie zajmie.

!!! tip "Czerwona flaga"
    Jeśli imię i nazwisko, e-mail lub telefon kandydata pasuje do
    kontaktu zewnętrznego z Twoim tagiem „czerwonej flagi”, lista i
    strona kandydata pokazują ostrzeżenie **Czerwona flaga**. Zob.
    [Kandydaci](../modules/applicants.md).

## 2. Nawiąż kontakt {#2-get-in-touch}

1. Otwórz **Kandydaci** i kliknij nowe zgłoszenie.
2. W polu **Skontaktuj się z kandydatem** sprawdź i popraw treść
   e-maila. Temat brzmi *„Dziękujemy za zapisanie się na naszą listę
   oczekujących!”*.
3. Kliknij **Wyślij** i potwierdź.

Parcella wysyła tekst e-mailem do kandydata i ustawia status na
**Skontaktowano**. To pole jest widoczne tylko przy statusie **Nowy**.
Jeśli skontaktowałeś się w inny sposób, po prostu zmień status ręcznie
(następny krok).

Domyślną treść tego e-maila zmienisz w **Administracja → Ustawienia →
Kandydaci → Treść e-maila do nowych kandydatów**.

## 3. Śledź status zgłoszenia {#3-track-the-applications-status}

W miarę postępów otwórz zgłoszenie, wybierz nowy **Status** i kliknij
**Zapisz**:

| Status | Znaczenie |
|---|---|
| **Nowy** | Właśnie wpłynęło. |
| **Skontaktowano** | Nawiązano kontakt; kandydat jest na liście oczekujących. |
| **Działka zaproponowana** | Zaproponowano konkretną działkę. |
| **Przyjęte** | Kandydat chce działkę; przekazanie jest w przygotowaniu. |
| **Odrzucone** | Bez kolejnych propozycji. |
| **Zamknięte (działka przydzielona)** | Ustawiane automatycznie przez **Przydziel działkę** (krok 5). |

Jeśli kandydat odrzuci działkę, ale chce zostać na liście, ustaw go z
powrotem na **Skontaktowano**. Każda zmiana statusu jest widoczna w
**Historia statusu** na stronie zgłoszenia.

## 4. Upewnij się, że działka jest wypowiedziana {#4-make-sure-the-parcel-is-terminated}

**Przydziel działkę** proponuje tylko działki ze statusem
**wypowiedziana** -- działkę, którą ktoś opuścił lub właśnie opuszcza.

1. Otwórz działkę w **Działki** i kliknij **Edytuj**.
2. Ustaw **Status** na **wypowiedziana**, opcjonalnie dodaj **Notatka o
   wypowiedzeniu** i kliknij **Zapisz zmiany**.

Jeśli dotychczasowy dzierżawca jest jeszcze w trakcie odchodzenia, zob.
[Przekazanie działki](parcel-handover.md) -- opisuje całe przekazanie,
łącznie ze stroną dotychczasowego dzierżawcy.

## 5. Przydziel działkę {#5-assign-the-parcel}

1. Otwórz zgłoszenie i kliknij **Przydziel działkę**. (Przycisk jest
   dostępny przy każdym otwartym zgłoszeniu -- **Nowy**,
   **Skontaktowano**, **Działka zaproponowana** albo **Przyjęte**.)
2. Wybierz **Wypowiedziana działka**. Lista pokazuje każdą działkę z jej
   obecnymi dzierżawcami.
3. Ustaw **Data przekazania** -- dzień, w którym nowy dzierżawca
   przejmuje działkę. Może leżeć w przyszłości.
4. Opcjonalnie zaznacz **Kolejni kandydaci (współdzierżawcy)** -- na
   przykład partnera, który zgłosił się osobno i przejmuje działkę
   razem z tym kandydatem.
5. Opcjonalnie wpisz **Folder dokumentów dla nowych dzierżawców**
   (widoczne tylko, jeśli możesz zarządzać folderami w chmurze).
6. Kliknij **Podgląd**.
7. Sprawdź pole **Przekazanie działki … w dniu …**:
    - **Dotychczasowi dzierżawcy**: ich dzierżawa kończy się w dniu
      przekazania. Jeśli nie mają innej działki, ich członkostwo kończy
      się dzień wcześniej.
    - **Nowi dzierżawcy i odbiorcy faktur**: każdy kandydat albo
      **zostaje nowym członkiem** (imię i nazwisko, e-mail i telefon
      pochodzą ze zgłoszenia), albo -- jeśli aktywny członek używa już
      tego samego adresu e-mail -- zostaje powiązany z tym istniejącym
      członkiem.
8. Kliknij **Przekaż działkę** i potwierdź.

Co dzieje się w jednym kroku:

- Kandydaci zostają członkami, z **Członek od** ustawionym na datę
  przekazania.
- Zostają dzierżawcami działki od daty przekazania, z zaznaczonym
  **Użyj jako adresu do faktury**.
- Dotychczasowi dzierżawcy stają się byłymi dzierżawcami -- historia
  zostaje na stronie działki.
- Status działki wraca na **aktywna**.
- Zgłoszenia otrzymują status **Zamknięte (działka przydzielona)**.

Przy dacie przekazania w przyszłości dotychczasowi dzierżawcy pozostają
dzierżawcami, członkami i odbiorcami faktur do tego dnia; nowi są
pokazani na stronie działki jako przyszli („od …”) i przejmują działkę
w tym dniu.

## 6. Uzupełnij kartotekę nowego członka {#6-complete-the-new-members-record}

Przekazanie kopiuje tylko imię i nazwisko, e-mail i telefon. Uzupełnij
resztę:

1. Otwórz **Członkowie** i kliknij nowego członka (albo skorzystaj z
   linku na stronie działki).
2. Kliknij **Edytuj** i dodaj **Data urodzenia**, **IBAN** oraz adres
   (**Ulica i numer domu**, **Kod pocztowy**, **Miejscowość**).
3. Sprawdź **Może otrzymywać informacje e-mailem**. Jest zaznaczone u
   członków utworzonych przez **Przydziel działkę**, bo kandydat podał
   adres e-mail; odznacz je, jeśli członek chce tylko korespondencji
   papierowej. Bez tego faktury i ogłoszenia trafiają do stosu do
   wydruku zamiast do skrzynki odbiorczej.
4. W **Tagi** zaznacz istniejące tagi albo wpisz nowe (na przykład
   „ekipa od żywopłotu”), oddzielone przecinkami.
5. Kliknij **Zapisz zmiany**.

Tagi możesz też dodać bezpośrednio na stronie członka, na karcie
**Tagi**, przyciskiem **Dodaj tag**.

## 7. Bez zgłoszenia: utwórz członka ręcznie {#7-without-an-application-create-the-member-by-hand}

1. Otwórz **Członkowie** i kliknij **Nowy członek**.
2. Wypełnij **Imię** i **Nazwisko** (wymagane), adres, **Data
   urodzenia**, **IBAN**, **Członek od**, **Adres e-mail** i **Numer
   telefonu**, **Może otrzymywać informacje e-mailem** oraz ewentualne
   **Tagi**.
3. Kliknij **Utwórz członka**.
4. Na stronie członka, w **Przypisane działki**, wybierz działkę w
   **Wybierz działkę…**, zostaw zaznaczone **Użyj jako adresu do
   faktury**, jeśli ten członek ma dostawać faktury za działkę, i
   kliknij **Przypisz**.

Możesz też przypisać ze strony działki: **Obecni dzierżawcy → Wybierz
członka… → Przypisz**, gdzie możesz też podać datę początkową. Aby
później poprawić datę początkową, użyj ikony ołówka obok dzierżawcy na
stronie działki (**Edytuj dzierżawę**, pole **Dzierżawca od**).

Jeśli na działce jest jeszcze dotychczasowy dzierżawca, najpierw
zakończ jego dzierżawę -- zob. [Przekazanie
działki](parcel-handover.md).

## 8. Przywitaj nowego członka {#8-welcome-the-new-member}

Parcella nie ma automatycznego e-maila powitalnego. Pomagają dwie
rzeczy:

**Proces przyjęcia.** Moduł **Procesy** zawiera przykładowy szablon
**Przyjęcie nowego członka** z trzema etapami: **Powitanie**
(**Spotkanie powitalne**, **Przekazano statut i regulamin ogrodu**),
**Dokumenty** (**Podpisana deklaracja członkowska**, **Otrzymano
polecenie zapłaty**) i **Zakończenie** (**Dodano do listy mailingowej**,
**Notatki**).

1. Jednorazowo: otwórz **Procesy → Szablony** i w **Zacznij od
   przykładu** kliknij **Użyj** obok **Przyjęcie nowego członka**.
   Dostosuj etapy i pola według potrzeb. (Tworzenie szablonów wymaga
   pełnego dostępu.)
2. Dla każdego nowego członka: na stronie członka, na karcie
   **Procesy**, kliknij **Rozpocznij proces**, wybierz **Szablon** i
   kliknij **Rozpocznij**.
3. Wypełniaj pola w miarę postępów i klikaj **Gotowe -- następny etap**.
   Pola wymagane trzeba wypełnić, zanim przejdziesz dalej.

**Osobista wiadomość.** Przy włączonym module **Ogłoszenia** zaznacz
nowego członka na liście **Członkowie** i kliknij **Napisz do
zaznaczonych**.

## Powiązane {#related}

- [Kandydaci](../modules/applicants.md)
- [Członkowie](../modules/members.md)
- [Działki](../modules/parcels.md)
- [Procesy](../modules/processes.md)
- [Ogłoszenia](../modules/announcements.md)
- [Przekazanie działki](parcel-handover.md)
- Słownik: [kandydat](../glossary.md#applicant),
  [dzierżawa](../glossary.md#tenancy),
  [adres do faktury](../glossary.md#invoice-address)
