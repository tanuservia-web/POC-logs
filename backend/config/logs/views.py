from rest_framework import status
from django.db.models import Count
from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import LogFile, ParsedLogEntry, AnalysisResult
from .serializers import *
from .parser import parse_log_file
from .ai_service import analyze_logs
from rest_framework.pagination import PageNumberPagination
import threading
from logs.services.log_processor import process_log_file


class LogPagination(PageNumberPagination):
    page_size = 50


class LogListView(APIView):
    def get(self, request):
        logs = LogFile.objects.all().order_by("-id")
        return Response(LogFileSerializer(logs, many=True).data)


class UploadLogView(APIView):
    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=400)

        log = LogFile.objects.create(
            filename=file.name,
            status="PROCESSING"
        )

        file_data = file.read()

        threading.Thread(
            target=process_log_file,
            args=(file_data, log.id)
        ).start()

        return Response({
            "log_id": log.id,
            "status": "PROCESSING"
        })


class LogEntriesView(APIView):
    def get(self, request, log_id):
        logs = ParsedLogEntry.objects.filter(
            log_file_id=log_id).order_by("-id")

        paginator = LogPagination()
        result_page = paginator.paginate_queryset(logs, request)

        return paginator.get_paginated_response(
            ParsedLogEntrySerializer(result_page, many=True).data
        )


class LogStatusView(APIView):
    def get(self, request, log_id):
        log = LogFile.objects.get(id=log_id)

        return Response({
            "status": log.status,
            "progress": getattr(log, "progress", 0)
        })


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
        logs = ParsedLogEntry.objects.all().order_by("-id")

        level = request.GET.get("level")
        category = request.GET.get("category")
        limit = request.GET.get("limit")

        if limit:
            logs = logs[:int(limit)]

        if level:
            logs = logs.filter(level__iexact=level)

        if category:
            logs = logs.filter(category__iexact=category)

        paginator = LogPagination()
        result_page = paginator.paginate_queryset(logs, request)

        return paginator.get_paginated_response(
            ParsedLogEntrySerializer(result_page, many=True).data
        )


class ErrorSummaryView(APIView):
    def get(self, request):
        summary = (
            ParsedLogEntry.objects
            .values("message")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        return Response(summary)
