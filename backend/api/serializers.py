from rest_framework import serializers

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.md']

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        file_name = getattr(value, 'name', '')
        file_size = getattr(value, 'size', 0)

        # Check extension
        ext = '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Unsupported file extension '{ext}'. Allowed extensions are: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Check file size (10MB limit)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed limit of 10MB (file size: {file_size / (1024*1024):.2f}MB)."
            )

        # Basic magic byte check for PDF files
        if ext == '.pdf':
            header = value.read(4)
            value.seek(0)
            if header and not header.startswith(b'%PDF'):
                raise serializers.ValidationError("Corrupted or invalid PDF header. File is not a valid PDF document.")

        return value

class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, max_length=255)
    max_results = serializers.IntegerField(required=False, default=5, min_value=1, max_value=10)

class QueryRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    execute_web_search = serializers.BooleanField(required=False, default=True)
    session_id = serializers.CharField(required=False, allow_blank=True, default=None)

class SynthesisRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    execute_web_search = serializers.BooleanField(required=False, default=True)
    session_id = serializers.CharField(required=False, allow_blank=True, default=None)

class SynthesisResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    synthesis = serializers.CharField()
    model_used = serializers.CharField()
    execution_time_ms = serializers.FloatField()
    document_context_used = serializers.BooleanField()
    document_name = serializers.CharField(allow_null=True)
    web_sources = serializers.ListField(child=serializers.DictField())
    recent_audit_logs = serializers.ListField(child=serializers.DictField())
