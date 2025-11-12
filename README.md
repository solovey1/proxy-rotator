# ProxyRotator

A single `rotate()` function for diverse proxy providers. It automatically detects where a provider keeps the session token (login or password) and/or which port needs to be randomized, then "refreshes" it according to provider-specific rules.

## Features

- Detects provider by host and applies the correct token/port rotation
- Force a specific handler by passing the handler class (useful if hosts/domains change)
- Randomizes session tokens while preserving character style/length
- Randomizes ports where required by the provider
- Simple, single entry point: `rotate(proxy_string)`
- Easily extensible with custom handlers
- Runtime host-to-handler registration

## Installation

```bash
pip install proxy-rotator
```

## Quick start

```python
from proxy_rotator import rotate
from proxy_rotator.proxy_handlers import NetnutHandler

proxy = "http://user:pass@as.lumiproxy.com:12345"

# Auto-detect by host
print(rotate(proxy))

# Force a handler explicitly (by class)
print(rotate(proxy, handler=NetnutHandler))
# or by instance
print(rotate(proxy, handler=NetnutHandler()))
```

Compatibility alias:

```python
# Old name kept for compatibility (supports the same 'handler' kwarg):
from proxy_rotator.proxy_handlers import randomize_proxy_string
rotated = randomize_proxy_string(proxy, handler=NetnutHandler)
```

## Supported providers (built-in)

- as.lumiproxy.com (LumiProxy): `session-` token in login
- core-residential.evomi.com (Evomi): `session-` token in password
- gate.nodemaven.com / gate-ru.nodemaven.com (NodeMaven): `sid-` token in login
- gate.nstproxy.io (NSTProxy): `s_` token in login
- geo.iproyal.com (IProyal): `session-` token in password
- gw-cs.netnut.net / gw.netnut.net (NetNut): `sid-` token in login
- gw.dataimpulse.com / w.dataimpulse.com (DataImpulse): port randomized in [10000–19999]
- premium.proxywing.com / quality.proxywing.com (ProxyWing): `session-` token in password
- proxy.geonode.io (GeoNode): `session-` token in login
- proxy.soax.com (SOAX): `sessionid-` token in login
- res.geonix.com (Geonix): port randomized in [10000–11000]
- resident.proxyshard.com (ProxyShard): `sid-` token in login
- 51.79.24.25 (DetectExpert): `sid-` token in login
- res.proxy-seller.io (Proxyseller): port randomized in [10000–11000]
- pool.infatica.io (Infatica): port randomized in [10000–11000]



## Development and publishing

```bash
python -m pip install -U pip build twine
python -m build
# TestPyPI
python -m twine upload -r testpypi dist/*
# Install from TestPyPI to verify:
pip install -i https://test.pypi.org/simple/ proxy-rotator
# PyPI
python -m twine upload dist/*
```