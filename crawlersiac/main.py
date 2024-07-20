import asyncio
import dynaconf
from config import settings as config
from Scrapper import Scrapper


async def main():
    async with Scrapper(
        url=config.LOGIN_SIAC.URL_BASE,
    ) as scp:
        try:
            await scp.run()
        except Exception as e:
            print(f"Erro ao tentar executar o crawler: {e}")


if __name__ == "__main__":
    asyncio.run(main())
