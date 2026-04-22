import traceback
from logs.models import LogFile, ParsedLogEntry
from logs.parser import parse_log_file  # adjust if different


import traceback
from logs.models import LogFile, ParsedLogEntry
from logs.parser import parse_log_file


def process_log_file(file, log_id):
    log = LogFile.objects.get(id=log_id)

    try:
        unique_entries = {}
        count = 0
        MAX_LINES = 100000  # safety limit

        for raw_line in file:
            if count > MAX_LINES:
                break

            try:
                line = raw_line.decode("utf-8").strip()
            except:
                continue

            if not line:
                continue

            # 👉 reuse your parser logic
            entry = parse_single_line(line)  # create this helper

            if entry["level"] not in ["ERROR", "CRITICAL"]:
                continue

            key = entry["hash"]

            if key not in unique_entries:
                unique_entries[key] = entry

            count += 1

        ParsedLogEntry.objects.bulk_create([
            ParsedLogEntry(
                log_file_id=log_id,
                timestamp=e["timestamp"],
                level=e["level"],
                category=e["category"],
                message=e["message"][:500],
                hash=e["hash"]
            )
            for e in unique_entries.values()
        ])

        log.status = "COMPLETED"
        log.save()

    except Exception as e:
        log.status = "FAILED"
        log.save()
