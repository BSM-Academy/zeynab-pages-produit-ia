"""Construit le modèle de page produit de Zeynab pour N'IMPORTE QUEL thème Shopify.

Principe : on part du modèle produit de l'élève (templates/product.json de SON thème), on garde tout tel quel
(galerie, titre, prix, variantes, bouton du thème) et on ajoute seulement :
  - des blocs « Liquid personnalisé » dans le bloc d'achat (avant ou après le bouton) ;
  - le bloc d'appli Moonbundle juste avant le bouton (offres de packs) ;
  - des sections « Liquid personnalisé » avant et après la section produit (les sections copiées du concurrent).

Usage :
  python3 modele.py <base.json> <page.json> <sortie.json> [--theme-blocks]
    base.json   : templates/product.json du thème (le commentaire /* ... */ du début est accepté)
    page.json   : {"bloc_avant": [html...], "bloc_apres": [html...], "sections_avant": [html...],
                   "sections_apres": [html...], "moonbundle": true}
                  - bloc_avant  : dans le bloc d'achat, juste avant le bouton (badges, puces, avis courts...)
                  - bloc_apres  : dans le bloc d'achat, juste après le bouton (réassurance, paiements, mini-avis...)
                  - sections_avant / sections_apres : sections pleine largeur avant / après la section produit
    --theme-blocks : thème « à blocs de thème » (Horizon et thèmes récents : fichier blocks/custom-liquid.liquid présent).
                     Sans l'option : thème classique (Dawn et la plupart des thèmes : bloc « custom_liquid »).
Affiche ce qui a été trouvé (section produit, bouton) et refuse si le bouton d'achat est introuvable.
"""
import json, re, sys

BOUTON = ("buy_buttons", "buy-buttons", "buy_button", "buy-button", "add_to_cart", "add-to-cart",
          "product-form", "product_form", "buy", "form")
MOON_BLOC = "shopify://apps/moon-bundles/blocks/app-block/aaf4cd95-8b9b-4a14-b929-0f7fc8fced27"


def lire_json(chemin):
    t = open(chemin, encoding="utf-8").read()
    t = re.sub(r"^\s*/\*.*?\*/", "", t, flags=re.S)  # commentaire automatique de Shopify
    return json.loads(t)


def conteneur_achat(section):
    """Renvoie le dict qui contient les blocs du bloc d'achat (section elle-même, ou bloc imbriqué type _product-details)."""
    def a_bouton(d):
        return any(b.get("type", "") in BOUTON for b in d.get("blocks", {}).values())
    if a_bouton(section):
        return section
    pile = list(section.get("blocks", {}).values())
    while pile:
        b = pile.pop(0)
        if a_bouton(b):
            return b
        pile.extend(b.get("blocks", {}).values())
    return None


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    base, page, sortie = lire_json(sys.argv[1]), json.load(open(sys.argv[2], encoding="utf-8")), sys.argv[3]
    blocs_theme = "--theme-blocks" in sys.argv
    type_bloc = "custom-liquid" if blocs_theme else "custom_liquid"
    produit_moon = "{{closest.product}}" if blocs_theme else "{{product}}"

    secs, ordre = base["sections"], base["order"]
    cle_main = next((k for k in ordre if conteneur_achat(secs[k]) is not None), None)
    if not cle_main:
        raise SystemExit("REFUS : bouton d'achat introuvable dans le modèle. Lire sections/main-product*.liquid et le signaler.")
    cont = conteneur_achat(secs[cle_main])
    cle_bouton = next(k for k, b in cont["blocks"].items() if b.get("type", "") in BOUTON)
    print(f"section produit : {cle_main} ({secs[cle_main]['type']}) | bouton : {cle_bouton} ({cont['blocks'][cle_bouton]['type']})"
          f" | blocs : {type_bloc}")

    def bloc(html):
        d = {"type": type_bloc, "settings": {"custom_liquid": html}}
        if blocs_theme:
            d["blocks"] = {}
        return d

    ordre_blocs = cont.setdefault("block_order", list(cont["blocks"]))
    i = ordre_blocs.index(cle_bouton)
    avant, apres = [], []
    if page.get("moonbundle"):
        cont["blocks"]["zeynab_moonbundle"] = {"type": MOON_BLOC, "settings": {"moonbundle_selected_product": produit_moon}}
        avant.append("zeynab_moonbundle")
    for n, html in enumerate(page.get("bloc_avant", []), 1):
        cont["blocks"][f"zeynab_b{n:02d}"] = bloc(html)
        avant.append(f"zeynab_b{n:02d}")
    for n, html in enumerate(page.get("bloc_apres", []), 1):
        cont["blocks"][f"zeynab_a{n:02d}"] = bloc(html)
        apres.append(f"zeynab_a{n:02d}")
    ordre_blocs[i:i + 1] = avant + [cle_bouton] + apres

    def section(html):
        return {"type": "custom-liquid", "settings": {"custom_liquid": html}}

    av = []
    for n, html in enumerate(page.get("sections_avant", []), 1):
        secs[f"zeynab_s{n:02d}"] = section(html)
        av.append(f"zeynab_s{n:02d}")
    ap = []
    for n, html in enumerate(page.get("sections_apres", []), len(av) + 1):
        secs[f"zeynab_s{n:02d}"] = section(html)
        ap.append(f"zeynab_s{n:02d}")
    j = ordre.index(cle_main)
    base["order"] = ordre[:j] + av + [cle_main] + ap + ordre[j + 1:]

    texte = json.dumps(base, ensure_ascii=False, separators=(",", ":"))
    json.loads(texte)
    open(sortie, "w", encoding="utf-8").write(texte)
    print(f"ok : {sortie} ({len(texte)} caractères) | blocs avant/après bouton : {len(avant)}/{len(apres)}"
          f" | sections avant/après : {len(av)}/{len(ap)}")


if __name__ == "__main__":
    main()
