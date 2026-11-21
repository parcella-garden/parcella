# Uživatelé a pozvánky {#users-and-invitations}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Zde rozhodujete, kdo se může do Parcelly přihlásit. Noví lidé jsou
zváni e-mailem a heslo si nastaví sami; vy vybíráte, do kterých skupin
patří.

!!! info "Kdo to může používat"
    Jen administrátoři. Otevřete **Administrace → Uživatelé**.

*Uživatel* je přihlašovací účet -- člen výboru, pokladník, člověk, který
odečítá měřidla. Není to totéž co *člen* spolku: většina zahrádkářů jsou
členové, ale uživatelský účet nikdy nedostanou.

## Správa uživatelů {#user-management}

![Správa uživatelů](../assets/screenshots/administration/users.png)

Na stránce je vlevo formulář pozvánky a vpravo seznam účtů. Zprávy o
tom, co jste právě udělali, se zobrazují nahoře.

### Pozvat uživatele {#invite-user}

| Pole / tlačítko | Co dělá |
|---|---|
| **E-mailová adresa** | E-mailová adresa nové osoby. Stane se jejím přihlašovacím jménem. |
| **Skupiny** | Zaškrtněte skupiny, do kterých má osoba patřit. Přístup získá jen z těchto skupin -- viz [Skupiny](groups.md). Pokud zatím žádné skupiny neexistují, uvidíte **Zatím žádné skupiny.** s odkazem **Vytvořit jednu**. |
| **Odeslat pozvánku** | Odešle e-mail s osobním odkazem. Odkaz platí **7 dní**. |

Co se stane:

- Osoba dostane e-mail **Pozvánka do Parcella** s tlačítkem **Přijmout
  pozvánku**. Jméno a heslo si zvolí sama (viz
  [První přihlášení](../getting-started/first-login.md#getting-an-account-the-invitation))
  a je zařazena do zaškrtnutých skupin.
- Pokud adresa už patří nějakému účtu, uvidíte **E-mail je již
  zaregistrován**.
- Pokud pro adresu už existuje čekající pozvánka, stará přestane
  fungovat a platí jen nová.
- Pokud nezaškrtnete žádnou skupinu, osoba si po přijetí může jen
  prohlížet členy a parcely. Skupiny můžete přidat později.

!!! warning "E-mail musí fungovat"
    Pozvánky potřebují funkční poštovní server (viz
    [Nastavení spolku](settings.md#email-smtp)). Pokud poštovní server
    e-mail odmítne, stránka to oznámí místo **Pozvánka odeslána**:
    pozvánka je uložena, ale e-mail se nepodařilo odeslat;
    zkontrolujte nastavení e-mailu a protokol e-mailů a pak pozvánku
    odešlete znovu. Pozvánka zůstane v **Čekající pozvánky**; jakmile
    nastavení pošty funguje, použijte **Znovu odeslat pozvánku**.
    [Protokol e-mailů](email-log.md) ukáže důvod uvedený poštovním
    serverem.

### Čekající pozvánky {#pending-invitations}

Zobrazují se pod formulářem, dokud pozvánky čekají na přijetí. Každý
řádek ukazuje adresu, zaškrtnuté skupiny (nebo **Nejsou vybrány žádné
skupiny**), **Platné do** s datem a odznak **čekající**.

| Tlačítko | Co dělá |
|---|---|
| **Znovu odeslat pozvánku** (kruhové šipky) | Odešle e-mail znovu a prodlouží platnost odkazu o dalších 7 dní ode dneška. Odkaz z prvního e-mailu dál funguje. Uvidíte **Pozvánka znovu odeslána**. |
| **Smazat pozvánku** (koš) | Po potvrzení se pozvánka odstraní a její odkaz přestane fungovat. |

Přijaté pozvánky ze seznamu zmizí; osoba se pak objeví v
**Registrovaní uživatelé**.

### Registrovaní uživatelé {#registered-users}

| Sloupec / tlačítko | Co ukazuje nebo dělá |
|---|---|
| **Jméno** | Avatar a jméno. |
| **E-mail** | Přihlašovací adresa. |
| **Skupiny** | Skupiny, do kterých účet patří. Starší účty bez skupin ukazují svou roli, **Správce** nebo **Výbor**; jinak **–**. |
| **Stav** | **aktivní** nebo **neaktivní**. |
| **Upravit** (tužka) | Otevře [Upravit uživatele](#edit-user). |
| **Deaktivovat** / **Aktivovat** (přepínač) | Jedním kliknutím účet vypne nebo znovu zapne. Nezobrazuje se u vašeho vlastního účtu, který je místo toho označen **Já**. |

**Deaktivace** účtu osobu okamžitě zablokuje -- i na každém počítači,
kde je právě přihlášena. Vše, co vytvořila nebo schválila, zůstává, s
jejím jménem. Když účet znovu aktivujete, může se přihlásit svým starým
heslem.

Nemůžete deaktivovat sami sebe a nemůžete deaktivovat poslední účet,
který může otevřít administraci.

## Upravit uživatele {#edit-user}

![Upravit uživatele](../assets/screenshots/administration/user-edit.png)

**Zrušit** nahoře vrátí do seznamu bez uložení.

### Avatar {#avatar}

Stejně jako na vlastním profilu uživatele: vyberte soubor PNG, JPEG nebo
WebP o velikosti nejvýše 2 MB a klikněte na **Nahrát**, nebo ho smažte
tlačítkem **Odebrat avatar**. Hodí se pro lidi, kteří si obrázek sami
nenahrají.

### Upravit uživatele {#edit-user_1}

| Pole / tlačítko | Co dělá |
|---|---|
| **Jméno** | Povinné. |
| **E-mailová adresa** | Povinné; je to přihlašovací jméno, takže osobě dejte vědět, když ho změníte. Nesmí patřit jinému účtu (**E-mail je již zaregistrován**). |
| **Role** | Zobrazuje se jen u starších účtů, které ještě mají roli **Správce** nebo **Výbor**, s poznámkou *Přístup tohoto účtu vychází z jeho role, nikoli z členství ve skupině.* Zde ji nelze upravit. |
| **Uložit změny** | Uloží jméno a e-mail. V seznamu uvidíte **Uživatel aktualizován**. |

### Odebrat starou roli {#remove-legacy-role}

Jen pro účty s rolí **Správce** nebo **Výbor**. **Odebrat starou roli**
roli odebere; od té doby získává účet přístup jen ze svých skupin, jako
každý novější účet.

!!! warning "Nejprve přidejte skupiny"
    Bez skupiny účet v okamžiku kliknutí klesne na základní přístup
    (čtení členů a parcel). U bývalého **Správce** nejprve přidejte účet
    do skupiny s oprávněním **Přístup k administračnímu panelu**; u
    **Výboru** do skupiny s **Plný přístup ke každému modulu**. Parcella
    odmítne odebrat roli poslednímu administrátorovi.

### Skupiny {#groups}

Uvádí všechny skupiny. **Přidat** zařadí účet do dané skupiny,
**Odebrat** ho z ní vyřadí. Změna platí okamžitě -- není třeba klikat na
**Uložit změny**.

### Nebezpečná zóna {#danger-zone}

Nezobrazuje se, když upravujete svůj vlastní účet.

| Tlačítko | Co dělá |
|---|---|
| **Deaktivovat** / **Aktivovat** | Jako v seznamu: osobu okamžitě zablokuje, nic se nesmaže. |
| <a id="reset-password"></a>**Obnovit heslo** | Pro někoho, kdo zapomněl heslo. Po potvrzení Parcella vytvoří **dočasné heslo** a ukáže ho **jednou**, s tlačítkem **Kopírovat**. Předejte ho osobě (telefonicky, osobně). Její staré heslo přestane fungovat, je všude odhlášena a při příštím přihlášení si musí zvolit nové heslo. Pokud je účet deaktivovaný, budete upozorněni, abyste ho aktivovali. |
| **Trvale smazat** | Po potvrzení účet úplně odstraní. Je to možné jen u účtů, které nikde nezanechaly žádnou stopu -- typicky u účtu vytvořeného omylem a nikdy nepoužitého. |

Pro vlastní heslo použijte místo toho **Změnit heslo** v postranním
panelu.

Jakmile osoba v Parcelle cokoli udělala -- vytvořila záznam, schválila
žádost, zadala odečet měřidla --, účet už nelze smazat a uvidíte *Tento
uživatel má historii aktivit a nelze jej trvale smazat -- místo toho
jej deaktivujte*. Záznamy spolku tak zůstávají úplné: i po letech je
vidět, kdo co udělal.

## Související {#related}

- [Skupiny](groups.md)
- [Role, skupiny a oprávnění](../getting-started/roles-and-permissions.md)
- [První přihlášení a váš účet](../getting-started/first-login.md)
- [API tokeny](api-tokens.md)
