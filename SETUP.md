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
   python scripts/make_portrait.py             -> data/portrait.json
   (tune with PORTRAIT_SPAN / PORTRAIT_COLS / PORTRAIT_GAMMA, see the top of the script)
5. Stats (needs internet):
   python scripts/fetch_contributions.py       -> data/contributions.json
   python scripts/fetch_github_stats.py        -> data/github.json
   (set GH_TOKEN first if you hit the API rate limit, e.g. GH_TOKEN=$(gh auth token))
6. Art: edit the CARD list at the top of scripts/render_neofetch_svg.py, then
   python scripts/render_neofetch_svg.py       -> assets/neofetch.svg
   python scripts/render_heatmap_svg.py        -> assets/contrib-heatmap.svg
   python scripts/render_buttons_svg.py        -> assets/btn-*.svg
   (STATIC=1 in front of the first two gives a frozen frame, handy for checking layout)
7. Push:
   git add . && git commit -m "Animated profile README" && git push
8. GitHub -> repo -> Settings -> Actions -> General -> Workflow permissions -> "Read and write".
   Then Actions tab -> "Update profile art" -> Run workflow. It refreshes the contribution
   graph and the live neofetch lines (Uptime, GitHub, Langs) every day.
