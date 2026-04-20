from django.db import models


class LogFile(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="logs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ParsedLogEntry(models.Model):
    log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE)
    timestamp = models.CharField(max_length=100, null=True, blank=True)
    level = models.CharField(max_length=20)
    category = models.CharField(max_length=50, default="GENERAL")  # NEW
    message = models.TextField()


# class ParsedLogEntry(models.Model):
#     log_file = models.ForeignKey(
#         LogFile, on_delete=models.CASCADE, related_name="entries")
#     timestamp = models.CharField(max_length=100, null=True, blank=True)
#     level = models.CharField(max_length=20)
#     message = models.TextField()

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
