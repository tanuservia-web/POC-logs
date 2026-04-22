from django.db import models


class LogFile(models.Model):
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default="PROCESSING")

    progress = models.IntegerField(default=0)   # ✅ NEW
    total_lines = models.IntegerField(default=0)  # ✅ NEW
    processed_lines = models.IntegerField(default=0)  # ✅ NEW

    uploaded_at = models.DateTimeField(auto_now_add=True)


class ParsedLogEntry(models.Model):
    log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE)
    timestamp = models.CharField(max_length=100, null=True, blank=True)

    level = models.CharField(max_length=20)
    category = models.CharField(max_length=50)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    hash = models.CharField(max_length=64, db_index=True)

    class Meta:
        unique_together = ("log_file", "hash")
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["category"]),
            models.Index(fields=["log_file"]),
            models.Index(fields=["hash"]),
        ]


class AnalysisResult(models.Model):
    log_file = models.OneToOneField(LogFile, on_delete=models.CASCADE)

    summary = models.JSONField()  # changed
    root_causes = models.JSONField()
    suggested_fixes = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ],
        default="COMPLETED"
    )

    error_count = models.IntegerField(default=0)
    critical_count = models.IntegerField(default=0)

    raw_ai_response = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

# class AnalysisResult(models.Model):
#     log_file = models.OneToOneField(LogFile, on_delete=models.CASCADE)
#     summary = models.TextField()
#     root_causes = models.JSONField()
#     suggested_fixes = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)
