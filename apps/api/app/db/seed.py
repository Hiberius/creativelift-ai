from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    demo_path = Path(__file__).resolve().parents[4] / "examples" / "demo-data" / "seed.json"
    print(json.dumps({"status": "seed_scaffold", "source": str(demo_path)}))


if __name__ == "__main__":
    main()
