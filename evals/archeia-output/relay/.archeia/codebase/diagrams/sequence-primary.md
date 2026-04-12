# Sequence — Spawn Agents and Send Message

```mermaid
sequenceDiagram
    participant developer as Developer
    participant sdk-relay as AgentRelay (SDK)
    participant broker-binary as Broker Binary
    participant relaycast-cloud as Relaycast Cloud
    participant claude-cli as Claude CLI

    developer->>sdk-relay: new AgentRelay() + connect()
    sdk-relay->>broker-binary: spawn broker subprocess
    broker-binary->>relaycast-cloud: WebSocket connect
    developer->>sdk-relay: relay.claude.spawn({name, task, channels})
    broker-binary-)claude-cli: spawn PTY subprocess + inject relay MCP config
    developer->>sdk-relay: relay.system().sendMessage({to: 'PlayerX', text: 'Start.'})
    broker-binary-)claude-cli: inject message into PTY stdin
    claude-cli-)broker-binary: send reply via relay MCP tool
    broker-binary-)relaycast-cloud: broadcast message to target
    sdk-relay-->>developer: onMessageReceived callback
```

**Source:** `.archeia/codebase/architecture/dataflow.json`
**Generated:** 2026-04-10
