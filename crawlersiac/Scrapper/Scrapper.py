import aiohttp

from crawlersiac.Model import Curso
from crawlersiac.config import settings as config
from parsel import Selector

# class Curso():
#     def __init__(self, nome, codigo, link, turno, campus, duracao_minima, duracao_maxima, periodo_curriculo, descricao_base_legal, descricao_profissional, ch_obrigatoria, ch_optativa, ch_atividade_complementar, link_obrigatoria, link_optativa):
#         self.nome = nome
#         self.codigo = codigo
#         self.link = link
#         self.turno = turno
#         self.campus = campus
#         self.duracao_minima = duracao_minima
#         self.duracao_maxima = duracao_maxima
#         self.periodo_curriculo = periodo_curriculo
#         self.descricao_base_legal = descricao_base_legal
#         self.descricao_profissional = descricao_profissional
#         self.ch_obrigatoria = ch_obrigatoria
#         self.ch_optativa = ch_optativa
#         self.ch_atividade_complementar = ch_atividade_complementar
#         self.link_obrigatoria = link_obrigatoria
#         self.link_optativa = link_optativa

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
        cursos_info = []
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
                    cursos_info.append(curso)
        return cursos_info

    async def extrair_cursos(self, session, cursos_info):
        cursos = []
        for curso in cursos_info:
            async with session.get(config.LOGIN_SIAC.URL_BASE + curso["link"]) as response:
                html = await response.text()
                selector = Selector(text=html)

                tr_curso = selector.xpath('//center/table/tr[@class="even"][1]')
                codigo, nome = tr_curso.xpath('./td[1]/text()').get().split(" - ")
                turno = tr_curso.xpath('./td[2]/text()').get()
                duracao_minima = tr_curso.xpath('./td[3]/text()').get()
                duracao_maxima = tr_curso.xpath('./td[4]/text()').get()
                periodo_curriculo = tr_curso.xpath('./td[5]/text()').get()
                descricao_base_legal = selector.xpath('//center/table/tr[@class="even"][2]/td/text()').get()
                descricao_profissional = selector.xpath('//center/table/tr[@class="even"][3]/td/text()').get()
                table_carga_horaria = selector.xpath('//center[4]/table')
                lista_carga_horaria = []
                for tr in table_carga_horaria.xpath('./tr[position()>1]'):
                    descricao = tr.xpath('./td[2]/text()').get().strip()
                    carga_horaria = tr.xpath('./td[3]/text()').get()
                    creditacao = tr.xpath('./td[4]/text()').get()
                    if descricao is None or descricao == "":
                        descricao = "Carga horária total"
                        carga_horaria = tr.xpath('./td[3]/b/text()').get()
                        creditacao = tr.xpath('./td[4]/b/text()').get()

                    lista_carga_horaria.append({
                        "descricao": descricao,
                        "carga_horaria": carga_horaria,
                        "creditacao": creditacao
                    })

                link_obrigatoria = selector.xpath('//table/tr[3]/td[2]/div[1]/a[1]/@href').get()
                link_optativa = selector.xpath('//table/tr[3]/td[2]/div[1]/a[2]/@href').get()

                curso = Curso(
                    nome=nome,
                    codigo=codigo,
                    link=curso["link"],
                    turno=turno,
                    campus="",
                    duracao_minima=duracao_minima,
                    duracao_maxima=duracao_maxima,
                    periodo_curriculo=periodo_curriculo,
                    descricao_base_legal=descricao_base_legal,
                    descricao_profissional=descricao_profissional,
                    info_carga_horaria=lista_carga_horaria,
                    link_obrigatoria=link_obrigatoria,
                    link_optativa=link_optativa,
                    disciplinas_obrigatorias=[],
                    disciplinas_optativas=[],
                )
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
