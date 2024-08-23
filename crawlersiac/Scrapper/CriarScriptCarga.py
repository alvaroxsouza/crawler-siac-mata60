import json
import os


class CriarScriptCarga:
    def __init__(self, tipo=""):
        self.tipo = tipo
        self.nome_arquivo_disciplina = "script_de_carga_disciplina.sql"
        self.nome_arquivo_curso = "script_de_carga_curso.sql"
        self.nome_arquivo_curso_disciplina = "script_de_carga_curso_disciplina.sql"
        self.nome_arquivo_disciplina_pre_requisito = "script_de_carga_disciplina_pre_requisito.sql"

        # Se o arquivo não existir, cria e adiciona um cabeçalho apropriado
        if not os.path.exists(self.nome_arquivo_disciplina):
            with open(self.nome_arquivo_disciplina, "w", encoding="utf-8-sig") as arquivo:
                arquivo.write(f"-- Script de carga de {self.tipo}\n")
                arquivo.write("-- Gerado automaticamente\n\n")

        if not os.path.exists(self.nome_arquivo_curso):
            with open(self.nome_arquivo_curso, "w", encoding="utf-8-sig") as arquivo:
                arquivo.write(f"-- Script de carga de Cursos\n")
                arquivo.write("-- Gerado automaticamente\n\n")

        if not os.path.exists(self.nome_arquivo_curso_disciplina):
            with open(self.nome_arquivo_curso_disciplina, "w", encoding="utf-8-sig") as arquivo:
                arquivo.write(f"-- Script de carga de Disciplinas\n")
                arquivo.write("-- Gerado automaticamente\n\n")

        if not os.path.exists(self.nome_arquivo_disciplina_pre_requisito):
            with open(self.nome_arquivo_disciplina_pre_requisito, "w", encoding="utf-8-sig") as arquivo:
                arquivo.write(f"-- Script de carga de Disciplinas Pré-Requisito\n")
                arquivo.write("-- Gerado automaticamente\n\n")

    def gerar_script_carga_curso(self, curso):
        # Cria a linha de inserção para o curso
        linha_insert = f"""INSERT INTO Curso (nome,codigo,link,turno,campus,duracao_minima,duracao_maxima,periodo_curriculo,descricao_base_legal,descricao_profissional,info_carga_horaria) VALUES ('{curso.nome}','{curso.codigo}','{curso.link}','{curso.turno}','{curso.campus}','{curso.duracao_minima}','{curso.duracao_maxima}','{curso.periodo_curriculo}','{curso.descricao_base_legal}','{curso.descricao_profissional}','{self._formatar_lista_carga_horaria(curso.info_carga_horaria)}');\n"""

        # Adiciona a linha de inserção ao arquivo com encoding utf-8-sig
        with open(self.nome_arquivo_curso, "a", encoding="utf-8-sig") as arquivo:
            arquivo.write(linha_insert)

    import json

    def _formatar_lista_carga_horaria(self, lista_carga_horaria):
        # Formata a lista de cargas horárias para ser inserida no SQL como JSON
        carga_horaria_json = [
            {
                "descricao": item['descricao'],
                "carga_horaria": f"{item['carga_horaria']}h",
                "creditacao": f"{item['creditacao']} créditos"
            }
            for item in lista_carga_horaria
        ]
        return json.dumps(carga_horaria_json, ensure_ascii=False)

    def gerar_script_carga_disciplina(self, disciplina):

        # Cria a linha de inserção para a disciplina
        linha_insert = f"""INSERT INTO Disciplina (codigo_disciplina,nome_disciplina,natureza,semestre,carga_horaria_pratica,carga_horaria_teorica,carga_horaria_estagio,carga_horaria_total,departamento,ementa,bibliografia,objetivos,conteudo,semestre_vigente) VALUES ('{disciplina.codigo}','{disciplina.nome}','{disciplina.natureza}','{disciplina.semestre}','{disciplina.carga_horaria_pratica}','{disciplina.carga_horaria_teorica}','{disciplina.carga_horaria_estagio}','{disciplina.carga_horaria_total}','{disciplina.departamento}','{disciplina.ementa}','{disciplina.bibliografia}','{disciplina.objetivos}','{disciplina.conteudo}','{disciplina.semestre_vigente}');\n"""

        # Adiciona a linha de inserção ao arquivo
        with open(self.nome_arquivo_disciplina, "a") as arquivo:
            arquivo.write(linha_insert)

    def gerar_script_carga_curso_disciplina(self, codigo_curso, codigo_disciplina):
        # Cria a linha de inserção para o relacionamento curso-disciplina
        linha_insert = f"""INSERT INTO CursoDisciplina (curso_codigo,disciplina_codigo) VALUES ('{codigo_curso}','{codigo_disciplina}');\n"""

        # Adiciona a linha de inserção ao arquivo com encoding utf-8-sig
        with open(self.nome_arquivo_curso_disciplina, "a", encoding="utf-8-sig") as arquivo:
            arquivo.write(linha_insert)

    def gerar_script_carga_disciplina_pre_requisito(self, codigo_disciplina, codigo_pre_requisito):
        # Cria a linha de inserção para o relacionamento curso-disciplina
        linha_insert = f"""INSERT INTO DisciplinaPreRequisito (codigo_disciplina, codigo_pre_requisito) VALUES ('{codigo_disciplina}','{codigo_pre_requisito}');\n"""

        # Adiciona a linha de inserção ao arquivo com encoding utf-8-sig
        with open(self.nome_arquivo_disciplina_pre_requisito, "a", encoding="utf-8-sig") as arquivo:
            arquivo.write(linha_insert)
