class Contas:
    def __init__(self, pot_eletro=0, pot_energia=0):
        self.pot_eletro = pot_eletro
        self.pot_energia = pot_energia

    def calculo(self):
        return self.pot_eletro + self.pot_energia

class Eletrolisador(Contas):
    def __init__(self, pot_eletro):
        super().__init__(pot_eletro)

    def pot_eletro(self):
        return self.pot_eletro * 10

class Energias(Contas):
    def __init__(self, pot_energia):
        super().__init__(pot_energia)

    def pot_energia(self):
        return self.pot_energia * 2

pot_pem = 10
pem = Eletrolisador(pot_pem)
pot_sol = 2
solar = Energias(pot_sol)

conta = Contas(pem.pot_eletro, solar.pot_energia)
resultado = conta.calculo()
print("Resultado do cálculo:", resultado)
