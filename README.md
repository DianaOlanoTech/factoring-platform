# Factoring Decision Service

A small factoring decision service built with Python, FastAPI, and TypeScript.

The service receives factoring applications, evaluates them through a mock external risk provider, applies the factoring business rules, and returns a normalized decision.

[Watch the walkthrough video](https://youtu.be/nHuDsGrz7-0)

## Features

- Submit factoring applications for risk evaluation.
- Evaluate applications through a mock external risk provider.
- Normalize provider responses into internal decision models.
- Calculate the available advance based on the approved percentage.
- Retrieve previously evaluated applications by application ID.
- Handle risk provider failures predictably through the API and TypeScript client.
- Provide a small TypeScript client for submitting applications and displaying decisions.

## API

### Create a factoring application

**POST** `/api/factoring/applications`

Example request:

    {
    "application_id": "FAC-1001",
    "customer_id": "CUS-101",
    "invoice_amount_cents": 125000,
    "requested_advance_cents": 90000,
    "due_date": "2026-10-15"
    }

Example response:

    {
    "application_id": "FAC-1001",
    "decision": "eligible",
    "requested_advance_cents": 90000,
    "available_advance_cents": 100000,
    "provider_reference": "RISK-9001"
    }

### Get a factoring application

**GET** `/api/factoring/applications/{application_id}`

Example request:

    GET /api/factoring/applications/FAC-1001

Example response:

    {
    "application_id": "FAC-1001",
    "decision": "eligible",
    "requested_advance_cents": 90000,
    "available_advance_cents": 100000,
    "provider_reference": "RISK-9001"
    }

### Mock risk provider

**POST** `/mock/risk/decision`

This endpoint simulates the external risk provider used by the application.

Example request:

    {
        "customer_id": "CUS-101",
        "invoice_amount_cents": 125000
    }

Example response:

    {
    "provider_reference": "RISK-9001",
    "status": "approved",
    "max_advance_percent": 80
    }

The mock provider supports different risk outcomes:

- `CUS-101` → `approved`
- `CUS-102` → `review`
- `CUS-103` → `declined`

## Architecture

The project follows a lightweight hexagonal architecture that keeps the core business logic independent from external technologies.

The main boundaries are:

    HTTP request
        |
        v
    FastAPI Router
    (Inbound Adapter)
        |
        v
    FactoringApplicationService
    (Application / Core)
        |
        +----------------------+
        |                      |
        v                      v
    RiskProvider          ApplicationRepository
       (Port)                    (Port)
        |                      |
        v                      v
    HttpRiskProvider      InMemoryApplicationRepository
    (Outbound Adapter)    (Outbound Adapter)
        |
        v
    Mock Risk Provider

### Core

`FactoringApplicationService` contains the factoring decision workflow and business rules. It works with domain models such as `FactoringApplication`, `RiskResult`, and `FactoringDecision` without depending on FastAPI, `httpx`, or concrete storage implementations.

### Ports

Ports define the contracts required by the core:

- `RiskProvider` defines how the application requests a risk evaluation.
- `ApplicationRepository` defines how evaluated applications are stored and retrieved.

They are implemented as Python protocols, allowing the core to work with different adapters and fake implementations in tests.

### Adapters

Adapters provide the concrete implementations of the ports and translate between the core and external systems.

- `FactoringRouter` is the inbound HTTP adapter and translates HTTP requests into domain objects.
- `HttpRiskProvider` is an outbound adapter that communicates with the external risk provider over HTTP and normalizes its response into `RiskResult`.
- `InMemoryApplicationRepository` is an outbound adapter that stores decisions in memory.

This separation allows external implementations to be replaced without changing the core business logic. For example, the in-memory repository could later be replaced by a SQLite or PostgreSQL adapter.

## Decision Rules

The final factoring decision is calculated by the application service based on the normalized risk result returned by the risk provider.

### Approved

When the risk provider returns `approved`, the available advance is calculated as:

    available_advance_cents =
        floor(invoice_amount_cents * max_advance_percent / 100)

- If `requested_advance_cents <= available_advance_cents`, the decision is `eligible`.
- If `requested_advance_cents > available_advance_cents`, the decision is `needs_review`.

### Review

When the risk provider returns `review`, the application decision is `needs_review`.

No available advance is calculated because the provider did not approve a maximum advance percentage.

### Declined

When the risk provider returns `declined`, the application decision is `rejected`.

No available advance is calculated.

### Integration failure

If the risk provider cannot be reached, returns a non-successful HTTP status, or returns an invalid response, the application returns `integration_error`.

The integration error is also persisted so that the application can be retrieved using its application ID.

## Error Handling

The API handles expected failures in a predictable way.

### Invalid application data

Invalid domain values are rejected with HTTP `422`.

For example:

- `invoice_amount_cents <= 0`
- `requested_advance_cents <= 0`

FastAPI also validates the request structure and data types before the request reaches the application service.

### Application not found

A request for an application ID that has not been stored returns HTTP `404`.

Example:

    GET /api/factoring/applications/UNKNOWN-ID

Response:

    {
      "detail": "Application not found"
    }

### Risk provider failure

The `HttpRiskProvider` adapter converts request failures, non-successful HTTP responses, invalid JSON, and unexpected provider payloads into a `RiskProviderError`.

The application service catches this error and creates an `integration_error` decision instead of allowing the exception to propagate and crash the API flow.

The integration error is persisted through the application repository and can be retrieved using the application ID.

Example response:

    {
      "application_id": "FAC-1005",
      "decision": "integration_error",
      "requested_advance_cents": 90000,
      "available_advance_cents": null,
      "provider_reference": null
    }

The core does not need to know about:

- Provider-specific JSON field names.
- HTTP status codes.
- The provider URL.
- HTTP client implementation details.

## Running Locally

### Prerequisites

- Python 3.10+
- Node.js 20+
- npm

### 1. Clone the repository

Clone the repository and move into the project directory.

    git clone <repository-url>
    cd factoring-platform

### 2. Create and activate the Python virtual environment

On Windows with Git Bash:

    python -m venv .venv
    source .venv/Scripts/activate

On macOS/Linux:

    python3 -m venv .venv
    source .venv/bin/activate

### 3. Install backend and frontend dependencies

    pip install -r requirements.txt
    npm install

### 4. Compile TypeScript

Compile the TypeScript client into JavaScript:

    npm run build

This compiles `frontend/app.ts` into `frontend/app.js`.

### 5. Start the application

    uvicorn app.main:app --reload

The application will be available at:

    http://localhost:8000/

The API documentation is available at:

    http://localhost:8000/docs

## Testing

The project uses `pytest` for automated tests.

Run the complete test suite with:

    python -m pytest

The tests cover the main business and integration boundaries, including:

- Domain model validation.
- Approved applications within the available advance limit.
- Approved applications exceeding the available advance limit.
- Review risk decisions.
- Declined risk decisions.
- Risk provider failures.
- Available advance calculation using floor rounding.
- HTTP risk provider response handling.
- In-memory repository behavior.
- API request validation and responses.
- Application not found responses.
- Mock risk provider outcomes.

The application service is tested independently from HTTP by using fake implementations of the `RiskProvider` and `ApplicationRepository` ports. This verifies the core business rules without requiring a real HTTP request.

## Assumptions

The following assumptions were made to keep the implementation simple while staying aligned with the assessment requirements.

- `max_advance_percent` is expected to be between 1 and 100. Values outside this range are considered invalid provider responses.
- `due_date` is required by the API but is not currently used in the decision rules because the assessment does not define any business rule based on the due date.
- A requested advance greater than the invoice amount is not rejected during request validation. The application service applies the defined decision rules and may return `needs_review` if the requested amount exceeds the available advance.
- The application uses an in-memory repository because persistent database storage is optional for the assessment. Stored applications are therefore lost when the application restarts.
- Risk provider failures are represented as an `integration_error` decision in the API response rather than exposing provider-specific errors to the client. The assessment does not prescribe a specific HTTP status code for this scenario.

## Project Structure

    factoring-platform/
    ├── app/
    │   ├── domain/
    │   │   └── models.py
    │   │
    │   ├── application/
    │   │   └── factoring_application_service.py
    │   │
        ├── ports/
        │   ├── exceptions.py
        │   └── ports.py
        │
        ├── adapters/
        │   ├── risk/
        │   │   └── http_risk_provider.py
    │   │   │
    │   │   └── repositories/
    │   │       └── in_memory_application_repository.py
    │   │
    │   ├── api/
    │   │   ├── dependencies.py
    │   │   ├── factoring.py
    │   │   ├── mock_risk.py
    │   │   └── models.py
    │   │
    │   └── main.py
    │
    ├── frontend/
    │   ├── app.ts
    │   ├── app.js
    │   ├── index.html
    │   └── styles.css
    │
    ├── tests/
    │
    ├── requirements.txt
    ├── package.json
    ├── tsconfig.json
    └── README.md

### Main responsibilities

- `domain/` contains the core business models and domain rules.
- `application/` contains the factoring use case and decision workflow.
- `ports/` defines the interfaces used by the application core.
- `adapters/risk/` contains the concrete HTTP implementation of the risk provider.
- `adapters/repositories/` contains the concrete storage implementation.
- `api/` contains the FastAPI inbound adapter, API models, dependencies, and mock provider.
- `frontend/` contains the small TypeScript client and static UI.
- `tests/` contains automated tests for the domain, application service, adapters, and API.
- `main.py` is responsible for assembling the application and wiring the concrete adapters to the application service.

## Design Decisions

### Lightweight hexagonal architecture

The project uses a lightweight hexagonal architecture to keep the factoring business logic independent from external technologies without introducing unnecessary layers.

### Protocols for ports

Python `Protocol` is used to define the `RiskProvider` and `ApplicationRepository` ports.

This allows the application service to depend on abstractions and makes it possible to use fake implementations in tests.

### Separate API and domain models

API request and response models are defined separately from domain models.

This keeps HTTP-specific structures outside the core business logic and allows the API representation to change independently.

### In-memory persistence

An in-memory repository was selected because persistent storage is optional for the assessment.

The repository still follows the port/adapter boundary, so a database implementation could be introduced later without changing the application service.

### HTTP risk provider

The risk provider integration is isolated in `HttpRiskProvider`.

The adapter is responsible for building the provider request, performing the HTTP call, handling integration errors, validating the response, and translating provider-specific values into the internal `RiskResult` model.

The application service therefore does not depend on `httpx` or the provider's JSON structure.

## Limitations & Future Improvements

The current implementation intentionally keeps the scope small and focused on the assessment requirements.

For a production system, the following improvements could be considered:

- **Persistent storage:** Replace the in-memory repository with a database-backed implementation such as PostgreSQL. The existing `ApplicationRepository` port would allow this without changing the application service.

- **Idempotency:** Add idempotency support for application creation to prevent duplicate processing when clients retry the same request.

- **Provider resilience:** Add configurable timeouts, retry policies, and potentially a circuit breaker based on provider reliability requirements.

- **Configuration management:** Move values such as the risk provider base URL and timeout to environment-based configuration.

- **Observability:** Add structured logging, metrics, and distributed tracing to improve monitoring of application processing and provider failures.

- **More comprehensive API tests:** Expand coverage for malformed payloads, unexpected provider responses, and additional end-to-end scenarios.

These improvements were intentionally left out to keep the solution within the scope of the assessment.