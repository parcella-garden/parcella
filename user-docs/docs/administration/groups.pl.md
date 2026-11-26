# Grupy {#groups}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Grupy decydują, co każda osoba może widzieć i zmieniać. Tworzysz grupę
dla zadania w stowarzyszeniu -- „Zarząd”, „Skarbnik”, „Zespół wodny” --
zaznaczasz, czego to zadanie potrzebuje, i dodajesz do niej właściwe
osoby.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → Grupy**.

Idee stojące za grupami -- Odczyt, Zapis i Usuwanie, pełny dostęp,
obszar administracji -- wyjaśnia strona
[Role, grupy i uprawnienia](../getting-started/roles-and-permissions.md).
Ta strona opisuje ekran.

![Grupy](../assets/screenshots/administration/groups.png)

## Utwórz grupę {#create-group}

| Pole / przycisk | Do czego służy |
|---|---|
| **Nazwa** | Wymagana i musi być unikalna (**Grupa o tej nazwie już istnieje**). |
| **Opis** | Opcjonalna notka, do czego służy grupa. |
| **Pełny dostęp do każdego modułu** | Członkowie grupy mogą czytać, zmieniać i usuwać wszystko w każdym włączonym module, jak zarząd. |
| **Dostęp do panelu administracyjnego** | Członkowie grupy mogą też otwierać **Administracja**. Zaznaczenie tego obejmuje pełny dostęp, więc pole pełnego dostępu znika. |
| **Utwórz grupę** | Tworzy grupę. Widzisz **Grupa utworzona**. |

Nowa grupa bez zaznaczonego żadnego z tych pól nie nadaje jeszcze
niczego. Otwórz ją niżej, aby zaznaczyć jej uprawnienia.

## Karty grup {#the-group-cards}

Każda grupa pojawia się jako zwinięta karta pod formularzem. Nagłówek
pokazuje jej nazwę oraz oznaczenie **Administracja** lub **Pełny
dostęp**, jeśli grupa nadaje jedno z nich. Kliknij nagłówek, aby
rozwinąć kartę.

Przycisk **kosza** w nagłówku usuwa grupę po potwierdzeniu. Jej
członkowie tracą to, co grupa im dawała. Parcella odmawia usunięcia
ostatniej grupy, która daje komukolwiek dostęp do obszaru administracji,
jeśli żadne inne konto go nie ma.

### Ustawienia i uprawnienia {#settings-and-permissions}

| Pole / przycisk | Do czego służy |
|---|---|
| **Nazwa**, **Opis** | Jak przy tworzeniu. |
| **Pełny dostęp do każdego modułu**, **Dostęp do panelu administracyjnego** | Jak przy tworzeniu. Gdy jedno z nich jest zaznaczone, tabela uprawnień jest ukryta, bo nie jest potrzebna. |
| Tabela uprawnień | Jeden wiersz na **Moduł** z polami **Odczyt**, **Zapis** i **Usuwanie**. Zob. listę modułów niżej. |
| **Zapisz** | Zapisuje nazwę, opis, oba pola i całą tabelę. Widzisz **Grupa zaktualizowana**. |

Moduły w tabeli: **Członkowie i działki**, **Prace społeczne**,
**Woda**, **Prąd**, **Ubezpieczenia**, **Wnioski zakupowe**,
**Kalendarz**, **Inwentarz**, **Finanse**, **Wsparcie (helpdesk)**,
**Kandydaci**, **Kontakty zewnętrzne**, **Raporty**, **Notatki**,
**Procesy**. Moduły wyłączone w Twoim stowarzyszeniu też są na liście;
ich zaznaczenia zaczynają działać po włączeniu modułu.

!!! tip "Odczyt przede wszystkim"
    Zaznacz **Odczyt** wszędzie tam, gdzie zaznaczasz **Zapis** lub
    **Usuwanie**. Bez Odczytu moduł nawet nie pojawi się na pasku
    bocznym tej osoby.

Tablicy zadań i ogłoszeń nie ma w tabeli: są dostępne wyłącznie z
pełnym dostępem.

### Przypisani użytkownicy {#assigned-users}

Pokazuje konta w grupie, z awatarem, imieniem i adresem e-mail.

| Element | Do czego służy |
|---|---|
| **×** obok osoby | Od razu usuwa ją z grupy (**Użytkownik usunięty**). |
| **Dodaj użytkownika...** + **Dodaj** | Wybierz konto i dodaj je (**Użytkownik dodany**). |

Lista **Dodaj użytkownika...** proponuje tylko konta, które dostają
dostęp z grup. Starsze konta z rolą **Administrator** lub **Zarząd**
mają już pełny dostęp i nie są tu proponowane; jeśli chcesz przełączyć
je na grupy, dodaj je ze strony
[Edytuj użytkownika](users.md#edit-user). Gdy wszystkie pasujące konta
są już w grupie, zamiast listy widzisz krótką notkę; gdy nie ma żadnych,
link **Zaproś teraz**.

Zmiany uprawnień działają od następnego kliknięcia tej osoby -- nie
musi logować się ponownie.

## Przykładowa konfiguracja {#example-set-up}

| Grupa | Zaznaczone |
|---|---|
| Administratorzy | **Dostęp do panelu administracyjnego** |
| Zarząd | **Pełny dostęp do każdego modułu** |
| Skarbnik | Finanse: Odczyt, Zapis, Usuwanie. Członkowie i działki: Odczyt, Zapis. Wnioski zakupowe: Odczyt. Ubezpieczenia: Odczyt. |
| Odczytujący liczniki | Woda: Odczyt, Zapis. Prąd: Odczyt, Zapis. |
| Zespół prac społecznych | Prace społeczne: Odczyt, Zapis. Kalendarz: Odczyt. |

Jedna osoba może należeć do kilku grup; jej uprawnienia się sumują.

## Powiązane {#related}

- [Użytkownicy i zaproszenia](users.md)
- [Role, grupy i uprawnienia](../getting-started/roles-and-permissions.md)
- [Włączanie i wyłączanie modułów](modules.md)
