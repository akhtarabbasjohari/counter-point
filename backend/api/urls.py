from django.urls import path
from .views import (
    HealthCheckView,
    DocumentUploadView,
    DocumentDetailView,
    WebSearchView,
    MultiHopQueryView,
    AuditLogsView,
    SessionResetView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('documents/upload/', DocumentUploadView.as_view(), name='document_upload_canonical'),
    path('documents/', DocumentDetailView.as_view(), name='document_detail'),
    path('search/', WebSearchView.as_view(), name='web_search'),
    path('query/', MultiHopQueryView.as_view(), name='multihop_query'),
    path('logs/', AuditLogsView.as_view(), name='audit_logs'),
    path('audit-logs/', AuditLogsView.as_view(), name='audit_logs_canonical'),
    path('session/reset/', SessionResetView.as_view(), name='session_reset'),
]
