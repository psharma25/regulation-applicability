# ThreatForge

ThreatForge is a browser-based product threat-modeling workbench with FDA
premarket views, security knowledge graphs, risk-register generation, framework
overlays, and continuous scan/advisory intake. This repository ships two
supported surfaces from one canonical application:

- `index.html` — standalone web app and GitHub Pages entry point.
- `extension/` — VS Code extension that persists the model in the open
  repository and watches `.threatforge/intake/`.

The original nested archives have been removed. The top-level app is the source
of truth; `npm run sync:extension` copies it into the extension.

## Run locally

Requirements: Node.js 20 or later.

```bash
npm test
npm start
```

Open <http://127.0.0.1:8080>.

The standalone app can also be opened directly from `index.html`, although an
HTTP server gives more consistent browser behavior.

## Publish with GitHub Pages

1. Upload this entire folder to a GitHub repository.
2. Open **Settings → Pages**.
3. Under **Build and deployment**, select **GitHub Actions**.
4. Push to `main`. The included workflow validates and publishes the top-level
   static app.

No API keys are required for the deterministic local analysis. Government feeds,
GitHub imports, outbound integrations, and hosted language-model calls require
network access and should use a server-side proxy in production.

## Run in a container

```bash
docker compose up --build
```

Open <http://127.0.0.1:8080>. The image serves only the static web application
through an unprivileged, read-only runtime layout.

## Use the VS Code extension

```bash
npm run sync:extension
cd extension
npx @vscode/vsce package
code --install-extension ai-security-knowledge-graph-1.0.0.vsix
```

For extension development, open `extension/` in VS Code and press `F5`.
Copy `extension-launch.example.json` to `extension/.vscode/launch.json` if your
editor does not generate a launch configuration automatically.

The extension writes the project model to:

```text
.threatforge/
├── model.json               # reviewable project model
└── intake/                  # SARIF, JSON, CSV, or XML scan/advisory inputs
```

Example intake files are included under
`extension/.threatforge/intake/`. The extension understands envelopes, SARIF,
CycloneDX, SPDX, and pentest CSV inputs.

## Repository layout

```text
.
├── index.html                       # canonical standalone app
├── extension/
│   ├── extension.js                 # VS Code host integration
│   ├── package.json                 # extension manifest
│   ├── media/index.html             # synchronized embedded app
│   └── .threatforge/intake/         # safe sample inputs
├── scripts/
│   ├── serve.mjs
│   ├── sync-extension.mjs
│   └── validate.mjs
├── docs/PRODUCTION.md
├── .github/workflows/
├── Dockerfile
├── compose.yaml
└── nginx.conf
```

## Release checklist

```bash
npm run sync:extension
npm test
```

The validator checks the canonical/extension HTML match, manifest JSON,
extension syntax, required app markers, and accidental nested ZIP files.

## Data and security boundary

The standalone app stores projects in the browser. The extension stores the
model in the repository. Do not place secrets, embargoed vulnerability data, or
regulated patient information into public GitHub Pages.

The current browser UI contains optional direct calls to third-party APIs. A
public production deployment must route secrets and restricted feeds through a
server-side service. See [docs/PRODUCTION.md](docs/PRODUCTION.md) and
[SECURITY.md](SECURITY.md) before handling sensitive data.
