"""
Financial Document Upload Analyst - Streamlit Application
Multi-agent system for analyzing uploaded financial documents for loan applications.
"""

import streamlit as st
import os
from datetime import datetime, timedelta
import json
from pathlib import Path
from agent import create_analyst_agent
from document_utils import DocumentProcessor, get_file_info_summary


# Page configuration
st.set_page_config(
    page_title="Financial Document Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .analysis-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .red-flag {
        color: #d32f2f;
        font-weight: 600;
    }
    .positive-signal {
        color: #388e3c;
        font-weight: 600;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'uploaded_files_data' not in st.session_state:
        st.session_state.uploaded_files_data = {}


def cleanup_old_files():
    """Remove uploaded files older than 24 hours (security measure)."""
    if 'uploaded_files_data' in st.session_state:
        current_time = datetime.now()
        files_to_remove = []

        for file_id, file_info in st.session_state.uploaded_files_data.items():
            upload_time = file_info.get('upload_time')
            if upload_time and (current_time - upload_time) > timedelta(hours=24):
                files_to_remove.append(file_id)

        for file_id in files_to_remove:
            del st.session_state.uploaded_files_data[file_id]


def display_header():
    """Display application header."""
    st.markdown('<p class="main-header">📊 Financial Document Analyst</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-Powered Document Authenticity & Financial Analysis</p>',
        unsafe_allow_html=True
    )

    with st.expander("ℹ️ About This Tool"):
        st.markdown("""
        This tool uses advanced AI to analyze financial documents for loan applications:

        **What we analyze:**
        - Document authenticity and fraud indicators
        - Financial health and cashflow patterns
        - Metadata and creation history
        - Visual consistency and quality

        **Supported documents:**
        - Bank statements (PDF, PNG, JPG)
        - Tax returns (W-2, 1099)
        - Pay stubs
        - Investment statements

        **Privacy & Security:**
        - Files are analyzed in memory and automatically deleted after 24 hours
        - No data is permanently stored
        - All connections are encrypted
        """)


def display_sidebar():
    """Display sidebar with configuration and info."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Your OpenAI API key for GPT-4 Vision analysis"
        )

        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key Set")
        else:
            st.warning("⚠️ Please enter your OpenAI API key")

        st.divider()

        # Document type selection
        st.subheader("Document Type")
        doc_type = st.selectbox(
            "Select document type",
            [
                "Bank Statement",
                "Tax Return (W-2)",
                "Tax Return (1099)",
                "Pay Stub",
                "Investment Statement",
                "Other Financial Document"
            ]
        )
        st.session_state.document_type = doc_type

        st.divider()

        # Analysis history
        st.subheader("📋 Analysis History")
        if st.session_state.analysis_history:
            st.metric("Total Analyzed", len(st.session_state.analysis_history))
            if st.button("Clear History"):
                st.session_state.analysis_history = []
                st.rerun()
        else:
            st.info("No documents analyzed yet")

        st.divider()

        # Security info
        with st.expander("🔒 Security Info"):
            st.caption(f"Files auto-delete after: 24 hours")
            st.caption(f"Current session files: {len(st.session_state.uploaded_files_data)}")


def process_uploaded_file(uploaded_file):
    """Process uploaded file and return analysis."""
    if not hasattr(st.session_state, 'api_key') or not st.session_state.api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar")
        return None

    try:
        # Read file data
        file_data = uploaded_file.read()
        filename = uploaded_file.name

        # Create document processor
        processor = DocumentProcessor()

        # Validate file
        is_valid, error_msg = processor.validate_file(file_data, filename)
        if not is_valid:
            st.error(f"❌ File Validation Failed: {error_msg}")
            return None

        # Store file data (with timestamp for cleanup)
        file_id = processor.calculate_file_hash(file_data)
        st.session_state.uploaded_files_data[file_id] = {
            'data': file_data,
            'filename': filename,
            'upload_time': datetime.now(),
            'type': st.session_state.get('document_type', 'Bank Statement')
        }

        # Display file info
        with st.expander("📄 File Information", expanded=True):
            file_summary = get_file_info_summary(file_data, filename)
            st.text(file_summary)

        # Create and run analysis
        with st.spinner("🔍 Analyzing document... This may take 30-60 seconds..."):
            analyst = create_analyst_agent(st.session_state.api_key)

            result = analyst.analyze_document(
                file_data=file_data,
                filename=filename,
                document_type=st.session_state.get('document_type', 'Bank Statement')
            )

            if result['success']:
                # Store in history
                st.session_state.analysis_history.append({
                    'filename': filename,
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                })

                return result
            else:
                st.error(f"❌ Analysis Failed: {result.get('error', 'Unknown error')}")
                return None

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        return None


def display_analysis_results(result):
    """Display analysis results in a structured format."""
    if not result or not result.get('success'):
        return

    analysis = result.get('analysis', '')

    st.success("✅ Analysis Complete!")

    # Display main analysis
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Detailed Analysis")
    st.markdown(analysis)
    st.markdown('</div>', unsafe_allow_html=True)

    # Try to extract structured data from analysis
    # (In a production system, you'd structure the agent output more formally)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🚩 Key Findings")
        if "red flag" in analysis.lower() or "concern" in analysis.lower():
            st.warning("⚠️ Some concerns detected - review carefully")
        else:
            st.success("✅ No major concerns detected")

    with col2:
        st.markdown("### 💡 Recommendations")
        if "approve" in analysis.lower():
            st.success("✅ Consider for approval")
        elif "deny" in analysis.lower():
            st.error("❌ Consider denial")
        elif "review" in analysis.lower() or "more" in analysis.lower():
            st.warning("⚠️ Request additional documentation")

    # Download results
    st.divider()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📥 Export Results")
    with col2:
        # Create downloadable report
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'success': True
        }
        st.download_button(
            label="Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def main():
    """Main application function."""
    initialize_session_state()
    cleanup_old_files()

    display_header()
    display_sidebar()

    # Main content area
    st.markdown("---")

    # File upload section
    st.markdown("### 📤 Upload Financial Document")

    uploaded_file = st.file_uploader(
        "Choose a file (PDF, PNG, or JPG)",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="Upload bank statements, tax returns, pay stubs, or other financial documents"
    )

    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("🔍 Analyze Document", type="primary", use_container_width=True):
                result = process_uploaded_file(uploaded_file)
                if result:
                    st.session_state.current_analysis = result

        with col2:
            if st.button("🗑️ Clear Upload", use_container_width=True):
                st.session_state.current_analysis = None
                st.rerun()

    # Display current analysis
    if st.session_state.current_analysis:
        st.markdown("---")
        display_analysis_results(st.session_state.current_analysis)

    # Display recent analyses
    if st.session_state.analysis_history:
        st.markdown("---")
        st.markdown("### 📚 Recent Analyses")

        for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):
            with st.expander(f"📄 {analysis['filename']} - {analysis['timestamp'][:19]}"):
                st.markdown(analysis['result'].get('analysis', 'No analysis available'))


if __name__ == "__main__":
    main()
