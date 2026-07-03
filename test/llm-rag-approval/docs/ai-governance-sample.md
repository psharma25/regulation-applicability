# Acme Corp AI governance standard (sample document)

## Approved use
Generative AI tools may be used for drafting, summarization, and code
assistance. All AI-generated content that leaves the company (customer
emails, marketing, legal text) requires human review and approval before
sending — a human must be accountable for every external output.

## Prohibited use
Employees may not paste Confidential or personal data into unapproved AI
tools. AI may not make automated decisions about hiring, credit, or medical
matters without documented human oversight.

## Model risk management
Each AI use case is risk-tiered (Low / Medium / High). High-risk use cases
require a documented impact assessment, bias evaluation, and sign-off from
the AI Governance Board. Retrieval-augmented generation (RAG) systems must
log retrieved sources for every answer to support auditability.

## Human-in-the-loop requirement
For customer-facing answers, the system must hold responses in a review
queue until an authorized reviewer approves, edits, or rejects the draft.
Approval decisions are logged with reviewer identity and timestamp.
