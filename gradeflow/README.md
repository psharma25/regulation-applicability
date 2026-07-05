# GradeFlow AI — standalone deployment package (v0.3-alpha)

Single-page worksheet grading console. Everything — deterministic grading engine,
synthetic samples, PDF export, reports, and OCR of uploaded scans — runs in the
user's browser. **No server-side compute, no installs for users, no data leaves
their machine.**

## Contents
    index.html            the entire application
    vendor/               in-browser OCR engine (Tesseract WASM, served same-origin)
      tesseract.min.js
      worker.min.js
      core/               WASM cores (SIMD + fallback)
      eng.traineddata     language data (fast variant)

Keep `vendor/` next to `index.html` — the OCR tier loads it same-origin.
Without it the app still works fully for synthetic sheets; uploaded scans
route to the review queue with an explanation.

## Deploy — GitHub Pages (recommended, free)
    gh repo create gradeflow --public
    git init && git add . && git commit -m "GradeFlow AI alpha"
    git branch -M main && git remote add origin <repo-url> && git push -u origin main
Then: repo → Settings → Pages → Deploy from branch → main / root.
URL: https://<user>.github.io/gradeflow/  — send that link; recipients need nothing else.

## Deploy — AWS (S3 + CloudFront)
    aws s3 mb s3://gradeflow-alpha
    aws s3 sync . s3://gradeflow-alpha --exclude "README.md"
Front with CloudFront (HTTPS, caching; set default root object index.html).
No EC2 required — this package has no server component.

## OCR tiers (automatic)
1. Local Ollama vision model — optional, best handwriting quality (each user's own machine).
2. In-browser engine (this vendor/ folder) — default, zero install, fully local.
   Clear pen/print reads well; faint pencil or skewed scans route to review
   rather than being guessed. Scores always come from the deterministic engine.
3. Review queue — the honest fallback.

## Do not deploy on GitHub Codespaces
Codespaces are authenticated dev environments that idle-stop; they are not a
hosting platform for end users.

Privacy: student IDs only, no names; all processing and storage stay in the
user's browser (localStorage).
