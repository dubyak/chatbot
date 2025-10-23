# 🚀 Quick Start Guide - Financial Document Analyst

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This will install:
- Streamlit (UI framework)
- LangChain (agent framework)
- OpenAI (GPT-4 Vision API)
- PyPDF2, Pillow (document processing)
- And other dependencies

## Step 2: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. **Important**: Make sure you have GPT-4 Vision access

## Step 3: Run the Application

### Option A: Enter API Key in UI (Quick Test)

```bash
streamlit run file_analyst_app.py
```

Then enter your API key in the sidebar when the app opens.

### Option B: Use Environment Variable (Recommended)

```bash
export OPENAI_API_KEY="your-key-here"
streamlit run file_analyst_app.py
```

### Option C: Use Streamlit Secrets (Production)

1. Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-key-here"
```

2. Run the app:
```bash
streamlit run file_analyst_app.py
```

## Step 4: Upload and Analyze

1. **Open Browser**: Go to `http://localhost:8501`
2. **Select Document Type**: Choose from dropdown (Bank Statement, Tax Return, etc.)
3. **Upload File**: Click "Browse files" or drag-and-drop
4. **Analyze**: Click "🔍 Analyze Document" button
5. **Review Results**: See authenticity score and detailed analysis

## 📝 Testing the System

### Test Document Types

Try uploading:
- ✅ **Authentic PDF**: Download a real statement from your bank
- ⚠️ **Screenshot**: Take screenshot of a document (will flag as less trustworthy)
- 📄 **Image**: Photo of a document (will detect as possible re-photographed)

### What to Look For

The system will analyze:
1. **Metadata** (creation date, software used)
2. **Visual Quality** (resolution, fonts, consistency)
3. **Authenticity Signals** (red flags vs. positive indicators)

## 🔧 Common Issues

### Issue: "API key not set"
**Solution**: Make sure you entered your OpenAI API key in the sidebar

### Issue: "File too large"
**Solution**: Files must be under 10MB. Compress or use a different file.

### Issue: "File type not supported"
**Solution**: Only PDF, PNG, and JPG files are accepted

### Issue: "Rate limit exceeded"
**Solution**: Wait a few moments. GPT-4 Vision has rate limits. Consider upgrading your OpenAI plan.

### Issue: Import errors
**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

## 📊 Understanding Results

### Authenticity Score

- **90-100**: High confidence - appears authentic
- **70-89**: Good confidence - minor concerns
- **50-69**: Medium confidence - manual review recommended
- **30-49**: Low confidence - request more documentation
- **0-29**: Very low confidence - likely fraudulent

### Red Flags

Common red flags include:
- Created with image editing software
- Low resolution or missing metadata
- Text not extractable (screenshot)
- Inconsistent formatting
- Suspicious patterns

### Follow-up Questions

The agent generates 3-5 targeted questions like:
- "Can you provide the original PDF from your bank?"
- "Do you have additional months of statements?"
- "Can you provide bank contact for verification?"

## 🎯 Next Steps

Once you've tested the basic functionality:

1. **Review Analysis Quality**: See if results match your expectations
2. **Test Edge Cases**: Try different document types and qualities
3. **Customize Prompts**: Edit `agent.py` to adjust analysis focus
4. **Add Red Flags**: Extend `document_utils.py` with domain-specific rules
5. **Review Security**: Check `security_utils.py` for compliance needs

## 💡 Tips for Best Results

1. **Use Original PDFs**: Direct downloads from banks work best
2. **High Quality Images**: If using images, ensure high resolution (300+ DPI)
3. **Clear Document Type**: Select the correct type in dropdown
4. **Multiple Documents**: Analyze several documents from same applicant for patterns
5. **Review Agent Output**: Check the reasoning, not just the score

## 📚 Full Documentation

For detailed documentation, see:
- **FILE_ANALYST_README.md**: Complete system documentation
- **agent.py**: Comments on agent architecture
- **document_utils.py**: Document processing details
- **security_utils.py**: Security and compliance features

## 🆘 Getting Help

If something isn't working:

1. Check the terminal for error messages
2. Review the application logs in the Streamlit UI
3. Verify your OpenAI API key is valid and has GPT-4 Vision access
4. Check that all dependencies installed correctly
5. Try with a simple, clean PDF first

## 🔐 Security Reminders

- **Don't commit API keys**: Never add `.env` or secrets to git
- **Test data only**: Use test documents, not real customer data during development
- **24-hour deletion**: Files automatically delete after 24 hours
- **Audit logging**: All operations are logged in `audit_log.json`

---

Happy analyzing! 🎉
