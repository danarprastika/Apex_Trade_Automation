import logging
import time

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.database.models.exchange import Exchange, ExchangeType
from app.database.models.market import Asset, AssetType, AssetStatus, MarketPair
from app.database.session import SessionLocal

logger = logging.getLogger(__name__)

DEFAULT_ASSETS = [
    {"symbol": "BTC", "name": "Bitcoin", "type": AssetType.CRYPTO},
    {"symbol": "USDT", "name": "Tether", "type": AssetType.CRYPTO},
    {"symbol": "ETH", "name": "Ethereum", "type": AssetType.CRYPTO},
]

DEFAULT_MARKET_PAIRS = [
    {"symbol": "BTC/USDT", "base": "BTC", "quote": "USDT", "exchange": "binance"},
    {"symbol": "ETH/USDT", "base": "ETH", "quote": "USDT", "exchange": "binance"},
]


def seed_default_market_pairs() -> None:
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            with SessionLocal() as session:
                exchange = session.execute(select(Exchange).where(Exchange.name == "binance")).scalar_one_or_none()
                if not exchange:
                    exchange = Exchange(name="binance", exchange_type=ExchangeType.SPOT, status="ACTIVE")
                    session.add(exchange)
                    session.commit()
                    session.refresh(exchange)
                
                existing_pair = session.execute(
                    select(MarketPair).where(MarketPair.symbol == "BTC/USDT")
                ).scalar_one_or_none()
                
                if existing_pair:
                    logger.info("market_pairs_already_seeded")
                    return
                
                for asset_data in DEFAULT_ASSETS:
                    asset = session.execute(
                        select(Asset).where(Asset.symbol == asset_data["symbol"])
                    ).scalar_one_or_none()
                    if not asset:
                        asset = Asset(
                            symbol=asset_data["symbol"],
                            name=asset_data["name"],
                            asset_type=asset_data["type"],
                            status=AssetStatus.ACTIVE,
                        )
                        session.add(asset)
                
                session.commit()
                
                for pair_data in DEFAULT_MARKET_PAIRS:
                    base_asset = session.execute(
                        select(Asset).where(Asset.symbol == pair_data["base"])
                    ).scalar_one_or_none()
                    quote_asset = session.execute(
                        select(Asset).where(Asset.symbol == pair_data["quote"])
                    ).scalar_one_or_none()
                    
                    if base_asset and quote_asset:
                        market_pair = MarketPair(
                            exchange_id=exchange.id,
                            base_asset_id=base_asset.id,
                            quote_asset_id=quote_asset.id,
                            symbol=pair_data["symbol"],
                            status="ACTIVE",
                        )
                        session.add(market_pair)
                
                session.commit()
                logger.info("market_pairs_seeded", count=len(DEFAULT_MARKET_PAIRS))
                return
                
        except (OperationalError, ProgrammingError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"database_not_ready_retry_attempt_{attempt + 1}", error=str(e))
                time.sleep(retry_delay)
            else:
                logger.error("database_seed_failed_after_retries", error=str(e))
                raise
        except Exception as e:
            logger.error("market_pairs_seed_error", error=str(e))
            raise