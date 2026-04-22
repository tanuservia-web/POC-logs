from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', UploadLogView.as_view()),
    path('<int:log_id>/entries/', LogEntriesView.as_view()),
    path('<int:log_id>/analyze/', AnalyzeView.as_view()),
    path('<int:log_id>/analysis/', AnalysisView.as_view()),
    path("<int:log_id>/status/", LogStatusView.as_view()),

    path("errors/", ErrorLogsView.as_view()),


]
