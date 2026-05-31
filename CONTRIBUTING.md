# Contributing

Thanks for contributing to DoclingRAG!

## Development setup

1. Fork and clone the repo
2. `pnpm install`
3. `pip install -r apps/worker/requirements.txt`
4. Run worker + web (see README)

## Pull requests

- Use conventional commits (`feat:`, `fix:`, `chore:`)
- Ensure `pnpm lint`, `pnpm typecheck`, and tests pass
- Add tests for new behavior

## Code style

- TypeScript strict mode for web/packages
- Python 3.12 + type hints for worker
