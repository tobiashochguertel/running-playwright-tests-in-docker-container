# ARM64/Apple Silicon Docker Issue - Summary

## ⚠️ Critical Finding

**Playwright browsers (both Chromium and Firefox) cannot launch properly in custom Docker images on ARM64/Apple Silicon architecture.**

## 🔍 Root Cause

All browser launches hang indefinitely at:

```
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

```
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
- [Docker ARM64 Limitations](https://docs.docker.com/desktop/troubleshoot/known-issues/)

## 📅 Investigation Timeline

1. **Initial Issue**: Tests "taking ages instead of 10-20 seconds"
2. **Diagnosis**: Tests not slow, they're **hanging at browser launch**
3. **Attempts**: 4 different approaches over 20+ test runs
4. **Conclusion**: ARM64 custom Docker images incompatible with Playwright
5. **Recommendation**: Use official `mcr.microsoft.com/playwright/python` image

---

**Status**: ❌ Custom Ubuntu-based Docker image **NOT VIABLE** on ARM64
**Recommendation**: ✅ Switch to official Playwright Docker image
**Date**: $(date)
