# Finanse {#finances}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Moduł Finanse to miejsce pracy skarbnika. Tworzy roczne faktury
stowarzyszenia dla każdej działki i każdego członka, śledzi, kto
zapłacił, wysyła upomnienia i zapisuje rachunki, które stowarzyszenie
samo otrzymuje. Prowadzi też prostą książkę kasową dla każdego rachunku
bankowego. Na tej podstawie tworzy zestawienie kasowe dla urzędu
skarbowego i plan budżetu na następny rok.

!!! info "Kto może z tego korzystać"
    - Moduł jest **domyślnie wyłączony**. Administrator włącza go w
      **Ustawienia stowarzyszenia** (przełącznik nazywa się **Finanse**),
      zob. [Włączanie i wyłączanie modułów](../../administration/modules.md).
      Zanim wyślesz pierwsze faktury, wypełnij **Ustawienia finansowe**
      (dane bankowe, format numeru faktury) w
      [Ustawieniach stowarzyszenia](../../administration/settings.md) --
      są drukowane w stopce każdej faktury.
    - Członkowie zarządu i administratorzy (oraz każdy w grupie z pełnym
      dostępem) mogą wszystko.
    - Wszyscy pozostali potrzebują [grupy](../../administration/groups.md),
      która nadaje uprawnienia do **Finanse**:
        - **odczyt** -- widzi każdy ekran, otwiera pliki PDF, eksportuje
          pliki CSV;
        - **zapis** -- tworzy i zmienia serie faktur, pozycje, płatności,
          upomnienia, konta, księgowania, faktury przychodzące, kategorie
          i budżet;
        - **usuwanie** -- usuwa te rzeczy z powrotem.
    - Kilka działań związanych z załącznikami faktur przychodzących w
      chmurze jest tylko dla członków zarządu i administratorów, zob.
      [Faktury przychodzące](incoming-invoices.md).

    Zob. [Role, grupy i uprawnienia](../../getting-started/roles-and-permissions.md).

## Gdzie to znaleźć {#where-to-find-it}

Gdy moduł jest włączony i możesz go czytać, pasek boczny pokazuje grupę
**Finanse** z czterema pozycjami:

| Pozycja menu | Otwiera |
|---|---|
| **Przegląd** | Panel finansów opisany niżej. |
| **Faktury wychodzące** | Listę serii faktur, zob. [Serie faktur](invoice-runs.md). |
| **Upomnienia** | Listę zaległych faktur, zob. [Faktury, płatności i upomnienia](invoices.md#reminders). |
| **Faktury przychodzące** | Rachunki otrzymane przez stowarzyszenie, zob. [Faktury przychodzące](incoming-invoices.md). |

Wszystko inne (konta, kategorie, katalog pozycji, księgowania,
zestawienie, budżet) otwiera się z kart panelu.

## Panel finansów {#finances-dashboard}

![Panel finansów](../../assets/screenshots/finances/dashboard.png)

Strona startowa modułu. Trzy liczby na górze pokazują od razu stan
faktur wychodzących. Pod nimi po jednej karcie na każdy obszar modułu
prowadzi dalej.

| Liczba | Co pokazuje |
|---|---|
| **Otwarte faktury** | Ile faktur wychodzących nie jest jeszcze w pełni zapłaconych. Częściowo zapłacone faktury liczą się tu jako otwarte. |
| **Kwota do zapłaty** | Suma wciąż niezapłacona z tych faktur (kwota faktury minus zapisane płatności). Opłaty za upomnienia nie są wliczone. |
| **Zaległe** | Ile otwartych faktur przekroczyło termin płatności swojej serii faktur. Na czerwono, gdy jest więcej niż zero. |

| Karta | Podpowiedź pod tytułem | Otwiera |
|---|---|---|
| **Faktury wychodzące** | *n* seria(e) faktur | [Serie faktur](invoice-runs.md) |
| **Kategorie** | zdefiniowano *n* kategorii | [Kategorie księgowe](bookkeeping.md#bookkeeping-categories) |
| **Katalog pozycji** | zdefiniowano *n* szablonów pozycji | [Katalog pozycji](invoice-runs.md#item-catalog) |
| **Konta** | *n* konto(a) zdefiniowane | [Konta](bank-accounts.md#accounts) |
| **Upomnienia** | Zaległych faktur: *n* | [Upomnienia](invoices.md#reminders) |
| **Faktury przychodzące** | zarejestrowano *n* faktur przychodzących | [Faktury przychodzące](incoming-invoices.md) |
| **Wszystkie księgowania** | Wszystkie płatności z faktur przychodzących i wychodzących | [Wszystkie księgowania](bookkeeping.md#all-bookings) |
| **Zestawienie księgowe** | Zestawienie kasowe dla urzędu skarbowego | [Zestawienie księgowe](bookkeeping.md#accounting-statement) |
| **Plan budżetu** | Planowane przychody i wydatki według kategorii na nadchodzący rok, obok wykonania z lat ubiegłych | [Plan budżetu](bookkeeping.md#budget-plan) |

Większość podstron ma na górnym pasku przycisk **Powrót do Finansów**,
który prowadzi tutaj.

<!-- TODO(verify): finances/coming_soon.html ("This feature is coming soon.") exists, but no route renders it any more, so it is not documented as a screen. -->

## Jak pieniądze płyną przez rok {#how-the-money-flows-through-a-year}

Typowy rok stowarzyszenia w Parcelli wygląda tak:

1. **Jednorazowa konfiguracja.** Utwórz
   [kategorie księgowe](bookkeeping.md#bookkeeping-categories) (albo
   zaimportuj swój plan kont), [rachunki bankowe i kasy](bank-accounts.md#accounts)
   oraz powtarzające się pozycje faktur w
   [katalogu pozycji](invoice-runs.md#item-catalog) (dzierżawa za m²,
   składka członkowska, woda, prąd, ubezpieczenie ...).
2. **Przygotuj roczne faktury.** Utwórz [serię faktur](invoice-runs.md)
   na dany rok, dodaj pozycje z katalogu, dostosuj ceny i sprawdź
   [podgląd](invoice-runs.md#preview-invoices). Odczyty liczników,
   ubezpieczenia i prace społeczne za ten rok powinny być w tym momencie
   kompletne -- pozycje zależne od zużycia odczytują je na bieżąco.
3. **Sfinalizuj i wyślij.** Finalizacja nadaje stałe numery faktur.
   Potem wyślij faktury e-mailem, prześlij je do folderów działek w
   chmurze i pobierz pakiet do druku dla wszystkich, którzy dostają
   papier.
4. **Zapisuj płatności.** Wpisuj płatności ręcznie na liście faktur
   serii albo zaimportuj wyciąg bankowy na
   [stronie księgowań konta](bank-accounts.md#bookings-of-an-account)
   i przypisz każdy wiersz do faktury, którą opłaca.
5. **Upominaj spóźnialskich.** Strona [Upomnienia](invoices.md#reminders)
   pokazuje każdą zaległą fakturę; wysyłaj pierwsze, drugie, trzecie
   upomnienie z faktury, z opłatą lub bez.
6. **Zapisuj rachunki stowarzyszenia** jako
   [faktury przychodzące](incoming-invoices.md) i oznaczaj je jako
   zapłacone, gdy pieniądze wychodzą.
7. **Zamknij rok.** [Zestawienie księgowe](bookkeeping.md#accounting-statement)
   pokazuje przychody i wydatki według kategorii, liczone w dniu, w
   którym pieniądze rzeczywiście się przemieściły. Użyj go dla urzędu
   skarbowego i na walne zebranie, a następny rok zaplanuj w
   [planie budżetu](bookkeeping.md#budget-plan).

Instrukcja [Roczne fakturowanie](../../guides/annual-invoicing.md)
przeprowadza po kolei przez kroki 2 do 5.

## Rozdziały {#chapters}

- [Serie faktur](invoice-runs.md) -- roczna partia faktur, jej pozycje
  i sposób obliczania każdej kwoty, katalog pozycji, podgląd i
  finalizacja.
- [Faktury, płatności i upomnienia](invoices.md) -- wszystkie faktury
  ze wszystkich serii, doręczanie, płatności i proces upominania.
- [Rachunki bankowe i księgowania](bank-accounts.md) -- Twoje konta,
  ich księgowania i import wyciągu bankowego z dopasowaniem do faktur.
- [Faktury przychodzące](incoming-invoices.md) -- rachunki otrzymane
  przez stowarzyszenie i ich płatności.
- [Kategorie, budżet i zestawienie](bookkeeping.md) -- kategorie
  księgowe, lista wszystkich księgowań stowarzyszenia, zestawienie
  księgowe i plan budżetu.
