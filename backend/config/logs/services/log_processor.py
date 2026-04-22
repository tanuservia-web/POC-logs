import traceback
from logs.models import LogFile, ParsedLogEntry
from logs.parser import parse_single_line


def process_log_file(file_data, log_id):
    log = LogFile.objects.get(id=log_id)

    try:
        lines = file_data.splitlines()
        total_lines = len(lines)

        log.total_lines = total_lines
        log.save(update_fields=["total_lines"])

        unique_entries = {}
        processed = 0

        for raw_line in lines:
            try:
                line = raw_line.decode("utf-8").strip()
            except:
                continue

            if not line:
                continue

            entry = parse_single_line(line)

            # ✅ only ERROR & CRITICAL
            if entry["level"] not in ["ERROR", "CRITICAL"]:
                continue

            key = entry["hash"]

            if key not in unique_entries:
                unique_entries[key] = entry

            processed += 1

            # ✅ update progress
            if processed % 100 == 0:
                log.processed_lines = processed
                log.progress = int((processed / total_lines) * 100)
                log.save(update_fields=["processed_lines", "progress"])

        # ✅ save unique entries
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
        log.progress = 100
        log.processed_lines = total_lines
        log.save()

    except Exception as e:
        print("❌ ERROR:", e)

        log.status = "FAILED"
        log.save()
