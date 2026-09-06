# Postmello — a furnished desk, with the original tagline

New local version: `desk-and-letters/`. The preferred fresh version in `creative-beginning/` remains unchanged, as do the evolved version and all other earlier studies.

## Hero copy

The headline returns to the original **A quiet place for letters.** The proposed younger-sounding headlines and the mechanical list of actions were discarded following the user's correction.

Three descriptions can be compared at `desk-and-letters/hero-options.html`. Each preview link changes only the hero description using a fixed, local list of options. The first description is the default:

1. Letters made with words, drawings, and beautiful stationery. A creative way for kids to connect on iPad, while phones and texting can wait.
2. An iPad app for thoughtful letters to friends and family. A creative way to stay connected, with more time before texting and a phone of their own.
3. A desk of their own on iPad, where ideas become letters. A way to connect at their pace, before the pull of texting, phones, and social media.

All 871 words in the main page after the hero match `creative-beginning/` exactly, including pricing, collection terms, testimonials, and the closing section. Changes to the description options are confined to this new version.

## Composition and materials

- The hero uses an empty cream wall and mint desktop, with room for live HTML text. The original mailbox and paper rack sit to the right. The pen, paper stack, stamps, and stickers sit lower on the work surface. The app's five named drawer fronts complete the desk below, at their original aspect ratio.
- On widths up to 60rem, the text flows above a separate desk scene. Copy and objects do not share that area.
- The generated plate is displayed through its upper 83%, ending at the maple front lip. The empty recess beneath it is replaced by a separate full-width strip of authentic drawer fronts, rather than stretching the fronts to fit the shallow recess.
- The desk demonstration uses painted mint. Fairy Glen and the sample letter share one continuous maple surface. Family correspondence and the founder story share a paper surface. Testimonials sit on a warmer surface, with the original note-paper artwork. Pricing and its FAQ share a single pale paper background. The closing returns to mint.
- The red mailbox mark, real app screenshots, collection icons, and stationery assets remain prominent.

## Asset provenance

All product objects are existing Postmello assets. No generated asset substitutes for an app screenshot or product object.

- Mailbox, rack, stack, stamps, and stickers: existing `assets/hero/` files used in the evolved site.
- Drawer fronts: copied unchanged from `/Users/pamihood/proj/posty/samples/hero-kit/drawers-row.png` to `desk-and-letters/assets/friend-drawers.png` (4164 × 588).
- Maple grain: copied unchanged from the previously imported app material in `creative-beginning/assets/app-maple-wood.jpg` to `desk-and-letters/assets/maple-wood.jpg`.
- New empty background plate: `desk-and-letters/assets/desk-backdrop.png` (1774 × 887). Generated once with the built-in OpenAI imagegen tool, using the original desk composite and drawer row as style references. The exact prompt is saved in `desk-and-letters/assets/desk-backdrop-prompt.txt`. The output was inspected and copied unchanged into the project. Its actual wall/table boundary is lower than requested; the layout accommodates the returned geometry.

## Validation

Static checks passed: all 54 referenced local resources returned HTTP 200; HTML nesting, unique IDs, anchors, image alt attributes, and CSS references are valid; JavaScript syntax checks passed. The three descriptions and preview query keys agree with their review page. Body-copy comparison found no changed words after the hero. Checksums confirmed all 177 original production files and all 31 preserved concept files are unchanged. The design index alone was updated to feature the new study.

The page is served at `http://127.0.0.1:8765/_concepts/desk-and-letters/`. Interactive browser testing and rendered layout inspection have not been performed.
