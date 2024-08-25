import asyncio
import re

import aiohttp

from crawlersiac.Model import Curso, Disciplina
from crawlersiac.Scrapper import CriarScriptCarga
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

    @staticmethod
    async def extrair_detalhes_disciplina(session, link):
        try:
            async with session.get(config.LOGIN_SIAC.URL_BASE + link) as response:
                html = await response.text()
                selector = Selector(text=html)
                tr_even_info = selector.xpath('//table/tr[3]/td[2]/center[2]/table/tr[@class="even"]')
                carga_horaria_teorica = tr_even_info[1].xpath("./td[1]/text()").get()
                carga_horaria_pratica = tr_even_info[1].xpath("./td[2]/text()").get()
                carga_horaria_estagio = tr_even_info[1].xpath("./td[3]/text()").get()
                carga_horaria_total = str(int(carga_horaria_pratica) + int(carga_horaria_teorica) + int(carga_horaria_estagio))
                departamento = tr_even_info[1].xpath("./td[4]/text()").get()
                if departamento is not None:
                    departamento = departamento.strip()
                    departamento = departamento.replace("'", "''")

                semestre_vigente = tr_even_info[1].xpath("./td[5]/text()").get()

                ementa = tr_even_info[2].xpath("./td/text()").get()
                if ementa is not None:
                    ementa = re.sub(r'\s+', ' ', ementa).strip()
                    ementa = ementa.replace("'", "''")
                objetivos = tr_even_info[3].xpath("./td/text()").get()
                if objetivos is not None:
                    objetivos = re.sub(r'\s+', ' ', objetivos).strip()
                    objetivos = objetivos.replace("'", "''")
                conteudo = tr_even_info[4].xpath("./td/text()").get()
                if conteudo is not None:
                    conteudo = re.sub(r'\s+', ' ', conteudo).strip()
                    conteudo = conteudo.replace("'", "''")
                bibliografia = tr_even_info[5].xpath("./td/text()").get()
                if bibliografia is not None:
                    bibliografia = re.sub(r'\s+', ' ', bibliografia).strip()
                    bibliografia = bibliografia.replace("'", "''")

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
        except Exception as e:
            print(f"Erro ao tentar extrair os detalhes da disciplina: {e}")

    async def extrair_disciplinas(self, session, link, codigo_curso):
        try:
            async with session.get(config.LOGIN_SIAC.URL_BASE + link) as response:
                html = await response.text()
                selector = Selector(text=html)
                semestre_fix = ""
                for tr in selector.xpath(
                    '//center/table/tr[@class="odd" or @class="even"]'
                ):
                    pattern = re.compile(r'\\$')
                    semestre_previsto = tr.xpath("./td[1]/text()").get()
                    if semestre_previsto.strip() != "":
                        semestre_fix = semestre_previsto
                    natureza = tr.xpath("./td[2]/text()").get()
                    codigo_disciplina = tr.xpath("./td[3]/text()").get()
                    nome = tr.xpath("./td[4]/a/text()").get()
                    link = tr.xpath("./td[4]/a/@href").get()
                    if link is None:
                        nome = tr.xpath("./td[4]/text()").get()
                        nome = nome.strip()
                        nome = nome.replace("'", "''")
                        nome = pattern.sub('', nome)

                    if nome is not None:
                        nome = nome.strip()
                        nome = nome.replace("'", "''")
                        nome = pattern.sub('', nome)


                    pre_requisitos = tr.xpath("./td[5]/text()").get()

                    if pre_requisitos != "--":
                        for pre_requisito in pre_requisitos.split(", "):
                            CriarScriptCarga().gerar_script_carga_disciplina_pre_requisito(codigo_disciplina, pre_requisito)

                    print("Crawler da disciplina: ", nome, " - ", codigo_disciplina)

                    if link is not None:
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
                    else:
                        carga_horaria_pratica = 0
                        carga_horaria_estagio = 0
                        carga_horaria_teorica = 0
                        carga_horaria_total = 0
                        departamento = ""
                        ementa = ""
                        bibliografia = ""
                        objetivos = ""
                        conteudo = ""
                        semestre_vigente = ""

                    disciplina = Disciplina(
                        nome=nome,
                        codigo=codigo_disciplina,
                        natureza=natureza,
                        semestre=semestre_fix,
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
                    CriarScriptCarga().gerar_script_carga_disciplina(disciplina)
                    CriarScriptCarga().gerar_script_carga_curso_disciplina(codigo_curso, codigo_disciplina, natureza, semestre_previsto, semestre_vigente)
        except Exception as e:
            print(f"Erro ao tentar extrair as disciplinas: {e}")

    async def extrair_cursos(self, session, cursos_info):
        tasks = []
        max_exec = 100
        for curso in cursos_info:
            tasks.append(self.scrapper_cursos_disciplinas(curso, session))
        for i in range(0, len(tasks), max_exec):
            await asyncio.gather(*tasks[i: i + max_exec])

    async def scrapper_cursos_disciplinas(self, curso, session):
        try:
            async with session.get(
                    config.LOGIN_SIAC.URL_BASE + curso["link"]
            ) as response:
                html = await response.text()
                selector = Selector(text=html)

                tr_curso = selector.xpath('//center/table/tr[@class="even"][1]')
                codigo, nome = tr_curso.xpath("./td[1]/text()").get().split(" - ", 1)
                print(f"Crawler do curso: {nome} - {codigo}")
                if nome is not None:
                    nome = nome.strip()
                    nome = nome.replace("'", "''")

                turno = tr_curso.xpath("./td[2]/text()").get()
                if turno is not None:
                    turno = turno.strip()
                    turno = turno.replace("'", "''")
                duracao_minima = tr_curso.xpath("./td[3]/text()").get()
                duracao_maxima = tr_curso.xpath("./td[4]/text()").get()
                periodo_curriculo = tr_curso.xpath("./td[5]/text()").get()
                descricao_base_legal = selector.xpath(
                    '//center/table/tr[@class="even"][2]/td/text()'
                ).get()
                if descricao_base_legal is not None:
                    descricao_base_legal = re.sub(r'\s+', ' ', descricao_base_legal).strip()
                    descricao_base_legal = descricao_base_legal.replace("'", "''")
                descricao_profissional = selector.xpath(
                    '//center/table/tr[@class="even"][3]/td/text()'
                ).get()
                if descricao_profissional is not None:
                    descricao_profissional = re.sub(r'\s+', ' ', descricao_profissional).strip()
                    descricao_profissional = descricao_profissional.replace("'", "''")

                table_carga_horaria = selector.xpath("//center[4]/table")
                lista_carga_horaria = []
                for tr in table_carga_horaria.xpath("./tr[position()>1]"):
                    descricao = tr.xpath("./td[2]/text()").get()
                    if descricao:
                        descricao = descricao.strip()
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
                )

                CriarScriptCarga("Curso").gerar_script_carga_curso(curso)

                await self.extrair_disciplinas(
                    session, link_obrigatoria, codigo
                )
                await self.extrair_disciplinas(
                    session, link_optativa, codigo
                )

        except Exception as e:
            print(f"Erro ao tentar extrair o curso {curso.get('link')}: {e}")

    async def extrair_link_por_tipo_curso(self, session):
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
            try:
                async with session.get(config.LOGIN_SIAC.URL_BASE + link) as response:
                    html = await response.text()
                    selector = Selector(text=html)
                    tr_curso = selector.xpath(
                        '//center/table/tr[@class="odd" or @class="even"]'
                    )
                    for tr in tr_curso:
                        curso = {
                            "codigo": tr.xpath("./td[1]/text()").get(),
                            "nome": tr.xpath("./td/a/text()").get(),
                            "link": tr.xpath("./td/a/@href").get(),
                        }
                        cursos_info.append(curso)
            except Exception as e:
                print(f"Erro ao tentar extrair os links dos cursos: {e}")
        return cursos_info

    async def crawler_siac_run(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url + config.LOGIN_SIAC.URL_SIAC_LOGIN,
                    data=self.payload_login(),
                ) as response:
                    links_classes_cursos = await self.extrair_link_por_tipo_curso(session)
                    cursos_info = await self.extrair_links_cursos(
                        session, links_classes_cursos
                    )
                    await self.extrair_cursos(session, cursos_info)
        except Exception as e:
            print(f"Erro ao tentar fazer login: {e}")

    async def run(self):
        await self.crawler_siac_run()