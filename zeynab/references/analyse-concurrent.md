# Analyser la page concurrente

But : un inventaire assez précis pour reconstruire la page **à l'identique**, sans retourner sur le site.

## 1. Données produit (Shopify public)
- `curl -sL "<url>.json"` (ou `/products/<handle>.json`) : titre, description, variantes, prix, prix barré,
  **photos de la galerie dans l'ordre**, en pleine taille, sans doublon.
- Si ce n'est pas une boutique Shopify, tout relever dans le HTML.

## 2. Sections de la page
- Récupérer le HTML (`curl -sL -A "Mozilla/5.0" <url>`) et lister les `id="shopify-section-…"` dans l'ordre :
  c'est la structure.
- Pour chaque section : type (image, texte, avis, comparatif, FAQ, accordéons…), **textes exacts**, nombre
  d'éléments (cartes, questions, icônes), couleurs, images et vidéos.
- `<picture><source media="(max-width: 699px)">` = **image mobile distincte** de l'image ordinateur : refaire les deux.
- Bloc d'achat : noter chaque bloc **dans l'ordre** (étoiles, titre, description, badges, puces, promo, **offres de
  packs**, stock, bouton et son libellé, paiements, réassurance, mini-avis, vidéos…).
- Pages construites entièrement en code (`custom_liquid`) : relever le rendu final dans le HTML, pas les blocs.

## 3. Avis
- Avis natifs : texte dans le HTML.
- **Loox** = iframe : récupérer le texte avec `curl` sur l'URL `loox.io/widget/...` trouvée dans la page.
- Garder prénom + texte, traduire. Photos d'avis : reprendre celles du concurrent ou les régénérer.

## 4. Offres de packs
- Relever les paliers : quantité, prix, % affiché, badge (« Le plus populaire »…), cadeau, palier choisi par défaut,
  titre au-dessus des paliers. Les données sont souvent dans un JSON de la page (Kaching, Moonbundle, Bundler…) :
  chercher `"quantity"`, `"discount"` dans le HTML.
- Prix dans une autre devise : convertir au **taux du jour** et arrondir à **,99** (prix et prix barré).

## 5. Médias
- Télécharger dans `travail/<…>/concurrent/` : galerie (g1…gN), images de section (s01_M, s01_D…),
  vidéos (`.mp4` du CDN Shopify : prendre la version 480p ou 720p).
- Les images du concurrent servent de **référence** à l'IA par leur URL `cdn.shopify.com` (rien à envoyer).

## Sortie : `page-concurrent.md`
```
SECTION 1  image hero (M + D), texte sur l'image : « … »
SECTION 2  logos presse « Ils en parlent » (2 cartes) → à neutraliser
…
BLOC D'ACHAT
  titre / étoiles « (Basé sur +603 avis) » / description / 3 badges / 4 puces
  offre : 1 = 39,99 · 2 = 59,99 (par défaut, badge « Le plus populaire ») + cadeau
  bouton « Profiter de l'offre » (vert, arrondi) / paiements / 4 réassurances / mini-avis
SECTION 9  accordéons (3) …
```
