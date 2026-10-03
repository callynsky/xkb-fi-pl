# Zgłoszenie układu do xkeyboard-config

## Czy coś takiego już istnieje

Nie. Sprawdzone programowo na rejestrze `xkeyboard-config` 2.46:

* żaden układ nie deklaruje jednocześnie języków `fi` i `pl`;
* warianty `fi`: `winkeys`, `classic`, `nodeadkeys`, `mac`, `smi` — żaden polski;
* warianty `pl`: `legacy`, `qwertz`, `dvorak`, `dvorak_quotes`,
  `dvorak_altquotes`, `dvp`, `csb`, `szl` — żaden fiński;
* żaden układ nie ma wariantu o nazwie `pl`;
* poza układem `pl` żaden opis wariantu nie wspomina o polskim.

Przed wysłaniem zgłoszenia trzeba to powtórzyć na gałęzi `master`
w repozytorium upstreamu i przejrzeć otwarte zgłoszenia oraz merge requesty —
wymaga tego instrukcja projektu.

## Co trzeba zmienić w pliku

Upstream **nie przyjmie samodzielnego układu `fipl`**. Wymagania:

1. **Wariant istniejącego układu, nie nowy układ.** Symbole trafiają do
   `symbols/{cc}`, gdzie `cc` to dwuliterowy kod kraju ISO 3166 — czyli
   sekcja musi wejść do `symbols/fi` jako `xkb_symbols "pl"`, dając `fi(pl)`.
2. **Rejestracja w `rules/base.xml`**, nie w `evdev.xml` — ten drugi jest
   generowany. Wymagany przetłumaczalny `<description>` i kody ISO 639-1.
3. **Pełny opis w dwóch miejscach**: jako nazwa grupy w pliku symboli i jako
   opis w `base.xml`.
4. **Przebudowa samego pliku**, bo obecny go nie spełnia:
   * klawisze posortowane alfabetycznie po nazwie keycode (teraz są
     w kolejności rzędów klawiatury);
   * zamiast definiowania wszystkich klawiszy od zera — `include "fi(fi)"`
     i tylko klawisze różniące się;
   * `include "level3(ralt_switch)"` dla trzeciego poziomu — to już jest;
   * tylko jedna grupa (Group1) — to już jest.
5. **Build i testy**: `meson setup build`, `meson compile -C build`,
   `meson install -C build`, walidacja przez `xkbcli`. Haki pre-commit
   pilnują stylu.
6. **Nazwa wariantu do dyskusji.** Instrukcja wymienia ustalone nazwy
   (`dvorak`, `intl`, `mac`, `nodeadkeys`, `phonetic`, `us`, `winkeys`)
   i żadna nie opisuje „drugiego języka". `fi(pl)` byłoby nową konwencją;
   wariant z precedensem to `fi(intl)` („multi-language support").
7. **Licencja**: MIT (Expat) — zgodna z tym, na czym stoi `xkeyboard-config`.

## Proces

Merge request na <https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config>,
po wcześniejszym sprawdzeniu, czy ktoś już tego nie zgłosił.
Instrukcja: <https://xkeyboard-config.pages.freedesktop.org/website/doc/contributing>
