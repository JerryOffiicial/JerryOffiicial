# Setup steps for JerryOffiicial's animated profile

1. Create the profile repo (name must be exactly your username):
   gh repo create JerryOffiicial --public --clone
   (or create "JerryOffiicial" on github.com/new, tick "Add a README", then git clone it)
2. Copy everything from this zip into that folder.
3. Python env:
   python -m venv .venv && source .venv/bin/activate     (Windows: .venv\Scripts\activate)
   pip install -r scripts/requirements.txt
4. Portrait: put a well-lit, front-facing photo in the folder as source-photo.jpg, then
   python scripts/prep_photo.py source-photo.jpg
   python scripts/make_ascii_svg.py            -> jerry-ascii.svg
5. Info card: edit the CARD list at the top of scripts/make_info_card.py, then
   python scripts/make_info_card.py            -> info-card.svg
6. Heatmap (needs internet):
   python scripts/fetch_contributions.py
   python scripts/render_heatmap_svg.py        -> contrib-heatmap.svg
7. Push:
   git add . && git commit -m "Animated profile README" && git push
8. GitHub -> repo -> Settings -> Actions -> General -> Workflow permissions -> "Read and write".
   Then Actions tab -> "Update profile art" -> Run workflow, to confirm it commits a fresh graph.
