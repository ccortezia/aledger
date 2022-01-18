# Code Structure Overview

## Where to Start

If unsure where to start reading the code, start from [aledger/controllers/http.py](../aledger/controllers/http.py).

That is where the HTTP endpoints are defined.

## Code Structure

The aledger-api project is structured for decoupled growth.

### Controllers
The package [aledger/controllers](../aledger/controllers) exposes system capabilities to different external consumers. Routines defined here wrap around a use case exposed by the Service Layer and adapt its input/output from/to a specific delivery mechanism such as HTTP/JSON, gRPC, or CLI.

### The Service Layer
The package [aledger/service](../aledger/service) exposes primary application use cases internally. Routines defined here handle commands and query messages sent by controllers. This is where events would be handled if there were events to react to. A Command handler will typically load domain entities from a repository, then interact with those domain entities, persist changes, and possibly emit events that represent state transitions resulting from those interactions. A Query handler will typically reach out to storage more freely to fulfill its objective in a more performant manner.

### Adapters
The package [aledger/adapters](../aledger/adapters) offers implementations of technical interfaces such as for data persistence. The Service Layer depends on the established interfaces, so it stays decoupled from changes to specific technical implementations.

### The Core Domain
The package [aledger/domain](../aledger/domain) expresses the core application domain. Here is where Domain Entities and their relationships are defined, as well as the schema for internal Commands and Queries.
