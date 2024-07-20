import aiohttp

from crawlersiac.Model import Curso, Disciplina
from crawlersiac.config import settings as config
from parsel import Selector

# class Disciplina:
#     def __init__(
#         self,
#         nome="",
#         codigo="",
#         natureza="",
#         semestre="",
#         pre_requisitos=[],
#         carga_horaria_teorica="",
#         carga_horaria_pratica="",
#         carga_horaria_estagio="",
#         carga_horaria_total="",
#         semestre_vigente="",
#         departamento="",
#         ementa="",
#         bibliografia="",
#         objetivos="",
#         conteudo="",
#     ):
#         self.nome = nome
#         self.codigo = codigo
#         self.natureza = natureza
#         self.semestre = semestre
#         self.pre_requisitos = pre_requisitos
#         self.carga_horaria_pratica = carga_horaria_pratica
#         self.carga_horaria_teorica = carga_horaria_teorica
#         self.carga_horaria_estagio = carga_horaria_estagio
#         self.carga_horaria_total = carga_horaria_total
#         self.departamento = departamento
#         self.ementa = ementa
#         self.bibliografia = bibliografia
#         self.objetivos = objetivos
#         self.conteudo = conteudo
#         self.semestre_vigente = semestre_vigente


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

    @staticmethod
    async def extrair_detalhes_disciplina(session, link):
        async with session.get(config.LOGIN_SIAC.URL_BASE + link) as response:
            html = await response.text()
            selector = Selector(text=html)
            tr_even_info = selector.xpath('//table/tr[3]/td[2]/center[2]/table/tr[@class="even"]')
            carga_horaria_teorica = tr_even_info[1].xpath("./td[1]/text()").get()
            carga_horaria_pratica = tr_even_info[1].xpath("./td[2]/text()").get()
            carga_horaria_estagio = tr_even_info[1].xpath("./td[3]/text()").get()
            carga_horaria_total = str(int(carga_horaria_pratica) + int(carga_horaria_teorica) + int(carga_horaria_estagio))
            departamento = tr_even_info[1].xpath("./td[4]/text()").get()
            semestre_vigente = tr_even_info[1].xpath("./td[5]/text()").get()
            ementa = tr_even_info[2].xpath("./td/text()").get()
            objetivos = tr_even_info[3].xpath("./td/text()").get()
            conteudo = tr_even_info[4].xpath("./td/text()").get()
            bibliografia = tr_even_info[5].xpath("./td/text()").get()

        return (
            carga_horaria_pratica,
            carga_horaria_estagio,
            carga_horaria_teorica,
            carga_horaria_total,
            departamento,
            ementa,
            bibliografia,
            objetivos,
            conteudo,
            semestre_vigente,
        )

    async def extrair_disciplinas(self, session, link):
        lista_disciplinas = []
        async with session.get(config.LOGIN_SIAC.URL_BASE + link) as response:
            html = await response.text()
            selector = Selector(text=html)
            semestre_fix = ""
            for tr in selector.xpath(
                '//center/table/tr[@class="odd" or @class="even"]'
            ):
                semestre = tr.xpath("./td[1]/text()").get()
                if semestre.strip() != "":
                    semestre_fix = semestre
                natureza = tr.xpath("./td[2]/text()").get()
                codigo = tr.xpath("./td[3]/text()").get()
                nome = tr.xpath("./td[4]/a/text()").get()
                link = tr.xpath("./td[4]/a/@href").get()
                pre_requisito = tr.xpath("./td[5]/text()").get()

                (
                    carga_horaria_pratica,
                    carga_horaria_estagio,
                    carga_horaria_teorica,
                    carga_horaria_total,
                    departamento,
                    ementa,
                    bibliografia,
                    objetivos,
                    conteudo,
                    semestre_vigente,
                ) = await self.extrair_detalhes_disciplina(session, link)

                disciplina = Disciplina(
                    nome=nome,
                    codigo=codigo,
                    natureza=natureza,
                    semestre=semestre_fix,
                    pre_requisitos=pre_requisito,
                    carga_horaria_pratica=carga_horaria_pratica,
                    carga_horaria_teorica=carga_horaria_teorica,
                    carga_horaria_estagio=carga_horaria_estagio,
                    carga_horaria_total=carga_horaria_total,
                    departamento=departamento,
                    ementa=ementa,
                    bibliografia=bibliografia,
                    objetivos=objetivos,
                    conteudo=conteudo,
                    semestre_vigente=semestre_vigente,
                )

        return lista_disciplinas

    async def extrair_cursos(self, session, cursos_info):
        cursos = []
        for curso in cursos_info:
            async with session.get(
                config.LOGIN_SIAC.URL_BASE + curso["link"]
            ) as response:
                html = await response.text()
                selector = Selector(text=html)

                tr_curso = selector.xpath('//center/table/tr[@class="even"][1]')
                codigo, nome = tr_curso.xpath("./td[1]/text()").get().split(" - ")
                turno = tr_curso.xpath("./td[2]/text()").get()
                duracao_minima = tr_curso.xpath("./td[3]/text()").get()
                duracao_maxima = tr_curso.xpath("./td[4]/text()").get()
                periodo_curriculo = tr_curso.xpath("./td[5]/text()").get()
                descricao_base_legal = selector.xpath(
                    '//center/table/tr[@class="even"][2]/td/text()'
                ).get()
                descricao_profissional = selector.xpath(
                    '//center/table/tr[@class="even"][3]/td/text()'
                ).get()
                table_carga_horaria = selector.xpath("//center[4]/table")
                lista_carga_horaria = []
                for tr in table_carga_horaria.xpath("./tr[position()>1]"):
                    descricao = tr.xpath("./td[2]/text()").get().strip()
                    carga_horaria = tr.xpath("./td[3]/text()").get()
                    creditacao = tr.xpath("./td[4]/text()").get()
                    if descricao is None or descricao == "":
                        descricao = "Carga horária total"
                        carga_horaria = tr.xpath("./td[3]/b/text()").get()
                        creditacao = tr.xpath("./td[4]/b/text()").get()

                    lista_carga_horaria.append(
                        {
                            "descricao": descricao,
                            "carga_horaria": carga_horaria,
                            "creditacao": creditacao,
                        }
                    )

                link_obrigatoria = selector.xpath(
                    "//table/tr[3]/td[2]/div[1]/a[1]/@href"
                ).get()
                link_optativa = selector.xpath(
                    "//table/tr[3]/td[2]/div[1]/a[2]/@href"
                ).get()

                lista_disciplinas_obrigatorias = await self.extrair_disciplinas(
                    session, link_obrigatoria
                )
                lista_disciplinas_optativas = await self.extrair_disciplinas(
                    session, link_optativa
                )

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
                        "codigo": tr.xpath("./td[1]/text()").get(),
                        "link": tr.xpath("./td/a/@href").get(),
                    }
                    cursos_info.append(curso)
        return cursos_info

    async def fazer_login(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url + config.LOGIN_SIAC.URL_SIAC_LOGIN,
                    data=self.payload_login(),
                ) as response:
                    links_classes_cursos = await self.extrair_link_cursos(session)
                    cursos_info = await self.extrair_links_cursos(
                        session, links_classes_cursos
                    )
                    cursos = await self.extrair_cursos(session, cursos_info)
        except Exception as e:
            print(f"Erro ao tentar fazer login: {e}")

    async def run(self):
        await self.fazer_login()
