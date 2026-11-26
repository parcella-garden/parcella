# Používatelia a pozvánky {#users-and-invitations}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Tu rozhodujete, kto sa môže prihlásiť do Parcelly. Noví ľudia sú
pozvaní e-mailom a heslo si nastavia sami; vy vyberáte, do ktorých
skupín patria.

!!! info "Kto to môže používať"
    Len administrátori. Otvorte **Administrácia → Používatelia**.

*Používateľ* je prihlasovací účet -- člen výboru, pokladník, osoba,
ktorá odčítava meradlá. Nie je to to isté ako *člen* spolku: väčšina
záhradkárov sú členovia, ale používateľský účet nikdy nedostanú.

## Správa používateľov {#user-management}

![Správa používateľov](../assets/screenshots/administration/users.png)

Stránka má vľavo formulár na pozvanie a vpravo zoznam účtov. Hlásenia o
tom, čo ste práve urobili, sa zobrazujú hore.

### Pozvať používateľa {#invite-user}

| Pole / tlačidlo | Čo robí |
|---|---|
| **E-mailová adresa** | E-mailová adresa novej osoby. Stane sa jej prihlasovacím menom. |
| **Skupiny** | Zaškrtnite skupiny, do ktorých má osoba patriť. Jej prístup pochádza len z týchto skupín -- pozri [Skupiny](groups.md). Ak ešte žiadne skupiny neexistujú, uvidíte **Zatiaľ žiadne skupiny.** s odkazom **Vytvoriť jednu**. |
| **Odoslať pozvánku** | Pošle e-mail s osobným odkazom. Odkaz platí **7 dní**. |

Čo sa stane:

- Osoba dostane e-mail **Pozvánka do Parcella** s tlačidlom **Prijať
  pozvánku**. Meno a heslo si zvolí sama (pozri
  [Prvé prihlásenie](../getting-started/first-login.md#getting-an-account-the-invitation))
  a zaradí sa do zaškrtnutých skupín.
- Ak adresa už patrí k účtu, uvidíte **E-mail je už zaregistrovaný**.
- Ak pre adresu už existuje čakajúca pozvánka, stará prestane fungovať
  a platí len nová.
- Ak nezaškrtnete žiadnu skupinu, osoba si po prijatí môže len
  prezerať členov a parcely. Skupiny môžete pridať neskôr.

!!! warning "E-mail musí fungovať"
    Pozvánky potrebujú funkčný poštový server (pozri
    [Nastavenia spolku](settings.md#email-smtp)). Ak poštový server
    e-mail odmietne, stránka namiesto **Pozvánka odoslaná** povie:
    „Pozvánka pre … je uložená, ale e-mail sa nepodarilo odoslať.
    Skontrolujte nastavenia e-mailu a Protokol e-mailov a potom pozvánku
    odošlite znova.“ Pozvánka zostáva v **Čakajúce pozvánky**; keď
    nastavenia pošty fungujú, použite **Znovu odoslať pozvánku**.
    [Protokol e-mailov](email-log.md) ukáže dôvod poštového servera.

### Čakajúce pozvánky {#pending-invitations}

Zobrazujú sa pod formulárom, kým pozvánky čakajú na prijatie. Každý
riadok ukazuje adresu, zaškrtnuté skupiny (alebo **Nie sú vybrané
žiadne skupiny**), **Platné do** s dátumom a odznak **čaká**.

| Tlačidlo | Čo robí |
|---|---|
| **Znovu odoslať pozvánku** (kruhové šípky) | Pošle e-mail znova a dá odkazu ďalších 7 dní odo dneška. Odkaz z prvého e-mailu naďalej funguje. Uvidíte **Pozvánka znovu odoslaná**. |
| **Vymazať pozvánku** (kôš) | Po potvrdení sa pozvánka odstráni a jej odkaz prestane fungovať. |

Prijaté pozvánky zo zoznamu zmiznú; osoba sa potom objaví v
**Registrovaní používatelia**.

### Registrovaní používatelia {#registered-users}

| Stĺpec / tlačidlo | Čo ukazuje alebo robí |
|---|---|
| **Meno** | Avatar a meno. |
| **E-mail** | Prihlasovacia adresa. |
| **Skupiny** | Skupiny, do ktorých účet patrí. Staršie účty bez skupín ukazujú svoju rolu, **Administrátor** alebo **Výbor**; inak **–**. |
| **Stav** | **aktívny** alebo **neaktívny**. |
| **Upraviť** (ceruzka) | Otvorí [Upraviť používateľa](#edit-user). |
| **Deaktivovať** / **Aktivovať** (prepínač) | Jedným kliknutím účet vypne alebo znova zapne. Nezobrazuje sa pri vašom vlastnom účte, ktorý je namiesto toho označený **Ja**. |

**Deaktivácia** účtu osobu okamžite zablokuje -- aj na každom počítači,
na ktorom je práve prihlásená. Všetko, čo vytvorila alebo schválila,
zostáva, s jej menom. Aktivujte účet znova a môže sa prihlásiť svojím
starým heslom.

Nemôžete deaktivovať sami seba a nemôžete deaktivovať posledný účet,
ktorý môže otvoriť administráciu.

## Upraviť používateľa {#edit-user}

![Upraviť používateľa](../assets/screenshots/administration/user-edit.png)

**Zrušiť** hore vás vráti do zoznamu bez uloženia.

### Avatar {#avatar}

Rovnako ako vo vlastnom profile používateľa: vyberte súbor PNG, JPEG
alebo WebP s veľkosťou najviac 2 MB a kliknite na **Nahrať**, alebo ho
zmažte tlačidlom **Odstrániť avatar**. Užitočné pre ľudí, ktorí si
obrázok nenahrajú sami.

### Upraviť používateľa {#edit-user_1}

| Pole / tlačidlo | Čo robí |
|---|---|
| **Meno** | Povinné. |
| **E-mailová adresa** | Povinná; je to prihlasovacie meno, preto osobe povedzte, keď ju zmeníte. Nesmie patriť inému účtu (**E-mail je už zaregistrovaný**). |
| **Rola** | Zobrazí sa len pri starších účtoch, ktoré ešte majú rolu **Administrátor** alebo **Výbor**, s poznámkou *Prístup tohto účtu vychádza z jeho role, nie z členstva v skupine.* Tu sa nedá upraviť. |
| **Uložiť zmeny** | Uloží meno a e-mail. V zozname uvidíte **Používateľ aktualizovaný**. |

### Odstrániť starú rolu {#remove-legacy-role}

Len pre účty s rolou **Administrátor** alebo **Výbor**. **Odstrániť
starú rolu** rolu odoberie; odvtedy prístup účtu pochádza len z jeho
skupín, ako pri každom novšom účte.

!!! warning "Najprv pridajte skupiny"
    Bez skupiny účet v momente kliknutia klesne na základný prístup
    (čítanie členov a parciel). Bývalého **Administrátora** najprv
    pridajte do skupiny s **Prístup k administračnému panelu**; účet
    **Výbor** do skupiny s **Plný prístup ku každému modulu**. Parcella
    odmietne odobrať rolu poslednému administrátorovi.

### Skupiny {#groups}

Uvádza každú skupinu. **Pridať** zaradí účet do skupiny, **Odstrániť**
ho z nej vyradí. Zmena platí okamžite -- netreba klikať na **Uložiť
zmeny**.

### Nebezpečná zóna {#danger-zone}

Nezobrazuje sa, keď upravujete vlastný účet.

| Tlačidlo | Čo robí |
|---|---|
| **Deaktivovať** / **Aktivovať** | Ako v zozname: okamžite osobu zablokuje, nič sa nezmaže. |
| <a id="reset-password"></a>**Obnoviť heslo** | Pre niekoho, kto zabudol heslo. Po potvrdení Parcella vytvorí **dočasné heslo** a ukáže ho **raz**, s tlačidlom **Kopírovať**. Odovzdajte ho osobe (telefonicky, osobne). Jej staré heslo prestane fungovať, všade bude odhlásená a pri ďalšom prihlásení si musí zvoliť nové heslo. Ak je účet deaktivovaný, dostanete pripomienku, aby ste ho aktivovali. |
| **Trvale vymazať** | Po potvrdení úplne odstráni účet. Možné len pri účtoch, ktoré nikde nezanechali stopu -- zvyčajne účet vytvorený omylom a nikdy nepoužitý. |

Na vlastné heslo použite namiesto toho **Zmeniť heslo** v bočnom
paneli.

Keď osoba v Parcelle čokoľvek urobila -- vytvorila záznam, schválila
žiadosť, zadala odpočet meradla --, účet sa už nedá zmazať a uvidíte
*Tento používateľ má niekde v systéme históriu aktivít ... Namiesto toho
ho deaktivujte.* Záznamy spolku tak zostanú úplné: aj po rokoch
uvidíte, kto čo urobil.

## Súvisiace {#related}

- [Skupiny](groups.md)
- [Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md)
- [Prvé prihlásenie a váš účet](../getting-started/first-login.md)
- [API tokeny](api-tokens.md)
