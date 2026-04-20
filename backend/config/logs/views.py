from rest_framework import status
from django.db.models import Count
from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import LogFile, ParsedLogEntry, AnalysisResult
from .serializers import *
from .parser import parse_log_file
from .ai_service import analyze_logs


class LogListView(APIView):
    def get(self, request):
        logs = LogFile.objects.all().order_by("-id")
        return Response(LogFileSerializer(logs, many=True).data)


class UploadLogView(APIView):
    def post(self, request):
        file = request.FILES['file']

        # ✅ Only metadata stored
        log = LogFile.objects.create(filename=file.name)

        entries = parse_log_file(file)

        parsed_objects = [
            ParsedLogEntry(
                log_file=log,
                timestamp=e["timestamp"],
                level=e["level"],
                category=e["category"],
                message=e["message"]
            )
            for e in entries
        ]

        ParsedLogEntry.objects.bulk_create(parsed_objects)

        return Response({
            "log_id": log.id,
            "stored_errors": len(parsed_objects)
        })


class LogEntriesView(APIView):
    def get(self, request, log_id):
        entries = ParsedLogEntry.objects.filter(log_file_id=log_id)
        return Response(ParsedLogEntrySerializer(entries, many=True).data)


class AnalyzeView(APIView):
    def post(self, request, log_id):
        entries = ParsedLogEntry.objects.filter(log_file_id=log_id)

        if not entries.exists():
            return Response({"error": "No logs found"}, status=status.HTTP_404_NOT_FOUND)

        # Avoid duplicate analysis
        if AnalysisResult.objects.filter(log_file_id=log_id).exists():
            existing = AnalysisResult.objects.get(log_file_id=log_id)
            return Response(
                AnalysisResultSerializer(existing).data,
                status=status.HTTP_200_OK
            )

        result = analyze_logs(entries)

        analysis = AnalysisResult.objects.create(
            log_file_id=log_id,
            summary=result["summary"],
            root_causes=result["root_causes"],
            suggested_fixes=result["suggested_fixes"],
            error_count=result["summary"]["levels"].get("ERROR", 0),
            critical_count=result["summary"]["levels"].get("CRITICAL", 0),
        )

        return Response(AnalysisResultSerializer(analysis).data)


class AnalysisView(APIView):
    def get(self, request, log_id):
        try:
            analysis = AnalysisResult.objects.get(log_file_id=log_id)
            return Response(AnalysisResultSerializer(analysis).data)
        except AnalysisResult.DoesNotExist:
            return Response(
                {"error": "Analysis not found. Please run analysis first."},
                status=404
            )


class ErrorLogsView(APIView):
    def get(self, request):
        level = request.GET.get("level")
        category = request.GET.get("category")

        logs = ParsedLogEntry.objects.all()

        if level:
            logs = logs.filter(level=level)

        if category:
            logs = logs.filter(category=category)

        logs = logs.order_by("-id")

        return Response(ParsedLogEntrySerializer(logs, many=True).data)
