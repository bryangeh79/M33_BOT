import argparse
import os
from pathlib import Path


def load_runtime_config(config_dir: str) -> dict:
    config_path = Path(config_dir)
    env_file = config_path / ".env"

    if not env_file.exists():
        raise FileNotFoundError(f"Config file not found: {env_file}")

    env_vars = {}
    with open(env_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def main():
    parser = argparse.ArgumentParser(description="Debug settlement with bot config")
    parser.add_argument("--config-dir", required=True, help="Path to generated bot config directory")
    parser.add_argument("--date", required=True, help="Settlement date, e.g. 2026-04-09")
    parser.add_argument("--regions", nargs="*", default=["MN", "MT", "MB"], help="Region groups to settle")
    args = parser.parse_args()

    env_vars = load_runtime_config(args.config_dir)
    os.environ["DB_PATH"] = env_vars.get("DB_PATH", "data/m33_lotto.db")
    os.environ["BOT_TOKEN"] = env_vars.get("BOT_TOKEN", "")
    os.environ["CLIENT_NAME"] = env_vars.get("CLIENT_NAME", "")
    os.environ["DEFAULT_LANGUAGE"] = env_vars.get("DEFAULT_LANGUAGE", "vi")
    os.environ["ALLOWED_GROUP_ID"] = env_vars.get("ALLOWED_GROUP_ID", "")
    os.environ["DEFAULT_ADMIN_USER_IDS"] = env_vars.get("DEFAULT_ADMIN_USER_IDS", "")
    os.environ["LOG_PATH"] = env_vars.get("LOG_PATH", "app.log")

    from src.modules.settlement.settlement_service import settle_region

    print(f"DB_PATH={os.environ['DB_PATH']}")
    for region in args.regions:
        region = str(region).strip().upper()
        print(f"\n=== settle_region({region}) ===")
        try:
            result = settle_region(args.date, region)
            print(result)
        except Exception as exc:
            print(f"ERROR: {exc}")
            raise


if __name__ == "__main__":
    main()
