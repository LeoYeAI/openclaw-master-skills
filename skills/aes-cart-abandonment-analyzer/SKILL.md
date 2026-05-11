---
name: aes-cart-abandonment-analyzer
description: Identify reasons for cart abandonment and build multi-touch recovery sequences across email, SMS, and push.
---

# Cart Abandonment Analyzer

Cart abandonment is one of the most expensive leaks in any ecommerce funnel — average abandonment rates hover around 70%, meaning seven out of ten shoppers who add items to their cart leave without purchasing. This skill diagnoses the likely causes of cart abandonment for your specific store and product mix, then builds tailored multi-touch recovery sequences across email, SMS, and push notification channels to win back lost revenue systematically.

## Use when

- Your Shopify, WooCommerce, or BigCommerce store shows a cart abandonment rate above 65% and you need to identify the root causes beyond just "they weren't ready to buy"
- You want to design a complete abandoned cart recovery flow with timed email sequences, SMS follow-ups, and push notifications but are unsure about optimal timing, copy angles, or incentive escalation
- Your existing cart recovery emails have an open rate below 40% or a click-through rate below 5% and you want fresh copy, subject lines, and send-time strategies to improve performance
- A marketing manager needs a documented cart recovery playbook they can hand off to the email marketing team or load into Klaviyo, Omnisend, or Mailchimp automation workflows

## What this skill does

This skill takes your store details, product category, average order value, and current abandonment data to perform a structured root-cause analysis of why shoppers are leaving. It examines pricing friction, shipping cost surprises, checkout complexity, trust gaps, payment method limitations, and mobile experience issues. Based on the diagnosis, it generates a complete multi-channel recovery sequence with specific message copy for each touchpoint, recommended send timing relative to the abandonment event, subject lines and preview text for emails, SMS message templates within character limits, and push notification copy. The sequence includes an incentive escalation ladder that starts with reminders and progressively introduces discounts or free shipping offers.

## Inputs required

- **Store platform and product category** (required): Which platform you sell on and what types of products you sell. Example: "Shopify store selling premium skincare products, AOV around $65."
- **Current abandonment rate** (required): Your approximate cart abandonment rate and any known patterns. Example: "72% abandonment, spikes on mobile, most drop off at shipping calculation step."
- **Existing recovery efforts** (required): What you currently do to recover abandoned carts — email flows, retargeting ads, nothing at all. Example: "One generic reminder email sent 24 hours after abandonment, 18% open rate."
- **Available channels** (optional): Which channels you can use for recovery — email, SMS, push, WhatsApp, retargeting. Defaults to email and SMS if not specified.
- **Discount budget** (optional): Maximum discount or incentive you are willing to offer in recovery sequences. Example: "Up to 15% off or free shipping on orders over $50."

## Output format

The output begins with a Root-Cause Diagnosis section that identifies the three to five most likely abandonment drivers for this specific store and product type, with reasoning for each. Next comes the Recovery Sequence Blueprint — a timeline-based plan showing each touchpoint across all channels, with exact timing relative to the cart abandonment event. For each touchpoint, the output provides the channel, send time, subject line or message hook, full message body copy, CTA text and destination, and any incentive offered. The output also includes a Segmentation Guide explaining how to split recovery flows by cart value, product type, and customer status (new versus returning). Finally, a Performance Benchmarks section sets realistic open rate, click rate, and recovery rate targets for each message in the sequence.

## Scope

- Designed for: ecommerce operators, email marketers, retention specialists, Shopify and WooCommerce store owners
- Platform context: Shopify, WooCommerce, BigCommerce, Klaviyo, Omnisend, Mailchimp, Attentive, platform-agnostic
- Language: English

## Limitations

- Cannot access your actual analytics or cart data in real time; analysis is based on the information you provide plus established ecommerce benchmarks for your product category
- Recovery copy is template-ready but may need adjustment to match your exact brand voice and comply with SMS marketing regulations in your jurisdiction
- Does not directly integrate with or configure your email service provider or marketing automation tool — output is designed to be implemented manually or pasted into your existing workflows
