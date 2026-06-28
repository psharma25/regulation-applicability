# FDA Premarket Cybersecurity (Section 524B) — working notes

## Statutory basis
Section 524B of the FD&C Act applies to "cyber devices" — devices that include software,
can connect to the internet, and could be vulnerable to cybersecurity threats. Sponsors must
provide a plan to monitor, identify, and address postmarket vulnerabilities; design and
maintain processes to provide reasonable assurance the device is cybersecure; and provide a
software bill of materials (SBOM) including commercial, open-source, and off-the-shelf components.

## SBOM expectations
The SBOM should reflect the NTIA minimum elements: supplier name, component name, version,
unique identifiers, dependency relationships, author, and timestamp. Machine-readable formats
(CycloneDX, SPDX) are expected. Each component should be assessable for known vulnerabilities,
and the submission should describe how the manufacturer assesses and manages those vulnerabilities
across the total product lifecycle.

## Vulnerability assessment
For each known vulnerability associated with a component, the manufacturer is expected to
characterize exploitability and the safety impact, and to document a disposition: whether it is
remediated, mitigated by a compensating control, or accepted with rationale. Exploitability should
consider attack vector, exploit maturity, and whether the vulnerable code is reachable in the
device's configuration. A vulnerability with a high CVSS base score but no reachable execution path
may carry low actual risk; this should be justified, not assumed.

## Safety impact and risk
Cybersecurity risk for a medical device is framed in terms of patient harm, not just data loss.
Manufacturers should connect a vulnerability to potential effects on the device's essential
performance and intended use, consistent with the risk framework in ISO 14971 and AAMI TIR57.
Residual risk after controls should be documented, and any residual risk that remains
unacceptable requires explanation and a plan.

## Coordinated disclosure and postmarket
Submissions are expected to include a coordinated vulnerability disclosure process and a plan for
monitoring, identifying, and addressing postmarket vulnerabilities and exploits in a reasonable
time. Unresolved anomalies should be listed with their assessed impact.

## Why a VEX matters here
A Vulnerability Exploitability eXchange (VEX) document lets a manufacturer state, per component
vulnerability, whether the product is actually affected. This prevents teams and regulators from
chasing vulnerabilities that are present in an SBOM but not exploitable in the shipped device.
