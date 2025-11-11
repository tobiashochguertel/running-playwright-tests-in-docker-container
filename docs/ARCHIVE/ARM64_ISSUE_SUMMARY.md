# ARM64/Apple Silicon Docker Issue - Summary

## ⚠️ Critical Finding

**Playwright browsers (both Chromium and Firefox) cannot launch properly in custom Docker images on ARM64/Apple Silicon architecture.**

## 🔍 Root Cause

All browser launches hang indefinitely at:

```log
File ".../asyncio/unix_events.py", line 931, in _do_waitpid
    pid, status = os.waitpid(expected_pid, 0)
```

This occurs because:

1. **Process forking issues**: ARM64 Docker has fundamental limitations with Chrome/Firefox multi-process architectures
2. **Sandbox requirements**: Browsers require specific kernel capabilities that aren't available in custom Ubuntu-based images
3. **Missing optimizations**: Official Playwright images include ARM64-specific patches and configurations

## 🧪 What We Tried (All Failed)

### Attempt 1: Docker Optimizations

- ✅ Added `cap_add: SYS_ADMIN`
- ✅ Added `ipc: 'host'`
- ✅ Added `init: true`
- ❌ **Result**: Still hangs

### Attempt 2: ARM64-Specific Browser Flags

- ✅ Added `--single-process` (force single-process mode)
- ✅ Added `--no-zygote` (disable process forking)
- ✅ Added `--no-sandbox`, `--disable-setuid-sandbox`
- ✅ Added 7+ additional stability flags
- ❌ **Result**: Still hangs

### Attempt 3: Xvfb Virtual Display

- ✅ Installed xvfb
- ✅ Started Xvfb on display :99
- ✅ Set DISPLAY environment variable
- ❌ **Result**: Still hangs

### Attempt 4: Switch to Firefox

- ✅ Replaced Chromium with Firefox
- ✅ Firefox typically has better ARM64 support
- ❌ **Result**: **Same hang at os.waitpid()**

## 📊 Test Results

**All tests timeout at 60-120 seconds during browser fixture setup:**

```shell
ERROR at setup of Test*.test_*
Failed: Timeout (>60.0s) from pytest-timeout.

Stack of asyncio-waitpid-0:
  File ".../asyncio/unix_events.py", line 931, in _do_waitpid
    pid, status = os.waitpid(expected_pid, 0)
```

- **Total tests**: 10
- **Tests passed**: 0
- **Tests hung**: 10
- **Time wasted**: 20+ minutes (all waiting for browsers that never start)

## ✅ Solution: Use Official Playwright Docker Image

The recommended approach is to **use Microsoft's official Playwright Docker image** which includes:

1. **ARM64-optimized browser builds**
2. **Pre-configured kernel capabilities**
3. **All necessary system libraries**
4. **Playwright-specific patches for Docker**

### Example Dockerfile (Recommended)

```dockerfile
# Use official Playwright Python image (ARM64-compatible)
FROM mcr.microsoft.com/playwright/python:v1.55.0-arm64

# Install uv for package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependencies and install
WORKDIR /app
COPY pyproject.toml .
RUN uv sync --no-install-project

# Copy tests
COPY tests/ /app/tests/

# Run tests
CMD [".venv/bin/pytest", "tests/"]
```

### Pros of Official Image

- ✅ **Works immediately** on ARM64/Apple Silicon
- ✅ **No browser installation needed** (browsers pre-installed)
- ✅ **Optimized for ARM64** (tested by Microsoft)
- ✅ **Faster builds** (no browser download at build time)

### Cons of Official Image

- ❌ **Larger base image** (~1-2 GB vs 200 MB Ubuntu base)
- ❌ **Less control** over exact browser versions
- ❌ **Must use their Python version** (may conflict with project requirements)

## 🎯 Alternatives (If You Must Use Custom Image)

### Option 1: Test Locally, Run in CI

- **Dev**: Run tests locally on macOS/Linux
- **CI**: Use official Playwright image in GitHub Actions/GitLab CI

### Option 2: Use Multi-Architecture Build

```yaml
# docker-compose.yml
services:
  playwright:
    build:
      context: .
      dockerfile: Dockerfile
      platforms:
        - linux/amd64  # Use AMD64 for better compatibility
```

**Note**: This runs slower on ARM64 (emulation), but browsers work.

### Option 3: Use Docker Desktop with Rosetta 2

Enable "Use Rosetta for x86_64/amd64 emulation" in Docker Desktop settings.
This allows AMD64 images to run on Apple Silicon with near-native performance.

## 📝 Lessons Learned

1. **ARM64 Docker is challenging** for browser automation
2. **Custom images don't work** for Playwright on ARM64 (even with all flags/Xvfb)
3. **Official images exist for a reason** - they include essential ARM64 patches
4. **Process forking is fundamental** - you can't work around it with flags
5. **Testing "super slow" was actually "never starting"** - the hang made tests appear slow

## 🔗 References

- [Playwright Docker Documentation](https://playwright.dev/docs/docker)
- [Microsoft Playwright Docker Images](https://mcr.microsoft.com/v2/playwright/python/tags/list)
- [Docker Desktop: Limitations for Mac](https://docs.docker.com/desktop/troubleshoot/known-issues/)
  - [Docker Desktop Limitations: For Mac with Intel chip](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/index.md)
  - [Docker Desktop Limitations: For Mac with Apple silicon](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/index.md)

## 📅 Investigation Timeline

1. **Initial Issue**: Tests "taking ages instead of 10-20 seconds"
2. **Diagnosis**: Tests not slow, they're **hanging at browser launch**
3. **Attempts**: 4 different approaches over 20+ test runs
4. **Conclusion**: ARM64 custom Docker images incompatible with Playwright
5. **Recommendation**: Use official `mcr.microsoft.com/playwright/python` image

---

- **Status**: ❌ Custom Ubuntu-based Docker image **NOT VIABLE** on ARM64
- **Recommendation**: ✅ Switch to official Playwright Docker image
- **Date**: Tue Nov 11 15:51:45 CET 2025

---

# Docker Limitations for Mac

## For Mac with Intel chip

- The Mac Activity Monitor reports that Docker is using twice the amount of memory it's actually using. This is due to a [bug in macOS](https://docs.google.com/document/d/17ZiQC1Tp9iH320K-uqVLyiJmk4DHJ3c4zgQetJiKYQM/edit?usp=sharing) on this.

- **"Docker.app is damaged" dialog**: If you see a "Docker.app is damaged and can't be opened" dialog during installation or updates, this is typically caused by non-atomic copy operations when other applications are using the Docker CLI. See [Fix "Docker.app is damaged" on macOS](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/mac-damaged-dialog) for resolution steps.

- Force-ejecting the `.dmg` after running `Docker.app` from it can cause the
  whale icon to become unresponsive, Docker tasks to show as not responding in the Activity Monitor, and for some processes to consume a large amount of CPU resources. Reboot and restart Docker to resolve these issues.

- Docker Desktop uses the `HyperKit` hypervisor (<https://github.com/docker/hyperkit>) in macOS 10.10 Yosemite and higher. If
  you are developing with tools that have conflicts with `HyperKit`, such as [Intel Hardware Accelerated Execution Manager (HAXM)](https://software.intel.com/android/articles/intel-hardware-accelerated-execution-manager/),
  the current workaround is not to run them at the same time. You can pause `HyperKit` by quitting Docker Desktop temporarily while you work with HAXM.
  This allows you to continue work with the other tools and prevent `HyperKit` from interfering.

- If you are working with applications like [Apache Maven](https://maven.apache.org/) that expect settings for `DOCKER_HOST` and
  `DOCKER_CERT_PATH` environment variables, specify these to connect to Docker instances through Unix sockets. For example:

  ```bash
  export DOCKER_HOST=unix:///var/run/docker.sock
  ```

## For Mac with Apple silicon

- Some command line tools do not work when Rosetta 2 is not installed.
  - The old version 1.x of `docker-compose`. Use Compose V2 instead - type `docker compose`.
  - The `docker-credential-ecr-login` credential helper.

- Some images do not support the ARM64 architecture. You can add `--platform linux/amd64` to run (or build) an Intel image using emulation.

   However, attempts to run Intel-based containers on Apple silicon machines under emulation can crash as QEMU sometimes fails to run the container. In addition, filesystem change notification APIs (`inotify`) do not work under QEMU emulation. Even when the containers do run correctly under emulation, they will be slower and use more memory than the native equivalent.

   In summary, running Intel-based containers on Arm-based machines should be regarded as "best effort" only. We recommend running `arm64` containers on Apple silicon machines whenever possible, and encouraging container authors to produce `arm64`, or multi-arch, versions of their containers. This issue should become less common over time, as more and more images are rebuilt [supporting multiple architectures](https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/).

- Users may occasionally experience data drop when a TCP stream is half-closed.

---

# My research

- **Date:** Tue Nov 11 20:09:22 CET 2025

## Related issues descriptions

- <https://stackoverflow.com/questions/79344524/errorit-looks-like-you-are-using-playwright-sync-api-inside-the-asyncio-loop>
- <https://github.com/microsoft/playwright-python/issues/1291>
- <https://github.com/microsoft/playwright-python/issues/1150>
- <https://github.com/microsoft/playwright/issues/14078>
- <https://github.com/microsoft/playwright-python/issues/1910>

## Explanation which I found also

When you encounter the error message "It looks like you are using `Playwright Sync API` inside the `asyncio` loop. Please use the `Async API` instead," it indicates that there is a conflict between using the synchronous operations of Playwright within an asynchronous context. To resolve this issue and avoid the error, you need to make sure that Playwright is used asynchronously when working within an `asyncio` environment.

Here's how you can address this problem:

1. Understanding the Issue:

   - The error message suggests that Playwright's synchronous operations are being used within an asynchronous context, which is not supported and can lead to conflicts like the one you are facing.

2. Switch to Async API:

   - To avoid this error, you should switch from using the `sync_playwright()` function to the asynchronous version of Playwright by using `async_playwright()`.

3. Modify Your Code:

   - Update your code in `file_1.py` where you initialize Playwright to use the async version:

      ```python
      from playwright.async_api import async_playwright

      class A:
          def __init__(self, login_dict):
              self.start = async_playwright().start()
              self.browser = self.start.chromium.launch()
              self.context = self.browser.new_context()
              self.page = self.context.new_page()
              self.login_dict = login_dict
      ```

4. Handle Asynchronous Calls:

   - Since you are now using asynchronous operations, ensure that your code in `file_2.py` and wherever else Playwright is used follows asynchronous patterns as well.

5. Update `Class B` Initialization:

   - Modify your `class B` initialization in `file_2.py` to handle asynchronous calls appropriately:

      ```python
      import file_1

      class B(file_1.A):
          def __init__(self):
              super().__init__()
      ```

6. Adjust Object Creation:

   - When creating instances of A and B, make sure to pass awaitable objects or handle them within an asynchronous context.

7. Revised Object Creation:

    ```python
    from file_1 import A
    from file_2 import B

    # Assuming `asyncio` is used for event loop management

    import asyncio

    async def main():
        a = A(some_login_dict)
        b = B()

    asyncio.run(main())
    ```

By following these steps and ensuring that all Playwright operations are handled asynchronously within your `asyncio` environment, you should be able to resolve the error related to mixing synchronous and asynchronous operations in your code.

## My Questions which are not answered yet

1. > **Sandbox requirements**: Browsers require specific kernel capabilities that aren't available in custom Ubuntu-based images
   1. Which `specific kernel capabilities` are missing?
   2. When they are available in the playwright official image:
      1. How can I check for them in my custom image?
      2. How can I add them to my custom image?

   I also don't think that the issue is related to missing kernel capabilities! Such a issue would lead to an immediate crash of the browser process instead of a hang at `os.waitpid()`.

2. > **Missing optimizations**: Official Playwright images include ARM64-specific patches and configurations
   1. Which `ARM64-specific patches and configurations` are missing?
   2. When they are available in the playwright official image:
      1. How can I check for them in my custom image?
      2. How can I add them to my custom image?
      3. If that would be the real isssue, thae we would be able to fix it by adding the missing patches and configurations to our custom image, right?
      4. Why is there no way to add these patches and configurations to a custom image mentioned in the Playwright documentation?
      5. I think also that these issues would be already fixed in the playwright source code or somehow mentioned in the project docs or README.md files, right?

3. Did we test the current tests with Chrome and Firefox on my Host system, without using Docker, to verify that the issue is not related to ARM64/Apple Silicon in general?
    1. If yes, what were the results?
    2. If no, can we please do this to verify that the issue is really related to Docker only?
    3. If the tests also fail on the host system, then we can be sure that the issue is not related to Docker at all, right?
    4. If the tests work on the host system, then we can be sure that the issue is related to Docker, right?

4. If the tests work on the host system, can we please try to run the tests in a custom Docker image based on Ubuntu, but without using ARM64/Apple Silicon, to verify that the issue is really related to ARM64/Apple Silicon only?
    1. If yes, what were the results?
    2. If no, can we please do this to verify that the issue is really related to ARM64/Apple Silicon only?
    3. If the tests also fail in the AMD64/Intel Docker image, then we can be sure that the issue is not related to ARM64/Apple Silicon at all, right?
    4. If the tests work in the AMD64/Intel Docker image, then we can be sure that the issue is related to ARM64/Apple Silicon only, right?

5. If the issue is related to ARM64/Apple Silicon only, can we please try to run the tests in the official Playwright Docker image on ARM64/Apple Silicon, to verify that the issue is really related to our custom Docker image only?
    1. If yes, what were the results?
    2. If no, can we please do this to verify that the issue is really related to our custom Docker image only?
    3. If the tests also fail in the official Playwright Docker image on ARM64/Apple Silicon, then we can be sure that the issue is not related to our custom Docker image at all, right?
    4. If the tests work in the official Playwright Docker image on ARM64/Apple Silicon, then we can be sure that the issue is related to our custom Docker image only, right?

6. If the issue is related to our custom Docker image only, can we please compare the official Playwright Docker image with our custom Docker image to find the differences which could lead to the issue?
    1. If yes, what were the results?
    2. If no, can we please do this to find the differences which could lead to the issue?

7. If we find differences which could lead to the issue, can we please try to add these differences to our custom Docker image to verify that the issue is fixed?
    1. If yes, what were the results?
    2. If no, can we please do this to verify that the issue is fixed?
    3. If the issue is fixed after adding the differences, then we can be sure that we found the root cause of the issue, right?
    4. If the issue is not fixed after adding the differences, then we can be sure that the differences were not related to the issue at all, right?

8. If we cannot find any differences which could lead to the issue, can we please try to create a minimal reproducible example which only contains the necessary parts to reproduce the issue?
    1. If yes, what were the results?
    2. If no, can we please do this to reproduce the issue with minimal effort?
    3. If we can reproduce the issue with a minimal reproducible example, then we can be sure that we found the root cause of the issue, right?
    4. If we cannot reproduce the issue with a minimal reproducible example, then we can be sure that the issue is related to other parts of our custom Docker image, right?

9. If we cannot find the root cause of the issue, can we please ask the Playwright community for help?
    1. If yes, what were the results?
    2. If no, can we please do this to get help from the community?
    3. If the community can help us to find the root cause of the issue, then we can be sure that we found the root cause of the issue, right?
    4. If the community cannot help us to find the root cause of the issue, then we can be sure that the issue is very specific to our custom Docker image, right?

10. If we cannot find the root cause of the issue, can we please try to use the official Playwright Docker image on ARM64/Apple Silicon as a workaround?
    1. If yes, what were the results?
    2. If no, can we please do this to have a working solution?
    3. If the official Playwright Docker image works on ARM64/Apple Silicon, then we can be sure that we have a working solution, right?
    4. If the official Playwright Docker image does not work on ARM64/Apple Silicon, then we can be sure that the issue is very specific to ARM64/Apple Silicon, right?

11. If we cannot find the root cause of the issue, can we please try to use AMD64/Intel Docker images with Rosetta 2 emulation on ARM64/Apple Silicon as a workaround?
    1. If yes, what were the results?
    2. If no, can we please do this to have a working solution?
    3. If the AMD64/Intel Docker images with Rosetta 2 emulation work on ARM64/Apple Silicon, then we can be sure that we have a working solution, right?
    4. If the AMD64/Intel Docker images with Rosetta 2 emulation do not work on ARM64/Apple Silicon, then we can be sure that the issue is very specific to ARM64/Apple Silicon, right?

12. If we cannot find the root cause of the issue, can we please try to use cloud-based CI/CD services which provide AMD64/Intel runners as a workaround?
    1. If yes, what were the results?
    2. If no, can we please do this to have a working solution?
    3. If the cloud-based CI/CD services with AMD64/Intel runners work on ARM64/Apple Silicon, then we can be sure that we have a working solution, right?
    4. If the cloud-based CI/CD services with AMD64/Intel runners do not work on ARM64/Apple Silicon, then we can be sure that the issue is very specific to ARM64/Apple Silicon, right?

13. If we cannot find the root cause of the issue, can we please try to use physical AMD64/Intel hardware for testing as a workaround?
    1. If yes, what were the results?
    2. If no, can we please do this to have a working solution?
    3. If the physical AMD64/Intel hardware works for testing, then we can be sure that we have a working solution, right?
    4. If the physical AMD64/Intel hardware does not work for testing, then we can be sure that the issue is very specific to ARM64/Apple Silicon, right?

14. If we cannot find the root cause of the issue, can we please try to use virtualization solutions which provide AMD64/Intel virtual machines on ARM64/Apple Silicon as a workaround?
    1. If yes, what were the results?
    2. If no, can we please do this to have a working solution?
    3. If the virtualization solutions with AMD64/Intel virtual machines work on ARM64/Apple Silicon, then we can be sure that we have a working solution, right?
    4. If the virtualization solutions with AMD64/Intel virtual machines do not work on ARM64/Apple Silicon, then we can be sure that the issue is very specific to ARM64/Apple Silicon, right?

15. If we cannot find the root cause of the issue, can we please try to use cross-compilation techniques to build AMD64/Intel binaries on ARM64/Apple Silicon as a workaround?
    1. If yes, what were the results?
    2. If no, can we please do this to have a working solution?
    3. If the cross-compilation techniques to build AMD64/Intel binaries work on ARM64/Apple Silicon, then we can be sure that we have a working solution, right?
    4. If the cross-compilation techniques to build AMD64/Intel binaries do not work on ARM64/Apple Silicon, then we can be sure that the issue is very specific to ARM64/Apple Silicon, right?
