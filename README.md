# Santa's Legacy — website

The marketing site for **Santa's Legacy**, by **Pixel Studio**.

Plain HTML, CSS and one JavaScript file. No build step, no framework, no
dependencies — what is in this repository is exactly what gets served. Open
`index.html` in a browser and it works.

```
index.html          The game page: hero, trailer, features, minigames,
                    screenshots, FAQ, studio.
press.html          Press kit: fact sheet, downloads, screenshots.
privacy.html        Privacy & cookie notice (required once GA is live).
404.html            Not-found page.
configure.py        Stamps your domain / GA ID / email over the placeholders.
tools/              Regenerates the images from the game repo (needs Pillow).
docs/               An optional GitHub Actions deploy workflow (see below).
assets/css/         One stylesheet.
assets/js/          One script: nav, lightbox, trailer, snow, analytics.
assets/fonts/       Oleo Script + Nunito, self-hosted and subsetted.
assets/img/         Hero, screenshots, thumbnails, icons, social card.
assets/video/       The 720p trailer (12 MB).
assets/press/       The downloadable press-kit zip (3.7 MB).
```

---

## Before you publish: four placeholders

The site ships with four deliberate placeholders. `configure.py` replaces all
of them everywhere in one command:

```bash
python configure.py --url https://santaslegacy.com \
                    --ga  G-ABC1234567 \
                    --email press@santaslegacy.com
```

| Placeholder | Where it appears | What to set it to |
|---|---|---|
| `https://example.com` | canonical links, Open Graph tags, JSON-LD, `sitemap.xml`, `robots.txt` | Your live URL, no trailing slash |
| `G-XXXXXXXXXX` | `assets/js/main.js` → `CONFIG.GA_MEASUREMENT_ID` | Your GA4 measurement ID |
| `press@example.com` | footer, press page, privacy page | A real inbox you read |
| `4006370` | every Steam link | Already correct — it is the app ID from `steam_appid.txt` |

Every flag is optional and the script is safe to re-run: it reads the *current*
value out of `index.html` first, so running it twice does not break anything.

There is one more thing worth a human eye before going live: the hero badge
says **"Free demo out now on Steam"** and the FAQ repeats it. That matches the
key art in the game repo — but if the Steam page is not published yet, change
both to "Coming soon" or the page promises something a visitor cannot get.

---

## Google Analytics

GA4 is wired up but **does not load until the visitor accepts the cookie
notice**. That is deliberate: it is the legal position in the EU and the UK,
and it means the site makes zero third-party requests to anyone who declines.

- Set `CONFIG.GA_MEASUREMENT_ID` in `assets/js/main.js` (or use `configure.py`).
- Until it is a real `G-` ID, nothing loads and the consent banner never
  appears — so a local copy stays silent.
- Consent is remembered in `localStorage` under `sl_consent_v1`. The privacy
  page has a **Change my cookie choice** button that clears it and drops the
  `_ga` cookies.
- To use a different consent tool, set `CONFIG.REQUIRE_CONSENT = false` and
  call `loadAnalytics()` from your own tool's callback.

Events sent beyond the automatic page views:

| Event | Fires when |
|---|---|
| `wishlist_click` | any Steam button, with `link_location` naming which one |
| `trailer_play` | the trailer poster is clicked |
| `screenshot_open` | a screenshot is opened in the lightbox |
| `file_download` | the press kit or trailer is downloaded |
| `email_click` | a `mailto:` link is used |

In GA4 these arrive as custom events. Mark `wishlist_click` as a **key event**
(Admin → Events) if you want conversion reporting on it.

---

## SEO

Already in place:

- Unique `<title>` and meta description per page, plus canonical URLs.
- Open Graph and Twitter card tags on every page, with a 1200×630 card.
- JSON-LD structured data: `Organization`, `WebSite`, `VideoGame` (with a
  nested `VideoObject` for the trailer) and `FAQPage`. The FAQ markup matches
  the visible FAQ text one-to-one, which is what Google requires.
- `sitemap.xml` with image and video extensions, and `robots.txt` pointing
  at it.
- One `<h1>` per page and a heading order that does not skip levels.
- Descriptive `alt` text on every image; decorative images have empty `alt`.
- `width`/`height` on every image, so nothing shifts while loading.

After you publish: submit the sitemap in
[Google Search Console](https://search.google.com/search-console) and
[Bing Webmaster Tools](https://www.bing.com/webmasters). That is the one step
that cannot be done from inside the repository.

## Performance

- Fonts are **self-hosted and subsetted** to Latin + Latin Extended, 105 KB
  total, with `font-display: swap` and the two used first preloaded. Nothing is
  fetched from Google's servers, so there is no third-party request and no
  consent question about fonts.
- Every photo ships as **WebP with a JPEG fallback**, at a gallery width and a
  thumbnail width. The page loads thumbnails; the full size is fetched only
  when a screenshot is opened.
- The hero is preloaded with a `srcset` at 1000/1600/2400px.
- **The trailer is `preload="none"`.** Twelve megabytes of video are not
  downloaded until someone presses play.
- Everything below the hero is `loading="lazy"`.
- The snowfall is a small canvas that stops when the hero scrolls away or the
  tab is hidden, and never starts at all under `prefers-reduced-motion`.

## Accessibility

Skip link, visible focus rings, a keyboard-operable lightbox (Esc, ←, →,
focus returned on close), `aria-expanded` on the mobile nav, and full respect
for `prefers-reduced-motion` — which disables the reveal animations, the
smooth scrolling and the snow.

---

## Deploying

### GitHub Pages (what this repo is set up for)

1. Push this folder to `main`.
2. Repository **Settings → Pages → Source: "Deploy from a branch"**, branch
   `main`, folder `/ (root)`.
3. That is it. Every push to `main` republishes; the first build takes a
   minute or two.

`.nojekyll` is present so Pages serves the files verbatim rather than running
them through Jekyll — which matters, because a folder here is named `assets`
and Jekyll has opinions about that.

**Why no Actions workflow?** There is one, written and ready, at
`docs/pages-workflow.yml` — but GitHub rejects any push that creates a file
under `.github/workflows/` unless the credential carries the `workflow` OAuth
scope, and a normal browser sign-in does not. A static site at the repo root
gains nothing from it, so branch deployment is the default here. If you want
the Actions route anyway, the header of that file has the three-step recipe
(copy it in through GitHub's web editor, which has the scope).

**A custom domain:** add a file called `CNAME` containing just your domain
(e.g. `santaslegacy.com`), point a `CNAME` DNS record at
`<your-user>.github.io`, then re-run `configure.py --url https://santaslegacy.com`.

**A project subpath** (`user.github.io/santas-legacy/`) works too — every link
and asset reference in the site is relative, so nothing has to change except
the canonical URL you pass to `configure.py`.

### Anywhere else

Netlify, Cloudflare Pages, Vercel, or any static host: point it at this folder
with no build command and no output directory. It is already the built site.

### Previewing locally

```bash
python -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` straight off the disk works too, but a server is closer to
the real thing.

---

## Where the media came from

Everything was generated from the game repository (`D:\Santa'sLegacy`), so it
can all be regenerated after an art pass:

| Here | Source |
|---|---|
| `assets/img/hero-*` | `Screenshots/01_village_hero.png` |
| `assets/img/shots/*`, `thumbs/*` | `Screenshots/` and `Screenshots/steam/` |
| `assets/img/trailer-poster.*`, `og-image.jpg` | `Recordings/SantasLegacy_Trailer_poster.png` |
| `assets/img/winter-update.*` | `Screenshots/steam_header_1600x900.png` |
| `assets/video/…trailer-720p.mp4` | `Recordings/SantasLegacy_Trailer_1080p.mp4`, re-encoded 1920→1280, CRF 26, `+faststart` (77 MB → 12 MB) |
| `assets/img/icon-*`, `favicon.ico` | Drawn from scratch — a gold star over a snow drift, in the game's navy |

`tools/build_images.py` regenerates every image in `assets/img/` from the game
repo in one pass — re-shoot the screenshots, fix the two paths at the top of it
and run `python tools/build_images.py`. It needs Pillow. The trailer re-encode
is the one-liner recorded in the table above and needs ffmpeg.

---

© Pixel Studio. Site content and game assets are proprietary. Oleo Script and
Nunito are used under the SIL Open Font License.
