# Someplace — Clothing Line Spec

**Someplace** is a premium, "vibey" resort/travel + swimwear brand for men &
women. Everything is **made-to-order, fulfilled via Printful**, sold on
**Shopify** (store `someplace-8dg8wmip`, USD). Brand promise:
*"Resort-luxe for nomadic travelers."*

> Destinations (Marrakech / Bali / Lisbon / Tulum) are a **lookbook /
> photography device only**. They are NOT baked into the brand UI or the
> garment prints. Colorways are the merchandising "drops"; the destination
> is just where the lookbook was shot.

## Fulfillment model — important

All-over-print (AOP) pieces use a **white base**; the colour is part of the
print file, so there is **no fabric-colour variant**. That means:

- **Each colorway = its own Printful sync product.** (e.g. "The Beach Dress —
  Sun" and "The Beach Dress — Tide" are two separate Printful products.)
- On Shopify, **Size is the only product option** for AOP pieces.
- Embroidered (Camp Cap) and blank/printed-label pieces (Travel Tee) follow
  the catalog product's normal variant model.

Printful is already connected to the Someplace Shopify store, so creating a
Printful **sync product** auto-pushes it to Shopify with rendered mockups.
All products are set to **DRAFT** in Shopify for review before launch.

---

## Printful identifiers (verified)

- Printful store: **"Someplace" id `18371850`** (the other store "Issue"
  id 18364191 is NOT ours).
- API base `https://api.printful.com`, header `Authorization: Bearer <token>`.
- Mockup-generator **and** `/store/*` endpoints REQUIRE header
  `X-PF-Store-Id: 18371850`.

### Reference: AOP Unisex Button Shirt (catalog id 659) — verified
Used by the flagship Resort Shirt, the Linen-look Shirt and the Camp Shirt.

- Placements: front, back, sleeve_right, sleeve_left, details, inside_yoke,
  label_inside.
- Printfiles: **449 = 5700×7500 @150dpi (cover)** for front/back/details;
  **450 = 5700×3000** for sleeves/inside_yoke; **64 = 375×150** inside label.
- 11 size variants (all White base):

  | variant id | size | variant id | size |
  |-----------:|:-----|-----------:|:-----|
  | 17117 | 2XS | 17121 | XL  |
  | 17118 | XS  | 17122 | 2XL |
  | 17119 | S   | 17123 | 3XL |
  | 16400 | M   | 17124 | 4XL |
  | 17120 | L   | 17125 | 5XL |
  |       |     | 17126 | 6XL |

---

## The line (~28 SKUs). Prices USD, premium resort positioning.

### Women
| Product | Printful product | Catalog id | Price |
|---|---|---:|---:|
| The Beach Dress | AOP T-Shirt Dress | 514 | $98 |
| The Skater Dress | AOP Skater Dress | 315 | $118 |
| The Bodycon | AOP Bodycon Dress | 198 | $108 |
| The Skater Skirt | AOP Skater Skirt | 314 | $78 |
| The Beach Tank | AOP Women's Tank Top | 202 | $52 |
| The Travel Tee | Bella+Canvas 3001 Unisex Staple Tee | 71 | $42 |

### Women · Swim
| Product | Printful product | Catalog id | Price |
|---|---|---:|---:|
| The One-Piece | AOP One-Piece Swimsuit | 272 | $98 |
| High-Waist Bikini Top | AOP Recycled Padded Bikini Top | 469 | $48 |
| High-Waist Bikini Bottom | AOP Recycled High-Waisted Bikini Bottom | 470 | $44 |
| String Bikini Top | AOP Recycled Padded String Bikini Top | 668 | $46 |
| String Bikini Bottom | AOP Recycled String Bikini Bottom | 669 | $42 |

### Men
| Product | Printful product | Catalog id | Price |
|---|---|---:|---:|
| The Resort Shirt (flagship, camp collar) | AOP Unisex Button Shirt | 659 | $108 |
| The Linen-look Shirt | AOP Unisex Button Shirt (textured solid print) | 659 | $98 |
| The Beach Tank | AOP Men's Tank Top | 276 | $54 |
| The Resort Short | AOP Unisex Athletic Shorts | 330 | $72 |
| The Swim Trunk | AOP Recycled Swim Trunks | 571 | $78 |
| The Travel Tee | Bella+Canvas 3001 | 71 | $42 |
| The Camp Cap | Yupoong 6245CM Classic Dad Hat (embroidered) | 206 | $38 |

### Unisex / Outerwear
| Product | Printful product | Catalog id | Price |
|---|---|---:|---:|
| The Camp Shirt | AOP Unisex Button Shirt | 659 | $108 |
| The Bomber | AOP Unisex Bomber Jacket | 390 | $148 |
| The Windbreaker | AOP Men's Windbreaker | 615 | $138 |
| The Lounge Hoodie | AOP Recycled Unisex Hoodie | 388 | $98 |
| The Sweatpant | AOP Recycled Men's Joggers | 400 | $88 |

### Accessories
| Product | Printful product | Catalog id | Price |
|---|---|---:|---:|
| The Bucket Hat | AOP Reversible Bucket Hat | 654 | $42 |
| The Beach Towel | Beach Towel | 259 | $58 |
| The Beach Bag | AOP Large Tote Bag w/ Pocket | 274 | $54 |
| The Tote | AOP Tote Bag | 84 | $34 |

**Launch plan:** Core + **Marrakech** colorway first; then Bali / Lisbon /
Tulum drops.

---

## House print system (apply to AOP pieces — NOT location-themed)

Generate at each product's printfile dimensions
(`GET /mockup-generator/printfiles/{id}` with the store header).

| Print | Description |
|---|---|
| **Sun** | Tangerine concentric arcs on bone |
| **Palm** | Olive/bone fronds + sun discs |
| **Tide** | Cyan wavy lines on cream |
| **Terrazzo** | Sand + multicolour specks |
| **Tile** | Ink + tangerine diamonds |
| **Dot** | Clay + bone |
| **Stripe** | Bone/ink awning stripe |

**House solids:** sand `#cdbba0`, olive `#9aa68f`, clay `#c0917e`, ink `#33302b`.

---

## Brand design tokens (for storefront theme)

- Ink `#221d17`, Paper/bone `#f4f0e8`, Canvas `#e7e2d8`, Tile bg `#ece5d8`,
  Border `#ddd5c4`, Body text `#6b6356`, Muted `#8a8170`.
- Accent (themeable) Tangerine `#ff5a36` (alts: hot pink `#ff2e88`, lime
  `#9be021`, cyan `#15c7d6`, clay `#b75e39`). Pop / `NEW` badge =
  Acid-lime `#9be021` (fixed).
- Type: **Bricolage Grotesque** (700/800, sentence case, tight tracking,
  lh .85–.9) for display; **Archivo** (400–700) for UI/body. Kickers:
  Archivo ~11px, .18–.24em, uppercase, accent/muted.
- Square everything (no border-radius), no content shadows, flat editorial.
- Page max-width 1280, 32px gutters. Grids: home/related 4-col, collection
  3-col, gap 22px. Tiles 3/4; PDP main 4/5; thumbs 1/1.
- Wordmark "someplace": Bricolage 800, lowercase, **rotated 180°**.
- Marquee: accent band, translateX 0→-50%, 30s linear infinite, `✸` separators.

---

## Shopify collections

New arrivals · Most wanted · Shop by piece (Shirts / Dresses / Swimwear /
Accessories) · Beach dresses & layers · Men · Women · Swim · Unisex ·
(destination capsules optional).

## Build sequence

1. Recreate this spec ✅
2. Resolve artwork hosting (public URL Printful can fetch)
3. Validate the Printful pipeline end-to-end on product 659 (Resort Shirt)
4. Create the full line as Printful sync products on store 18371850 (DRAFT)
5. Build the three theme templates (Home / Collection / Product)
