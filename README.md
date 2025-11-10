# Running Playwright Tests in Docker Container

## Introduction
This repository provides a structured way to run Playwright tests within a Docker container. It aims to offer a seamless experience for developers looking to leverage Playwright's capabilities in an isolated environment.

## Repository Structure
- `docker-compose.yml`: Configuration file for Docker Compose, orchestrating container operations.
- `Dockerfile`: Instructions for building the Docker image with the necessary dependencies.
- `tests/`: Directory containing various test scripts organized by functionality.
- `examples/`: Sample tests demonstrating best practices and usage of Playwright in different scenarios.

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/tobiashochguertel/running-playwright-tests-in-docker-container.git
   cd running-playwright-tests-in-docker-container
   ```
2. **Build the Docker image:**
   ```bash
   docker-compose build
   ```

## Usage
To run the tests within the Docker container, use the following command:
```bash
docker-compose up
```

This command will start the container and execute all tests defined in the `tests` directory.

### Running Specific Tests
You can also execute specific test files by modifying the command in the `docker-compose.yml` file or by directly running the Docker container with parameters.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This repository is licensed under the MIT License. See the LICENSE file for more information.