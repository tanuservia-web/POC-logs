import re
from datetime import datetime

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

CATEGORY_KEYWORDS = {
    "AUTH_ERROR": ["unauthorized", "authentication", "invalid token", "login failed"],
    "PERMISSION_ERROR": ["forbidden", "permission denied", "not allowed"],
    "DB_ERROR": ["database", "sql", "query failed", "integrity", "constraint"],
    "API_ERROR": ["timeout", "bad gateway", "service unavailable", "api failed"],
    "VALIDATION_ERROR": ["invalid", "missing field", "validation failed"],
    "SYSTEM_ERROR": ["exception", "crash", "stack trace"],
    "PERFORMANCE_WARNING": ["slow", "latency", "took too long"],
    "SECURITY_ALERT": ["attack", "breach", "suspicious", "malicious"],
}


def detect_level(line):
    for level in LOG_LEVELS:
        if level.lower() in line.lower():
            return level
    return "INFO"


def detect_category(line):
    line_lower = line.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in line_lower for keyword in keywords):
            return category
    return "GENERAL"


def extract_timestamp(line):
    # Supports multiple formats
    patterns = [
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",   # 2026-04-13 12:30:45
        r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}",   # 13/04/2026 12:30:45
    ]

    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            try:
                return match.group()
            except:
                pass

    return None


def parse_log_file(file):
    entries = []

    for line in file:
        try:
            line = line.decode("utf-8").strip()
        except:
            continue

        if not line:
            continue

        timestamp = extract_timestamp(line)
        level = detect_level(line)

        # fallback detection
        if level == "INFO":
            if "error" in line.lower() or "failed" in line.lower():
                level = "ERROR"
            elif "warn" in line.lower():
                level = "WARNING"

        # 🚨 ONLY STORE ERROR + CRITICAL
        if level not in ["ERROR", "CRITICAL"]:
            continue

        category = detect_category(line)

        entries.append({
            "timestamp": timestamp,
            "level": level,
            "category": category,
            "message": line
        })

    print("✅ Stored only critical logs:", len(entries))
    return entries
