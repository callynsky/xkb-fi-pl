#!/bin/sh
# Instalator ukladu fipl bez pakietu .deb.
#
# NIE wybiera ukladu i NIE zmienia zadnego Twojego ustawienia - ani
# w srodowisku graficznym, ani w /etc/default/keyboard. Wylacznie udostepnia
# uklad; wybor nalezy do Ciebie.
#
# Uzycie: ./install.sh {--check|--user|--system|--console|--uninstall} [--force]

set -eu

SRC="$(cd "$(dirname "$0")" && pwd)"
LAYOUT=fipl
VARIANT=fi_pl
USERDIR="${XDG_CONFIG_HOME:-$HOME/.config}/xkb"
SYSDIR=/etc/xkb
KMAP=/etc/console-keymap-fipl.kmap.gz
UNIT=/etc/systemd/system/console-keymap-fipl.service

die()  { printf '%s\n' "$*" >&2; exit 1; }
info() { printf '%s\n' "$*"; }

# Bramka: uklad, ktory sie nie kompiluje, potrafi zostawic pusta klawiature
# na ekranie logowania. Sprawdzamy ZANIM cokolwiek zainstalujemy.
check() {
    [ -f "$SRC/symbols/$LAYOUT" ] || die "Brak $SRC/symbols/$LAYOUT"
    if ! command -v xkbcli >/dev/null 2>&1; then
        info "xkbcli niedostepne (pakiet libxkbcommon-tools) - pomijam kompilacje."
        return 0
    fi
    tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
    mkdir -p "$tmp/symbols"
    cp "$SRC/symbols/$LAYOUT" "$tmp/symbols/$LAYOUT"
    if XKB_CONFIG_EXTRA_PATH="$tmp" xkbcli compile-keymap \
           --layout "$LAYOUT" --variant "$VARIANT" >/dev/null 2>&1; then
        info "OK: uklad $LAYOUT($VARIANT) kompiluje sie."
    else
        die "BLAD: uklad $LAYOUT($VARIANT) NIE kompiluje sie. Nie instaluje."
    fi
}

install_to() {   # $1 = katalog bazowy, $2 = polecenie podnoszace uprawnienia
    $2 mkdir -p "$1/symbols" "$1/rules"
    $2 cp "$SRC/symbols/$LAYOUT" "$1/symbols/$LAYOUT"
    $2 cp "$SRC/rules/evdev.xml" "$1/rules/evdev.xml"
    $2 chmod 644 "$1/symbols/$LAYOUT" "$1/rules/evdev.xml"
    info "Zainstalowano w $1"
    info "Wybierz uklad sam: Ustawienia -> Klawiatura -> Uklady -> Dodaj -> $LAYOUT"
}

case "${1:---check}" in
    --check)  check ;;
    --user)   check; install_to "$USERDIR" ""
              info "Uwaga: to dziala tylko dla Twojej sesji, nie dla ekranu logowania." ;;
    --system) check; install_to "$SYSDIR" "sudo"
              info "Dziala takze dla ekranu logowania (greeter czyta /etc/xkb)." ;;
    --console)
        command -v ckbcomp >/dev/null 2>&1 || die "Brak ckbcomp (pakiet console-setup)."
        [ -f "$SYSDIR/symbols/$LAYOUT" ] || [ -f "/usr/share/X11/xkb/symbols/$LAYOUT" ] \
            || die "Najpierw ./install.sh --system albo pakiet .deb."
        ckbcomp -I"$SYSDIR" "$LAYOUT" "$VARIANT" | gzip -9 | sudo tee "$KMAP" >/dev/null
        sudo cp "$SRC/systemd/console-keymap-fipl.service" "$UNIT"
        sudo systemctl daemon-reload
        info "Mapa: $KMAP, jednostka: $UNIT"
        info "Wlaczenie (swiadoma decyzja): sudo systemctl enable --now console-keymap-fipl.service"
        info "Alternatywa bez jednostki: XKBLAYOUT=\"$LAYOUT\" XKBVARIANT=\"$VARIANT\" w /etc/default/keyboard." ;;
    --uninstall)
        rm -f "$USERDIR/symbols/$LAYOUT" "$USERDIR/rules/evdev.xml"
        sudo rm -f "$SYSDIR/symbols/$LAYOUT" "$SYSDIR/rules/evdev.xml" "$KMAP"
        if [ -f "$UNIT" ]; then
            sudo systemctl disable --now console-keymap-fipl.service 2>/dev/null || true
            sudo rm -f "$UNIT"; sudo systemctl daemon-reload
        fi
        info "Usunieto. Jesli uklad byl wybrany w ustawieniach, zmien go sam." ;;
    -h|--help) sed -n '2,/^$/p' "$0" ;;
    *) die "Nieznany argument: $1" ;;
esac
