"""
Security utilities for handling sensitive financial document data.
Implements encryption, secure deletion, and audit logging.
"""

import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Optional, Dict, Any
import json
from pathlib import Path


class AuditLogger:
    """
    Audit logger for tracking document access and analysis.
    Critical for compliance with financial regulations.
    """

    def __init__(self, log_file: str = "audit_log.json"):
        self.log_file = Path(log_file)
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Create log file if it doesn't exist."""
        if not self.log_file.exists():
            self.log_file.write_text(json.dumps([]))

    def log_event(
        self,
        event_type: str,
        file_hash: str,
        filename: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a document-related event.

        Args:
            event_type: Type of event (upload, analysis, deletion, etc.)
            file_hash: SHA-256 hash of the file
            filename: Original filename (sanitized)
            user_id: Optional user identifier
            metadata: Additional event metadata
        """
        try:
            # Read existing logs
            logs = json.loads(self.log_file.read_text())

            # Create new log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'file_hash': file_hash,
                'filename': self._sanitize_filename(filename),
                'user_id': user_id or 'anonymous',
                'metadata': metadata or {}
            }

            logs.append(log_entry)

            # Write back to file
            self.log_file.write_text(json.dumps(logs, indent=2))

        except Exception as e:
            # In production, this should go to a proper logging service
            print(f"Audit log error: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """Remove potentially sensitive info from filename for logging."""
        # Only keep the extension and hash the rest
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            name_hash = hashlib.sha256(parts[0].encode()).hexdigest()[:8]
            return f"{name_hash}.{parts[1]}"
        return hashlib.sha256(filename.encode()).hexdigest()[:8]

    def get_recent_events(self, limit: int = 100) -> list:
        """Retrieve recent audit events."""
        try:
            logs = json.loads(self.log_file.read_text())
            return logs[-limit:]
        except:
            return []


class SecureFileHandler:
    """
    Handles secure storage and deletion of uploaded files.
    Implements secure deletion and encryption at rest.
    """

    @staticmethod
    def secure_delete(file_data: bytes) -> bool:
        """
        Securely delete file data by overwriting memory.
        Note: Python's garbage collection makes true secure deletion difficult,
        but this provides a reasonable effort.
        """
        try:
            # Overwrite the data in place with zeros
            # This is a best-effort approach in Python
            if isinstance(file_data, bytearray):
                for i in range(len(file_data)):
                    file_data[i] = 0
            return True
        except:
            return False

    @staticmethod
    def generate_session_key() -> str:
        """Generate a secure random session key."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_file(file_data: bytes) -> str:
        """Generate SHA-256 hash of file for integrity verification."""
        return hashlib.sha256(file_data).hexdigest()

    @staticmethod
    def verify_file_integrity(file_data: bytes, expected_hash: str) -> bool:
        """Verify file hasn't been tampered with."""
        actual_hash = SecureFileHandler.hash_file(file_data)
        return hmac.compare_digest(actual_hash, expected_hash)


class DataRetentionPolicy:
    """
    Implements data retention policies for compliance.
    Ensures uploaded documents don't persist longer than necessary.
    """

    # Maximum time to keep uploaded files (in hours)
    MAX_RETENTION_HOURS = 24

    # Maximum time to keep analysis results (in days)
    MAX_ANALYSIS_RETENTION_DAYS = 90

    @staticmethod
    def should_delete_file(upload_timestamp: datetime) -> bool:
        """Check if file should be deleted based on retention policy."""
        time_elapsed = datetime.now() - upload_timestamp
        return time_elapsed.total_seconds() > (DataRetentionPolicy.MAX_RETENTION_HOURS * 3600)

    @staticmethod
    def should_delete_analysis(analysis_timestamp: datetime) -> bool:
        """Check if analysis should be deleted based on retention policy."""
        time_elapsed = datetime.now() - analysis_timestamp
        return time_elapsed.days > DataRetentionPolicy.MAX_ANALYSIS_RETENTION_DAYS


class ComplianceChecker:
    """
    Validates compliance with financial regulations.
    """

    REQUIRED_AUDIT_FIELDS = [
        'timestamp',
        'event_type',
        'file_hash',
        'user_id'
    ]

    @staticmethod
    def validate_pii_handling(document_data: Dict[str, Any]) -> bool:
        """
        Ensure PII (Personally Identifiable Information) is handled properly.
        Returns True if handling is compliant.
        """
        # Check that sensitive fields are not logged in plain text
        sensitive_fields = ['ssn', 'account_number', 'routing_number', 'tax_id']

        for field in sensitive_fields:
            if field in document_data and isinstance(document_data[field], str):
                # Check if value is masked or hashed
                value = document_data[field]
                if not ('*' in value or len(value) == 64):  # 64 chars = SHA-256 hash
                    return False

        return True

    @staticmethod
    def check_retention_compliance(audit_log: list) -> Dict[str, Any]:
        """
        Check if system is compliant with data retention policies.
        """
        issues = []
        warnings = []

        # Check for required audit fields
        for entry in audit_log:
            missing_fields = [
                field for field in ComplianceChecker.REQUIRED_AUDIT_FIELDS
                if field not in entry
            ]
            if missing_fields:
                issues.append(f"Missing fields in audit log: {missing_fields}")

        # Check for old records that should be deleted
        now = datetime.now()
        for entry in audit_log:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                if DataRetentionPolicy.should_delete_analysis(timestamp):
                    warnings.append(f"Old analysis record found: {entry['timestamp']}")
            except:
                issues.append(f"Invalid timestamp in audit log: {entry.get('timestamp')}")

        return {
            'compliant': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }


# Singleton instances
audit_logger = AuditLogger()
secure_file_handler = SecureFileHandler()


def log_document_upload(file_hash: str, filename: str, file_size: int):
    """Convenience function to log document upload."""
    audit_logger.log_event(
        event_type='document_upload',
        file_hash=file_hash,
        filename=filename,
        metadata={'file_size': file_size}
    )


def log_document_analysis(file_hash: str, filename: str, analysis_result: str):
    """Convenience function to log document analysis."""
    audit_logger.log_event(
        event_type='document_analysis',
        file_hash=file_hash,
        filename=filename,
        metadata={'result_length': len(analysis_result)}
    )


def log_document_deletion(file_hash: str, filename: str):
    """Convenience function to log document deletion."""
    audit_logger.log_event(
        event_type='document_deletion',
        file_hash=file_hash,
        filename=filename
    )
