# Escalation Protocol Reference

## Escalation Message Template

Send this to each trusted contact when beginning escalation:

> Hi {contact.name}, this is an automated message from Afterself. The person who set this up has not checked in for an extended period. Have you been in contact with them recently?
>
> Reply YES if they are okay, or NO if you can't reach them either.
>
> This is important — your response helps determine whether to activate their digital will.

## Response Classification

### Alive Keywords
The contact is confirming the person is OK:
- alive, fine, ok, safe, here
- with them, saw them, talked, spoke
- yes, they're good, false alarm

### Absent Keywords
The contact is confirming the person is unreachable:
- no, haven't, can't reach, missing, worried
- gone, not responding, absent, disappeared, confirm

### Ambiguous Response
If the message doesn't match either keyword list, ask for clarification:

> Thanks for responding. To be clear: have you been in contact with the person recently? Reply YES if they're okay, or NO if you can't reach them either.

## Decision Matrix

| Condition | Decision |
|---|---|
| ANY contact confirmed alive | **Stand down** — return to armed state |
| Majority confirmed absent | **Trigger** — begin executor |
| Some absent, none alive, below majority | **Wait** for more responses |
| Escalation timeout, at least one absent | **Trigger** |
| Escalation timeout, no responses at all | **Trigger** (with caution log) |

**Majority** = `ceil(totalContacts / 2)`

A single "alive" confirmation always overrides any number of "absent" confirmations. This is the safety-first approach — false negatives (not triggering when the person is gone) are far less harmful than false positives (triggering when they're alive).
