from rest_framework import serializers

class PageSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=255)
    path = serializers.CharField(max_length=512)
    mime_type = serializers.CharField(max_length=255, default="text/html")