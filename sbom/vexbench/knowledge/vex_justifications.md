# VEX status and justifications — reference

## Status values
A VEX statement assigns one status per product/vulnerability pair:

- **Affected** — the vulnerability is exploitable in this product as shipped. A remediation or
  mitigation is recommended.
- **Not affected** — the product is not impacted; a machine-readable justification is required.
- **Fixed** — a release containing a fix is available; the affected version range is closed.
- **Under investigation** — triage is not complete. This should be temporary; submissions
  generally expect findings to be resolved to one of the other states.

## Not-affected justifications (CycloneDX / CSAF aligned)
Use the narrowest justification that is true:

- **component_not_present** — the vulnerable component is not actually in the build, despite an
  SBOM or scanner entry.
- **vulnerable_code_not_present** — the component is present but the specific vulnerable code
  (e.g. a function or module) is not included.
- **vulnerable_code_not_in_execute_path** — the vulnerable code exists but is never reached during
  execution in this configuration. This is the classic reason a high-CVSS finding can be benign in
  a specific device.
- **vulnerable_code_cannot_be_controlled_by_adversary** — the code runs but an attacker cannot
  influence the inputs needed to trigger it.
- **inline_mitigations_already_exist** — a built-in control (input validation, sandboxing,
  network isolation) already prevents exploitation.

## Disposition vs status
VEX status describes exploitability. Disposition describes the action: remediated, mitigated by a
compensating control, mitigable (a path exists but is not yet applied), not currently remediable
(no fix and no adequate control — must be explained), or accepted with rationale. A finding can be
"Affected" yet "Mitigated" when a compensating control reduces residual risk to acceptable.

## Documenting "why not"
When a vulnerability is real and remains unresolved, the rationale should state concretely why:
no upstream patch exists, the component is closed third-party software, the attack surface cannot
be fully removed without breaking essential performance, or a fix is scheduled for a later
maintenance release. Vague statements are not acceptable for an unresolved safety-relevant finding.
