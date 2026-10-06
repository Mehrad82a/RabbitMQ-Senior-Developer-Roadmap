# P07 Test Suite

This directory contains the integration tests for P07 — Message Persistence and Broker Recovery.

The tests connect to a real RabbitMQ broker. They verify Publisher Confirms and compare whether queues and messages survive a RabbitMQ restart under different durability and persistence settings.

These are not unit tests. The persistence scenarios restart the RabbitMQ Docker service, so run them sequentially and do not run them in parallel.

## Directory Structure

```text
tests/
├── README.md
├── __init__.py
├── conftest.py
├── helpers/
│   ├── __init__.py
│   ├── docker_compose.py
│   ├── settings.py
│   └── rabbitmq/
│       ├── __init__.py
│       ├── client.py
│       ├── publisher.py
│       ├── queue_repository.py
│       └── scenario.py
└── scenarios/
    ├── __init__.py
    ├── test_publisher_confirm.py
    ├── test_scenario_01_non_durable_transient_message.py
    ├── test_scenario_02_non_durable_persistent_message.py
    ├── test_scenario_03_durable_transient_message.py
    └── test_scenario_04_durable_persistent_message.py
```

## Test Support Files

### `tests/conftest.py`

Defines pytest fixtures that manage the Docker services and provide the scenario controller.

The session-scoped `rabbitmq_environment` fixture:

- Checks which Docker Compose services are running before the test session.
- Stops the Worker during persistence tests so it cannot consume and ACK the test message.
- Starts RabbitMQ if it was not already running.
- Waits until RabbitMQ is ready.
- Restores the original Worker and RabbitMQ service state after the session.

The `rabbitmq_scenario` fixture provides a `RabbitMQScenarioController` for individual scenario tests. It also cleans up queues registered by that controller when a test finishes.

### `tests/helpers/settings.py`

Loads test configuration from environment variables and the P07 `.env` file.

It provides:

- The RabbitMQ host and port used by host-side tests.
- RabbitMQ credentials.
- Docker Compose service names.
- RabbitMQ readiness timeout and retry delay.
- The P07 project root and `.env` path.

Host-side tests connect using `RABBITMQ_TEST_HOST`, usually `localhost`. The application containers use `RABBITMQ_HOST`, usually `rabbitmq`.

Do not commit `.env` or real credentials to Git.

### `tests/helpers/docker_compose.py`

Wraps Docker Compose commands used by the test fixtures.

It provides operations for:

- Listing running services.
- Starting and stopping services.
- Restarting RabbitMQ.

The commands run from the P07 project directory.

### `tests/helpers/rabbitmq/client.py`

Provides `RabbitMQTestClient`, which manages test connections and channels.

It can:

- Create a RabbitMQ connection using the test settings.
- Open a channel with a context manager.
- Close the channel and connection after an operation.
- Wait until RabbitMQ accepts connections after a restart.

### `tests/helpers/rabbitmq/publisher.py`

Provides `RabbitMQTestPublisher` for publishing messages used in the persistence scenarios.

It:

- Declares a queue with the requested durability.
- Enables Publisher Confirms.
- Sets the message delivery mode according to the persistence option.
- Publishes through RabbitMQ's default exchange with mandatory routing.
- Converts NACK and unroutable results into `RabbitMQTestError`.

### `tests/helpers/rabbitmq/queue_repository.py`

Provides `RabbitMQQueueRepository` and `QueueState` for inspecting and deleting queues.

Queue inspection uses a passive declaration, so it checks for an existing queue without creating one. The repository reports whether a queue exists and how many ready messages it contains.

### `tests/helpers/rabbitmq/scenario.py`

Provides `RabbitMQScenarioController`, which coordinates a persistence scenario.

The controller can:

- Publish a test message.
- Inspect the queue state.
- Restart RabbitMQ and wait for it to become ready.
- Track and delete test queues during cleanup.

Scenario tests use this controller instead of directly managing RabbitMQ connections, channels, and Docker commands.

The `__init__.py` files make the directories importable as Python packages. They do not run tests.

## Persistence Scenario Tests

Each persistence scenario performs these steps:

1. Creates a unique queue name.
2. Publishes a real message to RabbitMQ.
3. Checks the queue and message count before the restart.
4. Restarts the RabbitMQ service.
5. Waits for the broker to become ready.
6. Checks the queue and message count after the restart.
7. Compares the observed state with the expected result.
8. Deletes any remaining test queue.

The Worker is stopped during these tests so it does not consume and acknowledge the test message before the broker restart.

### Scenario 01 — Non-durable Queue and Transient Message

File:

```text
tests/scenarios/test_scenario_01_non_durable_transient_message.py
```

Configuration:

```text
queue_durable = False
message_persistent = False
```

Expected result:

| State | Queue exists | Message count |
|---|---:|---:|
| Before RabbitMQ restart | Yes | 1 |
| After RabbitMQ restart | No | 0 |

The queue is not durable, so RabbitMQ does not restore it after restart. The message is transient as well.

Run this scenario:

```bash
pytest tests/scenarios/test_scenario_01_non_durable_transient_message.py -v -s
```

### Scenario 02 — Non-durable Queue and Persistent Message

File:

```text
tests/scenarios/test_scenario_02_non_durable_persistent_message.py
```

Configuration:

```text
queue_durable = False
message_persistent = True
```

Expected result:

| State | Queue exists | Message count |
|---|---:|---:|
| Before RabbitMQ restart | Yes | 1 |
| After RabbitMQ restart | No | 0 |

The persistent message cannot be recovered because its non-durable queue is removed during broker recovery. Message persistence alone is insufficient.

Run this scenario:

```bash
pytest tests/scenarios/test_scenario_02_non_durable_persistent_message.py -v -s
```

### Scenario 03 — Durable Queue and Transient Message

File:

```text
tests/scenarios/test_scenario_03_durable_transient_message.py
```

Configuration:

```text
queue_durable = True
message_persistent = False
```

Expected result:

| State | Queue exists | Message count |
|---|---:|---:|
| Before RabbitMQ restart | Yes | 1 |
| After RabbitMQ restart | Yes | 0 |

RabbitMQ restores the durable queue, but it does not recover the transient message. Queue durability alone is insufficient for message recovery.

Run this scenario:

```bash
pytest tests/scenarios/test_scenario_03_durable_transient_message.py -v -s
```

### Scenario 04 — Durable Queue and Persistent Message

File:

```text
tests/scenarios/test_scenario_04_durable_persistent_message.py
```

Configuration:

```text
queue_durable = True
message_persistent = True
```

Expected result:

| State | Queue exists | Message count |
|---|---:|---:|
| Before RabbitMQ restart | Yes | 1 |
| After RabbitMQ restart | Yes | 1 |

Both the queue and the persistent message are recovered.

Run this scenario:

```bash
pytest tests/scenarios/test_scenario_04_durable_persistent_message.py -v -s
```

## Publisher Confirm Test

File:

```text
tests/scenarios/test_publisher_confirm.py
```

This integration test uses the P07 application `Producer` and a real RabbitMQ broker. It checks the Producer result with confirms enabled and disabled.

| Publisher Confirm | Expected Producer result | Message in queue |
|---|---|---|
| Enabled (`True`) | `True` | Yes |
| Disabled (`False`) | `None` | Yes |

With confirms enabled, the Producer waits for RabbitMQ to confirm that it accepted the publish. With confirms disabled, the Producer does not wait for a broker confirmation, but it still publishes the message.

The test creates a unique durable queue for each case and deletes it afterward.

A Publisher Confirm verifies broker acceptance. It does not prove that a Consumer processed the message or that the message will survive a broker restart.

Run this test:

```bash
pytest tests/scenarios/test_publisher_confirm.py -v -s
```

## Running the Tests

Run commands from the P07 project directory:

```text
part1_rabbitmq_fundamentals/p07_message_persistence
```

### 1. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Environment

Create `.env` from `.env.example`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Set valid RabbitMQ credentials in `.env`. The tests read the test host, port, and credentials from the test settings.

### 4. Check Docker

```bash
docker --version
docker compose version
```

Docker Desktop must be running. The test fixtures issue Docker Compose commands from the host.

### 5. Run All Tests

```bash
pytest tests/scenarios -v -s
```

The `-s` option displays scenario logs and RabbitMQ restart progress.

Do not run the scenarios in parallel. Each persistence scenario restarts the same RabbitMQ service.

### Run the Entire Test Suite

```bash
pytest -v -s
```

### Run an Individual Test

```bash
pytest tests/scenarios/test_publisher_confirm.py -v -s
pytest tests/scenarios/test_scenario_01_non_durable_transient_message.py -v -s
pytest tests/scenarios/test_scenario_02_non_durable_persistent_message.py -v -s
pytest tests/scenarios/test_scenario_03_durable_transient_message.py -v -s
pytest tests/scenarios/test_scenario_04_durable_persistent_message.py -v -s
```

## Interpreting Test Results

- `PASSED`: The test observed the expected RabbitMQ behavior.
- `FAILED`: An assertion did not match the observed state. Review the traceback and the scenario logs.
- `ERROR`: The test stopped before reaching its assertions, usually because setup failed. Check Docker, RabbitMQ readiness, credentials, and configuration.
- `ModuleNotFoundError`: A required Python dependency is missing from the active environment.

## Understanding the Results

The four persistence scenarios demonstrate that a message survives RabbitMQ restart only when both its queue is durable and the message is persistent.

| Queue durable | Message persistent | Queue after restart | Message after restart |
|---:|---:|---|---|
| No | No | Removed | Removed |
| No | Yes | Removed | Removed |
| Yes | No | Survives | Removed |
| Yes | Yes | Survives | Survives |

Publisher Confirms and persistence address different questions:

```text
Publisher Confirm:
Did RabbitMQ accept responsibility for the publish?

Durability and persistence:
Can the queue and message be recovered after a broker restart?
```

Publisher Confirms also do not indicate that a Consumer processed the message. Consumer acknowledgments are a separate mechanism.

## RabbitMQ 4.x Compatibility

P07 uses a non-durable, non-exclusive queue in Scenario 01 and Scenario 02. The RabbitMQ configuration file may include this compatibility setting:

```ini
deprecated_features.permit.transient_nonexcl_queues = true
```

The Compose configuration mounts `rabbitmq.conf` into the RabbitMQ container. Ensure the source path is an actual file before starting the broker.

After changing the RabbitMQ configuration, recreate the container:

```powershell
docker compose down
docker compose up --build -d
```

Do not use `docker compose down -v` during the persistence experiment unless you intentionally want to delete the RabbitMQ data volume.

## Troubleshooting

### Tests Cannot Connect to RabbitMQ

Check that Docker is running and inspect service state:

```bash
docker compose ps
```

Check RabbitMQ logs:

```bash
docker compose logs rabbitmq
```

Host-side tests normally connect through:

```text
RABBITMQ_TEST_HOST=localhost
```

Application containers normally connect through:

```text
RABBITMQ_HOST=rabbitmq
```

Also verify that port `5672` is published and that the credentials in `.env` match the RabbitMQ container configuration.

### RabbitMQ Does Not Become Ready

The test client retries connections until the configured readiness timeout expires. Check broker logs and service health:

```bash
docker compose ps
docker compose logs rabbitmq
```

### Messages Disappear Before RabbitMQ Restarts

The Worker may still be running and consuming the test message. The session fixture is designed to stop the Worker during the test session. Check that the fixture was loaded and inspect service state:

```bash
docker compose ps
```

### Queue Declaration Fails

RabbitMQ requires repeated declarations of the same queue to use matching properties. These tests use unique queue names to avoid collisions with application queues and other test runs.

### Transient Queue Declaration Is Rejected

Verify that the RabbitMQ configuration file contains the compatibility setting shown above, then recreate the RabbitMQ container.

## Cleanup and Service Restoration

The test fixtures record whether RabbitMQ and the Worker were running before the test session.

- If RabbitMQ was stopped, the fixture starts it and stops it again after testing.
- If the Worker was running, the fixture stops it for the tests and starts it again afterward.
- Queues created through `RabbitMQScenarioController` are deleted during fixture cleanup.
- The Publisher Confirm test deletes its own unique queue.

To stop the project while preserving the RabbitMQ data volume:

```bash
docker compose down
```

To also delete persisted RabbitMQ data:

```bash
docker compose down -v
```

Use `down -v` only when you intentionally want to remove the broker's stored data.