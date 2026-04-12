# Components — Relay CLI

```mermaid
flowchart TB
    subgraph boundary [Relay CLI]
        RELAY_CLI_BOOTSTRAP[Bootstrap<br/><i>TypeScript</i>]
        RELAY_CLI_COMMANDS[Commands<br/><i>TypeScript</i>]
        RELAY_CLI_LIB[CLI Library<br/><i>TypeScript</i>]
    end
    SDK_CLIENT[AgentRelayClient<br/><i>@agent-relay/sdk</i>]

    RELAY_CLI_BOOTSTRAP -->|Dispatches parsed command to implementation| RELAY_CLI_COMMANDS
    RELAY_CLI_COMMANDS -->|Uses shared helpers for output formatting and client factory| RELAY_CLI_LIB
    RELAY_CLI_COMMANDS -->|Creates AgentRelayClient to communicate with broker| SDK_CLIENT
```

**Source:** `.archeia/codebase/architecture/components.json`
**Generated:** 2026-04-10
