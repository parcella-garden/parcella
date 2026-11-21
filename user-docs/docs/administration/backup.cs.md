# Zálohování a obnova {#backup-and-restore}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Záloha je úplná kopie dat vašeho spolku v Parcelle v jednom souboru.
Díky ní můžete vše získat zpět po poruše serveru, po chybě nebo při
stěhování k novému poskytovateli. Zálohujte pravidelně a zálohy
uchovávejte jinde než na serveru Parcelly.

!!! info "Kdo to může používat"
    Jen administrátoři. Vše začíná v **Administrace → Systém**.

## Co záloha obsahuje {#what-a-backup-contains}

Jeden soubor `.zip` s:

- celou databází -- každý člen, parcela, odečet, faktura, nastavení a
  uživatelský účet,
- nahranými soubory uloženými v Parcelle: logo, obrázky oznámení,
  avatary a soubory procesů,
- klíčem, kterým Parcella šifruje uložená hesla (poštovní server, web,
  cloudové úložiště, helpdesk).

!!! warning "Se zálohou zacházejte jako s heslem"
    Protože obsahuje tento klíč a všechny osobní údaje vašich členů,
    každý, kdo soubor má, si může přečíst vše. Uložte ji tam, kam se
    dostane jen výbor.

Soubory uložené ve vašem cloudovém úložišti (složky parcel, přílohy
faktur, soubory poznámek) **nejsou** součástí zálohy -- už jsou v
cloudu, který má vlastní zálohování.

## Stažení zálohy {#download-a-backup}

V **Administrace → Systém** má karta **Záloha** tlačítko **Stáhnout
zálohu**. Prohlížeč soubor zip okamžitě stáhne. Na serveru se nic
neukládá, takže tento soubor je jediná kopie: uložte ho na bezpečné
místo.

Pokud se něco pokazí, uvidíte **Zálohování se nezdařilo:** a důvod.

## Obnovení ze zálohy {#restore-from-backup}

![Obnovit ze zálohy](../assets/screenshots/administration/backup-restore.png)

Otevřete ji tlačítkem **Obnovit ze zálohy** na stránce Systém.

!!! danger "Tím se přepíšou všechna současná data"
    Obnovení nahradí **celou** databázi a všechny nahrané soubory
    obsahem zálohy. Vše, co bylo zadáno od pořízení zálohy, je pryč,
    včetně uživatelských účtů a hesel vytvořených od té doby. Nelze to
    vrátit zpět. Pokud byste se možná chtěli vrátit, nejprve si
    **stáhněte zálohu současného stavu**.

| Pole / tlačítko | Co dělá |
|---|---|
| **Soubor zálohy (.zip)** | Vyberte soubor zálohy stažený z Parcelly (nejvýše 200 MB). |
| **Pro potvrzení napište RESTORE** | Napište slovo `RESTORE` velkými písmeny. Chrání to před nechtěným obnovením. |
| **Zrušit** | Zpět na stránku Systém. |
| **Obnovit** | Ještě jednou se zeptá a pak obnoví. Může to chvíli trvat. |

Potom uvidíte **Obnovení bylo úspěšně dokončeno.** Všichni -- včetně vás
-- teď pracují s daty ve stavu z doby pořízení zálohy; možná se budete
muset znovu přihlásit heslem, které platilo tehdy.

Možné zprávy:

| Zpráva | Význam |
|---|---|
| **Potvrzovací fráze se neshodovala -- nic nebylo změněno.** | Slovo nebylo přesně `RESTORE`. |
| **Soubor je příliš velký.** | Přes 200 MB. |
| **Soubor zálohy má neočekávanou strukturu: ...** | Nejde o zálohu Parcelly nebo je soubor poškozený. Nic nebylo změněno. |
| **Obnovení selhalo, nic nebylo změněno: ...** | Obnovení databáze selhalo a vaše data jsou jako dřív. |
| **Databáze byla úspěšně obnovena, ale obnovení nahraných souborů selhalo: ...** | Data jsou obnovena, ale některé soubory ne. Obnovení lze bezpečně spustit znovu. |

Zálohy ze starší verze Parcelly lze obnovit do novější; ten, kdo se
stará o server, možná bude muset poté spustit aktualizaci databáze.
<!-- TODO(verify): whether the app applies pending database migrations by itself after a restore of an older backup, or whether the server admin must always run them (developer docs say a restore doesn't run them). -->

## Zálohy v cloudu {#cloud-backups}

![Zálohy v cloudu](../assets/screenshots/administration/backup-cloud.png)

Otevřete je tlačítkem **Zálohy v cloudu** na stránce Systém. Parcella
umí stejnou zálohu vytvářet automaticky a nahrávat ji do vašeho
cloudového úložiště.

K tomu je potřeba zapnutý modul **Cloudové úložiště** a úložiště
nastavené v [Integrace](integrations.md#cloud-storage). Jinak vám
stránka řekne, co chybí, a nabídne odkaz.

### Plán {#schedule}

| Pole / tlačítko | Co dělá |
|---|---|
| **Automaticky zálohovat do cloudu** | Zapíná nebo vypíná automatické zálohy. |
| **Cílová složka** | Složka v cloudovém úložišti, např. `backups/parcella`. Pokud neexistuje, vytvoří se. Vyberte složku, kterou může otevřít jen výbor -- každá záloha obsahuje klíč k uloženým heslům. |
| **Frekvence** | **Každou hodinu**, **Denně** (výchozí), **Týdně** nebo **Měsíčně**. |
| **Kolik záloh uchovávat** | Kolik záloh ponechat, nejméně 1 (výchozí 10). Po přidání nové se smažou nejstarší nad tento počet. Týká se to jen vlastních souborů záloh Parcelly. |
| **Uložit** | Uloží plán (**Uloženo.**). |
| **Zálohovat do cloudu nyní** | Okamžitě vytvoří a nahraje zálohu, bez ohledu na to, zda jsou automatické zálohy zapnuté. |

Pod poli vidíte výsledek posledního běhu: **Poslední záloha do cloudu:
... (úspěšná).**, **... -- selhala:** s důvodem, nebo **Zatím neproběhla
žádná záloha do cloudu.** Občas to zkontrolujte -- záloha, která celé
týdny tiše selhává, není žádná záloha.

### Zálohy v cloudu {#backups-in-the-cloud}

Seznam záloh v cílové složce, od nejnovějších, s údaji **Název**,
**Velikost** a **Naposledy změněno**. Pokud žádné nejsou, zobrazí se
**V této složce zatím nejsou žádné zálohy.**

Chcete-li některou obnovit, napište do pole v jejím řádku `RESTORE` a
klikněte na **Obnovit**. Platí stejné varování jako výše: přepíše
všechna současná data.

## Osvědčený postup {#good-practice}

- Před velkými změnami si stáhněte zálohu: aktualizace, velký import,
  vyúčtování.
- Uchovávejte alespoň jednu kopii i mimo cloudové úložiště, např. na
  šifrovaném USB disku v trezoru spolku.
- Občas zálohu vyzkoušejte obnovením na náhradní testovací instalaci.
  Záloha, kterou jste nikdy neobnovili, je jen naděje.

## Související {#related}

- [Informace o systému a aktualizace](system.md)
- [Integrace](integrations.md#cloud-storage)
