# xkb-fi-pl 1.1.0

## Polski

Standardowy fiński układ klawiatury, w którym **AltGr daje polskie znaki
dokładnie tak samo jak na polskiej klawiaturze (`pl`)**. Fińska podstawa
zostaje nietknięta — `å`, `ö`, `ä` i martwe znaki na swoich miejscach.

| klawisz | AltGr | AltGr+Shift |
|---|---|---|
| `a` `c` `e` `l` `n` | ą ć ę ł ń | Ą Ć Ę Ł Ń |
| `o` `s` `x` `z` | ó ś ź ż | Ó Ś Ź Ż |

### Instalacja z pakietu .deb

```bash
sudo apt install ./xkb-fi-pl_1.1.0_all.deb
```

Pakiet **tylko udostępnia** układ. Niczego nie wybiera i nie zmienia żadnego
ustawienia — nie ma skryptów `postinst` ani `postrm`. Wybór należy do Ciebie:

```bash
# sesja graficzna: Ustawienia -> Klawiatura -> Uklady -> Dodaj -> "fipl"
# konsola i ekran logowania:
sudo localectl set-x11-keymap fipl pc105 fi_pl
```

### Instalacja bez pakietu

```bash
./install.sh --check      # sprawdza, czy uklad sie kompiluje; nic nie instaluje
./install.sh --user       # ~/.config/xkb        (tylko moja sesja)
./install.sh --system     # /etc/xkb             (takze ekran logowania)
./install.sh --uninstall
```

W trybie `--user` i `--system` podgląd układu w module „Klawiatura" KDE nie
zadziała — `xkbcomp` czyta wyłącznie systemowy katalog XKB. Podgląd wymaga
pakietu `.deb`.

### Co nowego w 1.1.0

* Plik przebudowany na styl upstreamu: `include "fi(classic)"` plus dziewięć
  klawiszy, posortowanych alfabetycznie po nazwie keycode.
* **Naprawiony klawisz `AD12`** — w 1.0.0 było tam przez pomyłkę drugie `ö`,
  przez co nie dało się napisać `ô`, `ñ` ani `ž`. Wracają martwe znaki
  z fińskiego układu.
* `include "kpdl(dot)"` — kropka na klawiaturze numerycznej zostaje kropką.
* 38 klawiszy odzyskuje poziomy AltGr standardowego fińskiego (`µ ß þ ð ø æ`,
  strzałki, martwe znaki), które w 1.0.0 nie dawały nic.

Jedyna świadoma strata względem `fi(classic)`: `AltGr+l` zajmuje miejsce
`dead_stroke`.

---

## English

A standard Finnish keyboard layout where **AltGr produces the Polish letters
in the same positions as on the Polish (`pl`) layout**. The Finnish base is
untouched — `å`, `ö`, `ä` and the dead keys all stay where they are.

| key | AltGr | AltGr+Shift |
|---|---|---|
| `a` `c` `e` `l` `n` | ą ć ę ł ń | Ą Ć Ę Ł Ń |
| `o` `s` `x` `z` | ó ś ź ż | Ó Ś Ź Ż |

### Install from the .deb

```bash
sudo apt install ./xkb-fi-pl_1.1.0_all.deb
```

The package only **makes the layout available**. It never selects it and never
edits your settings — there are no maintainer scripts at all. Pick it yourself:

```bash
# desktop: Settings -> Keyboard -> Layouts -> Add -> "fipl"
# console and login screen:
sudo localectl set-x11-keymap fipl pc105 fi_pl
```

### Install without the package

```bash
./install.sh --check      # verifies the layout compiles; installs nothing
./install.sh --user       # ~/.config/xkb        (your session only)
./install.sh --system     # /etc/xkb             (login screen too)
./install.sh --uninstall
```

With `--user` or `--system` the layout preview in KDE's Keyboard module will
not work — `xkbcomp` only reads the system XKB directory. The preview needs
the `.deb`.

### What is new in 1.1.0

* Rewritten in upstream style: `include "fi(classic)"` plus nine keys, sorted
  alphabetically by keycode name.
* **Fixed `AD12`** — 1.0.0 had a second `ö` there by mistake, which made `ô`,
  `ñ` and `ž` impossible to type. The Finnish dead keys are back.
* `include "kpdl(dot)"` keeps the keypad decimal separator a dot.
* 38 keys regain the standard Finnish AltGr levels (`µ ß þ ð ø æ`, arrows,
  dead keys) that produced nothing in 1.0.0.

The one deliberate trade-off against `fi(classic)`: `AltGr+l` replaces
`dead_stroke`.

---

Verified on a clean Ubuntu 26.04 container: package installs, `xkbcli list`
shows the layout, `xkbcli compile-keymap` yields the nine Polish letters with
`AD11` = `å` and `AD12` = dead keys, and `ckbcomp fipl fi_pl` puts `U+0105`
(`ą`) in the console keymap.

Licence: MIT (Expat). The included `fi(classic)` base remains the property of
the xkeyboard-config authors; see `debian/copyright`.
