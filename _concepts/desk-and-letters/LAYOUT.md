# Layout refinement — September 5, 2026

This edits the current `desk-and-letters/` study, as requested. Production files and all earlier studies remain unchanged.

## Hero

The generated backdrop now shows a deeper desktop: the wall ends at approximately 62% of the composition and the front lip begins at 96%. The original pen-and-paper pile ends at 90%, leaving a clear margin before the edge. On smaller screens it ends at 89%.

The mountain landscape and its handwritten pages return to the left side of the desktop. The paper rack and mailbox occupy the back right; the writing stack occupies the middle foreground. Stamps sit in front of the rack, with stickers farther forward. Flat artwork is turned in its own plane, then compressed vertically, following the projection approach in the original website. Close contact shadows replace the impression of floating objects.

The drawer band uses the lower 280 pixels of the original 1613 × 1200 app screenshot, displayed through a CSS viewport. This preserves the actual rail, recessed shading, close drawer spacing, and five labeled fronts without regenerating or altering the source image.

## Section boundaries and letters

Fairy Glen has its own wood surface, rendered with `cover` and `no-repeat`. Connection at their pace, family email, the founder story, and FAQs each have a separate material boundary. Pricing and its related collections remain together.

The leafy drawing and typewritten letter return in a dedicated section after the app demonstration. Its heading is restored from the production website. The mountain letter appears in the hero and the paddleboarding letter remains beside the slower-connection explanation. All existing visible copy is preserved.

## Checks

HTML nesting, unique IDs, anchors, image alt text, JavaScript syntax, and 56 local resource responses passed. Source-geometry calculations at widths 320, 375, 768, 960, 1024, 1280, 1440, 1920, and 2560 verify that the writing stack and projected mountain letter sit between the back and front desk edges. Production and older-study checksums remain unchanged. These checks do not constitute rendered browser layout testing.

## Responsive proportions follow-up

- Small-screen hero copy now uses the same generated cream-wall artwork as the desk, replacing the cooler paper-grain background. The scene's empty upper wall blends into it.
- The drawer rail now repeats horizontally at a maximum source width of 900px. Its height is capped at approximately 156px; wide screens reveal additional drawers rather than enlarging the five-drawer screenshot. On screens below 900px, one five-drawer span fits the screen.
- The mailbox now uses the existing front-facing native render from `posty/samples/hero-kit/mailbox-mint-mail-flag-up.png`, copied unchanged to `assets/mailbox-front.png`. No new image generation was needed. Its visible base is farther onto the desk, at approximately 76% of the scene height. The paper stack and loose stamps were shifted to leave clearance around it.
- HTML, resources, script syntax, source geometry at eight viewport widths, and original-file preservation checks passed. No rendered browser testing was performed.

## Finite rail and scrolling navigation

The repeating rail was replaced with five original drawers in a centered cabinet capped at 900px wide. On wider screens the maple fascia extends to either side; the drawer count stays fixed.

The single navigation header is transparent over the opening wall and scrolls away naturally. An IntersectionObserver fixes it on a white background only when the entire opening has passed above the viewport. A ResizeObserver reserves its measured height in the opening and updates anchor clearance. Returning into the hero restores the transparent, scrolling header. The copy-review page retains its own independent header.

The footer label is now “Blog,” retaining the same `/blog/` destination. Header state transitions and responsive measurement passed a mocked runtime check; HTML and preservation checks passed. No rendered browser testing was performed.

## Drawers removed

Removed the hero drawer cabinet following the large-screen review. The opening now ends at the generated desktop’s wooden front edge. The navigation still returns after the opening passes. Actual app screenshots elsewhere continue to show the friend drawers.

## Larger hero objects and full-size example letter

The desktop mailbox is 50% wider, the paper rack 30% wider, and the writing stack 50% wider. Their positions reserve the left text column and maintain desk-edge clearance. The hero height is capped at 700px to avoid excess wall space at large widths. Mobile uses a separate arrangement with the writing stack between the upright objects.

The four-page mountain letter moved from the hero to the wider column of the real-letters showcase, replacing the typewritten example. Its original aspect ratio and artwork are preserved without perspective compression. Existing page copy is unchanged. Static markup, asset response, and source-geometry checks passed.

## Rendered large-screen review

Visually inspected the live page through the in-app browser at 3840 × 2160 and 2560 × 1440. The original 1320px composition looked undersized on the full-width desk. Above 1600px, the hero now grows to 1920px with proportionally larger typography and artwork; the header alignment grows with it. The wall background now covers the full width, removing the exposed side patches beside the header. Added a stylesheet revision query so the browser loads these changes instead of its cached copy.

Reinspected the updated screenshots at both sizes, then reset the temporary viewport override and checked the restored 1029 × 1063 preview. This is rendered visual review, replacing the earlier calculation-only assessment for these dimensions.

## Copy and complete desk screenshots

Reworked the three hero descriptions without “for kids” or an iPad-first definition, retaining the platform label beside the download badge. The default leads with writing and drawing to approved friends. Replaced “send a little piece of your day” and the childhood closing. Email copy explicitly covers a traveling parent who already has Postmello. Restored FAQ coverage for texting, adults, email, siblings, collection ownership, and privacy; the section now has ten questions.

Replaced the cropped desk exports with four complete 2732 × 2048 screenshots from the app repo’s `samples/app-store/raw/`, copied unchanged into this study. Removed the imposed image aspect ratio and updated the selector paths. Visually inspected full Seaside framing at 1920 × 1440, activated all four choices, and confirmed their common 1020 × 765 rendered dimensions. Restored the normal viewport and original selection afterward.

Both HTML pages, three consistent description options, ten FAQs, four screenshot URLs, and JavaScript syntax passed validation. Git reports no production-file changes.
