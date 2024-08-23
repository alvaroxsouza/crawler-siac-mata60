import json


class Disciplina:
    def __init__(
        self,
        nome="",
        codigo="",
        natureza="",
        semestre="",
        carga_horaria_teorica="",
        carga_horaria_pratica="",
        carga_horaria_estagio="",
        carga_horaria_total="",
        semestre_vigente="",
        departamento="",
        ementa="",
        bibliografia="",
        objetivos="",
        conteudo="",
    ):
        self.nome = nome
        self.codigo = codigo
        self.natureza = natureza
        self.semestre = semestre
        self.carga_horaria_pratica = carga_horaria_pratica
        self.carga_horaria_teorica = carga_horaria_teorica
        self.carga_horaria_estagio = carga_horaria_estagio
        self.carga_horaria_total = carga_horaria_total
        self.departamento = departamento
        self.ementa = ementa
        self.bibliografia = bibliografia
        self.objetivos = objetivos
        self.conteudo = conteudo
        self.semestre_vigente = semestre_vigente

    def __str__(self):
        return (
            f"Disciplina {self.nome} -"
            f" {self.codigo} -"
            f" {self.semestre} -"
            f" {self.natureza} -"
            f" {self.departamento} -"
            f" {self.semestre_vigente} -"
            f" {self.carga_horaria_total} -"
            f" {self.carga_horaria_teorica} -"
            f" {self.carga_horaria_pratica} -"
            f" {self.carga_horaria_estagio} -"
            f" {self.ementa} -"
            f" {self.bibliografia} -"
            f" {self.objetivos} -"
            f" {self.conteudo} -"
            f" {self.semestre_vigente} -"
            f" {self.departamento} -"
            f" {self.ementa} -"
            f" {self.bibliografia} -"
            f" {self.objetivos} - {self.conteudo} -"
            f" {self.semestre_vigente} -"
            f" {self.departamento} -"
            f" {self.ementa} -"
            f" {self.bibliografia} -"
            f" {self.objetivos} -"
            f" {self.conteudo}"
        )

    def to_json(self):
        return json.dumps(self.__dict__)
