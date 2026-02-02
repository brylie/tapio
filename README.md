# Tapio
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Tapio is a RAG (Retrieval Augmented Generation) tool for extracting, processing, and querying information from websites like Migri.fi (Finnish Immigration Service). It provides complete workflow capabilities including web crawling, content parsing, vectorization, and an interactive chatbot interface.

## Version 2.0 - Breaking Changes

**Version 2.0 introduces dependency injection throughout the codebase for improved testability and maintainability.**

### What Changed

- **Service constructors** now accept dependencies instead of creating them internally
- **Factory pattern** introduced for easy object creation: `RAGOrchestratorFactory`, `VectorizerFactory`
- **Configuration classes** added: `RAGConfig` for grouping related parameters
- **CLI commands** remain the same - no user-facing changes to the command interface

### For Advanced Users

If you were directly instantiating classes in your code (not using the CLI), update as follows:

**Before (v1.x):**
```python
from tapio.services.rag_orchestrator import RAGOrchestrator

orchestrator = RAGOrchestrator(
    collection_name="my_docs",
    persist_directory="./db",
    model_name="llama3.2",
    max_tokens=1024
)
```

**After (v2.0) - Using Factory (Recommended):**
```python
from tapio import RAGConfig, RAGOrchestratorFactory

config = RAGConfig(
    collection_name="my_docs",
    persist_directory="./db",
    llm_model_name="llama3.2",
    max_tokens=1024
)
factory = RAGOrchestratorFactory(config)
orchestrator = factory.create_orchestrator()
```

**After (v2.0) - Manual (Advanced):**
```python
from langchain_huggingface import HuggingFaceEmbeddings
from tapio.vectorstore.chroma_store import ChromaStore
from tapio.services.document_retrieval_service import DocumentRetrievalService
from tapio.services.llm_service import LLMService
from tapio.services.rag_orchestrator import RAGOrchestrator

# Create dependencies
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
chroma_store = ChromaStore("my_docs", embeddings, "./db")
doc_service = DocumentRetrievalService(chroma_store, num_results=5)
llm_service = LLMService(model_name="llama3.2", max_tokens=1024)

# Create orchestrator
orchestrator = RAGOrchestrator(doc_service, llm_service)
```

### Testing Improvements

Version 2.0 includes:
- Mock fixtures for all major components in `tests/conftest.py`
- Integration tests using real components (run with `pytest -m integration`)
- Improved unit test isolation without import patching

Run fast unit tests only:
```bash
uv run pytest -m "not integration"
```

Run all tests including integration:
```bash
uv run pytest
```

## Features
- **Multi-site support** - Configurable site-specific crawling and parsing
- **End-to-end pipeline** - Crawl → Parse → Vectorize → Query workflow
- **Local LLM integration** - Uses Ollama for private, local inference
- **Semantic search** - ChromaDB vector database for relevant content retrieval
- **Interactive chatbot** - Web interface for natural language queries
- **Flexible crawling** - Configurable depth and domain restrictions
- **Comprehensive testing** - Full test suite for reliability

## Target Use Cases

**Primary Users:** EU and non-EU citizens navigating Finnish immigration processes
- Students seeking education information
- Workers exploring employment options
- Families pursuing reunification
- Refugees and asylum seekers needing guidance

**Core Needs:**
- Finding relevant, accurate information quickly
- Practice conversations on specific topics (family reunification, work permits, etc.)

## Installation and Setup

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- [Ollama](https://ollama.ai/) - For local LLM inference

### Quick Start

1. Clone and setup:
```bash
git clone https://github.com/Finntegrate/tapio.git
cd tapio
uv sync
```

2. Install required Ollama model:
```bash
ollama pull llama3.2
```

## Usage

### CLI Overview

Tapio provides a four-step workflow:

1. **crawl** - Collect HTML content from websites
2. **parse** - Convert HTML to structured Markdown
3. **vectorize** - Create vector embeddings for semantic search
4. **tapio-app** - Launch the interactive chatbot interface

Use `uv run -m tapio.cli --help` to see all commands or `uv run -m tapio.cli <command> --help` for command-specific options.

### Quick Example

Complete workflow for the Migri website:

```bash
# 1. Crawl content (uses site configuration)
uv run -m tapio.cli crawl migri --depth 2

# 2. Parse HTML to Markdown
uv run -m tapio.cli parse migri

# 3. Create vector embeddings
uv run -m tapio.cli vectorize

# 4. Launch chatbot interface
uv run -m tapio.cli tapio-app
```

### Available Sites

To list configured sites:
```bash
uv run -m tapio.cli list-sites
```

To view detailed site configurations:
```bash
uv run -m tapio.cli list-sites --verbose
```

## Site Configurations

Site configurations define how to crawl and parse specific websites. They're stored in `tapio/config/site_configs.yaml` and used by both crawl and parse commands.

### Configuration Structure

```yaml
sites:
  migri:
    base_url: "https://migri.fi"                # Used for crawling and converting relative links
    description: "Finnish Immigration Service website"
    crawler_config:                            # Crawling behavior
      delay_between_requests: 1.0              # Seconds between requests
      max_concurrent: 3                        # Concurrent request limit
    parser_config:                              # Parser-specific configuration
      title_selector: "//title"                # XPath for page titles
      content_selectors:                       # Priority-ordered content extraction
        - '//div[@id="main-content"]'
        - "//main"
        - "//article"
        - '//div[@class="content"]'
      fallback_to_body: true                   # Use <body> if selectors fail
      markdown_config:                         # HTML-to-Markdown options
        ignore_links: false
        body_width: 0                          # No text wrapping
        protect_links: true
        unicode_snob: true
        ignore_images: false
        ignore_tables: false
```

### Required vs Optional Fields

**Required:**
- `base_url` - Base URL for the site (used for crawling and link resolution)

**Optional (with defaults):**
- `description` - Human-readable description
- `parser_config` - Parser-specific settings (uses defaults if omitted)
  - `title_selector` - Page title XPath (default: "//title")
  - `content_selectors` - XPath selectors for content extraction (default: ["//main", "//article", "//body"])
  - `fallback_to_body` - Use full body content if selectors fail (default: true)
  - `markdown_config` - HTML conversion settings (uses defaults if omitted)
- `crawler_config` - Crawling behavior settings (uses defaults if omitted)
  - `delay_between_requests` - Delay between requests in seconds (default: 1.0)
  - `max_concurrent` - Maximum concurrent requests (default: 5)

### Adding New Sites

1. Analyze the target website's structure
2. Identify XPath selectors for content extraction
3. Add configuration to `site_configs.yaml`:

```yaml
sites:
  my_site:
    base_url: "https://example.com"
    description: "Example site configuration"
    parser_config:
      content_selectors:
        - '//div[@class="main-content"]'
```

4. Use with commands:
```bash
uv run -m tapio.cli crawl my_site
uv run -m tapio.cli parse my_site
uv run -m tapio.cli vectorize
uv run -m tapio.cli tapio-app
```

## Configuration

Tapio uses centralized configuration in `tapio/config/settings.py`:

```python
DEFAULT_DIRS = {
    "CRAWLED_DIR": "content/crawled",   # HTML storage
    "PARSED_DIR": "content/parsed",     # Markdown storage
    "CHROMA_DIR": "chroma_db",          # Vector database
}

DEFAULT_CHROMA_COLLECTION = "tapio"     # ChromaDB collection name
```

Site-specific configurations are in `tapio/config/site_configs.yaml` and automatically handle content extraction and directory organization based on the site's domain.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, code style requirements, and how to submit pull requests.

## License

Licensed under the European Union Public License version 1.2. See LICENSE for details.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/brylie"><img src="https://avatars.githubusercontent.com/u/17307?v=4?s=100" width="100px;" alt="Brylie Christopher Oxley"/><br /><sub><b>Brylie Christopher Oxley</b></sub></a><br /><a href="#infra-brylie" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/finntegrate/tapio/commits?author=brylie" title="Tests">⚠️</a> <a href="https://github.com/finntegrate/tapio/commits?author=brylie" title="Documentation">📖</a> <a href="https://github.com/finntegrate/tapio/issues?q=author%3Abrylie" title="Bug reports">🐛</a> <a href="#business-brylie" title="Business development">💼</a> <a href="#content-brylie" title="Content">🖋</a> <a href="#ideas-brylie" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-brylie" title="Maintenance">🚧</a> <a href="#mentoring-brylie" title="Mentoring">🧑‍🏫</a> <a href="#projectManagement-brylie" title="Project Management">📆</a> <a href="#promotion-brylie" title="Promotion">📣</a> <a href="#research-brylie" title="Research">🔬</a> <a href="https://github.com/finntegrate/tapio/pulls?q=is%3Apr+reviewed-by%3Abrylie" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/finntegrate/tapio/commits?author=brylie" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://akikurvinen.fi/"><img src="https://avatars.githubusercontent.com/u/74042688?v=4?s=100" width="100px;" alt="AkiKurvinen"/><br /><sub><b>AkiKurvinen</b></sub></a><br /><a href="#data-AkiKurvinen" title="Data">🔣</a> <a href="https://github.com/finntegrate/tapio/commits?author=AkiKurvinen" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ResendeTech"><img src="https://avatars.githubusercontent.com/u/142721352?v=4?s=100" width="100px;" alt="ResendeTech"/><br /><sub><b>ResendeTech</b></sub></a><br /><a href="https://github.com/finntegrate/tapio/commits?author=ResendeTech" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!