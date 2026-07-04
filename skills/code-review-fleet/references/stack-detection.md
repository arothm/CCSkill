# Stack detection

Goal: figure out what languages/frameworks are present, which parts are
frontend vs backend, and — most importantly — the *actual* commands the project
uses to test, lint, type-check, and build. Never hardcode a command; read it
from the project's own config so the agents run what CI runs.

## 1. Find the subprojects

Start by listing the repo root and looking one or two levels deep for the signal
files below. In a monorepo you'll often find several (e.g. `apps/web/package.json`
and `services/api/pyproject.toml`). Each cluster of signal files is a subproject
that may deserve its own agent.

| Signal file | Ecosystem | Usual role |
|---|---|---|
| `package.json` | Node / JS / TS | frontend or backend (check deps) |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python | usually backend |
| `go.mod` | Go | backend |
| `Cargo.toml` | Rust | backend / CLI |
| `pom.xml`, `build.gradle` | Java / Kotlin | backend |
| `Gemfile` | Ruby | backend / Rails |
| `composer.json` | PHP | backend |
| `*.csproj`, `*.sln` | .NET | backend |
| `Dockerfile`, `docker-compose.yml` | any | hints at services |

## 2. Frontend vs backend

For a `package.json`, read `dependencies`/`devDependencies`:

- **Frontend** signals: `react`, `vue`, `svelte`, `@angular/core`, `next`,
  `nuxt`, `vite`, `webpack`, `tailwindcss`, presence of `public/index.html`,
  `src/components`, `.jsx`/`.tsx`/`.vue` files.
- **Backend** signals: `express`, `fastify`, `koa`, `@nestjs/core`, `prisma`,
  `typeorm`, database drivers (`pg`, `mysql2`, `mongoose`), no DOM/bundler deps.

Python/Go/Rust/Java/Ruby/PHP subprojects are backend by default. A repo can be
frontend-only, backend-only, or both — plan agents accordingly.

## 3. Extract the real commands

Prefer commands the project already defines over generic ones.

**Node (`package.json` → `scripts`)** — look for keys like `test`, `test:unit`,
`test:e2e`, `lint`, `typecheck`/`type-check`, `build`. Run via the project's
package manager: detect the lockfile (`package-lock.json`→npm,
`yarn.lock`→yarn, `pnpm-lock.yaml`→pnpm, `bun.lockb`→bun) and use
`npm run <script>` / `yarn <script>` / `pnpm <script>` / `bun run <script>`.

**Python (`pyproject.toml`)** — test runner is usually `pytest`; linters/format
under `[tool.ruff]`, `[tool.flake8]`, `[tool.black]`, `[tool.mypy]`. Common
commands: `pytest`, `ruff check .`, `mypy .`, `black --check .`.

**Go** — `go test ./...`, `go vet ./...`, `gofmt -l .`, and `golangci-lint run`
if configured.

**Rust** — `cargo test`, `cargo clippy`, `cargo fmt --check`.

**Java/Kotlin** — `mvn test` / `./gradlew test`, plus `checkstyle`/`spotbugs`/
`ktlint` if present.

**Ruby** — `bundle exec rspec`, `bundle exec rubocop`.

**Fallbacks** — also check a `Makefile` (targets like `test`, `lint`), CI config
(`.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`) which reveals the
exact commands the team trusts, and `pre-commit-config.yaml` for the lint/format
tools they've standardized on.

## 4. Determine review scope

- **Diff scope** (default for pre-commit/pre-merge): `git status --porcelain`
  for uncommitted work, or `git diff --name-only <base>...HEAD` (base is usually
  `main`/`master`/`develop`) for a branch. Hand agents the changed file list.
- **Full scope**: the whole subproject tree, for a full audit or a small repo.

If `git` isn't available or the repo isn't a git repo, fall back to full scope
and note it.
