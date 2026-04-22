import re
from datetime import datetime
import hashlib

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


def parse_log_file(lines):
    entries = []

    for line in lines:
        try:
            line = line.decode("utf-8").strip()
        except:
            continue

        if not line:
            continue

        timestamp = extract_timestamp(line)
        level = detect_level(line)

        if level == "INFO":
            if "error" in line.lower():
                level = "ERROR"
            elif "warn" in line.lower():
                level = "WARNING"

        category = detect_category(line)

        # ✅ normalize + hash
        hash_value = generate_hash(line)

        entries.append({
            "timestamp": timestamp,
            "level": level,
            "category": category,
            "message": line,
            "hash": hash_value   # 🔥 NEW
        })

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


def normalize_message(msg):
    msg = msg.lower()

    # remove numbers, ids, timestamps → helps deduplication
    msg = re.sub(r'\d+', '', msg)
    msg = re.sub(r'0x[0-9a-f]+', '', msg)

    return msg.strip()


def generate_hash(message):
    normalized = normalize_message(message)
    return hashlib.md5(normalized.encode()).hexdigest()


def parse_single_line(line):
    timestamp = extract_timestamp(line)
    level = detect_level(line)

    # fallback detection
    if level == "INFO":
        if "error" in line.lower() or "failed" in line.lower():
            level = "ERROR"
        elif "warn" in line.lower():
            level = "WARNING"

    category = detect_category(line)

    return {
        "timestamp": timestamp,
        "level": level,
        "category": category,
        "message": line,
        "hash": generate_hash(line)  # ✅ IMPORTANT for deduplication
    }
