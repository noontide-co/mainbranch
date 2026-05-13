---
date: 2026-05-13
status: accepted
tags: [ads, creative, media-generation, providers, skills]
---

# Creative Media Generation Rails

## Decision

Treat creative media generation as an optional Ship rail, not a core `mb`
provider integration yet.

Main Branch can help operators plan, prompt, review, and record static ad
images, landing-page visuals, organic assets, and simple motion exports. It
should not claim first-class image, video, motion, or platform-creative
generation support until the provider path has current docs, setup detection,
approval gates, smoke evidence, and reproducibility metadata.

The recommended v0 rail is:

1. Store the creative brief, prompts, source files, claim/proof context,
   provider/model, output dimensions, post-processing settings, cost, retries,
   and final file paths.
2. Generate static images only when an approved provider is configured for the
   current run; otherwise save prompts for manual provider use.
3. Use deterministic local motion/export tools before raw AI video when the
   goal is reproducible short ads, captions, crops, variants, or page motion.
4. Treat AI video providers as candidate rails that need separate provider
   readiness and smoke issues.

## Recommended Rails

| Rail | State | Why |
| --- | --- | --- |
| Static image prompts plus output records | Recommended | Fits current `/mb-ads` and `/mb-site` workflows without claiming provider support. Prompts, source context, and final assets can be reviewed and saved in the business repo or a push record. |
| OpenAI image generation/editing | Candidate provider | Official docs expose image generation and editing APIs, output size/format controls, and Responses API image flows. Main Branch can adopt this after setup detection, approval, smoke, and artifact metadata are wired. |
| Google Gemini image generation/editing | Candidate provider | Official Gemini API docs expose image generation through Python, JavaScript, Go, Java, and REST, with current Nano Banana model families and aspect-ratio/image-size controls. Model IDs move quickly, so artifacts must pin the exact model used. |
| Remotion plus FFmpeg for deterministic motion/export | Recommended design rail | Remotion gives code-backed, parameterized video rendering; FFmpeg gives durable resizing, overlay, concatenation, captions, encoding, and platform export. This is a better first motion rail than raw AI video because the brief and render settings are inspectable. |

## Candidate Rails

| Rail | State | Boundary |
| --- | --- | --- |
| Google Veo | Candidate | Useful for short social/video ad generation, but paid/provider setup, temporary output storage, preview model churn, and low reproducibility keep it out of core until smoked. |
| OpenAI Sora | Candidate | Official API docs expose asynchronous video generation/edit/extend flows. Treat as optional video generation only after account access, cost, moderation, approval, and artifact recording are proven. |
| Runway | Candidate | Strong premium AI video surface with primary API docs, SDKs, moderation, tiers, and pricing. Higher maintenance burden than OpenAI/Google; needs a separate provider decision before adoption. |
| Shotstack-style hosted JSON render | Candidate | Good hosted template-render option if local Remotion/FFmpeg is too heavy. Not a generative rail and adds cloud billing/lock-in. |
| MoviePy | Reference helper | Useful for simple Python-native assembly, but FFmpeg is the better primitive for predictable transforms and Remotion is stronger for reusable motion systems. |
| TikTok Symphony Creative Studio | Manual platform rail | Useful free business-owner workflow inside TikTok Ads Manager, but not a reproducible API/CLI rail for Main Branch today. |

## Refused For Core

| Rail | Reason |
| --- | --- |
| Meta Advantage+ Creative as the generator | It is an in-platform optimization layer, not a reproducible asset generator. Main Branch can record whether the operator used it, but it should not treat platform-side resizing, background generation, or animation as source-of-truth creative production. |
| TikTok Symphony API automation | No public primary API/CLI rail was verified. Keep it as a manual handoff until official automation docs and smoke evidence exist. |
| Raw AI video as the first creative system | Video generation is slower, more expensive, less reproducible, and higher policy risk than static images plus deterministic motion/export. Start with briefs, static assets, and renderable templates. |

## Artifact Metadata

When a skill generates or helps the operator generate media assets, the durable
record should include:

- provider and model, or `manual`;
- docs-checked date when model/provider guidance affects the run;
- source files read, such as offer, audience, proof, voice, content strategy,
  visual style, and push/playbook;
- prompt text and negative constraints;
- output dimensions, format, compression, and crop/safe-zone rules;
- cost estimate and actual cost when known;
- failure/retry count and manual-generation notes;
- final approved asset paths;
- approval state for publishing, spending, provider mutation, or customer
  contact.

Generated binaries should not become required business-repo truth. Keep large
assets in a configured media folder, a site repo, or another approved location;
the business repo can store prompts, indexes, approval records, and links.

## Source Notes

Primary/current sources checked on 2026-05-13:

- OpenAI image generation docs:
  https://developers.openai.com/api/docs/guides/image-generation
- OpenAI video generation docs:
  https://developers.openai.com/api/docs/guides/video-generation
- Google Gemini image generation docs:
  https://ai.google.dev/gemini-api/docs/image-generation
- Google Veo API docs:
  https://ai.google.dev/gemini-api/docs/video
- Remotion docs:
  https://www.remotion.dev/docs/
- FFmpeg docs:
  https://ffmpeg.org/ffmpeg.html
- Runway API docs:
  https://docs.dev.runwayml.com/
- Shotstack docs:
  https://shotstack.io/docs/guide/
- MoviePy docs:
  https://zulko.github.io/moviepy/
- Meta Advantage+ Creative:
  https://www.facebook.com/business/ads/meta-advantage-plus/creative
- TikTok Symphony Creative Studio:
  https://ads.tiktok.com/help/article/about-symphony-creative-studio

## Follow-Ups

- Add the combined creative asset generation readiness rail before any `mb
  connect` provider state or motion/template support claim:
  https://github.com/noontide-co/mainbranch/issues/569
- The standalone deterministic motion-template follow-up was superseded by the
  combined readiness rail so provider images and deterministic templates share
  one artifact metadata contract:
  https://github.com/noontide-co/mainbranch/issues/568
