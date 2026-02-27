class CreateClienteCommand:
    def __init__(self, nome: str, email: str, telefone: str | None = None):
        self.nome = nome
        self.email = email
        self.telefone = telefone