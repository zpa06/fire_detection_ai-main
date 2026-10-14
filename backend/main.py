import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.CSDL.controllers.app_controller import AppController
from backend.CSDL.models.database import FireEyesDB


PROJECT_ROOT = Path(__file__).resolve().parent


def run_demo(db):
    """Tạo dữ liệu giả lập để kiểm tra luồng lưu CSDL thông qua Controller."""
    controller = AppController(db.path)
    return controller.run_demo()


def main():
    parser = argparse.ArgumentParser(
        description="FireEyes - Quan ly va kiem thu co so du lieu"
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="stats",
        choices=["init", "demo", "stats", "incidents"],
        help="Thao tac CSDL; mac dinh: stats",
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=PROJECT_ROOT / "data" / "fireeyes.db",
        help="Duong dan file SQLite",
    )

    args = parser.parse_args()

    db = FireEyesDB(args.db)
    db.initialize()

    if args.command == "init":
        print("Schema v2 ready:", db.path)
        return

    if args.command == "demo":
        result = run_demo(db)
    elif args.command == "stats":
        result = db.counts()
    else:
        result = db.list_incidents()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()