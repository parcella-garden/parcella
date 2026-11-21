# Informace o systému a aktualizace {#system-information-and-updates}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Stránka Systém ukazuje, kterou verzi Parcelly používáte, zda je k
dispozici novější, a je výchozím bodem pro zálohy.

!!! info "Kdo to může používat"
    Jen administrátoři. Otevřete **Administrace → Systém**.

![Systém](../assets/screenshots/administration/system.png)

## Upozornění na aktualizaci {#update-notice}

Parcella se pravidelně ptá GitHubu, kde je zveřejněna, zda vyšla
novější verze. Nic o vašem spolku se přitom neodesílá. Můžete to vypnout
v [Nastavení spolku → Aktualizace](settings.md#updates); upozornění na
aktualizaci pak z této stránky zmizí.

**Když máte aktuální verzi**, vidíte

> Verze v1.2.3 -- aktuální (naposledy zkontrolováno: 18.11.2026 14:05)

nebo hned po instalaci **... aktualizace zatím nebyly zkontrolovány**.

**Když existuje novější verze**, zvýrazněný rámeček ukazuje **Je k
dispozici aktualizace:** s číslem nové verze, verzi, kterou používáte,
a čtyři příkazy, které aktualizaci na serveru nainstalují.

| Tlačítko | Co dělá |
|---|---|
| **Zkontrolovat nyní** | Zeptá se GitHubu hned, místo čekání na další automatickou kontrolu (každých šest hodin). |

!!! note "Aktualizace se provádí na serveru"
    Samotná aktualizace není tlačítko v Parcelle. Příkazy z rámečku
    zadá ten, kdo spravuje server. Pokud to nejste vy, předejte mu je.
    Nejprve si stáhněte [zálohu](backup.md).

    Rámeček také upozorňuje, že první příkaz nahradí konfigurační soubor
    serveru aktuální verzí. Změny, které v tomto souboru udělal správce
    serveru, se ztratí, pokud je nemá v samostatném souboru s
    přepsáními, jak vysvětluje návod k instalaci.

Před aktualizací si na GitHubu přečtěte poznámky k vydání, abyste
věděli, co se změnilo.

## Záloha {#backup}

Karta **Záloha** má tři tlačítka:

| Tlačítko | Co dělá |
|---|---|
| **Zálohy v cloudu** | Otevře plán automatických záloh do vašeho cloudového úložiště. |
| **Obnovit ze zálohy** | Otevře stránku obnovy. |
| **Stáhnout zálohu** | Okamžitě stáhne kompletní zálohu. |

Všechna tři jsou popsána v části [Zálohování a obnova](backup.md).

## Související {#related}

- [Zálohování a obnova](backup.md)
- [Nastavení spolku](settings.md#updates)
