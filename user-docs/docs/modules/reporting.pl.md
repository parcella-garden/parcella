# Raporty {#reporting}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Najważniejsze dane Twojego stowarzyszenia w czasie, jako wykresy: ile
lat mają członkowie, jak zmieniała się liczba członków, ile działek
oddano, ile osób się zgłasza i jak szły prace społeczne. Przydatne do
sprawozdania rocznego lub na walne zebranie.

!!! info "Kto może z tego korzystać"
    - Przełącznik modułu to **Raporty** w **Administracja → Włączanie i
      wyłączanie modułów**. Domyślnie jest **włączony**.
    - Role **Zarząd** i **Administrator** oraz członkowie grupy z
      **Pełny dostęp do każdego modułu** zawsze go widzą.
    - Wszyscy pozostali potrzebują *odczytu* dla **Raporty** w jednej ze
      swoich [grup](../administration/groups.md). Strona pokazuje tylko
      sumy i liczby, nigdy nazwisk, więc nie wymaga też dostępu do
      członków, prac społecznych ani kandydatów.

## Strona raportów {#reporting-page}

![Raporty](../assets/screenshots/reporting/index.png)

Otwórz **Raporty** w menu. Strona jest tylko do odczytu. Każda liczba
jest obliczana z bieżących danych przy każdym otwarciu strony; nic nie
jest zapisywane ani nie wymaga aktualizacji. Szeregi czasowe pokazują do
10 ostatnich lat, od pierwszego roku z danymi do bieżącego roku. Miniony
rok jest liczony według stanu na 31 grudnia, bieżący według stanu na
dziś.

Każdy wykres to karta z:

- samym wykresem (najedź na niego, aby zobaczyć dokładne liczby);
- szarą notką z ikoną informacji tam, gdzie coś wymaga wyjaśnienia, np.
  ilu członków pominięto;
- **Pokaż dane jako tabelę**, co rozwija te same liczby jako tabelę,
  gotową do skopiowania. Wykresy kołowe dodają kolumnę **Udział / suma**
  z procentami, wykresy skumulowane kolumnę z sumą na rok.

Wykres bez danych mówi **Brak danych.**

Niektóre wykresy pojawiają się tylko przy włączonym module: wykresy
kandydatów wymagają **Kandydaci**, wykresy prac społecznych
**Zarządzanie pracami społecznymi**, a wykres prądu **Zarządzanie
prądem**.

## Wykresy {#the-charts}

| Wykres | Co liczy |
|---|---|
| **Członkowie według pokolenia** | Wykres kołowy dzisiejszych aktywnych członków według roku urodzenia: **Ciche pokolenie (do 1945)**, **Baby boomers (1946–1964)**, **Pokolenie X (1965–1980)**, **Millenialsi (1981–1996)**, **Pokolenie Z (1997–2012)**, **Pokolenie Alfa (od 2013)**. Członkowie bez daty urodzenia są pomijani; notka mówi ilu. |
| **Członkowie w poszczególnych latach** | Wykres liniowy liczby **Członkowie** w każdym roku: wszyscy, których data „członek od” przypada na koniec tego roku lub wcześniej i którzy do tego czasu nie odeszli. Członkowie bez daty wstąpienia są liczeni w każdym roku; notka mówi ilu. |
| **Wypowiedziane działki w poszczególnych latach** | Wykres słupkowy **Zakończone dzierżawy** na rok: każda dzierżawa, której data końcowa przypada w tym roku, łącznie z datami końcowymi ustawionymi już na później w tym roku. Działka przekazana od jednego dzierżawcy do następnego liczy się jako jedna zakończona dzierżawa. |
| **Kandydaci na kwartał** | Wykres słupkowy nowych **Kandydaci** według daty zgłoszenia, dla każdego kwartału zeszłego i bieżącego roku. |
| **Kandydaci na rok** | To samo na rok. |
| **Godziny pracy w poszczególnych latach** | Słupki skumulowane dla każdego roku, który ma konfigurację prac społecznych. Każda działka (lub członek, zob. niżej) jest liczona w dokładnie jednej grupie, sprawdzanej w tej kolejności: **Zwolnieni**, **Płaci opłatę (brak godzin)**, **Wypełnione dzięki patronatowi**, **Wypełnione przez prace**. W latach, w których godziny były należne od członka zamiast od działki, notka mówi „W latach ... liczone na członka zamiast na działkę.”. |
| **Przekazania godzin w poszczególnych latach** | Dwa słupki na rok: liczba **Przekazania** godzin i łączna liczba **Przekazane godziny**. |
| **Działki z prądem** | Wykres kołowy dzisiejszych aktywnych działek **Z przyłączem prądu** (co najmniej jeden licznik prądu na działce) i **Bez przyłącza prądu**. |

!!! note "O czym pamiętać"
    - **Członkowie według pokolenia** i **Działki z prądem** pokazują
      tylko stan dzisiejszy. Parcella nie przechowuje migawek, więc nie
      może powiedzieć, jak wyglądało to we wcześniejszym roku.
    - Członek, który został usunięty (zamiast dostać datę końcową),
      znika także ze wszystkich minionych lat. Kończ członkostwa zamiast
      usuwać członków, a historia pozostanie poprawna.
    - Liczby pochodzą z danych tak, jak zostały wprowadzone. Brakująca
      data wstąpienia lub data urodzenia pojawia się w notkach; popraw ją
      u [członka](members.md) i odśwież stronę.

Wykresy nie mają przycisku eksportu. Użyj **Pokaż dane jako tabelę**,
aby skopiować liczby, np. do arkusza kalkulacyjnego lub sprawozdania
rocznego.

## Powiązane {#related}

- [Członkowie](members.md) -- daty wstąpienia i daty urodzenia.
- [Działki](parcels.md) -- dzierżawy i ich daty końcowe.
- [Kandydaci](applicants.md)
- [Prace społeczne](work-hours.md) -- zwolnienia, patronaty i
  przekazania godzin.
- [Woda i prąd](metering.md) -- liczniki prądu na działkach.
