# Patient-safety risk framing — ISO 14971 / AAMI TIR57

## Cybersecurity risk as patient harm
For medical devices, security risk is evaluated through its potential to cause patient harm, not
only confidentiality or financial loss. AAMI TIR57 connects security risk management to the safety
risk process of ISO 14971: a security weakness becomes relevant when an exploit could lead to a
hazardous situation affecting the device's essential performance or intended use.

## Patient-safety impact bands
A practical severity scale for clinical impact:

- **Negligible** — no realistic effect on patient safety; nuisance or informational only.
- **Minor** — temporary or minor discomfort; no clinical intervention needed.
- **Serious** — injury or impairment requiring clinical intervention; reversible.
- **Critical** — life-threatening injury or permanent impairment.
- **Catastrophic** — death or multiple severe injuries.

## From vulnerability to hazard
The chain is: threat exploits a vulnerability -> causes a security compromise -> leads to a
hazardous situation -> which can produce harm. A buffer overflow in a logging library matters for
patient safety only if exploiting it can affect therapy delivery, monitoring accuracy, alarms, or
clinical decisions. Map each finding to the device function it could disturb.

## Residual risk acceptability
After controls, residual risk should be evaluated against the manufacturer's risk acceptability
criteria. Safety-relevant residual risk that remains High or Critical must be justified, with a
benefit-risk rationale and a remediation plan. Controls that reduce exploitability (network
segmentation, authentication, input validation, disabling unused features) or reduce harm (alarms,
fail-safe states, redundancy) both lower residual risk and should be documented as such.

## Compensating controls
When an upstream patch is unavailable, compensating controls can reduce residual risk: restrict
network exposure, isolate the component, validate inputs, monitor for exploitation, and constrain
the device to a fail-safe state on anomaly. Document the control, its expected effectiveness, and
the residual risk that remains after it is applied.
