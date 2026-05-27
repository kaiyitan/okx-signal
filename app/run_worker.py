import asyncio
import logging
from app.worker.universe import build_universe
from app.worker.market_worker import run_market_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


async def main():
    symbols = await build_universe()
    await run_market_worker(symbols)


if __name__ == "__main__":
    asyncio.run(main())
