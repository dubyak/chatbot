"""
Document Processing Utilities for Financial Document Analysis
Handles file processing, metadata extraction, and security checks.
"""

import io
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import PyPDF2
import magic
import base64


class DocumentProcessor:
    """Handles document processing and metadata extraction."""

    ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        self.magic = magic.Magic(mime=True)

    def validate_file(self, file_data: bytes, filename: str) -> Tuple[bool, str]:
        """
        Validate uploaded file for security and format compliance.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(file_data) > self.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024)}MB"

        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Supported types: {', '.join(self.ALLOWED_EXTENSIONS)}"

        # Check actual file type (MIME type)
        mime_type = self.magic.from_buffer(file_data)
        allowed_mimes = ['application/pdf', 'image/png', 'image/jpeg']
        if mime_type not in allowed_mimes:
            return False, f"File MIME type '{mime_type}' does not match extension"

        return True, ""

    def extract_pdf_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract metadata from PDF files."""
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            metadata = {
                'num_pages': len(pdf_reader.pages),
                'encrypted': pdf_reader.is_encrypted,
                'metadata': {},
                'text_extractable': False,
                'creation_date': None,
                'modification_date': None,
                'creator': None,
                'producer': None,
            }

            # Extract PDF metadata
            if pdf_reader.metadata:
                info = pdf_reader.metadata
                metadata['metadata'] = {
                    'title': info.get('/Title', ''),
                    'author': info.get('/Author', ''),
                    'subject': info.get('/Subject', ''),
                    'creator': info.get('/Creator', ''),
                    'producer': info.get('/Producer', ''),
                }
                metadata['creator'] = info.get('/Creator', 'Unknown')
                metadata['producer'] = info.get('/Producer', 'Unknown')

                # Parse dates
                if '/CreationDate' in info:
                    metadata['creation_date'] = self._parse_pdf_date(info['/CreationDate'])
                if '/ModDate' in info:
                    metadata['modification_date'] = self._parse_pdf_date(info['/ModDate'])

            # Check if text can be extracted (indicates searchable PDF vs scanned image)
            try:
                first_page_text = pdf_reader.pages[0].extract_text()
                metadata['text_extractable'] = len(first_page_text.strip()) > 0
            except:
                metadata['text_extractable'] = False

            return metadata

        except Exception as e:
            return {'error': str(e)}

    def extract_image_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract metadata from image files."""
        try:
            image = Image.open(io.BytesIO(file_data))

            metadata = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height,
                'exif': {},
                'dpi': image.info.get('dpi', None),
            }

            # Extract EXIF data if available
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    metadata['exif'][str(tag_id)] = str(value)

            return metadata

        except Exception as e:
            return {'error': str(e)}

    def calculate_file_hash(self, file_data: bytes) -> str:
        """Calculate SHA-256 hash of file for deduplication and integrity."""
        return hashlib.sha256(file_data).hexdigest()

    def encode_image_base64(self, file_data: bytes) -> str:
        """Encode image to base64 for vision API."""
        return base64.b64encode(file_data).decode('utf-8')

    def _parse_pdf_date(self, date_str: str) -> Optional[str]:
        """Parse PDF date format (D:YYYYMMDDHHmmSSOHH'mm')."""
        try:
            if date_str.startswith('D:'):
                date_str = date_str[2:]
            # Take first 14 characters (YYYYMMDDHHmmSS)
            date_str = date_str[:14]
            dt = datetime.strptime(date_str, '%Y%m%d%H%M%S')
            return dt.isoformat()
        except:
            return None

    def analyze_document_authenticity_signals(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyze document for authenticity signals based on metadata and structure.

        Returns dictionary with red flags and confidence signals.
        """
        signals = {
            'red_flags': [],
            'positive_signals': [],
            'metadata_analysis': {},
        }

        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext == '.pdf':
            metadata = self.extract_pdf_metadata(file_data)
            signals['metadata_analysis'] = metadata

            # Check for suspicious signs
            if metadata.get('encrypted'):
                signals['red_flags'].append("Document is encrypted - unusual for bank statements")

            if not metadata.get('text_extractable'):
                signals['red_flags'].append("Text not extractable - possible scanned/screenshot document")
            else:
                signals['positive_signals'].append("Text is extractable - appears to be original digital document")

            creator = metadata.get('creator', '').lower()
            producer = metadata.get('producer', '').lower()

            # Check for legitimate financial software
            legitimate_tools = ['quickbooks', 'bank', 'financial', 'acrobat', 'microsoft']
            if any(tool in creator or tool in producer for tool in legitimate_tools):
                signals['positive_signals'].append(f"Created with legitimate software: {creator or producer}")

            # Check for suspicious editing tools
            suspicious_tools = ['photoshop', 'gimp', 'paint', 'preview', 'pixlr']
            if any(tool in creator or tool in producer for tool in suspicious_tools):
                signals['red_flags'].append(f"Created/modified with image editing software: {creator or producer}")

            # Check modification dates
            if metadata.get('creation_date') and metadata.get('modification_date'):
                signals['positive_signals'].append("Document has creation and modification timestamps")

        elif file_ext in ['.png', '.jpg', '.jpeg']:
            metadata = self.extract_image_metadata(file_data)
            signals['metadata_analysis'] = metadata

            # Images of documents are generally less trustworthy
            signals['red_flags'].append("Document submitted as image rather than original PDF")

            # Check for screenshot indicators
            if metadata.get('format') == 'PNG' and not metadata.get('exif'):
                signals['red_flags'].append("PNG with no EXIF data - likely a screenshot")

            # Check resolution
            dpi = metadata.get('dpi')
            if dpi and dpi[0] < 150:
                signals['red_flags'].append(f"Low resolution ({dpi[0]} DPI) - may indicate re-photographed document")

        return signals


def get_file_info_summary(file_data: bytes, filename: str) -> str:
    """
    Generate a human-readable summary of file information.
    """
    processor = DocumentProcessor()

    # Validate file
    is_valid, error_msg = processor.validate_file(file_data, filename)
    if not is_valid:
        return f"⚠️ File Validation Error: {error_msg}"

    # Get authenticity signals
    signals = processor.analyze_document_authenticity_signals(file_data, filename)

    summary_parts = [
        f"📄 File: {filename}",
        f"📊 Size: {len(file_data) / 1024:.2f} KB",
        f"🔒 Hash: {processor.calculate_file_hash(file_data)[:16]}...",
        ""
    ]

    if signals['positive_signals']:
        summary_parts.append("✅ Positive Signals:")
        for signal in signals['positive_signals']:
            summary_parts.append(f"  • {signal}")
        summary_parts.append("")

    if signals['red_flags']:
        summary_parts.append("🚩 Red Flags:")
        for flag in signals['red_flags']:
            summary_parts.append(f"  • {flag}")
        summary_parts.append("")

    return "\n".join(summary_parts)
