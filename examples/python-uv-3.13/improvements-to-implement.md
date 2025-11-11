Can you implement the following optimizations in the dockerfile /of the playwright headless docker example project with python?
which is located at `/Users/tobiashochgurtel/code-workspace/running-playwright-tests-in-docker-container/examples/python-uv-3.13`:

~~~
# Add uv to PATH for subsequent stages
ENV PATH="/root/.local/bin:$PATH"
~~~

That is good, but I think that is not persisting after the Build or if we do a `docker exec ...` or even when the `entrypoint.sh` is used..
we should think about to add the Path addon correctly to the shell rc files for the user (which might be `root` or change in the future, so we should make it yet already dynamic by reading out the current user).

~~~
# Verify uv installation
RUN uv --version && echo "✓ uv installed"
~~~

that is good, but not perfect, because it hides which version of `uv` got installed, that might be good to know when we build the container.

~~~
# Let uv install Python 3.13+ (will be determined by pyproject.toml)
# This creates a managed Python installation
WORKDIR /tmp
RUN echo '[project]' > pyproject.toml && \
  echo 'name = "temp"' >> pyproject.toml && \
  echo 'version = "0.1.0"' >> pyproject.toml && \
  echo 'requires-python = ">=3.13"' >> pyproject.toml && \
  uv python install && \
  rm pyproject.toml
~~~

here I'm not sure if that is correct enough because that might install also python 3.14 in the future or so?
We might find a proper way and more correct way to install `python` with `uv` from the docs at <https://docs.astral.sh/uv/guides/install-python/> ? Please read the website and check if we should change to a different approach which is more reliable and maybe doesn't need a `pyproject.toml` dummy file?

~~~
# Verify Python installation
RUN uv python list && echo "✓ Python managed by uv"
~~~

this is also great, but not optiomal, because it hides the output of `uv python list` and we can't see at the build time which pythons are really installed, we can improve that please.

~~~
# Verify installation
RUN curl --version && echo "✓ curl installed"
~~~

this is similar / same, we should hide the output.

Overall it's nice to have a simple anwer in the output like `✓ curl installed"`  we can keep that, but we should also somehow show the real output to see the version numbers etc.

~~~
# Copy only dependency file (pyproject.toml)
# This enables Docker layer caching for dependency installation
COPY pyproject.toml .
~~~

this mostly perfect but has one damn downside, that each time when we change settings like pytest or ruff or mypy in the `pyproject.toml` that we will rebuild the Dockerfile stage becuase the settings changed and not the dependencies which are relevant for caching in this stage and should be the only reason why this stage should be rebuilded.
We should find improved solution like maybe we can define the dependencies in a second `.toml` file and tell `pyproject.toml` to include this second `.toml` into `pyproject.toml`, then we could just use the second `.toml` file in the Dockerfile Stage 3 to cache the dependencies by creating a generic `pyproject.toml` in the Dockerfile which includes the second `.toml` file with the dependencies.

~~~
# Create virtual environment and install Python dependencies
# Rebuilds only when pyproject.toml changes
ENV PIP_ROOT_USER_ACTION=ignore
RUN echo "📦 Installing Python dependencies..." && \
  uv sync --no-install-project && \
  echo "✓ Python dependencies installed"
~~~

here we might can add `--refresh` to the `uv sync ....` call, which would refresh the already existing venv with the dependencies. Atm. of course the `--refresh` doesn't make a difference because the dependencies get here the first time installed but I thought about to add Build Arguments, to build different variants of this Dockerfile Image, where we have a variant which can reuse a Build Cached `.venv` and would then apply via `uv sync --no-install-project --refresh` the needed changes to the `.venv` instead of installing all dependencies again? Is a idea from me, not sure if that idea is so great? Please tell me your opinion?

~~~
# Activate venv for subsequent commands
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"
~~~

The same as before with the `PATH` modifing....
> That is good, but I think that is not persisting after the Build or if we do a `docker exec ...` or even when the `entrypoint.sh` is used..
we should think about to add the Path addon correctly to the shell rc files for the user (which might be `root` or change in the future, so we should make it yet already dynamic by reading out the current user).

~~~
# Show installed Python version
RUN python --version && echo "✓ Python ready"
~~~

Here we executing directly `python` which looks for me like that we are executing the system python and maybe not the `uv` managed `python` or? We are also hiding the output and just show the success message, which I think we should always adjust to show the real output and then the success message to be more verbose and helpful.

Here we might want to add also `which python` or `command -v python` to see which python is in path and is used when we just call `python`?

~~~
# Install Playwright browsers (Firefox) - better ARM64 compatibility
# We do this in dependencies stage so it's cached
# Firefox typically works more reliably on ARM64/Apple Silicon than Chromium
# Note: Use .venv/bin/playwright directly since project doesn't have module structure
RUN echo "🦊 Installing Playwright Firefox browser..." && \
  .venv/bin/playwright install firefox --with-deps && \
  echo "✓ Firefox installed successfully"
~~~

That is good, but its unflexibel atm. because we always install Firefox. I thought we should add a Build Argument to control what we wantt to install Firefox, Chrome, or other browsers which are supported by playwright?

I have the following Snippet for installing Chrome:

~~~
# Install Playwright browsers (Chromium) - this is the heavy part
# We do this in dependencies stage so it's cached
RUN echo "🌐 Installing Playwright Chromium browser..." && \
  uv run playwright install chromium --with-deps && \
  echo "✓ Chromium installed"

# Verify browser installation
RUN echo "🔍 Verifying browser installation..." && \
  uv run playwright show-browsers && \
  echo "✓ Browser verification complete"
~~~

Which might help to build a flexible solution via Build Arguments.

~~~
# Copy test files
# This layer rebuilds when tests change, but dependencies are cached
# Note: pytest config is in pyproject.toml (already copied in dependencies stage)
COPY tests/ /app/tests/

# Verify tests were copied
RUN echo "📋 Test files:" && \
  find /app/tests -name "*.py" -type f && \
  echo "✓ Tests copied successfully"
~~~

That is also okay, but not perfect because we cache the tests in the container image and that could be improved by add Volume Mount to the Dockerfile so that we not copy the tests and rebuild the stage each time when the tests changed.

~~~
# Environment configuration
ENV PLAYWRIGHT_HEADLESS=true
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"
ENV UV_CACHE_DIR=/app/.cache/uv
~~~

The ENV variables which we are setting up here in the last stage, I'm not sure if that is the best approach because they might get lost when we execute the `entrypoint.sh` file or when we would add more stages to the Dockerfifle, I'm not sure if they would be available after Build or in the next stage.
I'm only not sure, if we can overwrite theses ENV variables via `docker` cli or `docker compose` cli or `docker-compose.yml`, that should be possible.

~~~
# Create output directories
RUN mkdir -p /app/test-results /app/htmlreport
~~~

This is okay, but I'm not sure if that works with a VOLUME Mount together, which I think would be the goal. Do we have to add `VOLUME` instruction (<https://docs.docker.com/reference/dockerfile/#volume>) to the Dockerfile for the Volume mounts which we want to have in the Dockerimage? At least for documentation that would be good?

~~~
# Default: run all tests with verbose output
# Override with: docker-compose run --rm playwright pytest -vv tests/test_google.py
CMD ["-vv", "--tb=short", "tests/"]
~~~

the default `CMD` could be improved with settings the VERBOSE Level via ENV variable and the default value of `--tb=` should be `long` and not `short` but we want to be able to overrwrite the default command `tb` value via ENV variable, if possible.

The shell script `examples/python-uv-3.13/entrypoint.sh` could be improved to use as much as possible bash builtin features instead of `echo` which is a external command as I know? Also the simple `sed` to search and replace in a string can be done via bash builtin features. That would improve the performance of the Dockerimage when it executed. We still can use colors with bash builtins. We should add a `NO_COLORS` ENV variable to deactivate colorful output.

~~~
# Check for Chromium browser
echo -e "${BLUE}🌐 Browser Installation Check:${NC}"
if .venv/bin/playwright show-browsers 2>&1 | grep -q "chromium"; then
  echo -e "   ${GREEN}✓ Chromium browser installed${NC}"
else
  echo -e "   ${RED}✗ Chromium browser NOT installed${NC}"
  echo -e "   ${YELLOW}Installing browsers now...${NC}"
  .venv/bin/playwright install chromium --with-deps
fi
echo ""
~~~

The check for the browser should be similar like the above announced change of using a Build Argument to create variants of the Dockerfile with Firefox, Chrome or other browsers preinstalled to check the defined Browser which we setup via Build Arguments while we build the image, and then we should make it possible to check / install in the `entrypoint.sh` via ENV variables a different Browser as we added while we builded the Dockerfile Image.

~~~
# Start Xvfb (virtual framebuffer X server) in the background
# Required for Chromium to run in headless mode on ARM64
echo -e "${BLUE}🖥️  Starting Xvfb on display :99...${NC}"
Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
export DISPLAY=:99
~~~

Here we have some issues, because we define fixed values to the call to `Xvfb` which already uses the Display Number `99` and later we export the Display Number via the ENV variable `DISPLAY`. That's not so elegant and flexible, and we should change the code so that we can define the `DISPLAY` env variable via `docker` cli or `docker-compose.yml` file via the env variables and by default if not defined we use `:99`.

The setting for the resolution of `1280x1024x24` is always fixed, what is not so good for the flexibility, because we can't define a different resolution which would be handy for several use cases.

~~~
# Wait for Xvfb to be ready
sleep 2
echo -e "${GREEN}✓ Xvfb ready (PID: $XVFB_PID)${NC}"
echo ""
~~~

the sleep of 2 seconds, is somehow a performance isssue, what we might can somehow improve?

~~~
# Execute command directly from venv (not through 'uv run')
# Note: 'uv run' requires module structure, but this is a test-only project
if [ $# -eq 0 ]; then
  .venv/bin/pytest
  EXIT_CODE=$?
else
  # Check if first argument is pytest-related
  if [[ "$1" == "pytest"* ]] || [[ "$1" == "-"* ]]; then
    # Run pytest directly from venv
    .venv/bin/pytest "$@"
    EXIT_CODE=$?
  else
    # For other commands, try to run from venv
    .venv/bin/"$*"
    EXIT_CODE=$?
  fi
fi

# Clean up Xvfb
kill $XVFB_PID 2>/dev/null || true
exit $EXIT_CODE
~~~

here we are using `EXIT_CODE` which might be not defined, we should set `EXIT_CODE` before the conditions with a default value, so that we will exit with a exit code in any case.

~~~
# Clean up Xvfb
kill $XVFB_PID 2>/dev/null || true
~~~

Here it could be that `XVFB_PID` is not defined, becaue of a previous error which could happend because we defined a resolution which is wrong (just a simple example), we might can improve that we check if `XVFB_PID` is defined with a value before we try to kill?

------

- Use `shellcheck` to check the `entrypoint.sh` for possible improvements and fix the issues which `shellcheck` reports.
- Use `hadolint` to check the Dockerfile for best practices and fix the issues which `hadolint` reports.
- Add comments to the Dockerfile and `entrypoint.sh` where needed to explain the purpose of complex commands or sections for better maintainability.
- Ensure consistent formatting and indentation throughout the Dockerfile and `entrypoint.sh` for improved readability.
- Test the Dockerfile and `entrypoint.sh` after making changes to ensure that all functionalities work as expected and that no new issues have been introduced.
- Document any new ENV variables or Build Arguments added to the Dockerfile and `entrypoint.sh` in a `README.md` file for users to understand how to use them.
- Document the Build Arguments which can be used to build different variants of the Dockerfile Image.
  - use `go-task` to create a Taskfile which can build different variants of the Dockerfile Image.
    - References:
      - [Task](https://taskfile.dev/)
      - [Task: Getting Started](https://taskfile.dev/docs/getting-started)
      - [Task: Guide](https://taskfile.dev/docs/guide)
      - [Task: Taskfile Schema Reference](https://taskfile.dev/docs/reference/schema)
      - [Task: Environment Reference](https://taskfile.dev/docs/reference/environment)
      - [Task: Configuration Reference](https://taskfile.dev/docs/reference/config)
      - [Task: Command Line Interface Reference](https://taskfile.dev/docs/reference/cli)
      - [Task: Templating Reference](https://taskfile.dev/docs/reference/templating)
      - [Task: Experiments](https://taskfile.dev/docs/experiments/)
        - [Task: Experiments: Env Precedence (#1038)](https://taskfile.dev/docs/experiments/env-precedence)
        - [Task: Experiments: Gentle Force (#1200)](https://taskfile.dev/docs/experiments/gentle-force)
        - [Task: Experiments: Remote Taskfiles (#1317)](https://taskfile.dev/docs/experiments/remote-taskfiles)
      - [Task: Taskfile Versions](https://taskfile.dev/docs/taskfile-versions)
      - [Task: Style Guide](https://taskfile.dev/docs/styleguide)
      - [Task: Changelog](https://taskfile.dev/docs/changelog)
      - [Task: FAQ](https://taskfile.dev/docs/faq)
      - [Task: Blog](https://taskfile.dev/blog/)
    - you can combine it with a `docker-compose.yml` file which builds the images with variant names like `myimage:python-uv-3.13-firefox` or `myimage:python-uv-3.13-chromium` etc. to make it easy to use the different variants.
- Consider security best practices when modifying the Dockerfile, such as minimizing the number of layers, using specific versions of base images, and avoiding the use of unnecessary packages.
- Optimize the Dockerfile for build speed and image size where possible, such as by combining RUN commands or using multi-stage builds if applicable.
- Review the Dockerfile and `entrypoint.sh` for any potential compatibility issues with different environments or platforms, especially considering ARM64/Apple Silicon support.
- Ensure that any changes made do not affect the existing functionality of running Playwright tests in a Docker container with Python and `uv`.
- After implementing the changes, provide a summary of the optimizations made and any new features added to the Dockerfile and `entrypoint.sh`.
- Update any related documentation or examples to reflect the changes made to the Dockerfile and `entrypoint.sh`.
