"""
Validate that Moses is properly configured for this assignment.

Usage:
    python scripts/validate_moses.py --source "Hello, how are you?"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.moses_interface import create_moses_decoder


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Moses configuration")
    parser.add_argument("--source", default="Hello, how are you?", help="English source sentence")
    args = parser.parse_args()

    decoder = create_moses_decoder()
    status = decoder.get_status()

    print("Moses validation report")
    print("=======================")
    print(f"Available     : {status['available']}")
    print(f"Moses binary  : {status['moses_bin']}")
    print(f"moses.ini path: {status['moses_ini']}")
    print(f"Binary exists : {status['moses_exists']}")
    print(f"INI exists    : {status['ini_exists']}")

    if not decoder.is_available:
        print("\nValidation result: FAIL")
        print("Set MOSES_BIN_PATH and MOSES_INI_PATH, then run again.")
        return 1

    translation = decoder.translate(args.source)
    if not translation:
        print("\nValidation result: FAIL")
        print("Decoder is available but returned empty output.")
        return 1

    print("\nValidation result: PASS")
    print(f"Source     : {args.source}")
    print(f"Translation: {translation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
