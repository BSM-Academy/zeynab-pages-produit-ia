"""Images IA de Zeynab (GPT Image 2.5 via l'API Kie), sans rien installer.

  python3 kie.py lancer <travail/images.json>
      images.json : [{"nom": "g1", "prompt": "...", "ref": "https://cdn.shopify.com/...", "ratio": "1:1", "taille": "1K"}, ...]
      Lance toutes les images en parallèle, écrit les numéros de tâche dans <travail/taches.json>.
  python3 kie.py recuperer <travail/>
      Attend la fin, télécharge <travail/images/<nom>.png>, écrit <travail/urls.json> (URL Kie de chaque image,
      à donner à Shopify fileCreate le jour même), affiche les crédits consommés.
  python3 kie.py planche <travail/>
      Fait <travail/planche.jpg> : toutes les images avec leur nom, à regarder une fois.

La clé est dans la variable KIE_API_KEY. Si elle vaut « cloud », le vrai secret est ajouté par claude.ai
(« secrets réseau ») : on n'envoie alors aucun en-tête d'autorisation. Ne jamais afficher la clé.
Coût indicatif : 6 crédits par image en 1K, 10 en 2K. Un échec ne coûte rien."""
import json, os, sys, time, urllib.request

API = "https://api.kie.ai/api/v1"
CLE = os.environ.get("KIE_API_KEY", "")


def appel(chemin, donnees=None):
    h = {"Content-Type": "application/json"}
    if CLE and CLE != "cloud":
        h["Authorization"] = "Bearer " + CLE
    req = urllib.request.Request(API + chemin, data=json.dumps(donnees).encode() if donnees is not None else None,
                                 headers=h, method="POST" if donnees is not None else "GET")
    return json.load(urllib.request.urlopen(req, timeout=60))


def lancer(fichier):
    images = json.load(open(fichier, encoding="utf-8"))
    dossier = os.path.dirname(os.path.abspath(fichier))
    taches_f = os.path.join(dossier, "taches.json")
    taches = json.load(open(taches_f)) if os.path.exists(taches_f) else {}
    for im in images:
        if im["nom"] in taches:
            continue
        entree = {"prompt": im["prompt"], "aspect_ratio": im.get("ratio", "1:1"), "resolution": im.get("taille", "1K")}
        mode = "text-to-image"
        if im.get("ref"):
            entree["input_urls"] = im["ref"] if isinstance(im["ref"], list) else [im["ref"]]
            mode = "image-to-image"
        r = appel("/jobs/createTask", {"model": f"gpt-image-2-5-flare-{mode}", "input": entree})
        if r.get("code") != 200:
            print(im["nom"], "REFUS :", r.get("msg"))
            continue
        taches[im["nom"]] = r["data"]["taskId"]
        print(im["nom"], "lancée")
    json.dump(taches, open(taches_f, "w"), indent=1)
    print(f"{len(taches)} tâche(s) dans {taches_f}")


def recuperer(dossier):
    taches = json.load(open(os.path.join(dossier, "taches.json")))
    urls_f = os.path.join(dossier, "urls.json")
    urls = json.load(open(urls_f)) if os.path.exists(urls_f) else {}
    os.makedirs(os.path.join(dossier, "images"), exist_ok=True)
    restantes = {n: t for n, t in taches.items() if n not in urls}
    credits = 0
    for _ in range(60):
        for nom, tid in list(restantes.items()):
            d = appel(f"/jobs/recordInfo?taskId={tid}")["data"]
            if d["state"] == "success":
                u = json.loads(d["resultJson"])["resultUrls"][0]
                urls[nom] = u
                urllib.request.urlretrieve(u, os.path.join(dossier, "images", nom + ".png"))
                credits += d.get("creditsConsumed") or 0
                print(nom, "ok")
                restantes.pop(nom)
            elif d["state"] == "fail":
                print(nom, "ÉCHEC :", d.get("failMsg"))
                restantes.pop(nom)
        if not restantes:
            break
        time.sleep(10)
    json.dump(urls, open(urls_f, "w"), indent=1)
    print("crédits consommés :", credits, "| encore en cours :", list(restantes))


def planche(dossier):
    from PIL import Image, ImageDraw
    d = os.path.join(dossier, "images")
    noms = sorted(f for f in os.listdir(d) if f.endswith(".png"))
    if not noms:
        raise SystemExit("aucune image")
    L, col = 360, 4
    lignes = (len(noms) + col - 1) // col
    out = Image.new("RGB", (col * L, lignes * (L + 28)), "white")
    for i, n in enumerate(noms):
        im = Image.open(os.path.join(d, n)).convert("RGB")
        im.thumbnail((L - 8, L - 8))
        x, y = (i % col) * L, (i // col) * (L + 28)
        out.paste(im, (x + 4, y + 4))
        ImageDraw.Draw(out).text((x + 6, y + L + 6), n[:-4], fill="black")
    out.save(os.path.join(dossier, "planche.jpg"), quality=85)
    print("planche :", os.path.join(dossier, "planche.jpg"))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("lancer", "recuperer", "planche"):
        raise SystemExit(__doc__)
    {"lancer": lancer, "recuperer": recuperer, "planche": planche}[sys.argv[1]](sys.argv[2])
