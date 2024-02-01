from core.btc_to_usd_converter import CryptoConverter, FakeCryptoExchangeRate

# import pytest


# @pytest.mark.vcr
# def test_api_converter() -> None:
#     stats = APICryptoExchangeRate()
#
#     assert stats.get_rate() == 42662.61375001


def test_convert() -> None:
    converter = CryptoConverter(FakeCryptoExchangeRate())

    converted_value = converter.convert(2.0)

    assert converted_value == 200.0
