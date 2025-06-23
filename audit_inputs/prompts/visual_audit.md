task: "Run a visual brand hygiene audit"

reference_assets - see PDF

instructions:

- Crawl and capture screenshots (desktop and mobile) of each URL.
- Analyze each page for:
  - Logo presence, correct variant, placement
  - Color palette usage (detect and compare primary colors)
  - Typography match (via OCR and visual inference)
  - Layout structure vs template
  - Image quality and alignment with brand style
- Flag and annotate any violations.
- Score visual hygiene 0-10 using these thresholds:
  - 0–3 = Missing/broken/off-brand
  - 4–5 = Basic presence, inconsistent
  - 6–7 = Competent but generic
  - 8–9 = Strong and consistent
  - 10 = Exceptional, fully aligned
- Apply gating rules:
  - Missing logo: cap at 3
  - Off-palette color: -2
  - Low-res images: -2
- Output:
  - Per-page visual hygiene score
  - Annotated screenshots (bounding boxes, notes)
  - Table of visual issues and fix suggestions
  - Section summary: “Visual Brand Score Tables”, “Consistency Check”, “Fix List”

URLS - audit all please

Tier 1 - Brand Positioning (5 URLs)
https://www.soprasteria.nl/
https://www.soprasteria.be/
https://www.soprasteria.com/
https://www.soprasteria.com/about-us/corporate-responsibility
https://www.soprasteria.com/about-us/history
Tier 2 - Value Propositions (5 URLs)
https://www.soprasteria.be/whatwedo/data-ai/data-science-and-ai/the-future-of-generative-ai
https://www.soprasteria.be/whatwedo/digital-themes/deliver-flexible-always-on-performance/cloud-infrastructure-platforms/sopra-steria-transformation-services-for-microsoft-azure
https://www.soprasteria.be/whatwedo/management-digital-transformation-consulting/services-operations-automation
https://www.soprasteria.be/industries/financial-services
https://www.soprasteria.be/industries/industry-retail-logistics-telecom-media
Tier 3 - Functional Content (5 URLs)
https://www.soprasteria.nl/newsroom/press-releases/details/welcome-to-the-future-of-innovation
https://www.soprasteria.nl/newsroom/press-releases/details/sopra-steria-next-predicts
https://www.soprasteria.nl/newsroom/blog
https://www.soprasteria.nl/newsroom/blog/details/interacting-with-large-language-models
https://www.soprasteria.nl/newsroom/blog/details/ecosystems-yes-please-but-how-can-we-trust-each-other
