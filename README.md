# Free Learn - Educational Resource Crawler

A scalable Nx monorepo for crawling and collecting educational resources across multiple platforms.

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 8.0.0
- **Python** >= 3.8
- **Git**

### Setup

1. **Clone and Install Dependencies**

   ```bash
   git clone <repository-url>
   cd free-learn
   pnpm install
   ```

2. **Setup Python Environment**

   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # venv\Scripts\activate   # On Windows

   # Install Python dependencies
   cd apps/data-crawler
   pip install -r requirements.txt
   cd ../..
   ```

3. **Install Development Tools**

   ```bash
   # Install Python linting and formatting tools
   pip install black flake8 isort mypy pytest pytest-cov
   ```

## 📁 Project Structure

```
free-learn/
├── apps/
│   └── data-crawler/           # Python crawler application
│       ├── src/               # Source code
│       ├── output/            # Crawler output
│       ├── main.py           # Entry point
│       ├── project.json      # Nx project configuration
│       └── requirements.txt  # Python dependencies
├── libs/                      # Shared libraries (future)
├── .vscode/
│   └── settings.json         # VS Code configuration
├── package.json              # Node.js dependencies and scripts
├── pnpm-workspace.yaml       # pnpm workspace configuration
├── pyproject.toml           # Python project configuration
├── .prettierrc              # Code formatting rules
├── nx.json                  # Nx workspace configuration
└── README.md               # This file
```

## 🛠️ Available Scripts

### Root Level Commands

```bash
# Start the crawler with example parameters
pnpm start:crawler:example

# Start the crawler with custom parameters
pnpm start:crawler

# Run linting across all projects
pnpm lint

# Format all code (Python, JSON, YAML, Markdown)
pnpm format

# Type checking across all projects
pnpm type-check

# Run tests across all projects
pnpm test

# Build all projects
pnpm build
```

### Nx-Specific Commands

```bash
# Run specific project tasks
nx run data-crawler:run
nx run data-crawler:lint
nx run data-crawler:format

# Run tasks on affected projects only
nx affected --target=lint
nx affected --target=test
nx affected --target=build

# View dependency graph
nx graph

# Reset Nx cache
nx reset
```

### Direct Crawler Usage

```bash
cd apps/data-crawler

# Basic usage
python main.py "computer science" --limit 10

# Advanced usage
python main.py "machine learning" --limit 50
python main.py "web development" --limit 25
```

## 🔧 Development Workflow

### 1. Code Formatting

The project uses consistent formatting across all file types:

- **Python**: Black + isort + Flake8
- **JSON/YAML**: Prettier
- **Markdown**: Prettier

Run formatting:

```bash
pnpm format
```

### 2. Linting

```bash
# Lint all projects
pnpm lint

# Lint specific project
nx run data-crawler:lint
```

### 3. Type Checking

```bash
# Type check all Python code
pnpm type-check

# Type check specific project
nx run data-crawler:type-check
```

### 4. Git Hooks

The project includes pre-commit hooks using Husky and lint-staged:

```bash
# Install git hooks (run once)
pnpm prepare
```

This will automatically format and lint staged files before commits.

## 🏗️ Architecture & Design

### Nx Monorepo Benefits

- **Consistent tooling** across all projects
- **Shared libraries** and utilities
- **Efficient caching** and task orchestration
- **Dependency graph** visualization
- **Affected project** detection

### Python Project Structure

The crawler follows Python best practices:

- **Modular design** with separate concerns
- **Type hints** for better code quality
- **Async support** for scalable web crawling
- **Configurable logging** and output
- **Extensible connector** architecture

### VS Code Integration

Optimized developer experience with:

- **Auto-formatting** on save
- **Integrated linting** and type checking
- **Python intellisense** and debugging
- **Nx task runner** integration
- **Consistent settings** across team members

## 📈 Scalability & Future Additions

### Backend Services

The monorepo is designed to easily accommodate:

```bash
# Future backend structure
apps/
├── data-crawler/          # Current Python crawler
├── api-server/           # FastAPI/Django REST API
├── data-processor/       # Data processing service
├── notification-service/ # Email/webhook notifications
└── web-scraper/         # Additional scraping service
```

### Frontend Applications

```bash
# Future frontend structure
apps/
├── web-dashboard/        # React/Next.js dashboard
├── mobile-app/          # React Native mobile app
└── admin-panel/         # Admin interface
```

### Shared Libraries

```bash
# Shared code structure
libs/
├── shared-types/        # TypeScript type definitions
├── python-utils/        # Python utility functions
├── api-client/         # API client library
└── ui-components/      # Reusable UI components
```

### Adding New Projects

1. **Create new app/library**:

   ```bash
   # For Python projects
   mkdir apps/new-python-app
   # Copy and modify project.json from data-crawler

   # For Node.js projects
   nx g @nx/node:app new-node-app
   ```

2. **Configure project.json**:

   ```json
   {
     "name": "new-project",
     "projectType": "application",
     "targets": {
       "build": { "executor": "nx:run-commands", ... },
       "serve": { "executor": "nx:run-commands", ... },
       "lint": { "executor": "nx:run-commands", ... }
     }
   }
   ```

3. **Update workspace dependencies**:
   - Add to `pnpm-workspace.yaml` if needed
   - Configure inter-project dependencies in Nx

## 🔍 Monitoring & Debugging

### Logs

```bash
# View crawler logs
tail -f apps/data-crawler/crawler.log

# Follow real-time output
python apps/data-crawler/main.py "topic" --limit 5
```

### Performance

```bash
# Analyze Nx performance
nx report

# View task execution times
nx run data-crawler:run --verbose
```

### Dependency Analysis

```bash
# View project dependencies
nx graph

# Check for circular dependencies
nx lint --fix
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the established patterns
4. **Run quality checks**: `pnpm lint && pnpm type-check && pnpm format`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## 📝 Configuration Files

### Key Configuration Files

- **`nx.json`**: Nx workspace configuration
- **`project.json`**: Individual project configurations
- **`pyproject.toml`**: Python project settings and tool configurations
- **`.vscode/settings.json`**: VS Code workspace settings
- **`package.json`**: Node.js dependencies and scripts
- **`.prettierrc`**: Code formatting rules

### Environment Variables

Create a `.env` file in the project root:

```env
# Example environment variables
CRAWLER_LOG_LEVEL=INFO
CRAWLER_OUTPUT_DIR=./output
CRAWLER_RATE_LIMIT=1
```

## 🚨 Troubleshooting

### Common Issues

1. **Python virtual environment not activated**:

   ```bash
   source venv/bin/activate
   ```

2. **Missing Python dependencies**:

   ```bash
   cd apps/data-crawler
   pip install -r requirements.txt
   ```

3. **Node.js version conflicts**:

   ```bash
   nvm use 18  # or your preferred version
   ```

4. **Nx cache issues**:
   ```bash
   nx reset
   ```

### Support

For issues and questions:

- Check the [Issues](https://github.com/your-org/free-learn/issues) page
- Review the [Wiki](https://github.com/your-org/free-learn/wiki) for detailed guides
- Contact the development team

---

**Built with ❤️ using Nx, Python, and modern development practices**
