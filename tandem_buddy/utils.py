import pathlib

# Define the marker file path
DOCKER_ENV_MARKER = "/.dockerenv"

def running_from_docker_container() -> bool:
    """Check if the code is running inside a Docker container."""
    return pathlib.Path(DOCKER_ENV_MARKER).exists()

