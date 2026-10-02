# Contributing to JARVIS Runtime

Thank you for your interest in contributing to the JARVIS AI Runtime!

## Development Guidelines

1. **Architecture Compliance**:
   - Strictly follow Hexagonal Architecture (Ports & Adapters).
   - Domain layer must never import from application, ports, or adapters.
   - Application layer communicates with infrastructure strictly via Ports (`ABCs`).
   - All adapters must implement exactly one port.

2. **Branch Naming Conventions**:
   - `feature/<description>` — New capabilities or workflow nodes.
   - `bugfix/<description>` — Bug and regression fixes.
   - `chore/<description>` — Tooling, dependency, or configuration updates.
   - `docs/<description>` — Documentation improvements.

3. **Code Quality**:
   - Ensure all code conforms to Ruff formatting and linting rules:
     ```bash
     make format
     make lint
     make typecheck
     ```
   - All checks must pass before opening a Pull Request:
     ```bash
     make quality
     ```

4. **Testing**:
   - Every LangGraph node and domain model must have unit test coverage.
   - Run tests locally:
     ```bash
     make test-unit
     ```
   - Target coverage is 80%+ (`make test-cov`).

5. **Pull Requests**:
   - Write clear PR descriptions referencing issues.
   - Ensure CI passes without warnings.

## Lead Maintainer

- **Vidit Jain** (<team@jarvis.dev>)
