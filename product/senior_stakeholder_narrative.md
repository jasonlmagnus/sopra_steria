# Project Brief: The Persona Experience & Brand Hygiene Tool

## Why are we building this? The challenge of speaking to two different audiences.

Our initial objective was to answer a critical business question: "Does our digital presence truly resonate with our key customer personas?" As we dug into this, we uncovered a fundamental tension.

On one hand, our brand reputation—especially as a provider of secure, mission-critical IT systems—rests on a foundation of precision, consistency, and fault-free execution. Our web presence must reflect this with flawless **brand hygiene**. This is an objective, data-driven requirement.

On the other hand, resonating with a customer persona is a deeply subjective and emotional exercise. It's about understanding their specific frustrations, speaking their language, and building trust. This requires nuanced, qualitative insight.

Our challenge is that we need to serve both of these masters—the brand team's need for objective data and the marketing team's need for subjective insight—at the same time.

## Why did we pivot from the "Manus" (Pure AI) approach?

We initially tried to solve this using a powerful, general-purpose AI. The hypothesis was that we could teach it our complex audit rules and have it perform the entire analysis.

This approach failed for a clear reason: **we were using the wrong tool for the job.**

Large Language Models are brilliant at subjective, creative, and persona-based tasks. They can "feel" like a Chief Data Officer and tell you if your language is compelling. However, they are not deterministic calculators. They struggle to consistently apply rigid, multi-layered mathematical rules, which is exactly what a brand hygiene audit requires.

This led to unreliable scores, inconsistent results, high costs, and significant manual rework. We were forcing a creative artist to do a tax accountant's job, and the results were predictably poor.

## Our New Approach: A "Best of Both Worlds" Tool

Our new strategy is to build a purpose-built application that uses technology for its greatest strengths:

1.  **Code for the Audit:** We use deterministic Python code to handle the objective brand hygiene audit. It programmatically scrapes pages, checks for logos, finds taglines, and calculates scores based on fixed rules. It is 100% reliable, fast, and cheap.

2.  **AI for the Experience:** We use a targeted AI call to do what it does best: inhabit a persona. We provide it the context of a page and ask it to write a narrative report from the persona's point of view.

This hybrid approach gives us the reliability of a calculator and the insight of a human expert.

## Key Outputs & Their Value

From a single click, our new tool will produce two distinct, fit-for-purpose reports:

1.  **The Persona Experience Report (.md):** A rich, qualitative narrative for strategists and marketers. It answers questions like: "What was the IT Director's gut reaction to this page?" and "Based on this page, what is their likely next action and why?" This is our engine for driving more effective content and messaging.

2.  **The Brand Hygiene Scorecard (.md):** A quantitative, data-driven report for brand and web teams. It provides a clear, actionable scorecard showing exactly where a page is non-compliant with our brand standards. This is our tool for ensuring quality and consistency across our digital estate.

Finally, the tool synthesizes all of this information into a **Strategic Summary Report.** This report rolls up the individual scores into a single, weighted brand performance metric. More importantly, it uses AI to perform a thematic analysis across all the qualitative feedback, automatically identifying the most critical, recurring strengths and weaknesses in our digital messaging.

This gives us, for the first time, a repeatable, data-driven system for not only benchmarking our brand's performance but for gaining actionable, strategic insight into _how_ we can improve our connection with customers, one webpage at a time. It moves us from subjective opinion to a scalable, evidence-based brand management process.

## Final Considerations

This project has evolved from an R&D effort into a plan to build a core operational asset. By investing in this tool, we move from an unpredictable, expensive process to one that is reliable, fast, and cost-effective. Most importantly, it allows us to finally solve both critical business needs—protecting our brand's integrity and deepening our connection with our customers—without compromising on either.
