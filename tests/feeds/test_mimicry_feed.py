from typing import get_type_hints

import pytest
from hexbytes import HexBytes

from telliot_feeds.datafeed import DataFeed
from telliot_feeds.feeds.mimicry.collection_stat_feed import mimicry_collection_stat_feed
from telliot_feeds.feeds.mimicry.macro_market_mashup_feed import mimicry_mashup_example_feed
from telliot_feeds.feeds.mimicry.nft_index_feed import mimicry_nft_market_index_eth_feed
from telliot_feeds.feeds.mimicry.nft_index_feed import mimicry_nft_market_index_usd_feed
from telliot_feeds.queries.mimicry.macro_market_mash_up import MimicryMacroMarketMashup
from telliot_feeds.queries.mimicry.nft_market_index import MimicryNFTMarketIndex


@pytest.mark.asyncio
async def test_fetch_new_datapoint():
    """Retrieve TAMI index and NFT market cap from source"""

    crypto_coven_address = "0x5180db8F5c931aaE63c74266b211F580155ecac8"

    mimicry_collection_stat_feed.source.chainId = 1
    mimicry_collection_stat_feed.source.collectionAddress = crypto_coven_address
    mimicry_collection_stat_feed.source.metric = 0

    tami, _ = await mimicry_collection_stat_feed.source.fetch_new_datapoint()
    print(tami)

    assert tami > 0

    mimicry_collection_stat_feed.source.metric = 1

    market_cap, _ = await mimicry_collection_stat_feed.source.fetch_new_datapoint()
    print(market_cap)

    assert market_cap > tami


def test_mimicry_nft_market_index_usd_feed():
    """Test NFT market index feed"""
    q = mimicry_nft_market_index_usd_feed.query
    exp_id = HexBytes("0x486e2149f25d46bb39a27f5e0c81be9b6f193abf46c0d49314b8d1dd104cd53b")
    exp_data = HexBytes(
        "0x0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000154d696d696372794e46544d61726b6574496e646578000000000000000000000000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000008657468657265756d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000037573640000000000000000000000000000000000000000000000000000000000"  # noqa: E501
    )

    assert q.query_data == exp_data
    assert q.query_id == exp_id
    assert isinstance(mimicry_nft_market_index_usd_feed, DataFeed)
    assert isinstance(q, MimicryNFTMarketIndex)


def test_mimicry_nft_market_index_eth_feed():
    """Test NFT market index feed"""
    q = mimicry_nft_market_index_eth_feed.query
    exp_id = HexBytes("0x891f39f24b8ae90f540b147d42c75b825fc733cc7294a1abd54e1adfb4a8e517")
    exp_data = HexBytes(
        "0x0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000154d696d696372794e46544d61726b6574496e646578000000000000000000000000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000008657468657265756d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000036574680000000000000000000000000000000000000000000000000000000000"  # noqa: E501
    )

    assert q.query_data == exp_data
    assert q.query_id == exp_id
    assert isinstance(mimicry_nft_market_index_eth_feed, DataFeed)
    assert isinstance(q, MimicryNFTMarketIndex)


@pytest.mark.asyncio
def test_mimicry_mashup_feed():
    """Test NFT mashup feed"""
    q = mimicry_mashup_example_feed.query
    exp_id = HexBytes("0x30717c1fa75f5bae0c11e13283bedcf72e9f4e526c642bd5b330b615d0db8708")
    exp_data = HexBytes(
        "0x0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000184d696d696372794d6163726f4d61726b65744d617368757000000000000000000000000000000000000000000000000000000000000000000000000000000620000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000000a6d61726b65742d63617000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000375736400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000000004000000000000000000000000050f5474724e0ee42d9a4e711ccfb275809fd6d4a0000000000000000000000000000000000000000000000000000000000000010657468657265756d2d6d61696e6e6574000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000f87e31492faf9a91b02ee0deaad50d51d56d5d4d0000000000000000000000000000000000000000000000000000000000000010657468657265756d2d6d61696e6e657400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000034d85c9cdeb23fa97cb08333b511ac86e1c4e2580000000000000000000000000000000000000000000000000000000000000010657468657265756d2d6d61696e6e6574000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000001400000000000000000000000000000000000000000000000000000000000000220000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000003845badade8e6dff049820680d1f14bd3903a5d00000000000000000000000000000000000000000000000000000000000000010657468657265756d2d6d61696e6e657400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000473616e6400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000f5d2fb29fb7d3cfee444a200298f468908cc9420000000000000000000000000000000000000000000000000000000000000010657468657265756d2d6d61696e6e65740000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000046d616e6100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000004d224452801aced8b2f0aebe155379bb5d5943810000000000000000000000000000000000000000000000000000000000000010657468657265756d2d6d61696e6e65740000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000036170650000000000000000000000000000000000000000000000000000000000"  # noqa: E501
    )

    assert q.query_data == exp_data
    assert q.query_id == exp_id
    assert isinstance(mimicry_mashup_example_feed, DataFeed)
    assert isinstance(q, MimicryMacroMarketMashup)
