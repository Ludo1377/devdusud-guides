#!/usr/bin/env python3
"""Génère plan.html — plan du site STATIQUE avec de vrais liens <a href>.

Pourquoi : l'accueil du hub construit ses cartes en JavaScript, donc Googlebot
ne voit AUCUN lien interne (1 seule page indexée sur 854, constaté le 24/10/2026).
Une page unique de liens réels débloque le crawl de tout le site.

Usage : python3 scripts/gen-plan.py   (depuis la racine du repo devdusud-guides)
"""
import html
import os
import re
import time
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(ROOT, "sitemap.xml")
OUT = os.path.join(ROOT, "plan.html")
HOST = "https://ludo1377.github.io/devdusud-guides/"

LANGS = [("en", "🇬🇧 English"), ("es", "🇪🇸 Español"), ("de", "🇩🇪 Deutsch"),
         ("pt", "🇧🇷 Português"), ("ar", "🇸🇦 العربية"), ("", "🇫🇷 Français")]

# jolis libellés pour les segments d'URL connus
WORDS = {
    "aspirateurs-robots": "Aspirateurs robots", "casques-audio": "Casques audio",
    "machines-a-cafe": "Machines à café", "montres-connectees": "Montres connectées",
    "enceintes-bluetooth": "Enceintes Bluetooth", "outils-bricolage": "Outils de bricolage",
    "televiseurs": "Téléviseurs", "imprimantes": "Imprimantes", "smartphones": "Smartphones",
    "top10-ssd": "SSD externes", "chauffages-dappoint": "Chauffages d'appoint",
    "friteuses-sans-huile": "Friteuses sans huile", "machines-a-pain": "Machines à pain",
    "robots-cuisine": "Robots de cuisine", "velos-electriques": "Vélos électriques",
    "velos-dappartement": "Vélos d'appartement", "drones": "Drones", "gaming": "Gaming",
    "ventilateurs": "Ventilateurs", "cafetieres": "Cafetières",
    "freelance-premiers-clients": "Freelance : premiers clients",
    "gagner-argent-en-ligne": "Gagner de l'argent en ligne", "outils-no-code": "Outils no-code",
    "10-scripts-python": "10 scripts Python", "email-marketing": "Email marketing",
    "besoins": "Bien choisir selon ses besoins", "comparatif": "Comparatif",
    "duel": "Duel", "entretien": "Entretien", "erreurs": "Erreurs à éviter",
    "faq": "FAQ", "guide-achat": "Guide d'achat",
}


def label(url):
    tail = url.rstrip("/").split("/")[-1]
    tail = re.sub(r"\.html?$", "", tail)
    if not tail or tail == "devdusud-guides":
        return "Accueil"
    return WORDS.get(tail, tail.replace("-", " ").capitalize())


def main():
    locs = [e.text.strip() for e in ET.parse(SITEMAP).getroot().iter()
            if e.tag.endswith("loc") and e.text]
    groups = {k: [] for k, _ in LANGS}
    other = []
    langs_codes = {k for k, _ in LANGS if k}
    for u in locs:
        rel = u.replace(HOST, "")
        if not rel:
            groups[""].append(u)
            continue
        seg = rel.split("/")[0]
        if seg in langs_codes:
            groups[seg].append(u)
        else:
            # tout ce qui n'est pas une autre langue = contenu français (racine)
            groups[""].append(u)
    if "plan.html" not in locs:
        locs.append(HOST + "plan.html")

    css = """
:root{--bg:#0b0f14;--card:#151b24;--fg:#e6edf3;--muted:#93a1b0;--accent:#4ade80}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,Segoe UI,Roboto,sans-serif}
header{padding:32px 20px 8px;max-width:1100px;margin:0 auto}
h1{margin:0 0 6px;font-size:1.7rem}
p.sub{color:var(--muted);margin:0 0 8px}
main{max-width:1100px;margin:0 auto;padding:8px 20px 60px}
h2{font-size:1.15rem;margin:28px 0 10px;color:var(--accent);border-bottom:1px solid #223}
ul{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:6px}
li a{display:block;padding:7px 10px;background:var(--card);border-radius:8px;color:var(--fg);text-decoration:none;font-size:.92rem}
li a:hover{background:#1d2632;color:var(--accent)}
footer{max-width:1100px;margin:0 auto;padding:20px;color:var(--muted);font-size:.85rem}
"""
    parts = [f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan du site — tous les guides Dev du Sud</title>
<meta name="description" content="Liste complète des guides d'achat Dev du Sud : toutes les catégories, toutes les langues.">
<link rel="canonical" href="{HOST}plan.html">
<style>{css}</style>
</head>
<body>
<header>
  <h1>Plan du site</h1>
  <p class="sub">Tous les guides Dev du Sud — {len(locs)} pages, 6 langues. Mise à jour : {time.strftime('%d/%m/%Y')}.</p>
  <p class="sub"><a href="./" style="color:var(--accent)">← Retour à l'accueil</a></p>
</header>
<main>
"""]
    for code, name in LANGS:
        items = sorted(set(groups.get(code) or []))
        if not items:
            continue
        parts.append(f"<h2>{name} — {len(items)} pages</h2>\n<ul>\n")
        for u in items:
            rel = u.replace(HOST, "./") or "./"
            parts.append(f'  <li><a href="{html.escape(rel)}">{html.escape(label(u))}</a></li>\n')
        parts.append("</ul>\n")
    rest = sorted(set(other) - set(groups.get("") or []))
    if rest:
        parts.append(f"<h2>Outils et boutique — {len(rest)} pages</h2>\n<ul>\n")
        for u in rest:
            rel = u.replace(HOST, "./")
            parts.append(f'  <li><a href="{html.escape(rel)}">{html.escape(label(u))}</a></li>\n')
        parts.append("</ul>\n")
    parts.append("</main>\n<footer>Dev du Sud — plan du site généré automatiquement.</footer>\n</body>\n</html>\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(parts))

    # ajoute plan.html au sitemap s'il n'y est pas
    with open(SITEMAP, encoding="utf-8") as f:
        sm = f.read()
    if "plan.html</loc>" not in sm:
        sm = sm.replace("</urlset>",
                        f'  <url><loc>{HOST}plan.html</loc><lastmod>{time.strftime("%Y-%m-%d")}</lastmod></url>\n</urlset>')
        with open(SITEMAP, "w", encoding="utf-8") as f:
            f.write(sm)

    n_links = sum(1 for code, _ in LANGS for _ in groups.get(code) or []) + len(rest)
    print(f"plan.html écrit — {n_links} liens réels, {len(locs)} URLs au sitemap")


if __name__ == "__main__":
    main()
