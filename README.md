# 💬 Chatbot Applications

This repository contains two Streamlit applications:

## 1. 💬 Simple Chatbot (Original)
A simple Streamlit app that shows how to build a chatbot using OpenAI's GPT-3.5.

**Run it:**
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 2. 📊 Financial Document Analyst (NEW)
An AI-powered document analysis system for verifying authenticity of financial documents for loan applications. Uses LangChain agents and GPT-4 Vision to detect fraud and assess financial health.

**Quick Start:**
```bash
pip install -r requirements.txt
streamlit run file_analyst_app.py
```

**Key Features:**
- 🔍 Document authenticity verification
- 🚩 Fraud detection using metadata and visual analysis
- 💰 Financial pattern analysis
- 📝 Automated follow-up question generation
- 🔒 Security-first with audit logging and auto-deletion

**Documentation:**
- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Full Documentation](FILE_ANALYST_README.md) - Complete system details

### Supported Document Types
- Bank statements
- Tax returns (W-2, 1099)
- Pay stubs
- Investment statements
- Other financial documents

### What It Analyzes
✅ PDF/image metadata (creation date, software used)
✅ Visual consistency (fonts, formatting, quality)
✅ Financial patterns (income, expenses, transactions)
✅ Authenticity signals (red flags vs. positive indicators)

**Output:** Authenticity score (0-100), red flags, follow-up questions, and recommendation (approve/review/deny)

---

### System Requirements

- Python 3.11+
- OpenAI API key (with GPT-4 Vision access for Document Analyst)
