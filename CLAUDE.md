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
- Prices, garment types, and colors for the 5 Matthew pieces
- The 5 products created in Shopify (drafts are fine) so the stops can link to them
- Product mockups/photos
- The 8 scene images downloaded from Higgsfield

## Phase 1 status (built Sept 25, 2026)
- `theme/sections/gs-matthew-journey.liquid`: the whole journey (opening, gate, 6 stops, shop grid, product popup with real sizes/prices, add to bag via Shopify's cart). Everything is editable in the theme editor: scene images, products, text. Styles are scoped under `.gs-mj` so it can't restyle the rest of his theme.
- `theme/templates/page.matthew.json`: page template pre-filled with all 6 stops in Bryant's words.
- **Installed Sept 25 via the Shopify connector** (Admin API, no CLI):
  - Live theme: "cleanslatepro-v1-10-10-licensed" (Clean Slate Pro, OS 2.0, id 153488130117). NOT touched.
  - Working copy: **"Clean Slate + Matthew Journey"** (id 153989251141, unpublished) holds both files. Upload method: `themeFilesUpsert` with body type URL pointing at the raw GitHub file at a pinned commit (repo is public), then verify `checksumMd5` matches local.
  - Bryant's other unpublished themes ("Clean slate REMAKE MATTHEW", "Horizon") are his. Leave them alone.
  - The 8 Higgsfield paintings were imported into Shopify Files as `gs-matthew-<scene>.png` (1344×752, standard quality) and referenced in the template as `shopify://shop_images/gs-matthew-<scene>.png`. Swap in hi-res re-renders later using the same filenames (fileCreate with duplicateResolutionMode REPLACE).
  - Page "The Book of Matthew" (/pages/book-of-matthew, id 122870792261) was created **hidden**, using template suffix `matthew`.
- The connector cannot publish themes or write to the live theme. Bryant clicks Publish himself.
- Draft products don't appear on the storefront, so the page can't show them. Products must be Active (or Unlisted) for the journey to show them and add them to the bag.
- As of Sept 25 none of the 5 Matthew pieces exist in Shopify yet. The stops show "Coming soon" cards until products are picked.
