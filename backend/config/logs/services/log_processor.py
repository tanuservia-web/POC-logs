import traceback
from logs.models import LogFile, ParsedLogEntry
from logs.parser import parse_log_file  # adjust if different


import traceback
from logs.models import LogFile, ParsedLogEntry
from logs.parser import parse_log_file


def process_log_file(file_data, log_id):
    log = LogFile.objects.get(id=log_id)

    try:
        lines = file_data.splitlines()
        entries = parse_log_file(lines)

        entries = entries[:5000]

        unique_entries = {}

        for e in entries:
            if e["level"] not in ["ERROR", "CRITICAL"]:
                continue

            key = e["hash"]

            if key not in unique_entries:
                unique_entries[key] = e

        if not unique_entries:
            log.status = "COMPLETED"
            log.save()
            return

        ParsedLogEntry.objects.bulk_create(
            [
                ParsedLogEntry(
                    log_file_id=log_id,
                    timestamp=e["timestamp"],
                    level=e["level"],
                    category=e["category"],
                    message=e["message"][:500],
                    hash=e["hash"],
                )
                for e in unique_entries.values()
            ],
            batch_size=1000
        )

        log.status = "COMPLETED"
        log.save()

    except Exception as e:
        print("❌ Error processing logs:", str(e))
        traceback.print_exc()

        log.status = "FAILED"
        log.save()
