import argparse
import sys

import task1
import task2


def main() -> None:
    parser = argparse.ArgumentParser(description="Лабораторна робота №2")
    parser.add_argument("task", choices=["1", "2"], help="Номер завдання")
    args, remaining = parser.parse_known_args()

    if args.task == "1":
        task1.main()
    else:
        sys.argv = [sys.argv[0]] + remaining
        task2.main()


if __name__ == "__main__":
    main()
