class Curso:
    def __init__(
        self,
        nome,
        codigo,
        link,
        turno,
        campus,
        duracao_minima,
        duracao_maxima,
        periodo_curriculo,
        descricao_base_legal,
        descricao_profissional,
        info_carga_horaria
    ):
        self.nome = nome
        self.codigo = codigo
        self.link = link
        self.turno = turno
        self.campus = campus
        self.duracao_minima = duracao_minima
        self.duracao_maxima = duracao_maxima
        self.periodo_curriculo = periodo_curriculo
        self.descricao_base_legal = descricao_base_legal
        self.descricao_profissional = descricao_profissional
        self.info_carga_horaria = info_carga_horaria

    def to_dict(self):
        return {
            "nome": self.nome,
            "codigo": self.codigo,
            "link": self.link,
            "turno": self.turno,
            "campus": self.campus,
            "duracao_minima": self.duracao_minima,
            "duracao_maxima": self.duracao_maxima,
            "periodo_curriculo": self.periodo_curriculo,
            "descricao_base_legal": self.descricao_base_legal,
            "descricao_profissional": self.descricao_profissional,
            "info_carga_horaria": self.info_carga_horaria
        }

    @staticmethod
    def from_dict(dict):
        return Curso(
            dict["nome"],
            dict["codigo"],
            dict["link"],
            dict["turno"],
            dict["campus"],
            dict["duracao_minima"],
            dict["duracao_maxima"],
            dict["periodo_curriculo"],
            dict["descricao_base_legal"],
            dict["descricao_profissional"],
            dict["info_carga_horaria"]
        )
