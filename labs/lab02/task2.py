import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

logger = logging.getLogger(__name__)

CRITICAL_RESOURCES = {
    "Confidential_HR_DB",
    "Finance_Server_NAS",
    "/api/v1/export",
}


def setup_logging(log_file: Path | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=handlers,
    )


def analyze_activity(activity_log_path: Path, after_hours_only: bool = False) -> dict:
    logger.info(f"Reading user activity log {activity_log_path}...")

    total_records = 0

    off_hours_alerts = []
    user_requests_per_min: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )

    try:
        with open(activity_log_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                total_records += 1

                user = row["UserID"]
                action = row["Action"]
                resource = row["Resource"]
                ip = row["IP"]
                ts_str = row["Timestamp"]

                ts = datetime.fromisoformat(ts_str)

                is_night = ts.hour >= 22 or ts.hour < 6
                is_weekend = ts.weekday() in (5, 6)

                if is_night or is_weekend:
                    alert = {
                        "user": user,
                        "action": action,
                        "resource": resource,
                        "ip": ip,
                        "timestamp": ts_str,
                        "reason": "Weekend" if is_weekend else "Off-Hours Night",
                    }
                    off_hours_alerts.append(alert)
                    logger.warning(
                        f"User '{user}' performed action '{action}' "
                        f"at {ts_str} (Resource: {resource}, IP: {ip})"
                    )

                minute_key = ts.strftime("%Y-%m-%d %H:%M")
                user_requests_per_min[user][minute_key][resource] += 1

    except FileNotFoundError as error:
        print(f"[FILE NOT FOUND]: {error}")
        return {}
    except PermissionError as error:
        print(f"[PERMISSION ERROR]: {error}")
        return {}
    except OSError as error:
        print(f"[IO ERROR]: {error}")
        return {}

    logger.info(f"Total records processed: {total_records}.")

    mass_download_alerts = []

    for user, minutes in user_requests_per_min.items():
        for min_key, resources in minutes.items():
            for resource, count in resources.items():
                if count > 50 and resource in CRITICAL_RESOURCES:
                    alert = {
                        "user": user,
                        "requests": count,
                        "time_window": min_key,
                        "resource": resource,
                    }
                    mass_download_alerts.append(alert)
                    logger.warning(
                        f"User '{user}' executed {count} requests "
                        f"to critical resource '{resource}' "
                        f"within time window {min_key}."
                    )

    print("\n=== Off-Hours Activity Alerts (22:00 - 06:00 / Weekends) ===")

    for alert in off_hours_alerts:
        print(
            f"[ALERT] User '{alert['user']}' performed action "
            f"'{alert['action']}' at {alert['timestamp']} "
            f"(Resource: {alert['resource']}, IP: {alert['ip']})"
        )

    if not after_hours_only:
        print("\n=== Mass Download Anomalies (>50 requests/min) ===")

        for alert in mass_download_alerts:
            print(
                f"[ALERT] User '{alert['user']}' executed "
                f"{alert['requests']} requests to "
                f"'{alert['resource']}' within time window "
                f"{alert['time_window']}."
            )

    return {
        "student": f"{STUDENT_NAME} ({GROUP_NAME}, Var {VARIANT_NUMBER})",
        "total_records": total_records,
        "off_hours_alerts": off_hours_alerts,
        "mass_download_alerts": mass_download_alerts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="User Activity Audit CLI Utility (Variant 7)"
    )

    parser.add_argument(
        "--activity-log",
        required=True,
        type=Path,
        help="Шлях до CSV-файлу логів активності",
    )

    parser.add_argument(
        "--after-hours",
        action="store_true",
        help="Фільтрувати та відображати лише події позаробочого часу",
    )

    parser.add_argument(
        "--out-report",
        type=Path,
        help="Шлях до файла вивантаження підсумкового JSON-звіту",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        help="Шлях до файлу системних логів",
    )

    args = parser.parse_args()

    setup_logging(args.log_file)

    report_data = analyze_activity(
        args.activity_log,
        args.after_hours,
    )
    if not report_data:
        return

    if args.out_report:
        args.out_report.parent.mkdir(parents=True, exist_ok=True)

        with open(args.out_report, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        logger.info(f"Anomalous activity report written to {args.out_report}")


if __name__ == "__main__":
    main()
