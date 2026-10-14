# Anandaswarup Vadapalli — personal website

A static personal research website for academic collaborators and industry research teams. Published with GitHub Pages at https://anandaswarup.github.io/.

## Preview

```sh
python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open http://localhost:8000. The server is bound to loopback. Stop it with Ctrl+C.

## Editing

- `projects.json`: project summaries, methods, findings, resources, and paper mappings.
- `scripts/build.py`: page templates and bibliography extraction.
- `assets/style.css`: responsive design.
- `assets/site.js`: publication search, category filters, and mobile navigation.
- `assets/publications.bib`: source bibliography copied from the complete Master CV.
- `assets/anandaswarup-vadapalli-cv.pdf`: unchanged four-page Master CV.
- `site/`: generated static website; serve this directory only.

Run `python3 scripts/build.py` after editing. The build requires Python's standard library; no package installation is needed. Fonts use Google Fonts with local system fallbacks. All body content and navigation work without JavaScript; JavaScript enables filters and the compact mobile menu.

## Validation

```sh
python3 scripts/check.py
node --check assets/site.js
```

The validation checks all generated local links, assets, anchors, one primary heading per page, and exact coverage of the 17 CV papers across nine project groups.

## Content provenance

Source: the complete Master CV (`cv_anandaswarup.tex`, `pubs.bib`, and the four-page PDF), reviewed on 14 October 2026.

The site includes only the 17 papers cited in the CV, excluding the uncited 2023 preprint present in the source bibliography. Accepted ACDSA 2027 manuscripts are marked accepted, with no invented publication dates, proceedings metadata, or manuscript links. Findings for the five selected CV projects come from the CV. Other project descriptions use titles and available primary abstracts; no individual contribution or quantitative result is inferred from coauthorship alone.

Additional primary sources consulted:

- https://www.isca-archive.org/blizzard_2017/achanta17_blizzard.html
- https://www.isca-archive.org/blizzard_2015/rallabandi15_blizzard.html
- https://www.isca-archive.org/blizzard_2013/prahallad13_blizzard.html
- https://www.isca-archive.org/blizzard_2014/prahallad14_blizzard.html
- https://www.isca-archive.org/blizzard_2015/prahallad15_blizzard.html
- https://arxiv.org/abs/1508.00354
- https://www.isca-archive.org/ssw_2016/achanta16_ssw.pdf
- https://aclanthology.org/P13-2035.pdf

Project visuals are decorative diagrams, not empirical plots or fabricated research results. The portrait is an unchanged copy of the user’s LinkedIn profile image, retrieved with authorization on 14 October 2026 and stored at `assets/anandaswarup-vadapalli.png`. No audio examples have been invented. The downloadable CV retains the original contact details.

## Publish updates

The `main` branch contains editable source and generated files. GitHub Pages serves the root of the `gh-pages` branch. No custom Actions workflow or runtime server is required.

```sh
python3 scripts/build.py
python3 scripts/check.py
git add README.md projects.json scripts assets site
git commit -m "Update personal website"
git push origin main
git subtree push --prefix site origin gh-pages
```

The generated `.nojekyll` file preserves the static output. Normal pages use relative URLs; the custom 404 page uses root-relative links for this user-site domain. GitHub builds and publishes after changes are pushed to `gh-pages`.

