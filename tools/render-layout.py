#!/usr/bin/env python3
"""Rysuje mape klawiatury ukladu XKB jako SVG (i opcjonalnie PNG).

Zrodlem jest RZECZYWISTY, skompilowany keymap z xkbcli, nie plik symbols -
dzieki temu obrazek pokazuje to, co naprawde dostaje aplikacja, razem ze
wszystkim, co wnosza include'y (latin, level3(ralt_switch) itd.).

Uzycie:
    python3 tools/render-layout.py [--layout fipl] [--variant fi_pl]
                                   [--keymap PLIK] [--out docs/uklad] [--png]

Zaleznosci: wylacznie biblioteka standardowa. PNG powstaje przez rsvg-convert,
inkscape albo cairosvg - pierwsze dostepne.
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

# --- keysym -> znak do wyswietlenia ---------------------------------------
NAMED = {
    "NoSymbol": "", "space": "␣",
    "Adiaeresis": "Ä", "adiaeresis": "ä", "Aring": "Å", "aring": "å",
    "Odiaeresis": "Ö", "odiaeresis": "ö",
    "Aogonek": "Ą", "aogonek": "ą", "Cacute": "Ć", "cacute": "ć",
    "Eogonek": "Ę", "eogonek": "ę", "Lstroke": "Ł", "lstroke": "ł",
    "Nacute": "Ń", "nacute": "ń", "Oacute": "Ó", "oacute": "ó",
    "Sacute": "Ś", "sacute": "ś", "Zabovedot": "Ż", "zabovedot": "ż",
    "Zacute": "Ź", "zacute": "ź",
    "ampersand": "&", "apostrophe": "'", "asterisk": "*", "at": "@",
    "backslash": "\\", "bar": "|", "braceleft": "{", "braceright": "}",
    "bracketleft": "[", "bracketright": "]", "brokenbar": "¦",
    "colon": ":", "comma": ",", "currency": "¤", "dollar": "$",
    "equal": "=", "exclam": "!", "greater": ">", "less": "<",
    "minus": "-", "numbersign": "#", "onehalf": "½", "parenleft": "(",
    "parenright": ")", "percent": "%", "period": ".", "plus": "+",
    "question": "?", "quotedbl": '"', "section": "§", "semicolon": ";",
    "slash": "/", "sterling": "£", "underscore": "_", "EuroSign": "€",
    # martwe klawisze oznaczamy kropka, zeby bylo widac, ze nie daja znaku od razu
    "dead_acute": "ˊ", "dead_grave": "ˋ",
    # Znaki wnoszone przez fi(classic) na trzecim i czwartym poziomie.
    "ae": "æ", "AE": "Æ", "oe": "œ", "OE": "Œ",
    "oslash": "ø", "Oslash": "Ø", "eth": "ð", "ETH": "Ð",
    "thorn": "þ", "THORN": "Þ", "eng": "ŋ", "ENG": "Ŋ",
    "ssharp": "ß", "kra": "ĸ", "idotless": "ı", "mu": "µ",
    "yen": "¥", "cent": "¢", "degree": "°",
    "paragraph": "¶", "registered": "®", "notsign": "¬",
    "periodcentered": "·", "hyphen": "‐",
    "exclamdown": "¡", "questiondown": "¿", "plusminus": "±",
    "masculine": "º", "ordfeminine": "ª",
    "onesuperior": "¹", "twosuperior": "²", "threesuperior": "³",
    "onequarter": "¼", "threequarters": "¾",
    # Martwe klawisze - pokazujemy sam znak diakrytyczny.
    "dead_diaeresis": "¨", "dead_circumflex": "ˆ",
    "dead_tilde": "˜", "dead_caron": "ˇ", "dead_macron": "¯",
    "dead_breve": "˘", "dead_cedilla": "¸", "dead_ogonek": "˛",
    "dead_greek": "μ",
}
POLISH = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")

# --- fizyczny uklad pc105: nazwa -> (rzad, x, szerokosc) ------------------
U = 1.0
GEOM = {}
def _row(y, items, x0=0.0):
    x = x0
    for name, w in items:
        GEOM[name] = (y, x, w)
        x += w

_row(0, [("TLDE", 1)] + [(f"AE{i:02d}", 1) for i in range(1, 13)] + [("BKSP", 2)])
_row(1, [("TAB", 1.5)] + [(f"AD{i:02d}", 1) for i in range(1, 13)])
_row(2, [("CAPS", 1.75)] + [(f"AC{i:02d}", 1) for i in range(1, 12)] + [("BKSL", 1)])
_row(3, [("LFSH", 1.25), ("LSGT", 1)] + [(f"AB{i:02d}", 1) for i in range(1, 11)]
        + [("RTSH", 2.75)])
_row(4, [("LCTL", 1.25), ("LWIN", 1.25), ("LALT", 1.25), ("SPCE", 6.25),
         ("RALT", 1.25), ("RWIN", 1.25), ("MENU", 1.25), ("RCTL", 1.25)])

# Klawisze funkcyjne. W skompilowanym keymapie MAJA swoje keysymy
# (Shift_L, Caps_Lock, ISO_Level3_Shift...), wiec bez tej listy rysowalyby
# surowe nazwy, wylewajace sie poza klawisz.
LABELS = {
    "BKSP": "Backspace", "TAB": "Tab", "CAPS": "Caps Lock", "LFSH": "Shift",
    "RTSH": "Shift", "LCTL": "Ctrl", "RCTL": "Ctrl", "LALT": "Alt",
    "RALT": "AltGr", "LWIN": "Super", "RWIN": "Super", "MENU": "Menu",
    "SPCE": "",
}


# Legenda w trzech jezykach - README projektu jest PL/EN/FI.
_Q = ('<tspan fill="#c2660a" font-weight="bold">{a}</tspan>, '
      '<tspan fill="#a0620f">{b}</tspan>.')
LEGEND = {
    "pl": ("Ćwiartki klawisza: lewa góra = zwykły, prawa góra = Shift, "
           + _Q.format(a="lewa dół = AltGr", b="prawa dół = AltGr+Shift"),
           '<tspan fill="#c2660a" font-weight="bold">Pomarańczowa ramka</tspan>'
           " = klawisz z polskim znakiem diakrytycznym."),
    "en": ("Key quadrants: top left = plain, top right = Shift, "
           + _Q.format(a="bottom left = AltGr", b="bottom right = AltGr+Shift"),
           '<tspan fill="#c2660a" font-weight="bold">Orange frame</tspan>'
           " = key carrying a Polish diacritic."),
    "fi": ("Näppäimen neljännekset: ylävasen = tavallinen, yläoikea = Shift, "
           + _Q.format(a="alavasen = AltGr", b="alaoikea = AltGr+Shift"),
           '<tspan fill="#c2660a" font-weight="bold">Oranssi kehys</tspan>'
           " = näppäin, jossa on puolalainen tarkemerkki."),
}

def keysym_to_text(sym):
    sym = sym.strip()
    if not sym:
        return ""
    if sym in NAMED:
        return NAMED[sym]
    if len(sym) == 1:
        return sym
    m = re.fullmatch(r"U([0-9A-Fa-f]{4,6})", sym)
    if m:
        return chr(int(m.group(1), 16))
    m = re.fullmatch(r"0x0*([0-9A-Fa-f]+)", sym)
    if m:
        v = int(m.group(1), 16)
        return chr(v - 0x1000000) if v > 0x1000000 else chr(v)
    return sym  # nieznana nazwa: pokaz ja wprost, lepsze niz cicha pustka


def load_keymap(args):
    if args.keymap:
        return Path(args.keymap).read_text(encoding="utf-8")
    cmd = ["xkbcli", "compile-keymap", "--layout", args.layout]
    if args.variant:
        cmd += ["--variant", args.variant]
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              check=True).stdout
    except FileNotFoundError:
        sys.exit("Brak xkbcli (pakiet libxkbcommon-tools). Uzyj --keymap PLIK.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"xkbcli nie skompilowal ukladu:\n{e.stderr}")


def parse_levels(keymap):
    """Zwraca {nazwa_klawisza: [poziom1, poziom2, poziom3, poziom4]}."""
    out = {}
    # blok klawisza moze zawierac type[...] i symbols[...]; bierzemy liste [...]
    for m in re.finditer(r"key\s+<([A-Z0-9]+)>\s*\{(.*?)\}\s*;", keymap, re.S):
        name, body = m.group(1), m.group(2)
        lst = re.search(r"\[([^\]]*)\]", body)
        if not lst:
            continue
        syms = [keysym_to_text(s) for s in lst.group(1).split(",")]
        syms += [""] * (4 - len(syms))
        out[name] = syms[:4]
    return out


def svg(levels, title, lang, subs=()):
    KW, KH, PAD, GAP = 62, 62, 18, 4
    width = PAD * 2 + 15 * KW
    height = PAD * 2 + 5 * KH + 86
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
         f'height="{height}" viewBox="0 0 {width} {height}">',
         '<style>',
         '  text{font-family:"DejaVu Sans",sans-serif}',
         '  .l1,.l2,.l3,.l4,.fn,.ti{text-anchor:middle}',
         '  .lg{text-anchor:start}',
         '  .k{fill:#f7f7f5;stroke:#9a9a94;stroke-width:1.2;rx:6}',
         '  .kp{fill:#fff4e0;stroke:#e08a1e;stroke-width:2;rx:6}',
         '  .ks{fill:#e8f1fb;stroke:#1f6fb2;stroke-width:2;rx:6}',
         '  .kf{fill:#e8e8e4;stroke:#9a9a94;stroke-width:1.2;rx:6}',
         '  .l1{font-size:17px;fill:#1a1a1a}',
         '  .l2{font-size:13px;fill:#444}',
         '  .l3{font-size:15px;fill:#c2660a;font-weight:bold}',
         '  .l4{font-size:12px;fill:#a0620f}',
         '  .fn{font-size:11px;fill:#555}',
         '  .ti{font-size:19px;fill:#111;font-weight:bold}',
         '  .lg{font-size:12px;fill:#333}',
         '</style>',
         f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
         f'<text class="ti" x="{width/2}" y="26">{html.escape(title)}</text>']

    def cell(name, row, x, w):
        px = PAD + x * KW + GAP / 2
        py = PAD + 34 + row * KH + GAP / 2
        cw, ch = w * KW - GAP, KH - GAP
        syms = None if name in LABELS else levels.get(name)
        if syms is None:
            p.append(f'<rect class="kf" x="{px}" y="{py}" width="{cw}" '
                     f'height="{ch}"/>')
            lab = LABELS.get(name, name)
            if lab:
                p.append(f'<text class="fn" x="{px+cw/2}" y="{py+ch/2+4}">'
                         f'{html.escape(lab)}</text>')
            return
        polish = any(c in POLISH for s in syms[2:4] for c in s)
        cls = "ks" if name in subs else ("kp" if polish else "k")
        p.append(f'<rect class="{cls}" x="{px}" y="{py}" '
                 f'width="{cw}" height="{ch}"/>')
        # cwiartki: lewa gora=zwykly, prawa gora=Shift,
        #           lewa dol=AltGr, prawa dol=AltGr+Shift
        for cls, sym, dx, dy in (("l1", syms[0], 0.30, 0.42),
                                 ("l2", syms[1], 0.74, 0.38),
                                 ("l3", syms[2], 0.30, 0.86),
                                 ("l4", syms[3], 0.74, 0.86)):
            if sym:
                p.append(f'<text class="{cls}" x="{px+cw*dx}" '
                         f'y="{py+ch*dy}">{html.escape(sym)}</text>')

    for name, (row, x, w) in GEOM.items():
        cell(name, row, x, w)
    # ISO Enter: dwa prostokaty, bo klawisz jest dwupoziomowy
    ex, ey = PAD + 13.5 * KW + GAP / 2, PAD + 34 + 1 * KH + GAP / 2
    p.append(f'<rect class="kf" x="{ex}" y="{ey}" width="{1.5*KW-GAP}" '
             f'height="{KH-GAP}"/>')
    p.append(f'<rect class="kf" x="{PAD+12.75*KW+GAP/2+KW}" '
             f'y="{PAD+34+2*KH+GAP/2}" width="{1.25*KW-GAP}" '
             f'height="{KH-GAP}"/>')
    p.append(f'<text class="fn" x="{ex+(1.5*KW-GAP)/2}" y="{ey+KH/2}">Enter</text>')

    ly = PAD + 34 + 5 * KH + 20
    a, b = LEGEND[lang]
    p.append(f'<text class="lg" x="{PAD}" y="{ly}">{a}</text>')
    if subs:
        b += ('  <tspan fill="#1f6fb2" font-weight="bold">Niebieska ramka</tspan>'
              " = moja podmiana wzgledem standardowego finskiego.")
    p.append(f'<text class="lg" x="{PAD}" y="{ly+18}">{b}</text>')
    p.append('</svg>')
    return "\n".join(p)


def to_png(svg_path, png_path):
    for cmd in (["rsvg-convert", "-z", "2", "-o", str(png_path), str(svg_path)],
                ["inkscape", "--export-type=png", "--export-dpi=192",
                 f"--export-filename={png_path}", str(svg_path)],
                ["cairosvg", "-f", "png", "-s", "2", "-o", str(png_path),
                 str(svg_path)]):
        if shutil.which(cmd[0]):
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                return cmd[0]
            print(f"{cmd[0]}: {r.stderr.strip()[:200]}", file=sys.stderr)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layout", default="fipl")
    ap.add_argument("--variant", default="fi_pl")
    ap.add_argument("--keymap", help="gotowy keymap z xkbcli, zamiast kompilacji")
    ap.add_argument("--out", default="docs/uklad-fipl")
    ap.add_argument("--title", default="Finnish + Polish AltGr (fipl / fi_pl)")
    ap.add_argument("--lang", default="pl", choices=sorted(LEGEND))
    ap.add_argument("--subs", default="",
                    help="klawisze z MOIMI podmianami, np. AD12 - inny kolor ramki")
    ap.add_argument("--png", action="store_true")
    a = ap.parse_args()

    levels = parse_levels(load_keymap(a))
    if not levels:
        sys.exit("Nie znalazlem zadnego klawisza w keymapie.")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    svg_path = out.with_suffix(".svg")
    svg_path.write_text(svg(levels, a.title, a.lang, {x.strip() for x in a.subs.split(",") if x.strip()}), encoding="utf-8")
    npl = sum(1 for s in levels.values()
              if any(c in POLISH for x in s[2:4] for c in x))
    print(f"SVG: {svg_path}  (klawiszy: {len(levels)}, z polskimi znakami: {npl})")
    if a.png:
        png_path = out.with_suffix(".png")
        tool = to_png(svg_path, png_path)
        print(f"PNG: {png_path}  (przez {tool})" if tool
              else "PNG: nie udalo sie - brak rsvg-convert/inkscape/cairosvg")


if __name__ == "__main__":
    main()
