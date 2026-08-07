"""Report how much of the DEEP long-form content is translated, per language.

DEEP (remover/page_content.py) is the biggest block of prose on a tool page and
was untranslatable until the deep_dive partial started routing it through
{% t %}. That made a gap visible that had always been there: a page listed in
views._CORE_TRANSLATED tells Google, through hreflang and the sitemap, that a
translation exists — while several hundred words at the bottom stayed English.

This prints the gap so it can be worked down deliberately. The DECLARED block is
the one that matters: those pages are making a promise. The rest are honest
English pages and can wait.

Run:  venv/bin/python scripts/deep-translation-status.py
      venv/bin/python scripts/deep-translation-status.py <tool>   # dump its strings
"""
import os
import sys

import django


def strings_of(entry):
    """Every translatable string in a DEEP entry, in render order."""
    out = [entry["title"]]
    for section in entry.get("sections", []):
        out.append(section["h"])
        out += section.get("p", [])
        out += section.get("list", [])
    return out


def main():
    sys.path.insert(0, ".")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()
    from django.urls import NoReverseMatch, reverse

    from remover.context_processors import TOOL_NAV
    from remover.page_content import DEEP
    from remover.translations import CATALOGUES, LANGUAGES
    from remover.views import _CORE_TRANSLATED

    # Dump one entry's strings, ready to paste into a catalogue.
    if len(sys.argv) > 1:
        key = sys.argv[1]
        if key not in DEEP:
            raise SystemExit(f"no DEEP entry for {key!r}")
        for s in strings_of(DEEP[key]):
            print(f'    "{s}":\n        "",')
        return 0

    declared = set()
    for tool in TOOL_NAV:
        try:
            if reverse(f"remover:{tool['name']}") in _CORE_TRANSLATED:
                declared.add(tool["name"])
        except NoReverseMatch:
            continue

    cats = {lang: CATALOGUES[lang].UI for lang in LANGUAGES}
    rows = []
    for key, entry in sorted(DEEP.items()):
        ss = strings_of(entry)
        done = {lang: sum(1 for s in ss if s in cats[lang]) for lang in LANGUAGES}
        rows.append((key, key in declared, len(ss), sum(len(s.split()) for s in ss), done))

    for label, want in (("DECLARED TRANSLATED — these pages promise a translation", True),
                        ("NOT DECLARED — honest English pages, no promise made", False)):
        group = [r for r in rows if r[1] is want]
        if not group:
            continue
        print(f"\n{label}")
        head = "  " + f"{'entry':28}{'strings':>8}{'words':>7}" + "".join(f"{l:>10}" for l in LANGUAGES)
        print(head)
        print("  " + "-" * (len(head) - 2))
        for key, _, n, words, done in group:
            cells = "".join(f"{f'{done[l]}/{n}':>10}" for l in LANGUAGES)
            flag = "" if all(done[l] == n for l in LANGUAGES) else "  <--"
            print(f"  {key:28}{n:>8}{words:>7}{cells}{flag}")
        for lang in LANGUAGES:
            miss = sum(n - done[lang] for _, _, n, _, done in group)
            words = sum(w for _, _, n, w, done in group if done[lang] < n)
            print(f"    {lang}: {miss} strings outstanding (~{words} words)")

    # Half-translated entries are the real defect: the page reads as a mix.
    partial = [(k, l, d[l], n) for k, _, n, _, d in rows for l in LANGUAGES
               if 0 < d[l] < n]
    if partial:
        print("\nPARTIALLY translated entries (a page rendering half in each language):")
        for k, l, d, n in partial:
            print(f"  {k} [{l}] {d}/{n}")
    else:
        print("\nNo entry is half-translated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
