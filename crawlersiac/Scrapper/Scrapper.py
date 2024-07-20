import aiohttp
from crawlersiac.config import settings as config
from parsel import Selector


class Scrapper:
    def __init__(self, url):
        self.url = url

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"Exception type: {exc_type}")
            print(f"Exception value: {exc_val}")
            print(f"Exception traceback: {exc_tb}")

    @staticmethod
    def payload_login():
        return {
            "cpf": config.LOGIN_SIAC.LOGIN,
            "senha": config.LOGIN_SIAC.PASSWORD,
        }

    async def extrair_link_cursos(self, session):
        async with session.get(self.url + config.LOGIN_SIAC.URL_CURSOS) as response:
            html = await response.text()
            selector = Selector(text=html)
            graduacao_link = selector.xpath("//a[text()='Graduação']/@href").get()
            mestrado_link = selector.xpath("//a[text()='Mestrado']/@href").get()
            doutorado_link = selector.xpath("//a[text()='Doutorado']/@href").get()

        return [graduacao_link, mestrado_link, doutorado_link]

    async def extrair_links_cursos(self, session, links):
        """
        :param session: Sessão do aiohttp para fazer requisições
        :param links: Lista com os links para os cursos de graduação, mestrado e doutorado
        :return: Lista com os cursos de graduação
        """
        # graduacao_link, mestrado_link, doutorado_link = links
        cursos = []
        for link in links:
            async with session.get(config.LOGIN_SIAC.URL_BASE + link) as response:
                html = await response.text()
                selector = Selector(text=html)
                tr_curso = selector.xpath(
                    '//center/table/tr[@class="odd" or @class="even"]'
                )
                for tr in tr_curso:
                    curso = {
                        "codigo": tr.xpath('./td[1]/text()').get(),
                        "link": tr.xpath('./td/a/@href').get(),
                    }
                    cursos.append(curso)
        return cursos

    async def fazer_login(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url + config.LOGIN_SIAC.URL_SIAC_LOGIN,
                                        data=self.payload_login()) as response:
                    links_classes_cursos = await self.extrair_link_cursos(session)
                    cursos_info = await self.extrair_links_cursos(session, links_classes_cursos)
                    cursos = await self.extrair_cursos(session, cursos_info)
        except Exception as e:
            print(f"Erro ao tentar fazer login: {e}")

    async def run(self):
        await self.fazer_login()
