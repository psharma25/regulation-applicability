# Security policy

## Reporting a vulnerability

Report suspected vulnerabilities privately to the repository owner or the
organization's established product-security channel. Do not include patient
information, credentials, embargoed exploit material, or private model exports
in a public issue.

Include the affected version, deployment surface (web or VS Code), reproduction
steps, expected impact, and any suggested mitigation. Allow the maintainer time
to validate and coordinate a fix before public disclosure.

## Deployment cautions

- GitHub Pages is public unless repository and organization controls provide a
  private Pages deployment.
- Browser local storage is not encrypted application storage.
- Do not put LLM, feed, GitHub, Jira, or ServiceNow credentials in `index.html`.
- Do not configure a CORS proxy that accepts an arbitrary URL.
- Treat imported scanner and advisory files as untrusted content.
- Review exports before sharing; they may contain architecture and vulnerability
  details useful to an attacker.

See `docs/PRODUCTION.md` for the required boundary for regulated or multi-user
operation.
