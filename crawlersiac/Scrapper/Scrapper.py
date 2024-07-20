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

        return graduacao_link, mestrado_link, doutorado_link

    async def extrair_info_cursos(self, session, links):
        graduacao_link, mestrado_link, doutorado_link = links

        async with session.get(graduacao_link) as response:
            html = await response.text()
            selector = Selector(text=html)
            tr_curso = selector.xpath(
                '//center/table/tbody/tr[@class="odd" or @class="even"]'
            ).getall()
            cursos = []
            for tr in tr_curso:
                curso = {}
                codigo_curso = selector.xpath('./td[1]/text()')
                link_curso = selector.xpath('./td/a/@href')

        return link_curso

    async def fazer_login(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url + config.LOGIN_SIAC.URL_SIAC_LOGIN,
                                        data=self.payload_login()) as response:
                    links_classes_cursos = await self.extrair_link_cursos(session)
                    disciplinas = await self.extrair_info_cursos(session, links_classes_cursos)

        except Exception as e:
            print(f"Erro ao tentar fazer login: {e}")

    async def run(self):
        sessao_login = await self.fazer_login()

