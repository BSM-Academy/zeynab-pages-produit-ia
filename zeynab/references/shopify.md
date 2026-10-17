# Shopify : produits, fichiers, thème (connecteur Shopify de l'élève)

Tout passe par le connecteur Shopify : `graphql_query` (lecture) et `graphql_mutation` (écriture, claude.ai demande
la confirmation de l'élève). Toujours découvrir les champs avec `graphql_schema` avant une mutation inconnue.

## Ce que le connecteur refuse (normal)
- Écrire dans le thème **en ligne** (rôle MAIN), publier un thème, supprimer un thème.
- Donc : `themeDuplicate` du thème en ligne → tout construire dans la copie → **l'élève publie**.

## Produits
- `productSet(synchronous: true, input: {…})` : titre, `descriptionHtml` courte, `productOptions` + `variants`
  (`optionValues`, `price`, `compareAtPrice`, `taxable: false`, `inventoryItem: {tracked: false}`),
  `files` (galerie dans l'ordre, URLs Kie), `templateSuffix: "<suffixe>"`, `status: ACTIVE`.
- Puis `publishablePublish` vers la publication **Online Store** (`publications` pour trouver son ID).
- Sans variante : `productOptions: [{name: "Title", values: [{name: "Default Title"}]}]` et
  `variants: [{optionValues: [{optionName: "Title", name: "Default Title"}], price: "…"}]`.
- Cadeau : même méthode (prix réel barré, image IA). Cadeau numérique : `requiresShipping: false`.

## Fichiers (images de section)
- `fileCreate(files: [{originalSource: "<URL Kie>", filename: "<suffixe>_s01_M.png", contentType: IMAGE}])`,
  puis attendre `fileStatus: READY`.
- Vidéos du concurrent : `stagedUploadsCreate` (resource VIDEO, `fileSize` exact) + envoi `curl` + `fileCreate`
  avec `resourceUrl`, puis lire `sources { url }` (prendre le mp4 480p) pour le mettre dans le code.

## Thème : copie et modèle « tout thème »
1. `themes(roles: [MAIN])` → ID et nom du thème en ligne. `themeDuplicate(id, name: "<nom> + Zeynab")`.
   Si une copie « … + Zeynab » non publiée existe déjà, la réutiliser.
2. Lire dans la copie : `templates/product.json` et la liste des fichiers `blocks/custom-liquid.liquid`,
   `sections/custom-liquid.liquid` (`theme(id){ files(filenames: [...]) { nodes { filename body { ... on OnlineStoreThemeFileBodyText { content } } } } }`).
   - `blocks/custom-liquid.liquid` existe → thème « à blocs de thème » (Horizon et récents) → option `--theme-blocks`.
   - Sinon → thème classique (Dawn et la plupart) : le bloc s'appelle `custom_liquid`.
   - `sections/custom-liquid.liquid` absent → le signaler et s'arrêter (rare).
3. Écrire `travail/<…>/base.json` (le contenu lu) et `travail/<…>/page.json`, puis :
   `python3 zeynab/scripts/modele.py base.json page.json product.<suffixe>.json [--theme-blocks]`.
4. Envoyer **une fois** : `themeFilesUpsert(themeId, files: [{filename: "templates/product.<suffixe>.json",
   body: {type: TEXT, value: <contenu>}}])` avec le contenu passé en **variables**. Mode URL : échoue sans message.
5. Assigner : `productUpdate` (ou `productSet`) avec `templateSuffix: "<suffixe>"`.
6. **Intégration Moonbundle** dans la copie : lire `config/settings_data.json`, ajouter dans `current.blocks`
   (s'il n'y est pas déjà) :
   `"zeynab_moonbundle": {"type": "shopify://apps/moon-bundles/blocks/app-embed/aaf4cd95-8b9b-4a14-b929-0f7fc8fced27", "disabled": false, "settings": {}}`
   puis renvoyer le fichier entier (sans le commentaire `/* … */` du début). Sans cette intégration, l'offre n'apparaît pas.

## Écrire le code des sections (page.json)
- Une section = un morceau de HTML + `<style>` qui reproduit la section du concurrent. Préfixe CSS propre à la page
  (`zy-`) pour ne pas casser le thème. HTML avec **apostrophes simples** (`class='…'`).
- Images : `{{ '<suffixe>_s01_M.png' | file_img_url: '1200x' }}` (mobile), `'1800x'` (ordinateur), `'500x'` (vignettes).
  `file_url` **sans** taille seulement (SVG) ; `file_url` avec une taille = « Liquid error ».
- Image mobile + ordinateur :
  ```html
  <div class='zy-img'><picture><source media='(max-width: 699px)' srcset='{{ "x_s01_M.png" | file_img_url: "1200x" }}'>
  <img src='{{ "x_s01_D.png" | file_img_url: "1800x" }}' alt='…' loading='lazy'></picture></div>
  <style>.zy-img img{display:block;width:100%;height:auto}</style>
  ```
- Accordéons : `<details><summary>…</summary>…</details>`. Vidéos : `<video autoplay muted loop playsinline>`.
- Libellé du bouton du thème : le changer en CSS dans un bloc (`font-size:0` sur le texte + `::after{content:'…'}`),
  jamais en JavaScript. Le sélecteur dépend du thème : le lire dans le HTML de l'aperçu.

## Vérifier
- La boutique de l'élève est souvent protégée par mot de passe : vérifier par le code (JSON relu, pas d'erreur
  `userErrors`), puis donner à l'élève le lien d'aperçu de l'éditeur :
  `https://admin.shopify.com/store/<handle-boutique>/themes/<id-copie>/editor?previewPath=/products/<handle>`.
- Lui demander une capture en mobile s'il voit un défaut (« Liquid error », image cassée, section vide).
