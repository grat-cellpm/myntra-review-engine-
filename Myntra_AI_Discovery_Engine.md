# Myntra AI-Powered Discovery Engine

## 1. Problem Statement

Fashion-shopping platforms such as Myntra have millions of users who discover products, shortlist them, and add products to their Wishlist, but a significant portion of wishlisted products do not convert into purchases.

The core problem is not simply a lack of product interest. Users may like a product but still postpone purchase because of unresolved uncertainty around price, fit, size, quality, reviews, comparison with alternatives, styling, occasion, or other factors.

The objective is to build an AI-powered Discovery Engine that analyzes large-scale public user feedback to identify, quantify where possible, and compare the major behavioral problems and unmet needs that may influence Wishlist-to-Purchase conversion.

The system must go beyond basic sentiment analysis or review summarization. It must convert raw user conversations into structured behavioral insights and ranked product opportunity areas.

### Business Goal

Identify the highest-impact user problems that can potentially improve:

**Wishlist → Purchase Conversion**

A target business metric for the project is:

**Increase the percentage of wishlisted products that are purchased within 30 days of being added to the Wishlist.**

---

# 2. Core Research Questions

The engine must help answer:

1. Why do users add fashion products to their Wishlist?
2. What prevents wishlisted products from eventually being purchased?
3. What uncertainty remains after users identify a product they like?
4. What causes users to postpone a purchase?
5. How do users compare multiple shortlisted products?
6. What information do users seek outside Myntra before purchasing?
7. What role do price, fit, size, styling, occasion, reviews, quality, and social validation play?
8. When is a Wishlist used as genuine purchase intent versus simple bookmarking?
9. What unmet needs repeatedly appear across user conversations?
10. Which opportunity areas have the strongest potential relationship with Wishlist-to-Purchase conversion?

---

# 3. Scope of Version 1

## Data Sources

Version 1 should focus on:

* Google Play Store reviews for Myntra
* Apple App Store reviews for Myntra
* Reddit discussions relevant to Myntra and online fashion shopping

Do NOT make YouTube comments, survey/interview ingestion, or other social platforms part of the initial data-collection pipeline.

The architecture should still be modular so additional sources can be added later.

---

# 4. High-Level Architecture

```text
                    ┌──────────────────────┐
                    │     DATA SOURCES     │
                    ├──────────────────────┤
                    │ Google Play Reviews  │
                    │ Apple App Reviews    │
                    │ Reddit Discussions   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  DATA INGESTION      │
                    │  / COLLECTOR LAYER   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ RAW REVIEW DATABASE  │
                    │                      │
                    │ Original text        │
                    │ Source               │
                    │ Rating               │
                    │ Date                 │
                    │ Review ID            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ CLEANING &           │
                    │ NORMALIZATION        │
                    ├──────────────────────┤
                    │ Deduplication        │
                    │ Language detection   │
                    │ Relevance filtering  │
                    │ Text normalization   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     GROQ AI ENGINE   │
                    ├──────────────────────┤
                    │ Intent Detection     │
                    │ Wishlist Intent      │
                    │ Purchase Intent      │
                    │ Pain Point Detection │
                    │ Uncertainty          │
                    │ Purchase Barriers    │
                    │ Comparison Behavior  │
                    │ Root Cause           │
                    │ User Segment         │
                    │ Opportunity Mapping  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ STRUCTURED INSIGHTS  │
                    │ DATABASE             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ OPPORTUNITY ENGINE   │
                    ├──────────────────────┤
                    │ Frequency            │
                    │ User Impact          │
                    │ Purchase Relevance   │
                    │ Evidence Strength    │
                    │ Opportunity Score    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ ANALYTICS DASHBOARD  │
                    └──────────────────────┘
```

---

# 5. Data Collection Layer

Build independent source adapters so each data source can be managed separately.

```text
Collectors
│
├── GooglePlayCollector
├── AppStoreCollector
└── RedditCollector
```

The collector must preserve the original user content.

Do NOT replace the original review with an AI summary.

Each collected record must retain source traceability.

## Raw Review Schema

```text
review_id
source
source_url
original_review
rating
review_date
collected_at
language
country
app_version
author_identifier
```

Where a field is unavailable from a source, store null rather than inventing information.

---

# 6. Data Processing Layer

Before AI analysis:

### Cleaning

* Remove exact duplicates
* Remove obvious spam
* Normalize whitespace
* Preserve the original review text
* Detect language
* Mark irrelevant reviews

### Relevance Classification

Each review should be classified as:

```text
Relevant to fashion shopping
Not relevant
Unclear
```

A review should be analyzed for the Discovery Engine only when it contains meaningful information related to shopping behavior, product discovery, purchase decisions, Wishlist behavior, or relevant shopping friction.

---

# 7. AI Analysis Engine

Use **Groq API** as the primary LLM inference layer.

The AI engine should analyze each relevant review independently.

## Required AI Output

### Sentiment

```text
positive
neutral
negative
mixed
```

Sentiment is supplementary and must NOT be the primary output.

### User Intent

Examples:

```text
discovery
consideration
wishlist
purchase
postponed_purchase
comparison
alternative_search
complaint
return
```

### Wishlist Intent

Classify:

```text
genuine_purchase_intent
future_purchase_intent
price_watch
comparison_shortlist
bookmarking
inspiration
unclear
not_wishlist_related
```

### Purchase Barrier

Detect one or more:

```text
price
discount_expectation
fit
size
quality
reviews
trust
comparison
alternative_product
styling
occasion
shipping
returns
availability
decision_overload
lack_of_information
other
```

### Uncertainty

Identify the unresolved question in the user's mind.

Examples:

```text
Will this fit me?
Is this price worth paying?
Is the quality good?
Will this look good on me?
Is there a better alternative?
Can I trust the reviews?
Should I buy now or wait?
```

### Comparison Behavior

Detect:

```text
no_comparison
comparing_products
comparing_prices
comparing_brands
comparing_platforms
alternative_found
unclear
```

### Root Cause

The AI must infer the underlying reason behind the behavior.

Example:

```text
Observed behavior:
User postpones purchase.

Root cause:
User lacks confidence that the current price is the best price.
```

### Opportunity Area

Map the review to a broader opportunity category.

Examples:

```text
Price Confidence
Fit Confidence
Review Trust
Product Comparison
Alternative Discovery
Styling Confidence
Occasion-Based Decision Support
Wishlist Re-engagement
Product Information
Purchase Timing
```

### Evidence Confidence

Return:

```text
high
medium
low
```

---

# 8. Structured AI Output

For every analyzed review, save:

```json
{
  "review_id": "...",
  "relevance": "relevant",
  "sentiment": "positive",
  "user_intent": "postponed_purchase",
  "wishlist_intent": "genuine_purchase_intent",
  "purchase_barriers": [
    "price",
    "fit"
  ],
  "uncertainties": [
    "price confidence",
    "size confidence"
  ],
  "comparison_behavior": "comparing_products",
  "alternative_found": true,
  "root_cause": "User likes the product but lacks confidence in price and fit.",
  "opportunity_area": "Purchase Confidence",
  "confidence": "high"
}
```

The exact schema can be implemented as database fields rather than JSON if preferred.

---

# 9. Aggregation Engine

The system must aggregate individual review-level insights into opportunity-level insights.

For each opportunity area calculate:

```text
mention_count
mention_percentage
source_count
rating_distribution
supporting_reviews
affected_segments
purchase_barrier_frequency
uncertainty_frequency
```

Example:

```text
Opportunity: Fit Confidence

Relevant conversations: 1,200
Mentions: 310
Mention rate: 25.8%

Primary uncertainty:
"Will this fit me correctly?"

Common related barriers:
- inconsistent sizing
- unclear reviews
- lack of body-fit information
- uncertainty about return consequences
```

---

# 10. Opportunity Scoring

The engine must compare opportunity areas rather than only listing them.

Create an opportunity score using:

```text
Opportunity Score =
Frequency
× User Impact
× Purchase Relevance
× Evidence Strength
```

Normalize the final score to 0–10.

The weights should be configurable.

Recommended starting weights:

```text
Frequency             30%
User Impact            25%
Purchase Relevance    30%
Evidence Strength     15%
```

The dashboard must show both the score and the underlying dimensions so the ranking is transparent.

---

# 11. Opportunity Comparison

Example output:

```text
┌────────────────────────┬──────────┬────────┬────────┬─────────┐
│ Opportunity            │ Frequency│ Impact │ Relev. │ Score   │
├────────────────────────┼──────────┼────────┼────────┼─────────┤
│ Price Confidence       │ 31%      │ High   │ High   │ 8.7     │
│ Fit Confidence         │ 26%      │ High   │ High   │ 8.5     │
│ Product Comparison     │ 19%      │ High   │ High   │ 7.9     │
│ Review Trust           │ 13%      │ Medium │ High   │ 6.8     │
│ Styling Confidence     │ 9%       │ Medium │ Medium │ 5.9     │
└────────────────────────┴──────────┴────────┴────────┴─────────┘
```

These numbers are illustrative only. The application must calculate actual values from collected data.

---

# 12. Dashboard Requirements

Build a clean web dashboard with these sections:

## Dashboard Overview

Show:

* Total reviews collected
* Reviews by source
* Relevant reviews
* Reviews analyzed
* Top opportunity areas
* Top purchase barriers
* Top uncertainties
* Opportunity scores

## Review Explorer

Allow users to:

* Search reviews
* Filter by source
* Filter by rating
* Filter by date
* Filter by opportunity
* Filter by purchase barrier
* Filter by user intent
* Open the original review

The original review must always remain visible.

## Review Detail

Show:

```text
Original Review
Source
Rating
Date

AI Analysis
Intent
Wishlist Intent
Purchase Barrier
Uncertainty
Comparison
Root Cause
Opportunity
Confidence
```

## Opportunity Explorer

For every opportunity show:

```text
Opportunity name
Opportunity score
Frequency
Percentage
User impact
Purchase relevance
Evidence strength
Affected behavior
Root causes
Representative original reviews
Source breakdown
```

## Opportunity Comparison

Allow side-by-side comparison of opportunity areas.

---

# 13. Evidence Traceability

Every AI-generated insight must be traceable back to original user evidence.

For example:

```text
Opportunity:
Fit Confidence

Evidence:
├── Google Play Review #123
├── Google Play Review #456
├── Reddit Post #789
└── Reddit Comment #901
```

Clicking an evidence item should open the original review/conversation stored by the system.

This is mandatory because the engine is being used for user research.

---

# 14. Technology Stack

Use this recommended stack:

### Frontend

```text
React
Next.js
TypeScript
Tailwind CSS
Recharts
```

### Backend

```text
Python
FastAPI
```

### AI

```text
Groq API
Structured JSON output
LLM-based classification/extraction
```

### Database

Use:

```text
PostgreSQL
```

Store both raw reviews and structured AI analysis.

### Data Processing

```text
Python
Pandas
Pydantic
```

### External APIs / Data Collection

Use official APIs or permitted public data-access methods where available.

Do not make the system dependent on brittle HTML scraping when an official API is available.

### Development Environment

```text
Antigravity
Git
.env configuration
```

---

# 15. Important Product Requirements

The system must:

1. Preserve original review text.
2. Never overwrite raw review data with AI-generated text.
3. Keep source and review IDs for traceability.
4. Separate raw data from AI-derived data.
5. Allow re-running AI analysis without recollecting data.
6. Allow adding new sources later.
7. Avoid duplicate reviews.
8. Show evidence behind every major opportunity.
9. Distinguish factual extraction from AI inference.
10. Show actual calculated frequencies instead of invented numbers.

---

# 16. Future Extensibility

Design the architecture so these can be added later:

```text
YouTube Comments
Survey Data
Interview Transcripts
Instagram / Other Social Sources
```

These are NOT required for Version 1.

The architecture should use a generic source interface:

```text
Source → Collector → Raw Data → Normalizer → AI Analyzer
```

so additional sources can be plugged in later.

---

# 17. Expected Final Output

The finished application should answer:

### What are users doing?

Example:

> Users save products they like but postpone purchase.

### Why are they doing it?

Example:

> They want to compare options or wait until they feel more confident about price and fit.

### What prevents conversion?

Example:

> Price uncertainty and fit uncertainty are recurring barriers.

### How large is the problem?

Example:

> Fit-related uncertainty appears in X% of relevant conversations.

### Which opportunity is strongest?

Example:

> Fit Confidence scores highest because it is frequent, high-impact, directly related to purchase hesitation, and supported by evidence from multiple sources.

---

# 18. Definition of Done

The MVP is complete when:

* Myntra Google Play reviews can be collected.
* Myntra App Store reviews can be collected.
* Reddit data can be collected through a permitted access method.
* Original review/conversation text is stored.
* Reviews can be cleaned and deduplicated.
* Groq analyzes each relevant review.
* Structured behavioral attributes are stored.
* Opportunity areas are automatically generated.
* Opportunity areas are quantified.
* Opportunity areas are ranked and compared.
* Dashboard displays the analysis.
* Every opportunity can be traced back to original user evidence.
* No statistics are fabricated.
* The application can support additional data sources later.

## Core Principle

Do NOT build a simple sentiment-analysis or review-summary application.

Build an:

**AI-powered User Research & Opportunity Discovery Engine**

that converts:

**Original User Conversations → Behavioral Insights → Quantified Problems → Opportunity Areas → Evidence-backed Product Opportunities**

with a specific focus on improving:

**Wishlist-to-Purchase Conversion.**

---

## Discovered Opportunity Areas (Wishlist Intent)

### 🎯 1. Genuine Purchase Intent (High Risk of Cart Abandonment)
*These are friction points experienced by users who actually intended to buy their wishlisted items right away but hit a barrier.*

- **Delivery Speed (8 mentions):** Poor delivery logistics and inaccurate shipping estimates are a primary reason customers hesitate to complete purchases.
- **Delivery Reliability (8 mentions):** Customers fear missing or delayed items compounded by ineffective customer support systems.
- **Refund Transparency (4 mentions):** The app misreporting refund status creates severe trust issues.
- **Authenticity Assurance (3 mentions):** Uncertainty around whether premium items are genuine.
- **Delivery Transparency (2 mentions):** Lack of transparent communication when a fulfillment error occurs.

### 💰 2. Price Watch (Waiting for a Drop)
*These barriers affect users who wishlisted an item specifically to track its price over time.*

- **Competitive Pricing (1 mention):** General high pricing compared to expectations.
- **Price Transparency (1 mention):** Inconsistent or surprisingly high pricing shifts.
- **Quality-Price Alignment (1 mention):** Customers are waiting for the price to drop to a level they feel matches the perceived product quality.
- **Offer Availability (1 mention):** Customers are waiting explicitly for promotional offers to become active.

### ⚖️ 3. Comparison Shortlist
*Users saving items to compare against other options on Myntra or competing platforms.*

- **Filter Reliability (1 mention):** Technical issues with the app's filter functionality make it difficult for users to confidently compare and narrow down their options.

### 🔖 4. Bookmarking / Inspiration
*Users saving items for general style inspiration or future reference without immediate intent to buy.*

- **App Experience Excellence (2 mentions):** Positive experiences that lean into inspiration and easy browsing.
- **Brand Affinity (2 mentions):** Excellent brand perception driving wishlist saves.
- **Product Detail Transparency (1 mention):** Lack of detailed product information that prevents casual browsers from moving deeper into the funnel.

---

## UI Mockup: Opportunity Area

```text
┌──────────────────────────────────────────────────────────────────────┐
│              AI WISHLIST OPPORTUNITY DISCOVERY                     │
│                 Product: [Selected Product]                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  500 Reviews Analyzed     326 High-Quality     7 Opportunities      │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  OPPORTUNITY AREAS                                                   │
│                                                                      │
│  #1  Purchase Uncertainty                         HIGH IMPACT 🔴    │
│      118 reviews · 23.6%                                             │
│      ████████████████████████                                        │
│                                                                      │
│  #2  Price & Value Hesitation                     HIGH IMPACT 🔴    │
│       82 reviews · 16.4%                                             │
│      █████████████████                                               │
│                                                                      │
│  #3  Choice & Comparison Overload               HIGH IMPACT 🔴     │
│       64 reviews · 12.8%                                             │
│      █████████████                                                   │
│                                                                      │
│  #4  Information & Trust Gaps                    MEDIUM IMPACT 🟠   │
│       51 reviews · 10.2%                                             │
│      ██████████                                                      │
│                                                                      │
│  #5  Fit & Size Confidence                       MEDIUM IMPACT 🟠   │
│       43 reviews ·  8.6%                                             │
│      ████████                                                        │
│                                                                      │
│  #6  Availability & Purchase Friction           MEDIUM IMPACT 🟠   │
│       31 reviews ·  6.2%                                             │
│      ██████                                                          │
│                                                                      │
│  #7  Wishlist Overload & Prioritization          LOW IMPACT 🟡      │
│       22 reviews ·  4.4%                                             │
│      ████                                                            │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  🔴 TOP OPPORTUNITY                                                  │
│                                                                      │
│  Purchase Uncertainty                                                │
│  118 / 500 reviews · 23.6%                                          │
│                                                                      │
│  Customer Problem                                                     │
│  Users are interested in the product but don't have enough          │
│  confidence to complete the purchase.                                │
│                                                                      │
│  Potential Business Impact                                           │
│  High — may reduce wishlist → purchase conversion.                  │
│                                                                      │
│  [ View Evidence ]    [ View Supporting Reviews ]                   │
└──────────────────────────────────────────────────────────────────────┘
```

When the user clicks an opportunity:

For example, Purchase Uncertainty:

```text
┌──────────────────────────────────────────────────────────────┐
│  PURCHASE UNCERTAINTY                                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  118 supporting reviews          23.6% of reviews            │
│  Impact: HIGH                   Confidence: HIGH             │
│                                                              │
│  WHAT ARE USERS WORRIED ABOUT?                              │
│                                                              │
│  • Fit uncertainty                                      48  │
│  • Product quality concerns                            37  │
│  • Product looks different from images                 21  │
│  • Missing product information                         12  │
│                                                              │
│  WHY IT MATTERS                                             │
│  Customers have expressed interest by wishlisting,         │
│  but uncertainty may prevent them from completing purchase. │
│                                                              │
│  ORIGINAL REVIEW EVIDENCE                                   │
│                                                              │
│  "The size was different from what I expected..."           │
│  "Material looks different in real life..."                 │
│                                                              │
│                   [ View All 118 Reviews ]                  │
└──────────────────────────────────────────────────────────────┘
```

