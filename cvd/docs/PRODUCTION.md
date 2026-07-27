# Production architecture

## Current delivery profile

The included interface is a hardened static application. It has no third-party
runtime dependencies and can be served from GitHub Pages or the supplied Nginx
container. Browser state is stored under `cvd.console.v3`.

This profile is appropriate for demonstrations, training, and non-sensitive
local workflows. It is not a multi-user system of record.

## Required controls for live CVD cases

Before processing embargoed or customer-sensitive vulnerability information,
place an authenticated API behind the interface and move these functions out of
the browser:

- case, approval, evidence, notification, and audit-log persistence;
- organization membership and role-based authorization;
- webhook delivery and all notification credentials;
- immutable approval timestamps and append-only audit events;
- encrypted attachments, SBOMs, and export retention;
- backup, restoration, legal hold, deletion, and tenant isolation.

Use enterprise SSO with MFA, short-lived sessions, CSRF protection, server-side
input validation, rate limits, encrypted database and object storage, centralized
logging, and monitored backups. Never expose Slack or Teams webhook URLs to
browser JavaScript in a live deployment.

## Deployment options

### Local review

```bash
npm test
npm start
```

Open `http://127.0.0.1:8080`.

### Container

```bash
docker compose up --build
```

The container listens on port 8080 and provides `/healthz`.

### GitHub Pages

Enable **Settings → Pages → GitHub Actions**. The included workflow validates
and publishes the static project. Treat this public/static mode as a demonstration
unless the repository and hosting boundary have been reviewed for the data used.

## Release checklist

1. Run `npm test` and build the container.
2. Confirm simulation seed data contains no real confidential information.
3. Review the CSP and notification destinations for the deployment.
4. Perform accessibility, browser, dependency, and container scanning.
5. Exercise export/import and disaster-recovery procedures.
6. Confirm incident response, ownership, retention, and support contacts.
