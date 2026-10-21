#!/bin/bash
# Installe Zeynab dans la session cloud, que le dossier du dépôt soit branché ou non.
# Appelé par le « Script de configuration » de l'atelier Zeynab (voir le guide).
pip install -q pillow 2>/dev/null || true

D="$HOME/zeynab-methode"
if [ -d "$D/.git" ]; then
  git -C "$D" pull -q 2>/dev/null || true
else
  git clone -q --depth 1 https://github.com/BSM-Academy/zeynab-pages-produit-ia "$D" 2>/dev/null || true
fi
[ -f "$D/zeynab/SKILL.md" ] || { echo "Zeynab : téléchargement impossible"; exit 0; }

mkdir -p "$HOME/.claude/skills"
ln -sfn "$D/zeynab" "$HOME/.claude/skills/zeynab"

cat > "$HOME/.claude/CLAUDE.md" <<'EOF'
# Zeynab
Tu es **Zeynab**, la créatrice de pages produit IA de l'élève (skill `zeynab`).
Ta méthode complète est dans `~/zeynab-methode`. Si le dossier `zeynab-pages-produit-ia` n'est pas branché
sur cette session, lis `~/zeynab-methode/CLAUDE.md` et suis-le à la lettre, en lançant tes commandes depuis
`~/zeynab-methode` (les chemins `zeynab/scripts/…` et `travail/` partent de là).
Quand l'élève envoie un lien de page produit concurrente, c'est toujours une demande de page produit :
applique le skill `zeynab`, n'utilise aucun autre skill de création de boutique.
EOF
echo "Zeynab installée"
