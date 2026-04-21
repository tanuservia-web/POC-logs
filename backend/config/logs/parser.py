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
    line_lower = line.lower()

    # 🔴 CRITICAL (highest priority)
    if "fatal error" in line_lower or "uncaught" in line_lower:
        return "CRITICAL"

    # 🔴 ERROR
    if "php:error" in line_lower or "error" in line_lower or "failed" in line_lower:
        return "ERROR"

    # 🟠 WARNING
    if "warn" in line_lower:
        return "WARNING"

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
    current_entry = ""

    for line in file:
        try:
            line = line.decode("utf-8").strip()
        except:
            continue

        if not line:
            continue

        # New log starts
        if "[" in line and "]" in line:
            if current_entry:
                process_entry(current_entry, entries)
            current_entry = line
        else:
            current_entry += " " + line

    if current_entry:
        process_entry(current_entry, entries)

    return entries


def process_entry(text, entries):
    level = detect_level(text)

    if level not in ["ERROR", "CRITICAL"]:
        return

    entries.append({
        "timestamp": extract_timestamp(text),
        "level": level,
        "category": detect_category(text),
        "message": text
    })

    print("✅ Stored:", len(entries))
    return entries
