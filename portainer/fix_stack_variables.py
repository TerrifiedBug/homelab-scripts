#!/usr/bin/env python3
# Requires: pip install ruamel.yaml
import logging
import re
from pathlib import Path

from ruamel.yaml import YAML

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base directory where portainer-stacks are located
BASE_DIR = "portainer-stacks"


def parse_env_file(env_file_path):
    """Parse a .env file and extract variable names that are marked as 'redacted'."""
    redacted_vars = []

    try:
        with open(env_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Match lines with format VAR=redacted or VAR="redacted"
                match = re.match(
                    r'^([A-Za-z0-9_]+)=(?:"?redacted"?|\'?redacted\'?)$', line
                )
                if match:
                    redacted_vars.append(match.group(1))
    except (IOError, OSError, UnicodeDecodeError) as e:
        logger.error("Error parsing env file %s: %s", env_file_path, e)

    return redacted_vars


def update_compose_file(compose_file_path, redacted_vars, _stack_path):
    """Update the docker-compose.yml file to use ${VAR} syntax for redacted variables."""
    logger.info("Processing %s", compose_file_path)

    try:
        # Configure YAML parser to preserve format
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)

        # Load the YAML file
        with open(compose_file_path, "r", encoding="utf-8") as f:
            compose_data = yaml.load(f)

        if not compose_data:
            logger.warning("Empty or invalid YAML in %s", compose_file_path)
            return False

        changes_made = False

        # Process all services
        if "services" in compose_data:
            for service_name, service_config in compose_data["services"].items():
                # Only modify services that explicitly use stack.env
                if "env_file" in service_config:
                    # Handle both string and list formats for env_file
                    env_files = service_config["env_file"]
                    if not isinstance(env_files, list):
                        env_files = [env_files]

                    # Skip if this service doesn't use stack.env
                    if "stack.env" not in env_files:
                        continue

                    # Add environment section if it doesn't exist
                    if "environment" not in service_config:
                        service_config["environment"] = {}

                    # If environment is a list, convert to dict
                    if isinstance(service_config["environment"], list):
                        env_dict = {}
                        for item in service_config["environment"]:
                            if "=" in item:
                                key, value = item.split("=", 1)
                                env_dict[key] = value
                        service_config["environment"] = env_dict

                    # Add redacted variables with ${VAR} syntax
                    for var in redacted_vars:
                        # Skip if already explicitly defined
                        if var not in service_config["environment"]:
                            service_config["environment"][var] = f"${{{var}}}"
                            changes_made = True
                            logger.info("Added ${%s} to service %s", var, service_name)

        # If changes were made, write the updated file
        if changes_made:
            with open(compose_file_path, "w", encoding="utf-8") as f:
                yaml.dump(compose_data, f)
            logger.info("Updated %s", compose_file_path)
            return True
        else:
            logger.info("No changes needed for %s", compose_file_path)
            return False

    except Exception as e:
        logger.error("Error updating %s: %s", compose_file_path, e)
        return False


def main():
    """Process all stacks in the base directory."""
    base_path = Path(BASE_DIR)

    # Check if base directory exists
    if not base_path.exists() or not base_path.is_dir():
        logger.error("Base directory %s does not exist or is not a directory", BASE_DIR)
        return

    # Count statistics
    total_stacks = 0
    updated_stacks = 0

    # Process each subdirectory (stack)
    for stack_dir in base_path.iterdir():
        if not stack_dir.is_dir():
            continue

        stack_name = stack_dir.name
        env_file_path = stack_dir / "stack.env"
        compose_file_path = stack_dir / "docker-compose.yml"

        # Skip if either file doesn't exist
        if not env_file_path.exists() or not compose_file_path.exists():
            logger.warning(
                "Stack %s is missing stack.env or docker-compose.yml, skipping",
                stack_name,
            )
            continue

        total_stacks += 1

        # Get redacted variables from stack.env
        redacted_vars = parse_env_file(env_file_path)

        if redacted_vars:
            logger.info(
                "Found %d redacted variables in %s: %s",
                len(redacted_vars),
                stack_name,
                ", ".join(redacted_vars),
            )

            # Update the compose file
            if update_compose_file(compose_file_path, redacted_vars, stack_dir):
                updated_stacks += 1
        else:
            logger.info("No redacted variables found in %s", stack_name)

    logger.info("Processed %d stacks, updated %d", total_stacks, updated_stacks)


if __name__ == "__main__":
    main()
