# Running Playwright Tests in Docker Container

A curated collection of **production-ready examples** demonstrating how to run Playwright tests in Docker containers across different programming languages and frameworks.

## 🎯 Why This Matters

- **Zero UI Interruptions**: Headless browsers run isolated in containers while you develop locally
- **Reproducible Tests**: Consistent environment across team members and CI/CD pipelines
- **Language Agnostic**: Examples for Python, TypeScript/Node, Java, and more
- **Simplified Focus**: Uses public websites (Google, GitHub) so you focus on Docker setup, not app logic

---

## 📁 Repository Structure

```
examples/
├── python-uv-3.13/          # Python 3.13+ with uv package manager ✅
├── typescript-node/          # TypeScript + Node.js (coming soon)
├── java-maven/               # Java + Maven (coming soon)
└── go-testify/               # Go + Testify (coming soon)

docs/
├── ARCHITECTURE.md           # High-level design & Docker setup
├── BEST_PRACTICES.md         # Testing patterns & tips
└── TROUBLESHOOTING.md        # Common issues & solutions
```

---

## 🚀 Quick Start

### Python 3.13+ with `uv`

The fastest way to get running:

```bash
git clone https://github.com/tobiashochguertel/running-playwright-tests-in-docker-container.git
cd running-playwright-tests-in-docker-container/examples/python-uv-3.13

# Build and run tests in Docker
make build
make test
```

**See [Python Example →](./examples/python-uv-3.13/README.md)**

---

## 📚 All Examples

| Language | Framework | Status | Docs |
|----------|-----------|--------|------|
| **Python** | 3.13+ + uv | ✅ Ready | [View →](./examples/python-uv-3.13/) |
| **TypeScript** | Node.js + Jest | 🔄 Coming | [View →](./examples/typescript-node/) |
| **Java** | Maven + JUnit | 🔄 Coming | [View →](./examples/java-maven/) |
| **Go** | Testify | 🔄 Coming | [View →](./examples/go-testify/) |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────┐
│   Your macOS/Linux Dev      │
│  • IDE • Code Changes       │
│  • Local Workflow Intact    │
└──────────────┬──────────────┘
               │ Docker API
               ▼
┌─────────────────────────────┐
│   Docker Container          │
│  • Headless Browsers        │
│  • Test Runner              │
│  • No UI Interruptions      │
└─────────────────────────────┘
```

For detailed architecture, see [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

---

## 📖 Key Documentation

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** — System design, Docker setup deep dive
- **[BEST_PRACTICES.md](./docs/BEST_PRACTICES.md)** — Testing patterns, CI/CD integration
- **[TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** — Common issues & solutions
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** — How to add new language examples

---

## 🤝 Contributing

We welcome contributions! To add a new language example:

1. Create a folder in `examples/` named `{language}-{framework}`
2. Add a `README.md` with setup & usage instructions
3. Include `Dockerfile`, `docker-compose.yml`, and working tests
4. Submit a PR—see [CONTRIBUTING.md](./CONTRIBUTING.md) for details

---

## 📝 License

MIT License — see [LICENSE](./LICENSE) for details.

---

## 🔗 Resources

- **[Playwright Documentation](https://playwright.dev/)** — Official docs & API reference
- **[Docker Documentation](https://docs.docker.com/)** — Container & Docker Compose guides
- **[uv Package Manager](https://docs.astral.sh/uv/)** — Fast Python package manager
- **[pytest](https://docs.pytest.org/)** — Python testing framework

---

**Ready to get started?** Pick an example above and dive in! 🚀
