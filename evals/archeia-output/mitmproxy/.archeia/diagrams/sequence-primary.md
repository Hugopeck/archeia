# HTTP/HTTPS Request Interception (Primary Flow)

```mermaid
sequenceDiagram
    participant client-application as Client Application
    participant proxy-core-server as Proxy Server
    participant proxy-core-layers as Protocol Layers
    participant proxy-core-addonmanager as AddonManager
    participant proxy-core-addons as Built-in Addons
    participant target-server as Target HTTP Server

    client-application ->> proxy-core-server: TCP connect + HTTP/HTTPS request
    proxy-core-server ->> proxy-core-layers: ConnectionMadeEvent + DataReceiveEvent
    proxy-core-layers ->> proxy-core-addonmanager: trigger_event(RequestHook(flow))
    proxy-core-addonmanager ->> proxy-core-addons: addon.request(flow)
    proxy-core-addons -->> proxy-core-addonmanager: flow modified or intercepted
    proxy-core-layers ->> target-server: Forwarded HTTP/HTTPS request
    target-server -->> proxy-core-layers: HTTP response
    proxy-core-layers ->> proxy-core-addonmanager: trigger_event(ResponseHook(flow))
    proxy-core-server -->> client-application: Forwarded HTTP response
```

**Source:** `.archeia/codebase/architecture/dataflow.json`
**Generated:** 2026-04-10
