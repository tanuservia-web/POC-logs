from rest_framework import serializers
from .models import LogFile, ParsedLogEntry, AnalysisResult


class LogFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogFile
        fields = "__all__"


class LogFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogFile
        fields = "__all__"


class ParsedLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedLogEntry
        fields = "__all__"


class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = "__all__"
