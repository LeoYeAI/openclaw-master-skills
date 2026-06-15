# Customization Guide

## Feedback Patterns
Edit `feedback-signals.json` to match your human's language. If they say "ship it" when happy, add it. If they say "bruh" when frustrated, add it.

## Pre-Action Checklist
Add sections for your specific work domains. Construction? Add permit checks. Finance? Add compliance checks. The checklist is yours to shape.

## Rule Categories
Use whatever categories match your work. Defaults: shell, auth, memory, cron, social, communication. Add api, browser, debugging, architecture - whatever you need.

## Promotion Threshold
Default: 3 applications before lesson becomes rule. Adjust in `promote-rules.sh` for stricter (5+) or faster (2+) promotion.
