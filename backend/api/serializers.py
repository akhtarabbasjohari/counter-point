from rest_framework import serializers

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, max_length=255)
    max_results = serializers.IntegerField(required=False, default=5, min_value=1, max_value=10)

class QueryRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    execute_web_search = serializers.BooleanField(required=False, default=True)
