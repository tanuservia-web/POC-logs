from collections import Counter

# def analyze_logs(entries):
#     error_count = sum(1 for e in entries if e["level"] == "ERROR")

#     summary = f"Found {error_count} errors in logs."

#     root_causes = []
#     fixes = []

#     if error_count > 0:
#         root_causes.append("Application exceptions or misconfigurations")
#         fixes.append("Check stack traces and validate configs")

#     return {
#         "summary": summary,
#         "root_causes": root_causes,
#         "suggested_fixes": fixes
#     }


def analyze_logs(entries):
    total = entries.count()

    level_counts = Counter()
    category_counts = Counter()

    error_messages = []

    for e in entries:
        level_counts[e.level] += 1
        category_counts[e.category] += 1

        if e.level in ["ERROR", "CRITICAL"]:
            error_messages.append(e.message)

    # 🔹 Summary
    summary = {
        "total_logs": total,
        "levels": dict(level_counts),
        "categories": dict(category_counts),
        "error_rate": round((level_counts["ERROR"] / total) * 100, 2) if total else 0
    }

    # 🔹 Root Cause Detection
    root_causes = []

    if category_counts["DB_ERROR"] > 0:
        root_causes.append("Database related failures detected")

    if category_counts["AUTH_ERROR"] > 0:
        root_causes.append("Authentication failures detected")

    if category_counts["API_ERROR"] > 0:
        root_causes.append("External/API service failures detected")

    if level_counts["CRITICAL"] > 0:
        root_causes.append("Critical system failure detected")

    if not root_causes:
        root_causes.append("No major issues detected")

    # 🔹 Suggested Fixes
    suggested_fixes = []

    if category_counts["DB_ERROR"] > 0:
        suggested_fixes.append(
            "Check database connection and query performance")

    if category_counts["AUTH_ERROR"] > 0:
        suggested_fixes.append("Verify authentication tokens and login flow")

    if category_counts["API_ERROR"] > 0:
        suggested_fixes.append(
            "Check third-party API availability and timeouts")

    if category_counts["PERFORMANCE_WARNING"] > 0:
        suggested_fixes.append("Optimize slow queries and reduce latency")

    if not suggested_fixes:
        suggested_fixes.append("System appears stable. Monitor logs regularly")

    return {
        "summary": summary,
        "root_causes": root_causes,
        "suggested_fixes": suggested_fixes
    }
