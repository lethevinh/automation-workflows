# Automation audit: Fixed-price automation service delivery

## Business problem

"I'm building a small automation service and I'm looking for reliable n8n /
Make specialists for ongoing project-based work." "I'm looking for people who
can work on clearly defined fixed-price projects with agreed deadlines." The
service runs on milestones: "Payment would be agreed per project or milestone
and paid after the corresponding client milestone is approved and funds are
released." Nothing tracks which milestone a project is on, whether the client
has signed it off, or whether the handover pack exists yet — so the owner
chases status by hand and payment waits on someone's memory.

## Scope in

- Intake of a clearly defined client brief, with the required fields filled in
- Tracking each project milestone from kickoff to client sign-off
- Generating the handover pack when a project closes

## Scope out

- Client billing and payment processing
- Delivering the automations themselves (the specialists' paid work)

## Success signal

A brief moves from the inbox to a fixed-price quote in one working day, every
milestone has an owner and a sign-off date, and closing a project produces its
runbook in minutes instead of an afternoon.

## Automation candidates (ordered)

1. **Track each project milestone from kickoff to client sign-off** — Milestone acceptance tracking · effort S (~3h)
2. **Client-brief intake with required-field checks** — Client-brief intake · effort S (~4h)
3. **Handover-pack generator (flow map + runbook when a project closes)** — Handover-pack generation · effort S (~5h)

_Ordered quickest-first by catalog effort; effort figures are catalog estimates, not source figures._

## Rough effort estimate

Total: **~12h** across 3 catalog-mapped candidate(s) (validate with a scoped quote before committing).
