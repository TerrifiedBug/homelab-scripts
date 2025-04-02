"""Script to move all compose variables into stack.env for tidyness"""

import os
import subprocess

import yaml

STACKS_DIR = "homelab-stacks"


def fix_yaml_tabs():
    """First ensure all tabs are fixed in compose files"""
    print("[*] Fixing tabs in docker-compose.yml files...")
    try:
        subprocess.run(
            [
                "find",
                STACKS_DIR,
                "-name",
                "docker-compose.yml",
                "-exec",
                "sed",
                "-i",
                "s/\t/  /g",
                "{}",
                "+",
            ],
            check=True,
        )
        print("[✓] Tabs replaced with spaces in all compose files")
    except subprocess.CalledProcessError as e:
        print("[!] Error while fixing tabs:", e)


def tidy_stack_envs():
    """Loop through all stacks and create stack.env files and update compose to use stack.env"""
    fix_yaml_tabs()  # Run tab fix before parsing anything

    for stack_name in os.listdir(STACKS_DIR):
        stack_path = os.path.join(STACKS_DIR, stack_name)
        compose_file = os.path.join(stack_path, "docker-compose.yml")
        env_file = os.path.join(stack_path, "stack.env")

        if not os.path.isfile(compose_file):
            continue

        with open(compose_file, "r", encoding="utf-8") as f:
            try:
                compose = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"[!] Skipping {stack_name}: invalid YAML ({e})")
                continue

        services = compose.get("services", {})
        updated = False
        merged_env = {}

        # Step 1: Load existing stack.env file (if exists)
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        merged_env[key] = value

        for service_name, service_def in services.items():
            env_list = service_def.get("environment")
            if not env_list:
                continue

            # Step 2: Merge in new environment variables from docker-compose.yml
            for item in env_list:
                if isinstance(item, str) and "=" in item:
                    key, value = item.split("=", 1)
                    merged_env[key.strip()] = value.strip()
                elif isinstance(item, dict):
                    for k, v in item.items():
                        merged_env[k.strip()] = str(v).strip()

            # Step 3: Replace environment block with env_file reference
            service_def.pop("environment")
            service_def["env_file"] = ["stack.env"]
            updated = True
            print(f"[+] Cleaned up {stack_name}/{service_name}")

        # Step 4: Write merged stack.env file
        if updated:
            with open(env_file, "w", encoding="utf-8") as f:
                for key in sorted(merged_env.keys()):
                    f.write(f"{key}={merged_env[key]}\n")
            print(f"[+] Merged stack.env written to {env_file}")

            # Step 5: Update docker-compose.yml
            with open(compose_file, "w", encoding="utf-8") as f:
                yaml.dump(compose, f, sort_keys=False)
                print(f"[✓] Updated: {compose_file}")


if __name__ == "__main__":
    tidy_stack_envs()
