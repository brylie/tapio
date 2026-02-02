# Contributing to Tapio Assistant

Thank you for considering contributing to Tapio Assistant! This document provides guidelines and instructions for contributing to this project.

## Table of Contents
- [Contributing to Tapio Assistant](#contributing-to-tapio-assistant)
  - [Table of Contents](#table-of-contents)
  - [Technical Architecture](#technical-architecture)
  - [Development Environment Setup](#development-environment-setup)
    - [Prerequisites](#prerequisites)
    - [Using Dev Container (Recommended)](#using-dev-container-recommended)
    - [Using GitHub Codespaces (Cloud Alternative)](#using-github-codespaces-cloud-alternative)
    - [Manual Setup (Alternative)](#manual-setup-alternative)
    - [Installing Required Models](#installing-required-models)
  - [Package Management](#package-management)
  - [Code Quality](#code-quality)
    - [Ruff](#ruff)
  - [Testing Guidelines](#testing-guidelines)
    - [Running Tests](#running-tests)
    - [Code Coverage](#code-coverage)
    - [Test Categories](#test-categories)
    - [Test Fixtures](#test-fixtures)
  - [Project Structure](#project-structure)
  - [Programmatic API](#programmatic-api)
    - [Using Factory Pattern (Recommended)](#using-factory-pattern-recommended)
    - [Manual Dependency Injection (Advanced)](#manual-dependency-injection-advanced)
    - [Key Components](#key-components)
  - [Configuration System](#configuration-system)
    - [Default Settings](#default-settings)
  - [Site Configurations](#site-configurations)
    - [Configuration Structure](#configuration-structure)
    - [Required vs Optional Fields](#required-vs-optional-fields)
    - [Adding New Sites](#adding-new-sites)
  - [Ollama for LLM Inference](#ollama-for-llm-inference)
  - [Pull Request Process](#pull-request-process)

## Technical Architecture

The following diagram illustrates the high-level architecture and data flow of the Tapio Assistant:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#f0f0f0', 'primaryTextColor': '#323232', 'primaryBorderColor': '#606060', 'lineColor': '#404040', 'secondaryColor': '#c0c0c0', 'tertiaryColor': '#e0e0e0' }}}%%
graph TD
    subgraph Data Pipeline
        A[Website Content] -->|Crawl| B[Raw HTML]
        B -->|Parse| C[Structured Markdown]
        C -->|Vectorize| D[ChromaDB Vector Store]
    end

    subgraph RAG System
        E[User Query] -->|Input| F[Gradio Interface]
        F -->|Query| G[Vector Search]
        G -->|Retrieve Docs| H[Context Assembly]
        H -->|Context + Query| I[Ollama LLM]
        I -->|Generate Response| F
    end

    D --> G

    subgraph Components
        J[crawler module] -.->|implements| A
        K[parsers module] -.->|implements| B --> C
        L[vectorstore module] -.->|implements| C
        M[utils module] -.->|supports| J & K & L
        N[gradio_app.py] -.->|implements| F & G & H & I
    end

    style A fill:#e0e0e0,stroke:#404040,stroke-width:1px,color:#232323
    style B fill:#e0e0e0,stroke:#404040,stroke-width:1px,color:#232323
    style C fill:#e0e0e0,stroke:#404040,stroke-width:1px,color:#232323
    style D fill:#ffcb8c,stroke:#404040,stroke-width:2px,color:#232323
    style E fill:#e0e0e0,stroke:#404040,stroke-width:1px,color:#232323
    style F fill:#9cd3ff,stroke:#404040,stroke-width:2px,color:#232323
    style G fill:#e0e0e0,stroke:#404040,stroke-width:1px,color:#232323
    style H fill:#e0e0e0,stroke:#404040,stroke-width:1px,color:#232323
    style I fill:#a3ffb0,stroke:#404040,stroke-width:2px,color:#232323
    style J fill:#e8e8e8,stroke:#404040,stroke-width:1px,color:#232323
    style K fill:#e8e8e8,stroke:#404040,stroke-width:1px,color:#232323
    style L fill:#e8e8e8,stroke:#404040,stroke-width:1px,color:#232323
    style M fill:#e8e8e8,stroke:#404040,stroke-width:1px,color:#232323
    style N fill:#e8e8e8,stroke:#404040,stroke-width:1px,color:#232323
```

The architecture follows a pipeline design with three main components:
1. **Data Pipeline**: Responsible for crawling, parsing, and vectorizing web content
2. **RAG System**: Handles user queries, vector search, and LLM response generation
3. **Components**: The specific modules that implement the functionality

## Development Environment Setup

### Prerequisites

Before starting development, ensure you have the following system tools installed:

- **Git**: For version control
- **Docker**: Required for dev container support (Docker Desktop recommended)
- **VS Code**: With the Dev Containers extension for dev container development

First, clone the repository:
```bash
git clone https://github.com/finntegrate/tapio.git
cd tapio
```

### Using Dev Container (Recommended)

This project includes a preconfigured development container that provides all necessary tools and dependencies.

**Requirements**: Docker must be installed on your system (Docker Desktop is recommended for ease of use).

If you're using VS Code:

1. Open the project in VS Code:
```bash
code .
```

2. VS Code will automatically detect the dev container configuration and prompt you to "Reopen in Container". Click this button to set up the development environment automatically.

The dev container includes:
- Python 3.12
- `uv` package manager
- Ollama for local LLM inference
- All required VS Code extensions (Python, Ruff, GitHub Copilot, etc.)
- Automatic dependency installation via `uv sync --dev`

### Using GitHub Codespaces (Cloud Alternative)

For a completely cloud-based development environment that requires no local setup:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/finntegrate/tapio?quickstart=1)

> [!WARNING]
> **Critical: Always stop your Codespace when not in use!**
>
> GitHub provides free Codespaces hours per month (typically 60-120 hours, subject to change). To avoid wasting your free hours:
> - **Manually stop your Codespace** every time you finish working
> - You can resume a stopped Codespace later, preserving all your work and changes
> - [Resume your most recent Codespace](https://codespaces.new/finntegrate/tapio?quickstart=1) for this repository

> [!TIP]
> **How to stop your Codespace:**
> 1. Go to [github.com/codespaces](https://github.com/codespaces)
> 2. Find your active Codespace for this repository
> 3. Click the "..." menu and select "Stop codespace"

The Codespace includes the same development environment as the local dev container:
- Python 3.12, `uv` package manager, and Ollama
- All required VS Code extensions pre-installed
- Automatic dependency installation

### Manual Setup (Alternative)

If you prefer not to use the dev container or are using a different editor:

1. Install `uv` package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and activate a virtual environment with uv:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# OR
.\.venv\Scripts\activate   # On Windows
```

3. Install dependencies:
```bash
uv sync --dev
```

4. Install Ollama for local LLM inference:
   - Follow the installation instructions at [ollama.ai](https://ollama.ai)

### Installing Required Models

Regardless of which setup method you chose, you'll need to install the required Ollama models for LLM text generation:

```bash
ollama pull llama3.2
```

**Note on Model Sizes**: Some Ollama models are substantially large (several GB) and may require significant computational resources. If you have limited disk space or computational power, consider experimenting with smaller parameter versions of models:

- `llama3.2:1b` - Lightweight 1 billion parameter version
- `llama3.2:3b` - Medium 3 billion parameter version
- `deepseek-r1:1.5b` - Efficient reasoning model
- `gemma3:1b` - Google's compact model
- `qwen3:1.7b` - Alibaba's efficient model

You can install any of these alternatives with:
```bash
ollama pull <model-name>
```

You can verify the model is installed by listing available models:

```bash
ollama list
```

**Embedding Models**: The vectorization process uses sentence-transformers models for generating embeddings (default: `all-MiniLM-L6-v2`). These models are automatically downloaded by the HuggingFace library when first used, so no manual installation is required.

*Note: While Ollama also provides embedding models (like `all-minilm`), the current implementation uses HuggingFace sentence-transformers models. If you've installed Ollama embedding models, they won't be used by the current vectorization process unless the code is modified to use Ollama embeddings instead.*

## Package Management

We use the `uv` package manager for this project. To add packages:

```bash
uv add <package-name>
```

Do not use `pip`, `uv pip install`, or `uv pip install -e .` to install packages or this project.

To synchronize dependencies from the lockfile:

```bash
uv sync
```

## Code Quality

### Ruff

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. Please ensure your code passes all checks before submitting a pull request.

You can run the linter with the following command:

```bash
uv run ruff check .
```

You can also run the linter with the `--fix` option to automatically fix some issues:

```bash
uv run ruff check . --fix
```


## Testing Guidelines

### Running Tests

When adding features, always include appropriate tests. Run the entire test suite with:

```bash
uv run pytest
```

### Code Coverage

We aim for high test coverage (minimum 80%). When submitting code:

1. Check your coverage with:

```bash
uv run pytest --cov=tapio
```

2. Generate HTML coverage reports for visual inspection:

```bash
uv run pytest --cov=tapio --cov-report=html
```

3. For specific module coverage:

```bash
uv run pytest --cov=tapio.utils tests/utils/
```

Aim for at least 80% coverage for new code. The HTML coverage report can be found in the `htmlcov` directory. Open `htmlcov/index.html` in your browser to view it.

### Test Categories

We maintain different types of tests:

**Unit Tests** - Fast, isolated tests with mocked dependencies:
```bash
uv run pytest -m "not integration"
```

**Integration Tests** - Tests using real components (marked with `@pytest.mark.integration`):
```bash
uv run pytest -m integration
```

**All Tests**:
```bash
uv run pytest
```

### Test Fixtures

Common mock fixtures are available in `tests/conftest.py`:
- `mock_embeddings` - Mocked HuggingFace embeddings
- `mock_chroma_store` - Mocked ChromaDB vector store
- `mock_llm_service` - Mocked LLM service
- `mock_doc_retrieval_service` - Mocked document retrieval service
- `mock_rag_orchestrator` - Mocked RAG orchestrator

Use these fixtures in your tests for consistent mocking:
```python
def test_my_feature(mock_rag_orchestrator):
    # Test uses mocked orchestrator
    pass
```

## Project Structure

The project has been designed with a clear separation of concerns:

- `crawler/`: Module responsible for crawling websites and saving HTML content
- `parsers/`: Module responsible for parsing HTML content into structured formats
- `vectorstore/`: Module responsible for vectorizing content and storing in ChromaDB
- `services/`: RAG orchestration and LLM services
- `config/`: Configuration settings for the project
- `app.py`: Gradio interface for the RAG chatbot
- `cli.py`: Command-line interface
- `factories.py`: Factory classes for dependency injection
- `utils/`: Utility modules for embedding generation, markdown processing, etc.
- `tests/`: Test suite for all modules

## Programmatic API

For developers who want to use Tapio as a library or extend its functionality:

### Using Factory Pattern (Recommended)

```python
from tapio import RAGConfig, RAGOrchestratorFactory

# Create configuration
config = RAGConfig(
    collection_name="my_docs",
    persist_directory="./db",
    llm_model_name="llama3.2",
    max_tokens=1024,
    num_results=5
)

# Create orchestrator using factory
factory = RAGOrchestratorFactory(config)
orchestrator = factory.create_orchestrator()

# Query the system
response, documents = orchestrator.query("What are the visa requirements?")
print(response)
```

### Manual Dependency Injection (Advanced)

For full control over component creation:

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

### Key Components

- **RAGOrchestrator**: Main orchestrator that coordinates document retrieval and LLM generation
- **DocumentRetrievalService**: Handles vector-based document retrieval
- **LLMService**: Manages LLM interactions via Ollama
- **ChromaStore**: Vector database abstraction layer
- **Factories**: Simplify dependency wiring with sensible defaults

## Configuration System

The application uses a centralized configuration system:

- `config/settings.py`: Contains global configuration settings used across different components
- `config/site_configs.yaml`: Site-specific parser configurations
- `config/config_models.py`: Pydantic models for configuration
- `config/config_manager.py`: Central manager for accessing configurations

When adding new features that require configuration values:

1. Use existing settings from `DEFAULT_DIRS` when possible
2. For new configuration needs, add them to the appropriate config file
3. Avoid hardcoding values that might need to change in the future
4. Use descriptive keys for configuration values

### Default Settings

Centralized configuration in `tapio/config/settings.py`:

```python
DEFAULT_DIRS = {
    "CRAWLED_DIR": "content/crawled",   # HTML storage
    "PARSED_DIR": "content/parsed",     # Markdown storage
    "CHROMA_DIR": "chroma_db",          # Vector database
}

DEFAULT_CHROMA_COLLECTION = "tapio"     # ChromaDB collection name
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_LLM_MODEL = "llama3.2"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_NUM_RESULTS = 5
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
  - `fallback_to_body` - Use full-body content if selectors fail (default: true)
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

## Ollama for LLM Inference

We use Ollama for local LLM inference.

The following Ollama models are used in the project:
- `llama3.2`: The base model for text generation.

To query the Ollama models that are installed, use the command:

```bash
ollama list
```

To list all Ollama commands, use the command:

```bash
ollama help
```

To get help for a specific command, use the command:

```bash
ollama <command> --help
```

Ensure you have the required models installed:

```bash
ollama pull llama3.2
```

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, if appropriate.
3. Make sure all tests pass and code is properly formatted with Ruff.
4. Check that code coverage meets our standards (minimum 80%).
5. Submit your pull request with a clear description of the changes, related issue numbers, and any special considerations.
6. The pull request will be merged once it receives approval from the maintainers.
