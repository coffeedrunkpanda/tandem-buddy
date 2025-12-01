# Use a Python image with uv pre-installed for development speed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS dev_base

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files only for initial installation
COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Set the PATH to include the virtual environment's executables
ENV PATH="/app/.venv/bin:$PATH"

# Gradio default port
EXPOSE 7860

# Set the entrypoint to run the application
CMD ["uv", "run", "python", "app.py", "--host", "0.0.0.0"] 
