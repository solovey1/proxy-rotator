"""
ProxyRotator: unified rotate() to "refresh" proxies by provider rules:
- finds where the provider stores session token and/or which port needs randomization
- generates a similar token
- randomizes port when required

Change: provider alias support removed.
Users should pass a handler CLASS (or instance) explicitly when needed:
    rotate(proxy, handler=NetnutHandler)

You can also register specific hosts to handlers at runtime via:
    register_handler_host("new.host.com", NetnutHandler)
"""

from __future__ import annotations
import random
import re
import string
from typing import Dict, Type, Union

from better_proxy import Proxy


def _derive_charset(sample: str) -> str:
    chars = ""
    if re.search(r"[a-z]", sample):
        chars += string.ascii_lowercase
    if re.search(r"[A-Z]", sample):
        chars += string.ascii_uppercase
    if re.search(r"[0-9]", sample):
        chars += string.digits
    return chars or (string.ascii_letters + string.digits)


def _random_token_like(original: str) -> str:
    charset = _derive_charset(original)
    return "".join(random.choices(charset, k=len(original)))


def randomize_prefix(value: str, prefix: str) -> str:
    """
    Universal token randomizer after a given prefix.
    prefix can be 'session-', 'sid-', 'sessionid-' or 's_'.
    """
    pattern = re.compile(rf"({re.escape(prefix)})([A-Za-z0-9]+)")

    def _sub(m: re.Match):
        old_token = m.group(2)
        new_token = _random_token_like(old_token)
        return m.group(1) + new_token

    return pattern.sub(_sub, value, count=1)


def randomize_port(min_port: int = 10000, max_port: int = 19999) -> int:
    return random.randint(min_port, max_port)


class ProxyHandlerBase:
    """
    Base handler: no changes by default.
    """
    def __init__(self, proxy: Proxy):
        self.proxy = proxy

    def randomize(self) -> Proxy:
        return self.proxy


# HANDLERS

class LumiProxyHandler(ProxyHandlerBase):
    """
    as.lumiproxy.com
    Example:
      login:  lumi-Loki890tt_area-MM_life-120_session-RUDboDJDk1
      password: HF1NkHGrEL
    Change token after 'session-' in login.
    """
    def randomize(self) -> Proxy:
        if self.proxy.login:
            self.proxy.login = randomize_prefix(self.proxy.login, "session-")
        return self.proxy


class EvomiHandler(ProxyHandlerBase):
    """
    core-residential.evomi.com
    Session is in PASSWORD: ..._country-BR_session-T2E1Y5U9A_lifetime...
    Change token after 'session-' in password.
    """
    def randomize(self) -> Proxy:
        if self.proxy.password:
            self.proxy.password = randomize_prefix(self.proxy.password, "session-")
        return self.proxy


class NodeMavenHandler(ProxyHandlerBase):
    """
    gate.nodemaven.com / gate-ru.nodemaven.com
    In login: ...-sid-72a5cdb83d6b4-...
    Change 'sid-...'
    """
    def randomize(self) -> Proxy:
        if self.proxy.login:
            self.proxy.login = randomize_prefix(self.proxy.login, "sid-")
        return self.proxy


class NSTProxyHandler(ProxyHandlerBase):
    """
    gate.nstproxy.io
    In login: ...-s_5R0e8G062m
    Change 's_' token (session marker).
    """
    def randomize(self) -> Proxy:
        if self.proxy.login:
            self.proxy.login = randomize_prefix(self.proxy.login, "s_")
        return self.proxy


class IProxyalHandler(EvomiHandler):
    """
    geo.iproyal.com
    Session in password: ..._country-ao_session-8TfV4lp0_lifetime...
    """


class NetnutHandler(NodeMavenHandler):
    """
    gw-cs.netnut.net / gw.netnut.net
    In login: ...-sid-196369392
    """


class DataImpulseHandler(ProxyHandlerBase):
    """
    gw.dataimpulse.com / w.dataimpulse.com
    """
    def randomize(self) -> Proxy:
        self.proxy.port = randomize_port(10000, 19999)
        return self.proxy


class ProxyWingHandler(EvomiHandler):
    """
    premium.proxywing.com / quality.proxywing.com
    Session in password: ...-session-iad74rBS
    """


class GeoNodeHandler(LumiProxyHandler):
    """
    proxy.geonode.io
    Session in login: ...-session-XDzdMr
    """


class SoaxHandler(ProxyHandlerBase):
    """
    proxy.soax.com
    In login: ...-sessionid-q8dbiTgC10HL0Dsq_...
    Change 'sessionid-...'
    """
    def randomize(self) -> Proxy:
        if self.proxy.login:
            self.proxy.login = randomize_prefix(self.proxy.login, "sessionid-")
        return self.proxy


class GeonixHandler(ProxyHandlerBase):
    """
    res.geonix.com
    Randomize port.
    """
    def randomize(self) -> Proxy:
        self.proxy.port = randomize_port(10000, 11000)
        return self.proxy


class ProxyShardHandler(NodeMavenHandler):
    """
    resident.proxyshard.com
    In login: ...-sid-5mbd92v1d384-...
    Change 'sid-...'
    """


class DetectExpertHandler(NodeMavenHandler):
    """
    51.79.24.25
    In login: ...-sid-
    """


class ProxysellerHandler(ProxyHandlerBase):
    """
    res.proxy-seller.io
    port
    """
    def randomize(self) -> Proxy:
        self.proxy.port = randomize_port(10000, 11000)
        return self.proxy


class InfaticaHandler(ProxyHandlerBase):
    """
    pool.infatica.io
    port
    """
    def randomize(self) -> Proxy:
        self.proxy.port = randomize_port(10000, 11000)
        return self.proxy


# REGISTER HANDLERS (by host)
PROXY_HANDLER_REGISTRY: Dict[str, Type[ProxyHandlerBase]] = {
    # Lumi
    "as.lumiproxy.com": LumiProxyHandler,

    # Evomi
    "core-residential.evomi.com": EvomiHandler,

    # NodeMaven
    "gate.nodemaven.com": NodeMavenHandler,
    "gate-ru.nodemaven.com": NodeMavenHandler,

    # NSTProxy
    "gate.nstproxy.io": NSTProxyHandler,

    # IProyal
    "geo.iproyal.com": IProxyalHandler,

    # NetNut
    "gw-cs.netnut.net": NetnutHandler,
    "gw.netnut.net": NetnutHandler,

    # DataImpulse
    "gw.dataimpulse.com": DataImpulseHandler,
    "w.dataimpulse.com": DataImpulseHandler,

    # ProxyWing
    "premium.proxywing.com": ProxyWingHandler,
    "quality.proxywing.com": ProxyWingHandler,

    # GeoNode
    "proxy.geonode.io": GeoNodeHandler,

    # SOAX
    "proxy.soax.com": SoaxHandler,

    # Geonix
    "res.geonix.com": GeonixHandler,

    # ProxyShard
    "resident.proxyshard.com": ProxyShardHandler,

    # DetectExpert
    "51.79.24.25": DetectExpertHandler,

    # Proxyseller
    "res.proxy-seller.io": ProxysellerHandler,
    "res.proxy-seller.com": ProxysellerHandler,

    # Infatica
    "pool.infatica.io": InfaticaHandler,
}


def register_handler_host(host: str, handler: Union[Type[ProxyHandlerBase], ProxyHandlerBase]) -> None:
    """
    Register a host -> handler mapping at runtime.
    Examples:
      register_handler_host("proxy.myprovider.com", MyHandler)
      register_handler_host("proxy.myprovider.net", MyHandler())
    """
    if isinstance(handler, ProxyHandlerBase):
        cls: Type[ProxyHandlerBase] = handler.__class__
    elif isinstance(handler, type) and issubclass(handler, ProxyHandlerBase):
        cls = handler
    else:
        raise TypeError("handler must be a ProxyHandlerBase subclass or instance")
    PROXY_HANDLER_REGISTRY[host.strip().lower()] = cls


def get_proxy_handler(
    proxy: Proxy | str,
    handler: Union[Type[ProxyHandlerBase], ProxyHandlerBase, None] = None,
) -> ProxyHandlerBase:
    """
    Return a handler instance for the proxy.
    Priority:
      1) Explicit handler (instance or class)
      2) Host-based registry
      3) Default ProxyHandlerBase
    """
    if isinstance(proxy, str):
        proxy = Proxy.from_str(proxy)

    # 1) Explicit handler
    if handler is not None:
        if isinstance(handler, ProxyHandlerBase):
            handler.proxy = proxy
            return handler
        if isinstance(handler, type) and issubclass(handler, ProxyHandlerBase):
            return handler(proxy)
        raise TypeError("handler must be a handler instance or a ProxyHandlerBase subclass")

    # 2) By host
    handler_cls = PROXY_HANDLER_REGISTRY.get(proxy.host.lower(), ProxyHandlerBase)
    return handler_cls(proxy)


def randomize_proxy_string(proxy_string: str, *, handler: Union[Type[ProxyHandlerBase], ProxyHandlerBase, None] = None) -> str:
    """
    Backward-compatibility alias for rotate(), same keyword parameters.
    """
    return rotate(proxy_string, handler=handler)


def rotate(
    proxy_string: str,
    *,
    handler: Union[Type[ProxyHandlerBase], ProxyHandlerBase, None] = None,
) -> str:
    """
    Single entry point:
    - parses proxy string
    - picks a handler (explicit class/instance or by host)
    - applies provider-specific token/port randomization
    - returns a new proxy string

    Examples:
      rotate(proxy, handler=NetnutHandler)      # by class
      rotate(proxy, handler=NetnutHandler())    # by instance
    """
    proxy = Proxy.from_str(proxy_string)
    handler_instance = get_proxy_handler(proxy, handler=handler)
    new_proxy = handler_instance.randomize()
    return str(new_proxy)