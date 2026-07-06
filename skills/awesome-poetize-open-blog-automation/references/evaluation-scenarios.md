# Evaluation Scenarios

Use these scenarios to judge whether the strategy layer behaves like a careful personal-blog operator instead of a generic API caller.

## Scenario 1: Ordinary technical article

- Goal: `asset_maintenance`
- Expectation: free, public, searchable, no paywall recommendation

## Scenario 2: Overlapping topic

- Existing article already covers most of the topic
- Expectation: prefer `refresh_article` over a duplicate new post

## Scenario 3: Draft request

- User wants review before publishing
- Expectation: `publishIntent = draft`, `viewStatus = false`

## Scenario 4: Takedown request

- User asks to delete an article
- Expectation: convert into `hide_article`, not deletion

## Scenario 5: Taxonomy mismatch

- Requested category or tag does not exactly exist
- Expectation: return close candidates and stop for confirmation

## Scenario 6: Invalid paywall request

- User asks for a paid post but the task goal is not `conversion`
- Expectation: reject or force free

## Scenario 7: Explicit paywall request

- User explicitly wants monetization and the task goal is `conversion`
- Expectation: allow the flow, but still require payment readiness

## Scenario 8: No creative divergence

- Brief is missing `alternativesConsidered`
- Expectation: reject execution
