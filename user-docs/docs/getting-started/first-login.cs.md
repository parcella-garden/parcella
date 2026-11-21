# První přihlášení a váš účet {#first-login-and-your-account}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Tato stránka pokrývá vše o vašem vlastním účtu: jak ho získáte, jak se
přihlásíte a jak změníte heslo a obrázek.

!!! info "Kdo to může používat"
    Každý, kdo má účet v Parcelle. Veřejná registrace neexistuje: účet
    vznikne, až když vás pozve administrátor.

## Získání účtu: pozvánka {#getting-an-account-the-invitation}

Administrátor vaší instalace vás pozve e-mailem (viz
[Uživatelé a pozvánky](../administration/users.md)). Dostanete e-mail s
předmětem **Pozvánka do Parcella** a tlačítkem **Přijmout pozvánku**.
Odkaz v něm platí **7 dní**.

!!! tip "Žádný e-mail nepřišel?"
    Nejprve se podívejte do složky se spamem. Pokud tam není, požádejte
    administrátora, aby zkontroloval
    [protokol e-mailů](../administration/email-log.md) a případně
    pozvánku odeslal znovu. Opětovným odesláním získá odkaz dalších
    7 dní; odkaz v prvním e-mailu dál funguje.

### Přijmout pozvánku {#accept-invitation}

<!-- TODO(verify): no screenshot of "Set up your account" -- it needs a valid invitation link, which the screenshot tool can't produce from the sample data. -->

Kliknutím na odkaz se otevře stránka **Nastavte si svůj účet**. Pod
nadpisem vidíte adresu, na kterou byla pozvánka odeslána (**Pozvánka
pro** ...). Tato adresa se stane vaším přihlašovacím jménem; zde ji
nelze změnit.

| Pole / tlačítko | Co dělá |
|---|---|
| **Jméno** | Vaše jméno a příjmení. Ostatní členové výboru ho vidí v seznamech, u úkolů, schválení a v historii změn. |
| **Heslo** | Nejméně 8 znaků. |
| **Potvrdit heslo** | Zadejte stejné heslo znovu. Pokud se neshodují, uvidíte **Hesla se neshodují.** |
| **Vytvořit účet** | Vytvoří váš účet a hned vás přihlásí. Ocitnete se na [Dashboardu](dashboard.md). |

Co pak uvidíte, závisí na skupinách, které administrátor při pozvání
vybral. Pokud nevybral žádnou, můžete si jen prohlížet členy a parcely
-- požádejte ho, aby vás přidal do skupiny. Viz
[Role, skupiny a oprávnění](roles-and-permissions.md).

### Pozvánka vypršela {#invitation-expired}

![Pozvánka vypršela](../assets/screenshots/getting-started/invitation-expired.png)

Zprávu **Pozvánka vypršela** -- *Tento odkaz na pozvánku již není
platný nebo byl již použit.* -- uvidíte, když:

- od odeslání (nebo posledního opětovného odeslání) pozvánky uplynulo
  více než 7 dní,
- jste si už tímto odkazem účet vytvořili, nebo
- administrátor pozvánku smazal nebo stejnou adresu pozval znovu
  (funguje jen nejnovější pozvánka).

Požádejte administrátora, aby vás pozval znovu. **Zpět na přihlášení**
vás vezme na přihlašovací stránku, což pomůže, jen pokud už účet máte.

## Přihlášení {#signing-in}

![Přihlašovací stránka](../assets/screenshots/getting-started/login.png)

Otevřete adresu Parcelly vašeho spolku ve webovém prohlížeči.
Přihlašovací stránka ukazuje logo a název vašeho spolku (obojí nastavuje
administrátor v [Nastavení spolku](../administration/settings.md)).

| Pole / tlačítko | Co dělá |
|---|---|
| **E-mail** | Adresa, na kterou přišla vaše pozvánka. Na velkých a malých písmenech nezáleží. |
| **Heslo** | Vaše heslo. |
| **Přihlásit** | Přihlásí vás a otevře [Dashboard](dashboard.md). |

Zprávy, které můžete vidět:

| Zpráva | Význam |
|---|---|
| **E-mail nebo heslo je nesprávné.** | Jedno z obou je špatně. Pro vaši ochranu Parcella neříká které. |
| **Váš účet byl deaktivován.** | Administrátor váš účet vypnul. Vaše data tam stále jsou; požádejte ho, aby ho znovu aktivoval. |
| **Příliš mnoho neúspěšných pokusů o přihlášení. Počkejte několik minut a zkuste to znovu.** | Po opakovaně špatném hesle Parcella pozastaví pokusy o přihlášení k tomuto účtu asi na 15 minut. |

Přihlášeni zůstanete **8 hodin** (pokud to ten, kdo vaši instalaci
provozuje, nezměnil). Potom vás Parcella požádá o nové přihlášení, i
když jste celou dobu pracovali.

Odhlásíte se kliknutím na **Odhlásit** dole v postranním panelu. Dělejte
to na každém sdíleném nebo veřejném počítači.

!!! note "Zapomněli jste heslo?"
    Odkaz „zapomenuté heslo“ záměrně neexistuje. Požádejte
    administrátora: může vaše heslo resetovat a dát vám dočasné (viz
    [Uživatelé a pozvánky](../administration/users.md#reset-password)).
    Při příštím přihlášení si pak musíte zvolit nové heslo.

## Úplně první přihlášení po instalaci {#the-very-first-login-after-installation}

Když se Parcella spustí poprvé, sama vytvoří jeden účet administrátora:

- **E-mail:** `admin@parcella.local`
- **Heslo:** `admin1234`

Tyto údaje jsou zveřejněny v návodu k instalaci Parcelly a jsou stejné v
každé nové instalaci, takže by je mohl použít kdokoli. Proto je tento
účet uzamčen, dokud se jeho heslo nezmění: po přihlášení se ocitnete
přímo na stránce **Změnit heslo** s upozorněním

> Tento účet stále používá výchozí heslo z prvotního nastavení. Zvolte
> prosím nové -- do té doby zůstává zbytek aplikace uzamčen.

Každá jiná stránka vás pošle zpět sem, dokud neuložíte nové heslo.

!!! warning "Udělejte to ze všeho nejdřív"
    Heslo změňte okamžitě, i na testovací instalaci dostupné z
    internetu. Potom v [Uživatelé a pozvánky](../administration/users.md)
    změňte jméno a e-mailovou adresu účtu na skutečnou osobu, nebo
    pozvěte skutečné administrátory a pracujte s jejich vlastními účty.

Stejná vynucená změna nastane i poté, co administrátor resetoval vaše
heslo: dočasné heslo vás dostane jen na stránku **Změnit heslo**.

## Změnit heslo {#change-password}

![Změnit heslo](../assets/screenshots/getting-started/change-password.png)

Otevřete ji tlačítkem **Změnit heslo** dole v postranním panelu. Stránka
je váš osobní profil: obsahuje také váš avatar a odkaz na vaše API
tokeny.

### Avatar {#avatar}

Avatar je malý kulatý obrázek zobrazený vedle vašeho jména v postranním
panelu, v seznamech uživatelů a u úkolů. Bez něj ukazuje Parcella
jednoduchou ikonu osoby.

| Pole / tlačítko | Co dělá |
|---|---|
| Pole souboru | Vyberte obrázek: PNG, JPEG nebo WebP, nejvýše 2 MB. |
| **Nahrát** | Uloží obrázek. Uvidíte **Avatar byl úspěšně nahrán.** Špatný typ souboru nebo příliš velký soubor se odmítne se zprávou. |
| **Odebrat avatar** | Zobrazí se, jen když nějaký máte. Opět ho odstraní. |

### API tokeny pro integrace {#api-tokens-for-integrations}

**Spravovat** otevře **Moje API tokeny**. Potřebujete to, jen pokud
chcete k Parcelle připojit jiný program (například asistenta AI). Viz
[API tokeny](../administration/api-tokens.md).

### Změna hesla {#changing-the-password}

| Pole / tlačítko | Co dělá |
|---|---|
| **Aktuální heslo** | Vaše současné heslo, aby ho nikdo nemohl změnit na počítači, na kterém jste zůstali přihlášeni. |
| **Nové heslo** | Nejméně 8 znaků a odlišné od současného. |
| **Potvrďte nové heslo** | Nové heslo znovu. |
| **Změnit heslo** | Uloží nové heslo. Uvidíte **Heslo bylo úspěšně změněno.** |

Možné chyby: **Aktuální heslo je nesprávné.**, **Hesla se neshodují.**,
**Heslo musí mít alespoň 8 znaků.** a **Nové heslo se musí lišit od
současného.**

Co se stane, když uložíte:

- V tomto prohlížeči zůstanete přihlášeni.
- **Všude jinde, kde jste byli přihlášeni, budete odhlášeni** -- na
  jiném počítači, v telefonu nebo v prohlížeči, kde s vaším účtem
  pracuje někdo jiný. Použijte to, pokud máte podezření, že někdo zná
  vaše heslo.
- Všechny vaše **API tokeny přestanou fungovat** (zobrazují se jako
  **ukončen**). Pokud je ještě potřebujete, vytvořte nové.

## Jazyk {#language}

Parcella ukazuje všem ve vašem spolku stejný jazyk. Přepínač jazyka pro
jednotlivé uživatele neexistuje. Jazyk volí administrátor v
[Nastavení spolku](../administration/settings.md#language) --
English, Deutsch, Polski, Čeština, Slovenčina, Français nebo
Nederlands. Tento jazyk používá i přihlašovací stránka a stránky
pozvánek.

Formáty čísel, dat a měny jsou samostatné nastavení (**Region** a
**Měna**), takže spolek může například používat anglická menu s
německými formáty čísel.

## Související {#related}

- [Orientace v aplikaci](navigation.md)
- [Role, skupiny a oprávnění](roles-and-permissions.md)
- [Uživatelé a pozvánky](../administration/users.md) -- pro administrátory
