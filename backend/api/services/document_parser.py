import io
import time
import logging
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

class DocumentParserService:
    @staticmethod
    def parse_uploaded_file(uploaded_file, session_id="global"):
        start_time = time.time()
        file_name = getattr(uploaded_file, 'name', 'unknown_file')
        file_size = getattr(uploaded_file, 'size', 0)
        
        extracted_text = ""
        file_type = "unknown"
        page_count = 1
        status = "SUCCESS"
        error_msg = None

        try:
            if file_size > MAX_FILE_SIZE_BYTES:
                raise ValueError(f"File size exceeds 10MB limit (size: {file_size / (1024*1024):.2f}MB).")

            if file_name.lower().endswith('.pdf'):
                file_type = "pdf"
                extracted_text, page_count = DocumentParserService._parse_pdf(uploaded_file)
            elif file_name.lower().endswith('.txt') or file_name.lower().endswith('.md'):
                file_type = "text"
                extracted_text, page_count = DocumentParserService._parse_txt(uploaded_file)
            else:
                raise ValueError("Unsupported file format. Only PDF (.pdf) and Text (.txt, .md) files are supported.")
        except Exception as e:
            status = "ERROR"
            error_msg = str(e)
            logger.error(f"Error parsing file {file_name}: {e}")
            raise ValueError(f"Failed to parse document: {str(e)}")
        finally:
            execution_time_ms = (time.time() - start_time) * 1000
            word_count = len(extracted_text.split()) if extracted_text else 0
            
            AuditLogger.log_tool_execution(
                tool_name="parse_positioning_doc",
                input_params={
                    "file_name": file_name,
                    "file_size_bytes": file_size,
                    "file_type": file_type
                },
                execution_time_ms=execution_time_ms,
                status=status,
                result_summary=error_msg or f"Extracted {word_count} words ({len(extracted_text)} chars across {page_count} pages)",
                session_id=session_id
            )

        return {
            "file_name": file_name,
            "file_type": file_type,
            "file_size_bytes": file_size,
            "page_count": page_count,
            "word_count": len(extracted_text.split()),
            "character_count": len(extracted_text),
            "text": extracted_text
        }

    @staticmethod
    def _parse_pdf(uploaded_file):
        text_content = []
        file_bytes = uploaded_file.read()
        page_count = 0
        
        # Try pdfplumber first
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                page_count = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {i+1} ---\n{page_text}")
            if text_content:
                return "\n\n".join(text_content), page_count
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed, trying pypdf fallback: {e}")

        # Fallback to pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            page_count = len(reader.pages)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Page {i+1} ---\n{page_text}")
            if text_content:
                return "\n\n".join(text_content), page_count
        except Exception as e:
            logger.error(f"pypdf extraction failed: {e}")

        raise ValueError("Could not extract legible text from PDF file. The PDF may be scanned or empty.")

    @staticmethod
    def _parse_txt(uploaded_file):
        content = uploaded_file.read()
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return content.decode(encoding), 1
            except (UnicodeDecodeError, AttributeError):
                continue
        return content.decode('utf-8', errors='ignore'), 1

