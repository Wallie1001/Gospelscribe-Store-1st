# Gospelscribe: Bible Journey Website

## Who I'm working with
Bryant (goes by Wallie too), founder and solo operator of **Gospelscribe**, a faith-based Christian streetwear brand (gospelscribe.com). He does NOT code. Explain every step in plain language, one step at a time, and tell him exactly what to click. He likes casual, fast, honest communication and pushback when there's a good reason.

## The store today
- Shopify store at gospelscribe.com (old domain gospelsb.com redirects)
- Print-on-demand fulfillment via Tapstitch, email via Klaviyo, affiliates via UpPromote (https://af.uppromote.com/Gospelscribe/register)
- Free shipping over $125
- Products, orders, checkout, Tapstitch, and Klaviyo must keep working. Never break checkout.

## The big idea
Every drop is built on a book of the Bible, to teach the Bible through clothing. The website should feel like stepping inside the Bible: cinematic and immersive, like Hound Archives (houndarchives.com, a custom-coded Shopify theme built like a video game), but the world is Scripture.

Structure:
1. **Opening**: dark screen, an oil lamp flickers on beside a closed Bible. "Open the book."
2. **Testament gate**: choose Old or New Testament. Old Testament is sealed ("Coming soon"). New Testament opens.
3. **Books**: Matthew is open; Mark, Luke, John sealed until their drops.
4. **The Matthew journey**: scroll through Jesus's life in story order. Each stop has a painted scene, scripture (KJV), what happened there, and the piece from that moment.
5. **Product pages**: verse, study note, sizes, add to bag. Immersive but buying stays dead simple.
6. **Ending**: the Great Commission, which sends people to shop, share, or join the ambassador program.

## The Book of Matthew drop (launching ~3 days from Sept 25, 2026)
Journey order (story order, not drop numbering):
| Stop | Scripture | Piece |
|---|---|---|
| Bethlehem | Matt 1:18–2:12 (key 1:23) | A Savior Is Born |
| The Wilderness | Matt 4:1–11 (key 4:4, red letter) | It Is Written |
| Sea of Galilee | Matt 14:22–33 (key 14:30) | Lord, Save Me |
| Golgotha / The Cross | Matt 27 (key 27:46, red letter) | NO product, just scripture |
| The Empty Tomb | Matt 28:1–10 (key 28:6) | He Is Not Here / He Has Risen |
| Mountain in Galilee | Matt 28:16–20 (key 28:19, red letter) | Go and Make Disciples |

Product descriptions (Bryant's own words) are in `prototype/matthew-journey.html` in the PIECES and STOPS data. Prices, garment types, colors, and product mockups are NOT decided yet; ask Bryant.

Possible bonus stop: his existing "Matthew 4:17" Black Hoodie ($64.99) fits between the Wilderness and Galilee. Not confirmed.

## Art direction (LOCKED)
**Dark oil painting**: Baroque chiaroscuro, candle-gold light on deep shadow, visible brushstrokes. Jesus's face stays out of frame or in shadow. All art generated in Higgsfield; the storm scene was used as the style reference for the rest.

Scene images (Higgsfield, 16:9, standard quality; re-render or upscale finals in high res):
- lamp: https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043255_99103f9a-5d85-466f-b1b1-6f8c2b224b35.png
- gate: https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043255_6a4834a6-ecca-497f-b3f2-07128e723c00.png
- bethlehem: https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043255_d3866415-a081-4475-b978-933fb9889170.png
- wilderness: https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043255_14c06e93-748c-45d1-bc58-371d537ddf9f.png
- galilee (storm): https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043103_094e58a1-5808-4b1a-a273-1d3c887c7b75.png
- cross: https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043255_145523c8-a0b8-4168-96b2-73b6dd09b4d5.png
- tomb: https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043255_06878797-da01-452c-a61a-472593287958.png
- mountain: https://d8j0ntlcm91z4.cloudfront.net/user_38hCSqRrQYUYpHFpLBY4eF0UnvE/hf_20260925_043255_696b7809-19c0-42ba-b84c-125a6d51793a.png

These links may block direct downloads. Best path: Bryant downloads them from Higgsfield, then they go into the Shopify theme's assets or Shopify Files.

## Palette
- Umber Black #15110E (background)
- Parchment #E8DCC4 (text, scripture)
- Candle Gold #C9A24D (wordmark, buttons, highlights)
- Red-Letter Crimson #8E1F1F / #A5282A (Jesus's words, Add to Bag)
- Smoke Bronze #6B5A48 (secondary text, lines)
- Scene lighting: Bethlehem midnight blue + starlight gold, Wilderness scorched ochre, Galilee storm slate/teal, Cross ash + deep crimson, Tomb dawn rose-gold, Mountain sunrise amber

Fonts: IM Fell English (display), IM Fell English SC (small caps labels), Cardo (body). Scripture is KJV.

## Rules
- Mobile first. Most traffic comes from Instagram and TikTok on phones. Animations must stay smooth; respect reduced motion.
- A "Skip to shop" shortcut is always visible. The journey is optional wow, never a wall.
- Keep Shopify handling products, cart, checkout, and Tapstitch orders. Build a custom theme or sections in Liquid, never a separate off-Shopify site.
- Always work on an UNPUBLISHED theme copy or a new page. Never edit the live theme directly without Bryant's OK.
- Bryant does all logins himself.

## Plan
**Phase 1: drop launch (next 3 days, don't overreach)**
Build the Matthew journey as a Shopify **section + page template** added to his CURRENT theme (not a full theme swap). Create a "Book of Matthew" page using it, and wire each stop to the real product pages and add-to-cart. Test on his phone via theme preview before publishing.

**Phase 2: after the drop**
Build the full custom Gospelscribe theme (opening, Testament gate, books, journeys, product pages, cart) and push it with Shopify CLI as an unpublished theme, then publish when ready.

## Still needed from Bryant
- Product descriptions (4 of 5 are just "."). He'll write them himself.
- Hi-res re-renders of the 8 paintings (optional, for desktop sharpness)
- Decision on the Matthew 4:17 Black Hoodie bonus stop

## Phase 1 status (built Sept 25, 2026)
- `theme/sections/gs-matthew-journey.liquid`: the whole journey (opening, gate, 6 stops, shop grid, product popup with real sizes/prices, add to bag via Shopify's cart). Everything is editable in the theme editor: scene images, products, text. Styles are scoped under `.gs-mj` so it can't restyle the rest of his theme.
- `theme/templates/page.matthew.json`: page template pre-filled with all 6 stops in Bryant's words.
- **Installed Sept 25 via the Shopify connector** (Admin API, no CLI):
  - Live theme: "cleanslatepro-v1-10-10-licensed" (Clean Slate Pro, OS 2.0, id 153488130117). NOT touched.
  - Working copy: **"Clean Slate + Matthew Journey"** (id 153989251141, unpublished) holds both files. Upload method: `themeFilesUpsert` with body type URL pointing at the raw GitHub file at a pinned commit (repo is public), then verify `checksumMd5` matches local.
  - Bryant's other unpublished themes ("Clean slate REMAKE MATTHEW", "Horizon") are his. Leave them alone.
  - The 8 Higgsfield paintings were imported into Shopify Files as `gs-matthew-<scene>.png` (1344×752, standard quality) and referenced in the template as `shopify://shop_images/gs-matthew-<scene>.png`. Swap in hi-res re-renders later using the same filenames (fileCreate with duplicateResolutionMode REPLACE).
  - Page "The Book of Matthew" (/pages/book-of-matthew, id 122870792261) was created hidden, then made **visible** Sept 25 (a hidden page 404s even in theme preview). Template suffix `matthew`.
- **Home page = the journey** (Bryant's call, Sept 25): the copy's `templates/index.json` has `matthew_journey` first, and all his original home sections follow in the same order, unchanged. The copy's header has `transparent_on_home: true`, so the logo floats over the lamp scene on home. `theme/templates/index.json` in the repo is a snapshot. If Bryant edits home in the editor, Shopify's copy is the truth, so re-read it before overwriting.
- Checksum trick: Shopify stores JSON templates exactly as uploaded. When it has normalized a file, its md5 matches compact JSON with `/` escaped as `\/` (no comment header).
- The connector cannot publish themes or write to the live theme. Bryant clicks Publish himself.
- Draft products don't appear on the storefront, so the page can't show them. Products must be Active (or Unlisted) for the journey to show them and add them to the bag.
- Products (created by Bryant Sept 25, vendor ODMPOD/Tapstitch, all $64.99, Color + Size variants), linked in the template by handle:
  - Bethlehem: `a-savior-is-born-zip-up`
  - Wilderness: `it-is-written-hoodie`
  - Galilee: `lord-save-me-hoodie`
  - Tomb: `he-has-risen-hoodie`
  - Mountain: `go-and-make-disciples-hoodie`
- **Drop day is Sept 27, 2026.** Bryant tested publishing on Sept 25, then unpublished on purpose; Clean Slate stays live until the 27th. The 5 Matthew hoodies are already ACTIVE, so they can show in the live shop early.
- **Launch day checklist**:
  1. Bryant publishes "Clean Slate + Matthew Journey" (Themes → Publish).
  2. ~~Make the page visible~~: done Sept 25 at Bryant's request (the preview 404ed while it was hidden). Its body reads "opens soon…"; only the live Clean Slate theme shows that body, the journey template ignores it.
  3. Products set to Active if they're still Unlisted.
  4. Add "The Book of Matthew" to the main menu.
  - Before publishing, check whether the live theme changed since Sept 25. If it did, those changes need copying to the working copy first.

## Gospelscribe theme layer (Sept 25, evening), replacing Clean Slate's look
Bryant wanted no Clean Slate look at all. Everything visible on the working copy (id 153989251141) is now ours:
- `layout/theme.liquid` is Clean Slate's layout with its static sections removed (announcement-bar, countdown-timer, search-drawer, landing-page, newsletter-popup, music-player, loading-screen), plus `{% render 'gs-head' %}` and `<main id="MainContent">`. Clean Slate's css-variables/theme-core snippets still load so any leftover Clean Slate pages keep working.
- Header group: `gs-announcement` + `gs-header`. Footer group: `gs-footer`.
- Home (`index.json`): `gs-landing` (lamp → Testament gate → **the Gospels** → Matthew opens the journey page; "Or enter the shop" / "Skip to shop" dismiss it into the home page. Bryant pushed back when New Testament went straight to the home page: **the journey is the star**, keep it that way; once per visit via sessionStorage `gs-entered`; `?landing=1` replays it; shows as a normal section in the editor), then Matthew banner, collection list, Best Sellers, Wear the Word banner, New Arrivals, features, ambassador, Judge.me reviews (`gs-apps`), Klaviyo newsletter (form RGpwcS).
- Section library for Bryant: gs-collection, gs-collection-list, gs-rich-text, gs-image-banner, gs-image-text, gs-features, gs-newsletter, gs-apps.
- Product/collection/cart pages: gs-main-product (AJAX add + dynamic checkout + @app blocks; optional metafield custom.scripture), gs-main-collection, gs-main-cart (free shipping bar at $125).
- Shared styles: `assets/gs-base.css` (tokens + .gs components). Placeholder class is `.gs-placeholder` (the journey owns `.gs-ph`). The journey CSS is scoped under `.gs-mj`.
- Cart count: any section dispatches `document` event `gs:cart` {count}; the header updates `[data-gs-cart-count]`.
- Matthew page (`page.matthew.json`): opening and gate are both **off** (Bryant: repeating the lamp after the landing felt wrong), so it opens straight on Bethlehem. When the page has no opening, the first stop's painting loads eagerly.
- Still Clean Slate inside (they get our header/footer/background): search results, Our Story / Contact / Charity pages, 404, blog, account.
- Gotcha: Shopify silently rejected a section whose range setting had only 2 values (min 1, max 2). Use a select instead. After every themeFilesUpsert, check that each file exists and its checksumMd5 matches.
- Local render harness (liquidjs + Playwright) lived in the session scratchpad and was not committed.
