# Production deployment

## Supported deployment profiles

### Public or internal static deployment

Use GitHub Pages or the included container for demonstrations, training, and
non-sensitive threat models. Data remains in each browser's local storage. There
is no central identity, synchronization, audit log, backup, or access control.

### Repository-backed developer workflow

Use the VS Code extension when the threat model should live beside source code.
Commit `.threatforge/model.json`, review it in pull requests, and feed scanner
outputs into `.threatforge/intake/`. Protect the repository using your normal
branch, identity, retention, and secret-scanning controls.

### Multi-user regulated deployment

Before using ThreatForge as a system of record, add an authenticated backend
that provides:

- SSO with role-based authorization and tenant isolation.
- Server-side encryption, backup, retention, and recovery.
- Immutable audit events for model changes, approvals, exports, and feed runs.
- A secrets vault for feed credentials, GitHub tokens, webhooks, and LLM keys.
- A same-origin API proxy with explicit host allowlists, request limits,
  response-size limits, timeouts, and schema validation.
- Malware/content scanning for imported SARIF, JSON, CSV, XML, and documents.
- Egress controls and data-loss prevention for prompts sent to any LLM.
- A reviewed privacy and regulatory classification. Never ingest PHI unless the
  complete deployment is authorized for it.

## Important browser limitations

The app's deterministic risk calculations run locally. NVD, CISA, GitHub, and
other feeds may reject browser cross-origin requests. Do not solve this with an
open CORS relay. Use an authenticated proxy that allows only approved upstream
hosts and never accepts arbitrary destination URLs.

The optional browser LLM path must not receive a provider API key. Put the key
in a server-side secret store and expose a narrow endpoint that validates prompt
size, authenticates the caller, records usage metadata, and strips unexpected
content. Review whether model data may leave your environment.

## Recommended release controls

1. Run `npm run sync:extension && npm test`.
2. Pin GitHub Actions to reviewed commit SHAs in high-assurance environments.
3. Generate an SBOM and scan the container and extension package.
4. Review the HTML for newly introduced remote endpoints.
5. Test backup/restore for `.threatforge/model.json` or the backend database.
6. Verify security headers at the deployed origin.
7. Run accessibility and browser compatibility checks.

## Persistence and recovery

- Web app: use the in-app export before clearing browser data or changing
  browsers. Browser local storage is not a backup.
- Extension: commit `.threatforge/model.json` to a private, access-controlled
  repository. Scanner outputs can be retained as CI artifacts if they should not
  enter version control.

## Content Security Policy

The application is currently a self-contained HTML document with inline styles
and scripts. A strict CSP requires splitting those blocks into versioned static
assets or supplying generated hashes. Do that before a high-assurance public
deployment; do not add `unsafe-eval`.
