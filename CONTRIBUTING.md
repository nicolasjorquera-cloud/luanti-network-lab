# Contributing

Thanks for your interest. This is a small learning homelab — keep changes small
and observable.

## Conventions

- **English only** for code, comments, docs, and commit messages.
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `ci:`, `chore:`, `infra:`.
- **Prefer small focused commits** over large ones.

## Checks

CI runs these on every push — run them locally too:

```bash
cd infra/terraform && terraform fmt -check && terraform validate
cd ../../rust/luanti-exporter && cargo fmt --check && cargo test
```

## Security

Never commit credentials. The service account key lives in Secret Manager.
Run `gitleaks detect` before pushing if you changed secrets-related files.
