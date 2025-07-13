from .fetch_byteme import ByteMeFetcher
from .fetch_pingperfect import PingPerfectFetcher
from .fetch_servusspeed import ServusSpeedFetcher
from .fetch_verbyndich import VerbynDichFetcher
from .fetch_webwunder import WebWunderFetcher

PROVIDER_FETCHERS = {
    "ByteMe": ByteMeFetcher(),
    "Ping Perfect": PingPerfectFetcher(),
    "Servus Speed": ServusSpeedFetcher(),
    "VerbynDich": VerbynDichFetcher(),
    "WebWunder": WebWunderFetcher(),
}