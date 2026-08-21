import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import (
    DocumentUploadSerializer,
    SearchRequestSerializer,
    QueryRequestSerializer,
    SynthesisRequestSerializer
)
from .services.document_parser import DocumentParserService
from .services.web_search import WebSearchService
from .services.groq_engine import GroqReasoningEngine
from .services.synthesis_engine import MultiHopSynthesisEngine
from .services.session_manager import SessionManager
from .services.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

def get_session_id(request):
    """
    Extract session key from request headers, JSON body parameter, or Django session cookie.
    """
    # 1. Custom Header
    header_session_id = request.headers.get('X-Session-ID') or request.META.get('HTTP_X_SESSION_ID')
    if header_session_id:
        return header_session_id

    # 2. JSON Body Parameter
    if hasattr(request, 'data') and isinstance(request.data, dict) and request.data.get('session_id'):
        return request.data.get('session_id')

    # 3. Standard Django Session
    if hasattr(request, 'session'):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    return SessionManager.get_or_create_session_id()


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "app": "counterpoint"
        }, status=status.HTTP_200_OK)


class DocumentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['file']
        session_id = get_session_id(request)

        try:
            parsed_doc = DocumentParserService.parse_uploaded_file(uploaded_file, session_id=session_id)
            
            doc_data = {
                'file_name': parsed_doc['file_name'],
                'file_type': parsed_doc['file_type'],
                'file_size_bytes': parsed_doc['file_size_bytes'],
                'page_count': parsed_doc.get('page_count', 1),
                'word_count': parsed_doc['word_count'],
                'character_count': parsed_doc['character_count'],
                'text': parsed_doc['text']
            }

            # Save in both SessionManager cache and request.session
            SessionManager.set_active_document(session_id, doc_data)
            if hasattr(request, 'session'):
                request.session['active_document'] = doc_data
                request.session.modified = True

            return Response({
                "message": "Document parsed and set as active session context successfully.",
                "session_id": session_id,
                "document": {
                    "file_name": parsed_doc['file_name'],
                    "file_type": parsed_doc['file_type'],
                    "file_size_bytes": parsed_doc['file_size_bytes'],
                    "page_count": parsed_doc.get('page_count', 1),
                    "word_count": parsed_doc['word_count'],
                    "character_count": parsed_doc['character_count'],
                    "preview": parsed_doc['text'][:500] + ("..." if len(parsed_doc['text']) > 500 else "")
                }
            }, status=status.HTTP_201_CREATED)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error processing document upload")
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentDetailView(APIView):
    def get(self, request):
        session_id = get_session_id(request)
        active_doc = SessionManager.get_active_document(session_id)
        if not active_doc and hasattr(request, 'session'):
            active_doc = request.session.get('active_document')

        if not active_doc:
            return Response({"active_document": None, "session_id": session_id}, status=status.HTTP_200_OK)

        return Response({
            "session_id": session_id,
            "active_document": {
                "file_name": active_doc.get('file_name'),
                "file_type": active_doc.get('file_type'),
                "file_size_bytes": active_doc.get('file_size_bytes'),
                "word_count": active_doc.get('word_count'),
                "character_count": active_doc.get('character_count'),
                "preview": active_doc.get('text', '')[:1000]
            }
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        session_id = get_session_id(request)
        SessionManager.clear_active_document(session_id)
        if hasattr(request, 'session') and 'active_document' in request.session:
            del request.session['active_document']
            request.session.modified = True

        return Response({"message": "Active document removed from session.", "session_id": session_id}, status=status.HTTP_200_OK)


class WebSearchView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['query']
        max_results = serializer.validated_data.get('max_results', 5)
        session_id = get_session_id(request)

        search_results = WebSearchService.search_competitor(query, max_results=max_results, session_id=session_id)
        search_results["session_id"] = session_id
        return Response(search_results, status=status.HTTP_200_OK)


class MultiHopQueryView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        serializer = SynthesisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['query']
        execute_web_search = serializer.validated_data.get('execute_web_search', True)
        body_session_id = serializer.validated_data.get('session_id')
        session_id = body_session_id or get_session_id(request)

        response_data = MultiHopSynthesisEngine.execute_synthesis(
            query=query,
            execute_web_search=execute_web_search,
            session_id=session_id
        )
        response_data["session_id"] = session_id
        return Response(response_data, status=status.HTTP_200_OK)


class AuditLogsView(APIView):
    def get(self, request):
        session_id = get_session_id(request)
        logs = AuditLogger.get_logs(session_id)
        if not logs:
            logs = AuditLogger.get_logs('global')

        return Response({
            "session_id": session_id,
            "log_count": len(logs),
            "logs": logs
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        session_id = get_session_id(request)
        AuditLogger.clear_logs(session_id)
        AuditLogger.clear_logs('global')
        return Response({"message": "Audit logs cleared.", "session_id": session_id}, status=status.HTTP_200_OK)


class SessionResetView(APIView):
    def post(self, request):
        session_id = get_session_id(request)
        SessionManager.clear_session(session_id)
        if hasattr(request, 'session'):
            request.session.flush()

        return Response({
            "message": "Session context, active document, history, and audit logs reset successfully.",
            "session_id": session_id
        }, status=status.HTTP_200_OK)
