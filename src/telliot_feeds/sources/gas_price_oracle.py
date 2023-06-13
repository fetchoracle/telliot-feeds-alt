from dataclasses import dataclass
from typing import Any
from typing import Optional

from telliot_core.apps.telliot_config import TelliotConfig
from web3 import Web3
from web3.exceptions import ExtraDataLengthError
from web3.middleware import geth_poa_middleware
from web3.types import BlockData

from telliot_feeds.datasource import DataSource
from telliot_feeds.dtypes.datapoint import datetime_now_utc
from telliot_feeds.dtypes.datapoint import OptionalDataPoint
from telliot_feeds.utils.log import get_logger
from telliot_feeds.utils.source_utils import update_web3


logger = get_logger(__name__)


@dataclass
class GasPriceOracleSource(DataSource[Any]):
    chainId: Optional[int] = None
    timestamp: Optional[int] = None
    cfg: TelliotConfig = TelliotConfig()
    web3: Optional[Web3] = None

    def binary_search_block(
        self, target_timestamp: int, left_block_number: int, right_block_number: int
    ) -> Optional[BlockData]:
        """Binary search for the block closest to the target timestamp (not later)

        Params:
            target_timestamp: The target Unix timestamp
            left_block_number: The left block number
            right_block_number: The right block number

        Returns:
            The block closest to the target timestamp (not later)
        """
        if self.web3 is None:
            raise ValueError("Web3 not instantiated")
        if left_block_number >= right_block_number:
            try:
                left_block = self.web3.eth.get_block(left_block_number)
                right_block = self.web3.eth.get_block(right_block_number)
            except Exception as e:
                logger.error(f"Failed to fetch block info: {e}")
                return None
            if left_block["timestamp"] > target_timestamp:
                return right_block
            if right_block["timestamp"] > target_timestamp:
                return left_block

            if left_block["timestamp"] - target_timestamp <= right_block["timestamp"] - target_timestamp:
                return left_block
            else:
                return right_block

        mid = (left_block_number + right_block_number) // 2
        try:
            mid_block = self.web3.eth.get_block(mid)
        except ExtraDataLengthError as e:
            logger.info(f"POA chain detected. Injecting POA middleware in response to exception: {e}")
            try:
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            except ValueError as e:
                logger.warning(f"Unable to inject web3 middleware for POA chain connection: {e}")
            mid_block = self.web3.eth.get_block(mid)
        except Exception as e:
            logger.error(f"Failed to fetch block info: {e}")
            return None
        mid_block_timestamp = mid_block["timestamp"]
        if mid_block_timestamp < target_timestamp:
            return self.binary_search_block(target_timestamp, mid + 1, right_block_number)
        else:
            return self.binary_search_block(target_timestamp, left_block_number, mid - 1)

    async def fetch_new_datapoint(self) -> OptionalDataPoint[Any]:
        """Fetch median gas price for a given timestamp by fetching
        block info for the closest block.

        Returns:
            Current time-stamped value
        """
        if not self.chainId:
            raise ValueError("Chain ID not provided")
        if self.timestamp is None:
            raise ValueError("Timestamp not provided")
        try:
            self.web3 = update_web3(self.chainId, self.cfg)
        except Exception as e:
            logger.warning(f"Error occurred while updating web3 instance: {e}")
            return None, None

        if not self.web3:
            raise ValueError("Web3 not instantiated")

        nearest_block = self.binary_search_block(self.timestamp, 0, self.web3.eth.block_number)
        if nearest_block is None:
            return None, None
        try:
            block = self.web3.eth.get_block(nearest_block["number"], full_transactions=True)
        except Exception as e:
            logger.error(f"Error occurred while fetching block: {e}")
            return None, None
        # sort the transactions by gas price
        try:
            sorted_gas_prices = sorted(tx["gasPrice"] for tx in block["transactions"])  # type: ignore
        except (KeyError, ValueError) as e:
            logger.error(f"Error occurred while sorting gas price from transactions: {e}")
            return None, None
        # find the median gas price
        middle = len(sorted_gas_prices) // 2
        if len(sorted_gas_prices) % 2 == 0:  # Even number of transactions
            gas_price = (sorted_gas_prices[middle - 1] + sorted_gas_prices[middle]) / 2
        else:  # Odd number of transactions
            gas_price = sorted_gas_prices[middle]

        datapoint = (self.web3.fromWei(int(gas_price), "gwei"), datetime_now_utc())

        self.store_datapoint(datapoint)

        return datapoint
