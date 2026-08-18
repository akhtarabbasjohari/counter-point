import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import DocumentUploadSerializer, SearchRequestSerializer, QueryRequestSerializer
from .services.document_parser import DocumentParserService
from .services.web_search import WebSearchService
from .services.groq_engine import GroqReasoningEngine
from .services.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

# Helper to obtain a unique session key
def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


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
            
            # Store in Django session
            request.session['active_document'] = {
                'file_name': parsed_doc['file_name'],
                'file_type': parsed_doc['file_type'],
                'file_size_bytes': parsed_doc['file_size_bytes'],
                'word_count': parsed_doc['word_count'],
                'character_count': parsed_doc['character_count'],
                'text': parsed_doc['text']
            }
            request.session.modified = True

            return Response({
                "message": "Document parsed and set as active session context successfully.",
                "document": {
                    "file_name": parsed_doc['file_name'],
                    "file_type": parsed_doc['file_type'],
                    "file_size_bytes": parsed_doc['file_size_bytes'],
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
        active_doc = request.session.get('active_document')
        if not active_doc:
            return Response({"active_document": None}, status=status.HTTP_200_OK)

        return Response({
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
        if 'active_document' in request.session:
            doc_name = request.session['active_document'].get('file_name', '')
            del request.session['active_document']
            request.session.modified = True
            
            AuditLogger.log_tool_execution(
                tool_name="clear_positioning_doc",
                input_params={"cleared_doc": doc_name},
                execution_time_ms=1.0,
                status="success",
                result_summary="Active document cleared from session",
                session_id=session_id
            )
        return Response({"message": "Active document removed from session."}, status=status.HTTP_200_OK)


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
        return Response(search_results, status=status.HTTP_200_OK)


class MultiHopQueryView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['query']
        execute_web_search = serializer.validated_data.get('execute_web_search', True)
        session_id = get_session_id(request)

        # 1. Retrieve internal document context from session
        document_context = request.session.get('active_document')

        # 2. Execute live web search tool if requested
        web_results = None
        if execute_web_search:
            web_results = WebSearchService.search_competitor(query, max_results=5, session_id=session_id)

        # 3. Retrieve prior conversation history
        conversation_history = request.session.get('conversation_history', [])

        # 4. Multi-hop synthesis via Groq Engine
        synthesis = GroqReasoningEngine.synthesize_counterpoint(
            query=query,
            document_context=document_context,
            web_results=web_results,
            conversation_history=conversation_history,
            session_id=session_id
        )

        # 5. Append message to conversation history
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": synthesis["synthesis"]})
        request.session['conversation_history'] = conversation_history
        request.session.modified = True

        return Response({
            "query": query,
            "synthesis": synthesis["synthesis"],
            "model_used": synthesis["model"],
            "execution_time_ms": synthesis["execution_time_ms"],
            "document_context_used": bool(document_context),
            "document_name": document_context.get('file_name') if document_context else None,
            "web_sources": web_results.get('results', []) if web_results else [],
            "recent_audit_logs": AuditLogger.get_logs(session_id)[:5]
        }, status=status.HTTP_200_OK)


class AuditLogsView(APIView):
    def get(self, request):
        session_id = get_session_id(request)
        logs = AuditLogger.get_logs(session_id)
        # Also return global logs if session specific is empty
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
        return Response({"message": "Audit logs cleared."}, status=status.HTTP_200_OK)


class SessionResetView(APIView):
    def post(self, request):
        session_id = get_session_id(request)
        request.session.flush()
        AuditLogger.clear_logs(session_id)
        return Response({
            "message": "Session context, active document, history, and audit logs reset successfully."
        }, status=status.HTTP_200_OK)
