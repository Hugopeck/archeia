# System Context

```mermaid
flowchart LR
    developer(["Developer / Security Researcher"])
    addon-author(["Addon Author"])
    client-application(["Client Application"])

    subgraph boundary["mitmproxy"]
        mitmproxy["mitmproxy<br/><i>Python 3.12+ / asyncio</i>"]
    end

    target-server[("Target HTTP Server<br/><i>HTTP/HTTPS</i>")]
    mitmproxy-rs[("mitmproxy_rs<br/><i>Rust (PyO3)</i>")]

    developer -->|"Controls proxy via console UI, CLI, or web browser interface"| mitmproxy
    addon-author -->|"Registers Python addon scripts that hook into the request/response lifecycle"| mitmproxy
    client-application -->|"Routes HTTP/HTTPS traffic through the proxy"| mitmproxy
    mitmproxy -->|"Forwards intercepted traffic to the upstream server"| target-server
    mitmproxy -->|"Delegates WireGuard, local redirect, and raw UDP/DNS transport to Rust extension"| mitmproxy-rs
```

**Source:** `.archeia/codebase/architecture/system.json`
**Generated:** 2026-04-10
