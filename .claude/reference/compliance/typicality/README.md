# Typicality Data

FTC-compliant outcome data for testimonial disclosures.

---

## Why This Exists

The FTC Endorsement Guides (updated 2023, effective Oct 2024) require that testimonials either:

1. Represent typical results (with substantiation), OR
2. Include clear disclosure of what typical results ARE

"Results not typical" is **no longer sufficient**. You must state what typical IS.

**Source:** [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking)

---

## The Survivorship Bias Problem

**Wrong approach:** Survey the #wins channel and average those results.

The FTC explicitly addressed this: A disclosure saying "The typical weight loss of users who stick with the program for 6 months is 35 pounds" is **inadequate** if only 1/5 of people who start actually stick with it for 6 months.

**Correct approach:** Measure outcomes for ALL users who START, including:
- Those who dropped out
- Those who didn't engage
- Those who saw no results
- Those who saw negative results

---

## Data Collection Methodology

### Option A: Platform Analytics (Ideal)

If the platform tracks engagement/outcomes:
1. Export total members joined (by date cohort)
2. Export engagement metrics (logins, completions)
3. Export outcome data if tracked (scores, funding, etc.)

### Option B: Representative Survey (Acceptable)

If no platform analytics:
1. Survey a RANDOM sample of ALL members, not just active ones
2. Use email list, not community post (self-selection bias)
3. Incentivize response from inactive members
4. Document methodology for FTC defense

### Option C: Cohort Analysis (Best for New Data)

Going forward:
1. Track starting state for new members (baseline)
2. Track outcomes at defined intervals (30, 90, 180 days)
3. Include non-responders as "no measured improvement"

---

## Required Data Points

For each client/offer, document:

### 1. Population Denominator
- Total members who joined (all-time or by cohort)
- Date range covered
- Source of this number

### 2. Outcome Distribution
- % who achieved NO measurable result
- % who achieved modest results
- % who achieved the testimonial-level results
- Median and mean outcomes (if quantifiable)

### 3. Timeframe Context
- How long did members need to be active to see results?
- What % stayed active that long?
- What's the typical timeframe for the average member?

### 4. Methodology Documentation
- How was data collected?
- What's the response rate?
- What are the limitations?

---

## File Format

Each client typicality file should include:

```markdown
# [Client] Typicality Data

**Last Updated:** YYYY-MM-DD
**Data Source:** [Platform analytics / Survey / Cohort study]
**Population:** [Total members in scope]
**Methodology:** [How data was collected]

## Summary Statistics

| Metric | Value | Source |
|--------|-------|--------|
| Total members | X | [source] |
| Active at 90 days | X% | [source] |
| Achieved any improvement | X% | [source] |
| Achieved testimonial-level results | X% | [source] |

## Compliant Disclosure Language

Based on this data, use this disclosure:

> "[Testimonial name] achieved [result]. The average [client] member
> achieves [typical result]. [X]% of members see no measurable
> improvement. Individual results vary based on [factors]."

## Raw Data

[Link to spreadsheet or data source]

## Limitations

[What this data doesn't capture]
```

---

## When Typicality Data Is Missing

If no typicality file exists for a client, the ad-review skill should:

1. Flag as P1: "No typicality data on file"
2. Generate research task: "Collect typicality data for [client]"
3. Block testimonial ads until data is collected

**Alternative:** Use process testimonials only ("I learned a lot") rather than outcome testimonials ("I made $X") until typicality data exists.

---

## Where Client Data Lives

**This folder contains the TEMPLATE only.**

Client-specific typicality data lives in each client's own repo:

```
{client-repo}/.claude/context/compliance/typicality/{client}-typicality.md
```

Copy the template below to create a new client typicality file.

---

## Sources

- [FTC Endorsement Guides FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking)
- [16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255)
- [Arnold & Porter Analysis](https://www.arnoldporter.com/en/perspectives/advisories/2023/07/ftc-endorsement-guides)
