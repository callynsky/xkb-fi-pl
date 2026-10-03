# Konsola tekstowa

Są dwie drogi. **Pierwsza jest prostsza i w większości wypadków wystarczy.**

## 1. Przez console-setup (zalecane)

Jeśli plik układu leży w systemowym katalogu XKB — a tak jest po instalacji
pakietu `.deb` — `ckbcomp` znajdzie go sam i nie trzeba niczego podawać:

```bash
sudo sed -i 's/^XKBLAYOUT=.*/XKBLAYOUT="fipl"/;  s/^XKBVARIANT=.*/XKBVARIANT="fi_pl"/' \
    /etc/default/keyboard
sudo setupcon --save
```

Sprawdzenie:

```bash
zcat /etc/console-setup/cached_UTF-8_del.kmap.gz | grep -m1 '^keycode  *30 ='
# trzecia kolumna ma byc +U+0105, czyli ą
```

**Pułapka, o której warto wiedzieć.** `/etc/default/keyboard` **nie jest**
plikiem konfiguracyjnym dpkg (conffile) — generuje go `keyboard-configuration`
z bazy debconf przy każdej aktualizacji tego pakietu. Zmiana wprowadzona
powyższym `sed`-em zostanie przy najbliższej aktualizacji wymazana. Żeby
przetrwała, trzeba ustawić także debconf:

```bash
sudo debconf-set-selections <<'EOS'
keyboard-configuration keyboard-configuration/layoutcode  string fipl
keyboard-configuration keyboard-configuration/variantcode string fi_pl
EOS
```

Dopiero wtedy postinst odtworzy **właściwy** plik, zamiast go psuć.

## 2. Przez własną jednostkę systemd

Potrzebna tylko wtedy, gdy nie chcesz ruszać `/etc/default/keyboard` — na
przykład gdy układ masz wyłącznie w `/etc/xkb`, bez pliku w `/usr/share`.
Mapa powstaje raz, a jednostka wczytuje ją **po** `console-setup`:

```bash
./install.sh --console
sudo systemctl enable --now console-keymap-fipl.service
```

Kolejność `After=console-setup.service` jest konieczna: bez niej
`console-setup` wczytałby własną mapę po naszej i nadpisał ją.

Przykład jednostki instaluje się także z pakietem, do
`/usr/share/doc/xkb-fi-pl/examples/`. Pakiet **nie włącza go sam**.

## Czego to nie obejmuje

Konsola w initramfs (przed uruchomieniem systemd) zachowa starą mapę. Ma to
znaczenie tylko wtedy, gdy wpisujesz tam hasło — czyli przy szyfrowanym
dysku (LUKS). Wtedy dodatkowo:

```bash
sudo update-initramfs -u -k all
```
