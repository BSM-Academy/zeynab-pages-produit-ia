# Images par IA (GPT Image 2.5 via Kie)

## Outil et coût
- Script `scripts/kie.py` (API Kie, clé de l'élève). **6 crédits par image en 1K, 10 en 2K**, 1 à 3 min.
  Un échec ne coûte rien.
- Une page = 20 à 30 images (galerie 6-8 carrées + sections mobile/ordinateur + cadeau + photos d'avis)
  → **150 à 250 crédits. L'annoncer avant de lancer et attendre le « ok ».**
- Ratios : `1:1` (galerie), `3:4` / `4:3`, `16:9` / `9:16`, `2:3` / `3:2`. **Pas de 4:5** (prendre 3:4).
  `9:8`, `8:9`, `27:16`, `16:27` existent seulement en 1K.
- L'image du concurrent passe directement en référence (`"ref"` = son URL `cdn.shopify.com`).

## Lancer
`travail/<…>/images.json` :
```json
[{"nom": "g1", "ratio": "1:1", "taille": "1K", "ref": "https://cdn.shopify.com/…/photo1.jpg", "prompt": "…"},
 {"nom": "s01_M", "ratio": "3:4", "taille": "1K", "ref": "https://cdn.shopify.com/…/hero-mobile.jpg", "prompt": "…"}]
```
Puis : `python3 zeynab/scripts/kie.py lancer travail/<…>/images.json`,
`python3 zeynab/scripts/kie.py recuperer travail/<…>/`, `python3 zeynab/scripts/kie.py planche travail/<…>/`.

## Prompts
Recréation fidèle (cas général) :
```
Recreate this image identically (same layout, same product, same people, same colors, same composition).
Only change: translate every text into perfect <LANGUE> (no leftover <langue source> word, correct accents of <LANGUE> only),
and replace the brand "<MARQUE CONCURRENT>" by "<NOTRE NOM>" everywhere, including on the product itself.
Exact texts to write: 1) "…" 2) "…" 3) "…"
Do not change the product shape, color or details. No other logo.
```
- **Donner la liste exacte des textes** traduits : l'IA écrit mieux ce qu'on lui dicte.
- Dire ce qui **ne doit pas changer** (couleur du produit, fond blanc qui reste blanc).

## Contrôle (obligatoire)
1. Regarder la **planche** (`planche.jpg`).
2. **Zoomer sur chaque texte** : accents d'une autre langue, lettre en trop, mot resté dans la langue d'origine,
   logo du concurrent.
3. Corriger : repasser l'image **déjà traduite** (son URL Kie en `ref`) avec « fix one word only: replace "X" by "Y",
   change nothing else ».
4. Ne reprendre ni logos presse, ni « Certifié CE », ni drapeau du pays du concurrent.

## Après
- `urls.json` contient l'URL Kie de chaque image : la donner à Shopify (`fileCreate`) **le jour même**
  (les URLs Kie sont temporaires).
