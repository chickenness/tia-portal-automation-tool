import base64
import json
import argparse
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple tool for automating TIA Portal projects.")
    parser.add_argument("-r", "--res",
                        type=Path,
                        required=True,
                        help="Directory for Siemens.Engineering.dll"
                        )
    args = parser.parse_args()

    res_dir: Path = args.res

    b64_dlls: dict[str, str] = {}

    count = 0
    for child in res_dir.iterdir():
        if not child.is_file():
            continue
        with open(child, 'rb') as dll:
            if child.suffix.lower() != '.dll':
                continue
            print(f"Opening {child}...")
            encoded_dll = base64.b64encode(dll.read()).decode('utf-8')
            b64_dlls[child.stem] = encoded_dll
            count += 1

    b64_output_script: Path = res_dir / "dlls.py"

    with open(b64_output_script, 'w', encoding='utf-8') as file:
        file.write(f"b64_dlls = {json.dumps(b64_dlls, indent=4)}\n")
        print(f"Written {count} DLLs to {b64_output_script}.")
