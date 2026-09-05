# Postmello website review and two local directions

## The central message

Postmello gives children an independent way to keep up with people they care about, before that means a phone and the expectations of texting. The positive promise is connection and creativity. The parent boundaries, calm pace, and business model make that promise credible.

The website should convey confidence through concrete product evidence and precise language. It should not imply market leadership through invented awards, family counts, ratings, endorsements, security certifications, or guarantees about developmental outcomes.

## What is already working

- The actual app artwork is distinctive: material paper, a mailbox, drawers, stamps, and the little courier bee. This is an identity worth preserving in both approaches.
- “A quiet place for letters” and “Texting can wait” already establish a memorable point of view.
- The real letters are stronger evidence of creative possibility than a generic feature illustration.
- The two blog posts explain unusually considered product decisions: preserving a letter as an object, making immediacy optional, protecting work, and keeping purchasing behind the adult boundary.
- The existing site has substantial, useful functionality: collection exploration, letter examples, the email correspondence explanation, safety information, pricing, and FAQs.

## What I would improve

1. **Make the product immediately concrete.** The first screen should establish kids, iPad, making letters, and approved friends. The existing poetic headline works best with a direct explanatory sentence.
2. **Move the parent case forward.** On the original page, the detailed rationale comes after the desk and collections tour; safety comes later still. Parents should understand why this exists and who can reach their child before considering decorative collections.
3. **Give the page a clearer hierarchy.** The original gives many sections a similar weight. A shorter narrative can let friendship, real creative work, and parent control stand out.
4. **Let the app carry the whimsy.** A composed adult-facing website can feel mature while preserving the handmade world in the artwork. The site need not imitate the entire desk interface to belong to the same brand.
5. **Explain the business model as part of trust.** The free desk is useful indefinitely. Membership buys capacity and collection discounts; collections are separate permanent purchases. Safety and letter limits are not upsells.
6. **Keep claims bounded.** Approval controls are concrete. “Completely safe,” unqualified encryption claims, or promises to prevent phone/social-media use would exceed the evidence. The goal of delaying that transition is an intention, not a measured outcome.

## Direction 1: evolution

`evolution/index.html` is a separate copy of the existing homepage. It reuses `/home.css` and all existing assets without editing them. `evolution/evolution.css` contains only the prototype overrides.

Changes:

- More direct hero copy: an iPad app for kids to write and draw letters to approved friends, with independence before a phone.
- The founder rationale and full existing safety section move immediately after the first product walkthrough.
- A tighter section rhythm and a distinct, quiet safety background improve hierarchy.
- The existing gallery, collection selectors, pricing, FAQs, testimonials, and page scripts are retained.

This is intentionally an evolution. It retains the original page's breadth and familiar warm identity. It is the lower-change option, although its overall length remains a tradeoff.

## Direction 2: fresh design

`new-direction/` is independently authored HTML, CSS, and JavaScript. It does not load either production stylesheet.

The design uses deep blue ink, the existing Postmello yellow wordmark, large editorial typography, and substantial areas of breathing room. A real handmade letter and the actual mailbox form the first image; the next product section shows the actual app, with four selectable desk screenshots.

The narrative is: friendship → creative independence → the actual experience → room to put it down → parent boundaries → family by email → founder rationale → the free and paid options.

The shorter page deliberately leaves deeper explanations to the existing safety pages and blog. It uses no invented social proof. The new FAQ is native HTML and works without JavaScript. The desk selector is a small progressively enhanced control; the original desk remains visible without JavaScript.

My preferred foundation is this second direction: it gives Postmello a more distinct and confident public identity, while the real art keeps it connected to the app. The first remains useful if continuity with the existing site is the priority.

## Product grounding

Read across both repositories, with particular attention to:

- `posty/docs/PRODUCT.md`: the correspondence model, approved friends, desk rituals, typewriter, family email, and product boundaries.
- `posty/docs/ARCHITECTURE.md`: native SwiftUI/PencilKit app, local-first drafts, immutable sent letter artifacts, server-enforced relationships, PIN-gated adult surfaces, and bidirectional email.
- `posty/docs/MONETIZATION.md` and `posty/pricing.json`: current free desk, Membership capacity, collection discounts, permanent collection ownership, founding annual prices, and the separation of child discovery from adult commerce.
- `posty/docs/CHILD_SAFETY.md`: structural and reactive moderation; this older document contains consent details superseded by the current product/architecture documents. It was not treated as current authority for those details.
- `posty/docs/recipes/DESK_STYLE_REFERENCE.md` and `ART_ASSET_MAP.md`: material consistency, desk personalities, and the distinction between source art and shipped assets.
- Website `README.md`, `brand.json`, homepage, stylesheets, safety copy, and both blog posts.

The app architecture matters here because its strongest marketing claims are implemented boundaries: approved relationships are enforced by the server, drafts are preserved locally, email senders are checked, and purchasing is an adult action. The website communicates the parent-facing consequence rather than the implementation detail.

## Scope and local use

All new files live under `_concepts/`. Neither repository's existing files were edited. No publication or production changes were made.

From the website repository, run:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/_concepts/` to compare both directions with the original. The prototype pages include a fixed comparison link for review; this is review navigation, not part of a proposed production page.

App Store links reuse `brand.json`'s configured listing; its availability was not independently verified. All blog, policy, support, and safety links intentionally lead to existing pages. Google Fonts require internet access; serif and sans-serif fallbacks are provided. Prices are a snapshot of `posty/pricing.json`, not a new authoritative pricing source.

## Validation

Static checks cover local assets and navigation targets, duplicate IDs, fragment destinations, JavaScript syntax, HTTP responses for the local previews, and checksums confirming that pre-existing website files are unchanged. The previews are responsive by construction with desktop and mobile breakpoints and reduced-motion handling. Interactive browser and visual layout testing have not been performed; these are local review prototypes.
