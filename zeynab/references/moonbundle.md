# Offre de packs avec Moonbundle (connecteur de l'élève)

But : reproduire l'offre du concurrent (paliers, prix, badge, cadeau, palier par défaut) sur le produit de l'élève.

## Avant
- L'élève a installé Moonbundle et choisi la **démo gratuite** (« Continue on demo », module **Bundles**) :
  offres illimitées jusqu'à 500 $ de ventes par mois. Sans plan ni démo, la publication est refusée
  (`feature_not_in_plan`) : le lui dire, ne rien contourner.
- Le bloc Moonbundle est déjà dans le modèle (`"moonbundle": true` dans page.json) et l'intégration est activée
  dans la copie du thème (`references/shopify.md`, étape 6).

## Créer l'offre
1. `product_search` avec le nom du produit → ID et handle exacts.
2. `bundle_list_templates(bundleType: "quantity-breaks")` → choisir le modèle le plus proche du concurrent
   (vertical / horizontal, cadeau ou non).
3. Lire la doc une seule fois : `get_moonbundle_doc(domain: "bundle")` (longue : chercher les parties
   « CREATE OFFER COUNT », « ATOMIC CREATE », « TEMPLATE LEAK TRAP »).
4. `bundle_create` en **un seul appel** avec `templateId`, `visibility: "products"`, `products: [...]` et un
   `configPatch` complet :
   - `configs[0].settings.headerTitle` (titre au-dessus des paliers, mot pour mot) et `headerSubtitle: ""` si absent ;
   - `offers: {"$replace": [...]}` avec **exactement** le nombre de paliers du concurrent (chaque palier : quantité,
     remise, titre, badge, palier par défaut…) ;
   - couleurs (`design`) si l'offre du concurrent en a.
   - cadeau offert : `settings.featuresEnabled.gift: true` et `gifts: {"$replace": [...]}`. Pièges vus en test :
     `match` s'écrit `">=,1"` (palier 1 et suivants ; `"==,2"` = palier 2 seulement), et `variant` doit contenir
     `show`, `show_options`, `confirm_button_text`, `toggle_button_text`. Le cadeau doit exister comme produit Shopify.
   Premier appel sans `merchantConfirmed` = aperçu. **Résumer l'offre à l'élève en 3 lignes, attendre son « ok »**,
   puis rappeler avec les mêmes arguments + `merchantConfirmed: true`. L'offre est créée en brouillon.
5. Montrer l'aperçu : `storefrontPreviewUrl` renvoyé par l'outil (boutique protégée : l'élève doit être connecté).
6. Publier : `bundle_set_status(status: "published")`, avec accord de l'élève (même règle).

## Vérifier
- Sur la page : les paliers au-dessus du bouton, le bon palier choisi par défaut.
- Au panier : la remise du palier est appliquée (ex. 2 × 26,99 au lieu de 2 × 29,99).

## Si l'offre n'apparaît pas
1. Intégration « Moon Bundle - Bundles » désactivée dans le thème regardé (copie **et** thème en ligne une fois publié).
2. Pas de démo ni de plan → publication bloquée (en aperçu seulement).
3. Bloc Moonbundle absent du modèle du produit.
