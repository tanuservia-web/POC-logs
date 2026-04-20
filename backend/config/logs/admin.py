from django.contrib import admin
from django.utils.html import format_html
from .models import LogFile, ParsedLogEntry, AnalysisResult


class ParsedLogEntryInline(admin.TabularInline):
    model = ParsedLogEntry
    extra = 0
    max_num = 50
    readonly_fields = ("timestamp", "level", "category", "message")


@admin.register(LogFile)
class LogFileAdmin(admin.ModelAdmin):
    list_display = ("id", "filename", "uploaded_at")
    search_fields = ("filename",)
    inlines = [ParsedLogEntryInline]


@admin.register(ParsedLogEntry)
class ParsedLogEntryAdmin(admin.ModelAdmin):
    readonly_fields = ("log_file", "timestamp", "level", "category", "message")

    # ✅ USE colored_level here
    list_display = ("id", "log_file", "timestamp", "colored_level", "category")

    list_filter = ("level", "category", "log_file")
    search_fields = ("message",)
    ordering = ("-id",)

    def colored_level(self, obj):
        color = "black"
        if obj.level == "ERROR":
            color = "red"
        elif obj.level == "WARNING":
            color = "orange"
        elif obj.level == "CRITICAL":
            color = "darkred"

        return format_html('<span style="color: {};">{}</span>', color, obj.level)

    colored_level.short_description = "Level"


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    readonly_fields = ("summary", "root_causes", "suggested_fixes")
    list_display = ("id", "log_file", "status", "error_count",
                    "critical_count", "created_at")
    list_filter = ("status",)
