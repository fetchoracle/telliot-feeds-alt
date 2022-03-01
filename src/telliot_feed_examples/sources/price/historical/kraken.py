from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Optional
from urllib.parse import urlencode

from telliot_core.dtypes.datapoint import datetime_now_utc
from telliot_core.dtypes.datapoint import OptionalDataPoint
from telliot_core.pricing.price_service import WebPriceService
from telliot_core.pricing.price_source import PriceSource

from telliot_feed_examples.utils.log import get_logger


logger = get_logger(__name__)


# Hardcoded supported assets & currencies
kraken_assets = {"ETH"}
kraken_currencies = {"USD"}


class KrakenHistoricalPriceService(WebPriceService):
    """Kraken Historical Price Service"""

    def __init__(self, **kwargs: Any) -> None:
        kwargs["name"] = "Kraken Historical Price Service"
        kwargs["url"] = "https://api.kraken.com"
        super().__init__(**kwargs)

    async def get_price(
        self, asset: str, currency: str, ts: Optional[int]
    ) -> OptionalDataPoint[float]:
        """Implement PriceServiceInterface

        This implementation gets the historical price from
        the Kraken API using a timestamp."""
        if ts is None:
            ts = self.ts

        asset = asset.upper()
        currency = currency.upper()

        if asset not in kraken_assets:
            raise Exception(f"Asset not supported: {asset}")
        if currency not in kraken_currencies:
            raise Exception(f"Currency not supported: {currency}")

        url_params = urlencode(
            {"pair": f"{asset}{currency}", "since": ts}  # Unix timestamp
        )

        # Source: https://docs.kraken.com/rest/#operation/getRecentTrades
        request_url = f"/0/public/Trades?{url_params}"

        d = self.get_url(request_url)

        if "error" in d:
            logger.error(d)
            return None, None

        elif "response" in d:
            response = d["response"]

            try:
                price = float(response["result"][f"X{asset}Z{currency}"][0][0])
            except KeyError as e:
                msg = f"Error parsing Kraken API response: KeyError: {e}"
                logger.critical(msg)

        else:
            raise Exception("Invalid response from get_url")

        return price, datetime_now_utc()


@dataclass
class KrakenHistoricalPriceSource(PriceSource):
    ts: int = 0
    asset: str = ""
    currency: str = ""
    service: KrakenHistoricalPriceService = field(
        default_factory=KrakenHistoricalPriceService, init=False
    )
