# 🚀 JarvisX — Full Advanced Desktop AI Assistant

**JarvisX** is a production-grade Windows desktop AI assistant with persistent memory, strong permission controls, and master-level skills capable of executing real projects on command.

## ✨ Features

- **🤖 Local AI**: Ollama integration with llama3 model
- **🧠 Persistent Memory**: Supabase-powered conversation history
- **🔐 Security**: Strict permission controls for dangerous actions
- **🎨 Beautiful UI**: Modern PyQt5 interface with light/dark themes
- **📊 Rich Output**: Charts, tables, and file previews
- **🛠️ 10 Master Skills**: NLP, ML, Data Science, ETL, Analytics, Automation, Cybersecurity, System Control, Web Search, UI/UX
- **🔄 Self-Updating**: Automatic updates with rollback capability
- **🧪 Auto-Evaluation**: Built-in skill testing and validation

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Ollama** running locally with llama3 model
3. **Supabase** project (for persistent memory)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jarvisx.git
cd jarvisx

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.template .env

# Edit .env with your Supabase credentials
notepad .env

# Start JarvisX
python main.py
```

### First Run Setup

1. **Configure Supabase**: Add your project URL and anon key to `.env`
2. **Start Ollama**: Ensure Ollama is running with `ollama run llama3`
3. **Launch App**: Run `python main.py`

## 🏗️ Architecture

```
JarvisX/
│── main.py                 # Application entry point
│── core/                   # Core system components
│   ├── app.py             # PyQt5 app bootstrap
│   ├── assistant.py       # Main orchestrator
│   ├── router.py          # Intent classification
│   ├── memory.py          # Supabase + local cache
│   ├── models.py          # LLM adapters
│   ├── permissions.py     # Security engine
│   └── ...
│── ui/                    # User interface
│   ├── chat_window.py     # Main window
│   ├── widgets.py         # Rich components
│   └── assets/            # Themes & icons
│── skills/                # AI capabilities
│   ├── nlp.py            # Natural language processing
│   ├── ml.py             # Machine learning
│   ├── data_science.py   # Data analysis
│   └── ...
│── tools/                 # Utility tools
│── tests/                 # Test suite
│── logs/                  # Application logs
│── temp/                  # Temporary files
```

## 🧩 Skills Overview

### 1. **NLP** - Natural Language Processing
- Text summarization and rewriting
- Project plan generation
- Requirement extraction
- Translation assistance

### 2. **AI/ML** - Machine Learning
- Train/test small models (LogReg, RandomForest)
- Model evaluation and metrics
- Prediction on new data
- Model persistence

### 3. **Data Science** - Exploratory Data Analysis
- Statistical summaries
- Data profiling
- Visualization (histograms, scatter plots)
- Missing data analysis

### 4. **Data Engineering** - ETL Pipelines
- Extract from CSV/JSON/HTTP
- Transform and clean data
- Load to SQLite/CSV
- Schema validation

### 5. **Analytics** - Business Intelligence
- SQL queries on SQLite
- KPI dashboards
- Data aggregation
- Report generation

### 6. **Automation** - Workflow Management
- Task sequencing (YAML)
- Batch operations
- Windows Task Scheduler integration
- File operations

### 7. **Cybersecurity** - Security Analysis
- Password strength checking
- File hash verification
- Log analysis
- Security scanning

### 8. **System Control** - OS Integration
- Application launching
- File operations
- Shell command execution
- System monitoring

### 9. **Web Search** - Information Retrieval
- Web scraping
- API integration
- Content summarization
- Link extraction

### 10. **UI/UX** - Interface Design
- Wireframe generation
- Component trees
- CSS/QSS suggestions
- Design reviews

## 🎯 Example Commands

### Data Science
```
"Create a binary classifier on heart.csv and evaluate it"
"Do EDA on sales.csv and show me the trends"
"Build an ETL pipeline: read users.csv, clean nulls, load to SQLite"
```

### Project Management
```
"Generate a project plan for a Flask dashboard that ingests CSV and shows KPIs"
"Create a brief for a React e-commerce app with user authentication"
"Write requirements for a Python API that processes sensor data"
```

### System Operations
```
"Open Chrome and navigate to github.com"
"Scan this system.log for errors and suspicious activity"
"Create a backup of the documents folder"
```

### Automation
```
"Create a workflow to compress all PDFs in the downloads folder"
"Schedule a daily backup task at 2 AM"
"Batch rename all .txt files to add date prefix"
```

## 🔐 Security & Permissions

JarvisX implements a strict permission model:

- **Dangerous Actions**: File writes, process execution, system control require explicit confirmation
- **Permission Levels**: Ask every time (default), trusted once, always deny
- **Dry-Run Mode**: Preview actions before execution
- **Action Logging**: All privileged operations are logged with timestamps

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_skills.py
pytest tests/test_permissions.py
pytest tests/test_memory.py

# Generate coverage report
pytest --cov=core --cov=skills --cov=ui tests/
```

## 📦 Packaging

### PyInstaller Build

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-folder distribution
pyinstaller --noconfirm --clean --onedir --name JarvisX \
  --add-data "ui/assets;ui/assets" \
  --hidden-import "sklearn.utils._cython_blas" \
  main.py

# Build single executable
pyinstaller --noconfirm --clean --onefile --name JarvisX \
  --add-data "ui/assets;ui/assets" \
  --hidden-import "sklearn.utils._cython_blas" \
  main.py
```

### Common DLL Issues

If you encounter DLL issues with PyQt5 or sklearn:

1. **PyQt5 DLLs**: Copy from `site-packages/PyQt5/Qt5/bin/` to dist folder
2. **sklearn DLLs**: Use `--hidden-import` flags for missing modules
3. **Visual C++ Redistributable**: Ensure latest version is installed

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check OLLAMA_HOST in .env
   - Verify llama3 model: `ollama list`

2. **Supabase Connection Error**
   - Verify SUPABASE_URL and SUPABASE_ANON_KEY
   - Check internet connection
   - Ensure Supabase project is active

3. **PyQt5 Import Error**
   - Reinstall PyQt5: `pip uninstall PyQt5 && pip install PyQt5==5.15.11`
   - Check Python version compatibility

4. **Permission Denied Errors**
   - Check file permissions
   - Run as administrator if needed
   - Verify .env configuration

### Logs

Check logs in the `logs/` directory:
- `jarvisx.log` - Application logs
- `actions.jsonl` - Permission and action logs
- `errors.log` - Error details

## 🔄 Updates

JarvisX can self-update from a remote repository:

1. Set `REMOTE_UPDATE_URL` in `.env`
2. Updates are downloaded and verified
3. Automatic rollback on failure
4. Manual update check via Settings menu

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: This README and inline code docs

---

**Built with ❤️ using Python, PyQt5, and modern AI technologies**