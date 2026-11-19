# The World in One Image — Wednesday, 19 November 2026

A make.fun entry for **news-image-20261119**: the whole day's world news,
distilled into a single square front page.

`entry.png` (1024 × 1024) is the deliverable. Across the top sits a
seven-panel editorial collage; underneath it, seven headline cards tell
the stories in words, so the page works both as a picture and as a
readable summary of Wednesday, 19 November 2026.

## The seven stories

1. **Lead — Trump, Xi and Putin meet in first three-way summit.** The
   US, Chinese and Russian presidents held their first-ever trilateral
   meeting on the sidelines of the APEC summit in Shenzhen, with
   Ukraine, Iran, trade, AI and nuclear arms control on the agenda.
2. **Middle East — US and Iran trade fire as Gulf attacks widen.** US
   forces struck a missile site on Qeshm Island, Iran hit US facilities
   in Kuwait and Bahrain, Hormuz shipping came under attack, and the US
   raised its carrier deployment in the region to three.
3. **US Politics — Jeffries nominated to be first Black US House
   Speaker.** House Democrats nominated Hakeem Jeffries by 251 votes to
   11; a full-House vote on 3 January could make him the first Black
   lawmaker to hold the Speaker's chair.
4. **Europe — EU proposes 45 billion euro loan for Ukraine.** The
   European Commission proposed borrowing €45 billion on capital markets
   for Ukraine's budget, to be repaid after Russia pays reparations.
5. **Tech — Nvidia's interim CEO steadies staff after Huang exit.** At
   the first all-hands since Jensen Huang's resignation, interim CEO
   Colette Kress promised earlier pay raises and larger stock grants.
6. **Space — Voyager 1 reaches a full light-day from Earth.** After
   almost fifty years in flight, the probe's signals now take a full
   day to reach home — a first for any human-made object.
7. **Culture — GTA VI launches worldwide after a 13-year wait.** The
   game went on sale at midnight local time on PlayStation 5 and Xbox
   Series X|S, with record pre-orders and a return to Vice City.

The full editorial record — headlines, summaries and the source behind
each story — lives in `news.json`. That file also carries an
`also_noted` list: three further items researched on the day (the Fed
minutes pointing to further rate hikes, the Pew report on world
religions, and Cyclone Akvan's approach to India's east coast) that did
not make the front page but were part of the day's picture.

## How the image was made

The collage artwork (`front-page.png`) was generated as one editorial
illustration with seven panels, one per story: a summit handshake, a
burning tanker in the Gulf, a Speaker's gavel, an EU chamber, a chip
company all-hands, a deep-space probe, and a neon launch-night queue.

`build_image.py` then turned that artwork into the finished page with
Pillow: it adds the masthead ("THE WORLD IN ONE IMAGE" and the
dateline), crops the collage into a band, and lays out one card per
story — section kicker, headline and summary — driven entirely by the
contents of `news.json`, finishing with a source credit strip.

## Running it

Deliver the committed image to the runner's output directory:

```sh
python3 main.py
```

`main.py` copies `entry.png` byte-for-byte to `$MAKEFUN_OUTPUT_DIR`
(or `/output` when the variable is unset) and prints the delivered
size. Copying, rather than re-rendering, keeps the submitted pixels
exactly as reviewed.

Regenerate the page from its ingredients (requires Pillow):

```sh
python3 build_image.py
```

That rewrites `entry.png` in place from `front-page.png` and
`news.json`.

## Files

- `entry.png` — the finished 1024 × 1024 front page (the entry itself)
- `front-page.png` — the generated seven-panel collage artwork
- `news.json` — the day's stories, summaries and sources
- `build_image.py` — the Pillow renderer that composes the page
- `main.py` — the entrypoint; delivers `entry.png` to the output dir

## License

MIT — see `LICENSE`.
