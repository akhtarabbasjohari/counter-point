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
    path('health', HealthCheckView.as_view()),
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('upload', DocumentUploadView.as_view()),
    path('documents/upload/', DocumentUploadView.as_view(), name='document_upload_canonical'),
    path('documents/upload', DocumentUploadView.as_view()),
    path('documents/', DocumentDetailView.as_view(), name='document_detail'),
    path('documents', DocumentDetailView.as_view()),
    path('search/', WebSearchView.as_view(), name='web_search'),
    path('search', WebSearchView.as_view()),
    path('query/', MultiHopQueryView.as_view(), name='multihop_query'),
    path('query', MultiHopQueryView.as_view()),
    path('synthesis/', MultiHopQueryView.as_view(), name='multihop_synthesis'),
    path('synthesis', MultiHopQueryView.as_view()),
    path('logs/', AuditLogsView.as_view(), name='audit_logs'),
    path('logs', AuditLogsView.as_view()),
    path('audit-logs/', AuditLogsView.as_view(), name='audit_logs_canonical'),
    path('audit-logs', AuditLogsView.as_view()),
    path('session/reset/', SessionResetView.as_view(), name='session_reset'),
    path('session/reset', SessionResetView.as_view()),
]
