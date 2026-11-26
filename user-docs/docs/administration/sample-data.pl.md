# Dane przykładowe {#sample-data}

!!! note "Tłumaczenie maszynowe"
    Ta strona została przetłumaczona maszynowo z języka angielskiego i nie została jeszcze sprawdzona. Jeśli coś jest niejasne, obowiązuje wersja angielska (język zmienisz u góry).

Dane przykładowe wypełniają nową instalację realistycznymi, zmyślonymi
rekordami w każdym module, dzięki czemu możesz przeklikać Parcellę i
wypróbować różne rzeczy, zanim wprowadzisz prawdziwe stowarzyszenie. Gdy
skończysz, jedno kliknięcie usuwa je z powrotem.

!!! info "Kto może z tego korzystać"
    Tylko administratorzy. Otwórz **Administracja → Dane przykładowe**.

![Dane przykładowe](../assets/screenshots/administration/sample-data.png)

## Co zostanie dodane {#what-this-adds}

Lewa karta pokazuje, co zostanie utworzone:

- **Dane podstawowe:** 6 członków, 5 działek ogrodowych i ich
  przypisania, w tym jedno wspólne gospodarstwo domowe i jeden były
  dzierżawca.
- **Godziny pracy:** konfiguracja roczna, przeszły i nadchodzący termin
  prac z uczestnikami oraz kilka zadań.
- **Liczniki:** licznik wody i prądu z odczytami z dwóch lat.
- **Ubezpieczenie:** konfiguracja roczna, pakiety ubezpieczenia mienia
  i ochrona dla dwóch działek.
- **Wsparcie:** kilka przykładowych rozmów z helpdesku w różnych
  stanach.
- **Wnioski zakupowe:** jeden otwarty, jeden zatwierdzony i jeden
  odrzucony.
- **Kalendarz:** kilka przeszłych i nadchodzących wydarzeń
  stowarzyszenia.
- **Inwentarz:** kategorie, kilka przedmiotów i jeden przedmiot obecnie
  wypożyczony.
- **Tablica zadań:** kilka kart rozłożonych na wszystkie trzy kolumny.
- **Finanse:** kilka przykładowych kategorii księgowych.

Parcella zapamiętuje każdy rekord utworzony w ten sposób. **Usuń
wszystkie dane przykładowe** usuwa dokładnie te rekordy i nic, co
wprowadziłeś sam. Konta użytkowników nigdy nie są tworzone ani
zmieniane.

Dane przykładowe trafiają do modułów nawet wtedy, gdy są wyłączone;
włącz moduł, aby je zobaczyć.

## Dodaj lub usuń {#add-or-remove}

To, co pokazuje prawa karta, zależy od stanu Twojej instalacji:

| Sytuacja | Co widzisz |
|---|---|
| Nowa instalacja, jeszcze bez członków i działek | *Ta instalacja wygląda na nową -- nie ma jeszcze danych o członkach ani działkach.* i przycisk **Dodaj dane przykładowe**. Po potwierdzeniu dane zostają utworzone (**Dodano dane przykładowe.**). |
| Dane przykładowe istnieją | **Obecnie istnieją dane przykładowe:** z liczbą dla każdego obszaru i przycisk **Usuń wszystkie dane przykładowe**. Po potwierdzeniu zostają usunięte (**Usunięto wszystkie dane przykładowe.**). Tego nie można cofnąć. |
| Istnieją już prawdziwi członkowie lub działki | Informacja, że dane przykładowe można dodać tylko do nowej instalacji. Nie ma przycisku. |

!!! warning "Usuń je przed startem na produkcji"
    Nie mieszaj danych przykładowych z prawdziwymi. Usuń je, zanim
    zaczniesz wprowadzać prawdziwych członków i działki stowarzyszenia
    -- gdy istnieją prawdziwe dane, danych przykładowych nie można już
    dodać ponownie, a zmyślone rekordy musiałbyś odróżniać ręcznie.

## Powiązane {#related}

- [Konfiguracja nowego stowarzyszenia](../guides/new-club-setup.md)
- [Włączanie i wyłączanie modułów](modules.md)
