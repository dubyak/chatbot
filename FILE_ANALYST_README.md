# 📊 Financial Document Upload Analyst

An AI-powered document analysis system for verifying the authenticity of financial documents submitted for loan applications. Uses LangChain agents and GPT-4 Vision to detect fraud, assess financial health, and generate targeted follow-up questions.

## 🎯 Purpose

This tool helps lending institutions analyze uploaded financial documents to:
- **Detect fraud**: Identify signs of document tampering or forgery
- **Assess authenticity**: Verify documents appear to be original and unaltered
- **Analyze financials**: Extract and evaluate cashflow patterns and financial health
- **Generate follow-ups**: Produce targeted questions to increase confidence in applications

## 🏗️ Architecture

### Multi-Agent System

The system uses specialized tools coordinated by a LangChain agent:

1. **Metadata Analyzer**: Examines PDF/image metadata for red flags
2. **Visual Inspector**: Uses GPT-4 Vision to detect visual inconsistencies
3. **Financial Analyzer**: Assesses financial patterns and cashflow

### Key Components

```
file_analyst_app.py      - Main Streamlit UI application
agent.py                 - LangChain agent orchestration
document_utils.py        - Document processing and metadata extraction
security_utils.py        - Security, audit logging, and compliance
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key with GPT-4 Vision access

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the application**:
```bash
streamlit run file_analyst_app.py
```

3. **Access the UI**:
   - Open browser to `http://localhost:8501`
   - Enter your OpenAI API key in the sidebar
   - Upload a financial document (PDF, PNG, or JPG)

## 📋 Supported Document Types

- **Bank Statements** - Checking/savings account statements
- **Tax Returns** - W-2, 1099 forms
- **Pay Stubs** - Employee wage statements
- **Investment Statements** - Brokerage and retirement accounts
- **Other Financial Documents** - Any financial proof document

## 🔍 What Gets Analyzed

### Metadata Analysis
- PDF creation date and modification history
- Software used to create/edit document
- Encryption status
- Text extractability (searchable vs. scanned)

### Visual Analysis (GPT-4 Vision)
- Font consistency
- Layout and alignment
- Professional quality assessment
- Signs of digital manipulation
- Screenshot vs. original detection
- Watermarks and security features

### Financial Pattern Analysis
- Income consistency
- Expense patterns
- Suspicious transactions (round numbers, unusual amounts)
- Balance trends
- NSF/overdraft indicators

### Authenticity Signals

**🚩 Red Flags:**
- Document created with image editing software
- Text not extractable (screenshot/scan)
- Low resolution or missing metadata
- Inconsistent fonts or formatting
- Suspicious round numbers
- Missing standard banking elements

**✅ Positive Signals:**
- Created with legitimate financial software
- High resolution with proper metadata
- Consistent professional formatting
- Extractable, searchable text
- Standard banking security features present

## 🛡️ Security Features

### Data Protection
- **Automatic deletion**: Files auto-delete after 24 hours
- **Audit logging**: All document access tracked
- **No persistent storage**: Analysis done in memory
- **Encrypted connections**: All API calls use HTTPS

### Compliance
- **GLBA-aware**: Designed with financial privacy regulations in mind
- **PII protection**: Sensitive data never logged in plain text
- **Data retention policies**: Configurable retention periods
- **Audit trails**: Complete access history

### File Validation
- File type verification (MIME type checking)
- Size limits (10MB max)
- Extension validation
- Malware-resistant processing

## 📊 Output Structure

The agent provides:

1. **Authenticity Score**: 0-100 confidence rating
2. **Red Flags**: List of concerning findings
3. **Positive Signals**: Indicators of authenticity
4. **Follow-up Questions**: 3-5 targeted questions for applicants
5. **Recommendation**: One of:
   - `approve` - Document appears authentic
   - `review` - Manual review recommended
   - `request_more` - Additional documentation needed
   - `deny` - Strong indicators of fraud

## 🔧 Configuration

### API Key Setup

**Option 1: Environment Variable** (Recommended)
```bash
export OPENAI_API_KEY="your-key-here"
```

**Option 2: Streamlit Secrets**
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-key-here"
```

**Option 3: UI Input**
Enter directly in the sidebar (less secure, for testing only)

### Customization

Edit these files to customize behavior:

- `agent.py`: Modify agent prompts and tools
- `document_utils.py`: Adjust red flag detection rules
- `security_utils.py`: Configure retention policies
- `file_analyst_app.py`: Customize UI and workflow

## 📈 Usage Examples

### Basic Analysis Flow

1. **Upload Document**: Drag-and-drop or select file
2. **Select Type**: Choose document type (bank statement, tax return, etc.)
3. **Analyze**: Click "Analyze Document" button
4. **Review Results**: See authenticity score, red flags, and recommendations
5. **Export**: Download JSON report for records

### Interpreting Results

**High Confidence (80-100)**:
- Original digital document
- Created with legitimate software
- No signs of tampering
- Consistent formatting and data

**Medium Confidence (50-79)**:
- Some minor concerns
- May be scanned copy
- Request additional verification
- Consider manual review

**Low Confidence (0-49)**:
- Multiple red flags detected
- Possible tampering or forgery
- Request original documents
- Strong consideration for denial

## 🧪 Testing

### Test with Sample Documents

Create test cases with:
- Authentic bank statements (downloaded from real banks)
- Screenshots of statements (should flag as less trustworthy)
- PDFs created in different software (observe metadata analysis)

### Expected Behavior

**Authentic Document**:
```
✅ Text extractable - original digital document
✅ Created with legitimate software: Adobe Acrobat
✅ High resolution with proper metadata
Authenticity Score: 85/100
```

**Suspicious Document**:
```
🚩 Created with image editing software: Photoshop
🚩 Text not extractable - possible screenshot
🚩 Low resolution (72 DPI)
Authenticity Score: 25/100
```

## 🚧 Limitations & Future Improvements

### Current Limitations

1. **PDF Visual Analysis**: Requires conversion to image for vision analysis
2. **OCR Extraction**: Limited numerical data extraction from images
3. **Template Matching**: No database of known bank statement formats
4. **Cross-Document**: Can't yet verify consistency across multiple uploads

### Planned Enhancements

**Phase 2**:
- Advanced OCR with numerical data extraction
- Cashflow calculation and analysis
- Debt-to-income ratio computation

**Phase 3**:
- Multi-document cross-verification
- Template matching against known formats
- Historical upload comparison

**Phase 4**:
- Real-time bank verification (Plaid integration)
- Machine learning fraud pattern detection
- Automated decision recommendations

## 🤝 Contributing

To extend this system:

1. **Add new detection rules**: Edit `document_utils.py`
2. **Create new agent tools**: Add to `agent.py`
3. **Enhance UI**: Modify `file_analyst_app.py`
4. **Add security features**: Extend `security_utils.py`

## 📝 Compliance Notes

This tool is designed for **concept validation** and **research purposes**. For production use:

- Consult with legal counsel on GLBA, FCRA, and Fair Lending compliance
- Implement proper user authentication and access controls
- Use dedicated secure storage (not session state)
- Implement proper encryption at rest
- Set up professional audit logging infrastructure
- Consider third-party security audits

## 📧 Support

For issues or questions about this implementation:
- Review code comments in each module
- Check agent prompt in `agent.py` for customization
- Examine `document_utils.py` for detection logic

## 📄 License

See LICENSE file for details.

---

**⚠️ Important**: This is a research tool for concept validation. Always conduct thorough testing and legal review before deploying in production for actual loan decisions.
