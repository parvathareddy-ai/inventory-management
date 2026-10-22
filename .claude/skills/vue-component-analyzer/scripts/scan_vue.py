#!/usr/bin/env python3
"""Scan Vue 3 SFCs and print structural metrics and duplication candidates.

Heuristic, regex-based and read-only: it narrows where to look, it does not
prove a problem. Usage: scan_vue.py [src_dir] [--json]
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

BLOCK = {k: re.compile(rf"<{k}\b[^>]*>(.*?)</{k}>", re.S) for k in ("template", "script", "style")}


def block(src, name):
    m = BLOCK[name].search(src) if name != "template" else re.search(r"<template>(.*)</template>", src, re.S)
    return m.group(1) if m else ""


def lines(text):
    return len([l for l in text.splitlines() if l.strip()])


def analyze(path):
    src = path.read_text(encoding="utf-8")
    tpl, script, style = block(src, "template"), block(src, "script"), block(src, "style")
    vfor_tags = re.findall(r"<[\w-]+[^>]*\sv-for=[^>]*>", tpl, re.S)
    no_key = [t for t in vfor_tags if not re.search(r"(:|v-bind:)key=", t)]
    index_key = [t for t in vfor_tags if re.search(r":key=\"\s*(i|idx|index)\s*\"", t)]
    vif_vfor = [t for t in vfor_tags if re.search(r"\sv-if=", t)]
    return {
        "file": str(path),
        "lines": {"total": lines(src), "template": lines(tpl), "script": lines(script), "style": lines(style)},
        "state": {
            "refs": len(re.findall(r"\b(?:ref|shallowRef)\(", script)),
            "reactive": len(re.findall(r"\breactive\(", script)),
            "computed": len(re.findall(r"\bcomputed\(", script)),
            "watchers": len(re.findall(r"\bwatch(?:Effect)?\(", script)),
            "deep_watchers": len(re.findall(r"deep:\s*true", script)),
            "props": len(re.findall(r"defineProps|props:\s*\{", script)),
            "emits": len(re.findall(r"defineEmits|emits:\s*\[", script)),
        },
        "template_smells": {
            "v_for_total": len(vfor_tags),
            "v_for_missing_key": len(no_key),
            "v_for_index_key": len(index_key),
            "v_if_with_v_for": len(vif_vfor),
            "inline_arrow_handlers": len(re.findall(r"@[\w.:-]+=\"\s*\(?[\w, ]*\)?\s*=>", tpl)),
            # Work done in the template re-runs on every render.
            "array_ops_in_template": len(re.findall(r"(?:\{\{|=\")[^}\"]*\.(?:filter|map|sort|reduce)\(", tpl)),
            # i18n lookups (t(...), $t(...)) are cheap and ubiquitous, so they are excluded.
            "function_calls_in_mustache": len(re.findall(r"\{\{[^}]*(?<![\w$])(?!t\()[a-z]\w*\([^}]*\}\}", tpl)),
            "tables": len(re.findall(r"<table\b", tpl)),
            "modal_like_roots": len(re.findall(r"class=\"[^\"]*modal[^\"]*\"", tpl)),
        },
        "scoped_style": bool(re.search(r"<style[^>]*\bscoped\b", src)),
        "_style": style,
        "_funcs": set(re.findall(r"(?:const|function)\s+(format\w+|get\w+Color|get\w+Class|\w+Badge\w*)\b", script)),
        "_imports": re.findall(r"import\s+.*?from\s+['\"](.+?)['\"]", script),
    }


def css_rules(style):
    out = {}
    for sel, body in re.findall(r"([^{}@]+)\{([^{}]+)\}", style):
        body = " ".join(sorted(p.strip() for p in body.split(";") if p.strip()))
        if len(body) > 40:  # skip trivial one-liners
            out[(" ".join(sel.split()), body)] = 1
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else "client/src")
    results = [analyze(p) for p in sorted(root.rglob("*.vue"))]

    sel_files, body_files, func_files = defaultdict(set), defaultdict(set), defaultdict(set)
    for r in results:
        for (sel, body) in css_rules(r["_style"]):
            sel_files[sel].add(r["file"])
            body_files[body].add(r["file"])
        for f in r["_funcs"]:
            func_files[f].add(r["file"])
    dup = {
        "css_selectors_in_3plus_files": {k: sorted(v) for k, v in sel_files.items() if len(v) >= 3},
        "identical_css_bodies_in_3plus_files": {
            k[:80] + "...": sorted(v) for k, v in body_files.items() if len(v) >= 3
        },
        "helper_functions_redefined_in_2plus_files": {k: sorted(v) for k, v in func_files.items() if len(v) >= 2},
    }
    for r in results:
        for k in ("_style", "_funcs", "_imports"):
            r.pop(k)

    if "--json" in sys.argv:
        print(json.dumps({"files": results, "duplication": dup}, indent=2))
        return
    print(f"{'file':52} {'total':>5} {'tpl':>5} {'scr':>5} {'sty':>5} {'ref':>4} {'cmp':>4} {'wch':>4} {'v-for':>5} {'nokey':>5}")
    for r in sorted(results, key=lambda r: -r["lines"]["total"]):
        l, s, t = r["lines"], r["state"], r["template_smells"]
        print(f"{r['file'][-52:]:52} {l['total']:>5} {l['template']:>5} {l['script']:>5} {l['style']:>5} "
              f"{s['refs']:>4} {s['computed']:>4} {s['watchers']:>4} {t['v_for_total']:>5} {t['v_for_missing_key']:>5}")
    print("\nTemplate smells (non-zero only):")
    for r in results:
        bad = {k: v for k, v in r["template_smells"].items()
               if v and k in ("v_for_missing_key", "v_for_index_key", "v_if_with_v_for",
                              "array_ops_in_template", "function_calls_in_mustache", "inline_arrow_handlers")}
        deep = r["state"]["deep_watchers"]
        if deep:
            bad["deep_watchers"] = deep
        if bad:
            print(f"  {r['file']}: {bad}")
    print("\nDuplication candidates:")
    for title, d in dup.items():
        print(f"  {title}: {len(d)}")
        for k, v in list(d.items())[:15]:
            print(f"    {k}  ->  {len(v)} files")


if __name__ == "__main__":
    main()
