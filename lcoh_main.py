import numpy as np 
import matplotlib.pyplot as plt 


class Eletrolisador:
    # Define as caracteristicas do eletrolisador
    def __init__(self, name, pot, h2, capex, opex, efficiency, lifetime, FlowRate, Pressure):
        self.name = name
        self.pot = pot
        self.h2 = h2
        self.capex = capex
        self.opex = opex
        self.ef = efficiency
        self.lifetime = lifetime
        self.FlowRate = FlowRate
        self.Pressure = Pressure

    def capexCompressor(self):
        NumCompressor = 1 
        IsotropricCoefficient = 1.4 
        CompressorEfficiency = 0.75 
        M = 2.016 # Massa molecular hidrogenio
        R = 8.314 # Constante gas ideal
        T = 310 # temperatura
        Z = 1.03 # Fator de compressibilidade
        p0 = 70 # Output pressure
        Q = self.FlowRate
        pi = self.Pressure
        
        CompressorCapex = Q*((R*T*Z)/(CompressorEfficiency*M))*(NumCompressor/(IsotropricCoefficient-1))*((p0/pi)**((IsotropricCoefficient-1)/(NumCompressor)) - 1)
        return CompressorCapex

    # Energia para produzir 1kg de hidrogenio
    def energy_prod_1kg(self):
        energy_1kg = self.pot/self.h2
        tot_energy = energy_1kg+energy_1kg*0.1
        return tot_energy
    
    # Calcula o capex e opex total, com base na potencia multiplicada pelo preco por kW
    def electrolyser_capex_opex(self):
        CapexCompressor = self.capexCompressor()
        if 'AEM' in self.name.upper():
            CapexElectrolyzer = self.capex*self.pot
            capex_total = (CapexElectrolyzer+CapexCompressor)*0.66
            # Material - 2.5% | Labor - 5.0%   Deionized water - 0.01$/kg | Electrolyte (KOH) 2.75$/kg | Steam 0.01$/kg
            opex_total = (0.025+0.05)*capex_total + (0.01 + 2.75 + 0.01)*(self.h2)

        else:  
            CapexElectrolyzer = self.capex*self.pot
            capex_total = (CapexElectrolyzer+CapexCompressor)*0.66
            opex_total = self.opex*capex_total
        
        print('=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
        print(f'{self.name} Capex compressor = {CapexCompressor*10**-3:.2f} k$')
        print(f'{self.name} Capex total {capex_total*10**-3:.2f} k$')
        print(f'{self.name} Opex total {opex_total*10**-3:.2f} k$')
        print('=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
        return capex_total, opex_total
    

class Energia:
    def __init__(self, name, capex, opex, cf):
        self.name = name
        self.capex = capex
        self.opex = opex
        self.cf = cf
        self.t = 20
        self.CapexBateria = 7350
        self.OpexBateria = 70/self.CapexBateria 

    """
    Total capex e opex da fonte energia com base na potência do eletrolisador.
    As potências dos eletrolisadores estão próximas de 1 MW então o capex e o opex são similares
    Essa fórmula multiplica o capex pelo total de energia que minha planta deve ter com base no fator de capacidade
    Se meu eletrolisador tem 1 MW e cf_sol 0.25, minha planta deve ter 1 MW/0.25 = 4 WM
    """
    def energy_total_capex_opex(self,pot,cf, nome, lifetime):
        EnergyToStore = self.CapexBateria*(pot/cf - pot)*0.66

        plantLifetime = self.t*365*24 # Tempo de vida em horas
        TimeOperationElectrolyser = plantLifetime/(lifetime)
        ciclosEletrolisador = np.ceil(TimeOperationElectrolyser*cf)

        capex_energy = self.capex*(pot)*0.66 # capex_energy = self.capex*(pot/cf)
        tot_opex_energy = self.opex*capex_energy

        print('---------------------------------')
        print(f'O {nome} - {self.name} tem {ciclosEletrolisador:.2f} ciclos')
        print(f'{self.name} - {nome} Capex total {capex_energy * 10**-6:.2f} M$')
        print(f'{self.name} - {nome} Opex total {tot_opex_energy*10**-6:.2f} M$')
        print('---------------------------------')

        return capex_energy, tot_opex_energy, ciclosEletrolisador # Ta funcionando

# Calcula a producao anual de energia em kg
def wh2(pot, energy1kg, nome,cf):
    aep = pot*24*365*cf*0.913 # 91.3% Fator de capacidade eletrolisadores
    wh2 = aep/energy1kg
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print(f'{nome} WH2: {wh2:.2f} kg')
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    return wh2

# Calculo do Levelised Cosf Of Hydrogen
def lcoh(tot_capex_el, tot_opex_el, tot_capex_energy, tot_opex_energy, ciclos, wh2, t, nome, energia_nome, wacc):
    """
    Consideracoes:
    Stack replacement costs  = 50% Total CAPEX
    Installation cost = 12% Total CAPEX
    Indirect cost = 20% Total CAPEX
    """
    #capexEletrolisador = tot_capex_el + tot_capex_el*0.5*ciclos + 0.12*tot_capex_el + 0.2*tot_capex_el
    capexEletrolisador = tot_capex_el*(1.32+0.5*ciclos)
    capex_total = capexEletrolisador + tot_capex_energy
    opex_ano = tot_opex_el + tot_opex_energy
    ahp_ano = wh2
    
    print(f'{nome} - {energia_nome} Capex total: {capex_total*10**-6:.2f}')
    print(f'{nome} - {energia_nome} Opex anual: {opex_ano*10**-6:.2f}')
    
    opex = 0
    total_lcoh = 0
    ahp_total = 0

    # Calcula o opex total considerando o wacc ao longo de t anos
    for i in range(1,t+1):
        op = (opex_ano)/((1 + wacc)**i)
        opex += op 

    # Calcula a produção total de hidrogenio ao longo de t anos
    for i in range(1, t+1):
        ahp_i = ahp_ano/((1 + wacc)**i)
        ahp_total += ahp_i

    total_lcoh = ((capex_total) + (opex))/(ahp_total)

    print(f'A conta é {nome} - {energia_nome} ({capex_total*10**-6:.2f} + {opex*10**-6:.2f})/({ahp_total*10**-3:.2f} t) = LCOH = {total_lcoh:.2f} $/kg')
    print('---------------------------------------------%')
    return total_lcoh

def plot_graph(lcoh_pem_pv, lcoh_pem_WindOnshore ,lcoh_pem_WindOffshore, lcoh_pem_nuclear, lcoh_alk_pv, lcoh_alk_WindOnshore, lcoh_alk_WindOffshore, lcoh_alk_nuclear, 
               lcoh_soec_pv,lcoh_soec_WindOnshore, lcoh_soec_WindOffshore, lcoh_soec_nuclear, lcoh_aem_pv, lcoh_aem_WindOnshore, lcoh_aem_WindOffshore, lcoh_aem_nuclear):
    # Dados
    eletrolisadores = ['PEM', 'ALK', 'SOEC', 'AEM']
    tecnologias = ['Solar', 'Eólica OnShore', 'Eólica OffShore', 'Nuclear']
    custo_pem = [lcoh_pem_pv, lcoh_pem_WindOnshore, lcoh_pem_WindOffshore, lcoh_pem_nuclear]
    custo_alk = [lcoh_alk_pv, lcoh_alk_WindOnshore, lcoh_alk_WindOffshore, lcoh_alk_nuclear]
    custo_soec = [lcoh_soec_pv, lcoh_soec_WindOnshore, lcoh_soec_WindOffshore, lcoh_soec_nuclear]
    custo_aem = [lcoh_aem_pv, lcoh_aem_WindOnshore, lcoh_aem_WindOffshore, lcoh_aem_nuclear]

    # Cores mais sóbrias
    cores = [
        (46/255, 139/255, 87/255),  # ForestGreen
        (138/255, 43/255, 226/255),  # Blueviolet
        (255/255, 69/255, 0/255),  # Laranja avermelhado
        (255/255, 200/255, 0/255)     # Amarelo
    ]  

    # Configuração do gráfico
    barWidth = 0.2
    fig, ax = plt.subplots(figsize=(10, 6)) 

    # Posição das barras
    r = np.arange(len(tecnologias))
    r1 = r - barWidth
    r2 = r
    r3 = r + barWidth
    r4 = r + 2*barWidth

    # Plotagem das barras
    ax.bar(r1, custo_pem, color=cores[0], width=barWidth, label= eletrolisadores[0]) 
    ax.bar(r2, custo_alk, color=cores[1], width=barWidth, label=eletrolisadores[1]) 
    ax.bar(r3, custo_soec, color=cores[2], width=barWidth, label=eletrolisadores[2]) 
    ax.bar(r4, custo_aem, color=cores[3],width=barWidth, label=eletrolisadores[3]) 

    # Personalização do gráfico
    ax.set_xlabel('Tecnologia', fontweight='bold', fontsize=15) 
    ax.set_ylabel('LCOH ($/kg)', fontweight='bold', fontsize=15) 
    ax.set_xticks(r)
    ax.set_xticklabels(tecnologias)
    ax.legend()

    plt.title('LCOH por Tecnologia de Eletrolisador e Fonte de Energia - 2030', fontsize=16, fontweight='bold')

    ax.grid(True, linestyle='--')
    
    ax.set_yticks(np.arange(0, max(max(custo_pem), max(custo_alk), max(custo_soec), max(custo_aem)) + 1.25, 1.25))

    # Função para fechar o gráfico ao pressionar 'q'
    def press(event):
        if event.key == 'q' or 'Q':
            plt.close()

    # Conectar a função de pressionar tecla ao gráfico
    plt.connect('key_press_event', press)

    # Mostrar gráfico
    plt.show() 

def write_txt(lcoh_pem_pv, lcoh_pem_WindOnshore, lcoh_pem_WindOffshore, lcoh_pem_nuclear,
              lcoh_alk_pv, lcoh_alk_WindOnshore, lcoh_alk_WindOffshore, lcoh_alk_nuclear,
              lcoh_soec_pv, lcoh_soec_WindOnshore, lcoh_soec_WindOffshore, lcoh_soec_nuclear,
              lcoh_aem_pv, lcoh_aem_WindOnshore, lcoh_aem_WindOffshore, lcoh_aem_nuclear):
    
    lcoh_dict = {
        'Solar PEM': lcoh_pem_pv,
        'WindOnshore PEM': lcoh_pem_WindOnshore,
        'WindOffshore PEM': lcoh_pem_WindOffshore,
        'Nuclear PEM': lcoh_pem_nuclear,
        'Solar AWE': lcoh_alk_pv,
        'WindOnshore AWE': lcoh_alk_WindOnshore,
        'WindOffshore AWE': lcoh_alk_WindOffshore,
        'Nuclear AWE': lcoh_alk_nuclear,
        'Solar SOEC': lcoh_soec_pv,
        'WindOnshore SOEC': lcoh_soec_WindOnshore,
        'WindOffshore SOEC': lcoh_soec_WindOffshore,
        'Nuclear SOEC': lcoh_soec_nuclear,
        'Solar AEM': lcoh_aem_pv,
        'WindOnshore AEM': lcoh_aem_WindOnshore,
        'WindOffshore AEM': lcoh_aem_WindOffshore,
        'Nuclear AEM': lcoh_aem_nuclear
    }

    with open('valores_lcoh.txt', 'w') as arquivo:
        i = 0
        for chave, valor in lcoh_dict.items():
            i += 1
            if i % 4 == 0:
                arquivo.write(f'{chave}: {valor:.2f} $/kg\n')
                arquivo.write('\n')
            else:
                arquivo.write(f'{chave}: {valor:.2f} $/kg\n')

    # Restante do código para escrever no arquivo


def main():
    e = Energia('a',0,0,0)
    t = e.t
    wacc = 8/100
    ########### Energia ################
    ### custos energias
    # Solar
    capex_sol = 3200*0.2 # USD/kW
    opex_sol = 0.02 # %
    cf_sol = 0.25

    # Wind Onshore
    capex_WindOnshore = 4500*0.2 # USD/kW - EPE
    opex_WindOnshore = 90/capex_WindOnshore # %/ano 0.2
    cf_WindOnshore = 0.4
    
    # wind offshore
    capex_WindOffshore = 12250*0.2 # USD/kW - EPE
    opex_WindOffshore = 0.04 # %
    cf_WindOffshore = 0.47
    
    # Nuclear
    capex_nuclear = 24500
    opex_nuclear = 0.013
    cf_nuclear = 1 

    # Energias
    solar = Energia('Solar', capex_sol, opex_sol, cf_sol)
    WindOnshore =Energia('WindOnshore', capex_WindOnshore, opex_WindOnshore, cf_WindOnshore)
    WindOffshore = Energia('WindOffshore', capex_WindOffshore, opex_WindOffshore, cf_WindOffshore)
    nuclear = Energia('Nuclear', capex_nuclear, opex_nuclear, cf_nuclear)

    ######### Eletrolisador ############
    ### Custos e parametros
    # PEM parametros
    capex_pem = 1000 # USD/kW
    opex_pem = 0.02 # %

    pot_pem = 988.68 # kW
    h2_pem = 17.976 # kg/h 
    FlowRate_pem = 200 # Nm3/h
    ef_pem = 0
    pem_energy_prod1kg = 55*1.01 # kWh/kg
    lifetime_pem = 80000 # h IEA
    bar_pem = 30

    # Alkalino parametros
    capex_alk = 650 # $/kW
    opex_alk = 0.02
    
    pot_alk = 1000 # kW
    FlowRate_alk = 200
    h2_alk = FlowRate_alk*0.08988 # kg/h  nao to usando pra nada pois calculamos por fora a energia para produzir 1kg
    ef_alk = 0
    alk_energy_prod1kg = (4.8/0.08988) + (4.8/0.08988)*0.1 # kWh/kg
    lifetime_alk = 80000 # h  Datasheet
    bar_alk = 30

    # Parametros SOEC
    capex_soec = 1800 # $/kW
    opex_soec = 0.02 # %

    pot_soec = 1100 # kW
    h2_soec = 24 # kg/h nao to usando pra nada pois calculamos por fora a energia para produzir 1kg
    FlowRate_soec = h2_soec/0.08988
    soec_energy_prod1kg = 39.4 + 39.4*0.1 # kWh/kg
    soec_ef = 0
    lifetime_soec = 50000 # h IEA
    bar_soec = 1

    # Parametros AEM
    capex_aem = (469.13+258.02) # $/kW
    nao_utilizado_opex = 1

    pot_aem = 1000 # kW
    FlowRate_aem = 210 # Nm3/h
    h2_aem = 453/24 # kg/h -> So esta sendo utilizado para calcular o opex, pois energia para produzir 1kg eh calculada por fora
    aem_energy_prod1kg = 53.3 # kWh/kg
    aem_ef = 0.625 # LHV
    lifetime_aem = 20000 # h - (M. KIM et. al, 2024) - AEM Techno-economic
    bar_aem = 30

    # Eletrolisadores
    pem = Eletrolisador('PEM-HyLYZER-200', pot_pem, h2_pem, capex_pem, opex_pem, ef_pem, lifetime_pem, FlowRate_pem, bar_pem)
    alk = Eletrolisador('Alkaline P200', pot_alk, h2_alk, capex_alk, opex_alk, ef_alk, lifetime_alk, FlowRate_alk, bar_alk)
    soec = Eletrolisador('SOEC FuelCell Energy', pot_soec, h2_soec, capex_soec, opex_soec, soec_ef, lifetime_soec, FlowRate_soec, bar_soec)
    aem = Eletrolisador('AEM Nexus 1000',pot_aem, h2_aem, capex_aem, nao_utilizado_opex, aem_ef, lifetime_aem, FlowRate_aem, bar_aem)

    ############# Calculos #################
    ### Total capex opex energias, que é parecido porque as plantas tem apriximadamente 1 MW
    # Energias Capex e Opex PEM
    tot_capex_solar_pem, tot_opex_solar_pem, ciclo_pem_solar = solar.energy_total_capex_opex(pem.pot,cf_sol, pem.name, lifetime_pem) # Entro com a potencia pois a potencia instalada é com base na potencia do eletrolisador e do cf
    tot_capex_WindOnshore_pem, tot_opex_WindOnshore_pem, ciclo_pem_WindOnshore = WindOnshore.energy_total_capex_opex(pem.pot, cf_WindOnshore, pem.name, lifetime_pem)
    tot_capex_WindOffshore_pem, tot_opex_WindOffshore_pem, ciclo_pem_WindOffshore = WindOffshore.energy_total_capex_opex(pem.pot, cf_WindOffshore, pem.name, lifetime_pem)
    tot_capex_nuclear_pem, tot_opex_nuclear_pem, ciclo_pem_nuclear = nuclear.energy_total_capex_opex(pem.pot, cf_nuclear, pem.name, lifetime_pem)

    # Energia Capex e Opex AWE
    tot_capex_solar_alk, tot_opex_solar_alk, ciclo_alk_solar = solar.energy_total_capex_opex(pot_alk, cf_sol, alk.name, lifetime_alk)
    tot_capex_WindOnshore_alk, tot_opex_WindOnshore_alk, ciclo_alk_WindOnshore = WindOnshore.energy_total_capex_opex(pot_alk, cf_WindOnshore, alk.name, lifetime_alk)
    tot_capex_WindOffshore_alk, tot_opex_WindOffshore_alk, ciclo_alk_WindOffshore = WindOffshore.energy_total_capex_opex(pot_alk, cf_WindOffshore, alk.name, lifetime_alk)
    tot_capex_nuclear_alk, tot_opex_nuclear_alk, ciclo_alk_nuclear = nuclear.energy_total_capex_opex(alk.pot, cf_nuclear, alk.name, lifetime_alk)

    # Energia Capex e Opex SEOC
    tot_capex_solar_soec, tot_opex_solar_soec, ciclo_soec_solar = solar.energy_total_capex_opex(soec.pot, cf_sol, soec.name, lifetime_soec)
    tot_capex_WindOnshore_soec, tot_opex_WindOnshore_soec, ciclo_soec_WindOnshore = WindOnshore.energy_total_capex_opex(soec.pot, cf_WindOnshore, soec.name, lifetime_soec)
    tot_capex_WindOffshore_soec, tot_opex_WindOffshore_soec, ciclo_soec_WindOffshore = WindOffshore.energy_total_capex_opex(soec.pot, cf_WindOffshore, soec.name, lifetime_soec)
    tot_capex_nuclear_soec, tot_opex_nuclear_soec, ciclo_soec_nuclear = nuclear.energy_total_capex_opex(soec.pot, cf_nuclear, soec.name, lifetime_soec)

    # Energia capex opex AEM
    tot_capex_solar_aem, tot_opex_solar_aem, ciclo_aem_solar = solar.energy_total_capex_opex(aem.pot, cf_sol, aem.name, lifetime_aem)    
    tot_capex_WindOnshore_aem, tot_opex_WindOnshore_aem, ciclo_aem_WindOnshore = WindOnshore.energy_total_capex_opex(aem.pot, cf_WindOnshore, aem.name, lifetime_aem)
    tot_capex_WindOffshore_aem, tot_opex_WindOffshore_aem, ciclo_aem_WindOffshore = WindOffshore.energy_total_capex_opex(aem.pot, cf_WindOffshore, aem.name, lifetime_aem)
    tot_capex_nuclear_aem, tot_opex_nuclear_aem, ciclo_aem_nuclear = nuclear.energy_total_capex_opex(aem.pot, cf_nuclear, aem.name, lifetime_aem)

    #########
    ####### Eletrolisador Capex e opex ##### Busco na classe o valor do meu capex e opex total
    tot_cap_pem, tot_op_pem = pem.electrolyser_capex_opex()
    tot_cap_alk, tot_op_alk = alk.electrolyser_capex_opex()
    tot_cap_soec, tot_op_soec = soec.electrolyser_capex_opex()
    tot_cap_aem, tot_op_aem = aem.electrolyser_capex_opex()

    ## producao de H2
    # PEM Energias
    wh2_pem_solar = wh2(pem.pot, pem_energy_prod1kg, pem.name, cf_sol)
    wh2_pem_WindOnshore = wh2(pem.pot, pem_energy_prod1kg, pem.name, cf_WindOnshore)
    wh2_pem_WindOffshore = wh2(pem.pot, pem_energy_prod1kg, pem.name, cf_WindOffshore)
    wh2_pem_nuclear = wh2(pem.pot, pem_energy_prod1kg, pem.name, cf_nuclear)

    # Alkalino producao anual h2
    wh2_alk_solar = wh2(alk.pot, alk_energy_prod1kg, alk.name, cf_sol)
    wh2_alk_WindOnshore = wh2(alk.pot, alk_energy_prod1kg, alk.name, cf_WindOnshore)
    wh2_alk_WindOffShore = wh2(alk.pot, alk_energy_prod1kg, alk.name, cf_WindOffshore)
    wh2_alk_nuclear = wh2(alk.pot, alk_energy_prod1kg, alk.name, cf_nuclear)

    # SOEC producao anual h2
    wh2_soec_solar = wh2(soec.pot, soec_energy_prod1kg, soec.name,cf_sol)
    wh2_soec_WindOnshore = wh2(soec.pot, soec_energy_prod1kg, soec.name, cf_WindOnshore)
    wh2_soec_WindOffshore = wh2(soec.pot, soec_energy_prod1kg, soec.name, cf_WindOffshore)
    wh2_soec_nuclear = wh2(soec.pot, soec_energy_prod1kg, soec.name, cf_nuclear)

    # AEM producao anual h2
    wh2_aem_solar = wh2(aem.pot, aem_energy_prod1kg, aem.name, cf_sol)
    wh2_aem_WindOnshore = wh2(aem.pot, aem_energy_prod1kg, aem.name, cf_WindOnshore)
    wh2_aem_WindOffshore = wh2(aem.pot, aem_energy_prod1kg, aem.name, cf_WindOffshore)
    wh2_aem_nuclear = wh2(aem.pot, aem_energy_prod1kg, aem.name, cf_nuclear)


    ### Calculo lcoh
    # Pem
    lcoh_pem_pv = lcoh(tot_cap_pem, tot_op_pem, tot_capex_solar_pem, tot_opex_solar_pem, ciclo_pem_solar, wh2_pem_solar, t, pem.name, solar.name, wacc)
    lcoh_pem_WindOnshore = lcoh(tot_cap_pem, tot_op_pem, tot_capex_WindOnshore_pem, tot_opex_WindOnshore_pem, ciclo_pem_WindOnshore, wh2_pem_WindOnshore, t, pem.name, WindOnshore.name, wacc)
    lcoh_pem_WindOffshore = lcoh(tot_cap_pem, tot_op_pem, tot_capex_WindOffshore_pem, tot_opex_WindOffshore_pem, ciclo_pem_WindOffshore, wh2_pem_WindOffshore, t, pem.name, WindOffshore.name, wacc)
    lcoh_pem_nuclear = lcoh(tot_cap_pem, tot_op_pem, tot_capex_nuclear_pem, tot_opex_nuclear_pem, ciclo_pem_nuclear, wh2_pem_nuclear, t, pem.name, nuclear.name, wacc)

    # Alkalino
    lcoh_alk_pv = lcoh(tot_cap_alk, tot_op_alk, tot_capex_solar_alk, tot_opex_solar_alk, ciclo_alk_solar, wh2_alk_solar, t, alk.name, solar.name, wacc)
    lcoh_alk_WindOnshore = lcoh(tot_cap_alk, tot_op_alk, tot_capex_WindOnshore_alk, tot_opex_WindOnshore_alk, ciclo_alk_WindOnshore, wh2_alk_WindOnshore,t, alk.name, WindOnshore.name, wacc)
    lcoh_alk_WindOffshore = lcoh(tot_cap_alk, tot_op_alk, tot_capex_WindOffshore_alk, tot_opex_WindOffshore_alk, ciclo_alk_WindOffshore, wh2_alk_WindOffShore,t, alk.name, WindOffshore.name, wacc)
    lcoh_alk_nuclear = lcoh(tot_cap_alk, tot_op_alk, tot_capex_nuclear_alk, tot_opex_nuclear_alk, ciclo_alk_nuclear, wh2_alk_nuclear,t, alk.name, nuclear.name, wacc)

    # SOEC
    lcoh_soec_pv = lcoh(tot_cap_soec, tot_op_soec, tot_capex_solar_soec, tot_opex_solar_soec, ciclo_soec_solar, wh2_soec_solar, t, soec.name, solar.name, wacc)
    lcoh_soec_WindOnshore = lcoh(tot_cap_soec, tot_op_soec, tot_capex_WindOnshore_soec, tot_opex_WindOnshore_soec, ciclo_soec_WindOnshore, wh2_soec_WindOnshore, t, soec.name, WindOnshore.name, wacc)
    lcoh_soec_WindOffshore = lcoh(tot_cap_soec, tot_op_soec, tot_capex_WindOffshore_soec, tot_opex_WindOffshore_soec, ciclo_soec_WindOffshore, wh2_soec_WindOffshore, t, soec.name, WindOffshore.name, wacc)
    lcoh_soec_nuclear = lcoh(tot_cap_soec, tot_op_soec, tot_capex_nuclear_soec, tot_opex_nuclear_soec, ciclo_soec_nuclear, wh2_soec_nuclear, t, soec.name, nuclear.name, wacc)
    
    # AEM
    lcoh_aem_pv = lcoh(tot_cap_aem, tot_op_aem, tot_capex_solar_aem, tot_opex_solar_aem, ciclo_aem_solar, wh2_aem_solar, t, aem.name, solar.name, wacc)
    lcoh_aem_WindOnshore = lcoh(tot_cap_aem, tot_op_aem, tot_capex_WindOnshore_aem, tot_opex_WindOnshore_aem, ciclo_aem_WindOnshore, wh2_aem_WindOnshore, t, aem.name, WindOnshore.name, wacc)
    lcoh_aem_WindOffshore = lcoh(tot_cap_aem, tot_op_aem, tot_capex_WindOffshore_aem, tot_opex_WindOffshore_aem, ciclo_aem_WindOffshore, wh2_aem_WindOffshore, t, aem.name, WindOffshore.name, wacc)
    lcoh_aem_nuclear = lcoh(tot_cap_aem, tot_op_aem, tot_capex_nuclear_aem, tot_opex_nuclear_aem, ciclo_aem_nuclear, wh2_aem_nuclear, t, aem.name, nuclear.name, wacc)


    print('\n')
    print(f'Solar PEM LCOH = {lcoh_pem_pv:.2f} $/kg')
    print(f'WindOnshore PEM LCOH = {lcoh_pem_WindOnshore:.2f} $/kg')
    print(f'WindOffshore PEM LCOH = {lcoh_pem_WindOffshore:.2f} $/kg')
    print(f'Nuclear PEM LCOH = {lcoh_pem_nuclear:.2f} $/kg')
    print('\n')
    print(f'Solar AWE LCOH = {lcoh_alk_pv:.2f} $/kg')
    print(f'WindOnshore AWE LCOH = {lcoh_alk_WindOnshore:.2f} $/kg')
    print(f'WindOffshore AWE LCOH = {lcoh_alk_WindOffshore:.2f} $/kg')
    print(f'Nuclear AWE LCOH = {lcoh_alk_nuclear:.2f} $/kg')
    print('\n')
    print(f'Solar SOEC LCOH = {lcoh_soec_pv:.2f} $/kg')
    print(f'WindOnshore SOEC LCOH = {lcoh_soec_WindOnshore:.2f} $/kg')
    print(f'WindOffshore SOEC LCOH = {lcoh_soec_WindOffshore:.2f} $/kg')
    print(f'Nuclear SOEC LCOH = {lcoh_soec_nuclear:.2f} $/kg')
    print('\n')
    print(f'Solar AEM LCOH = {lcoh_aem_pv:.2f} $/kg')
    print(f'WindOnshore AEM LCOH = {lcoh_aem_WindOnshore:.2f} $/kg')
    print(f'WindOffshore AEM LCOH = {lcoh_aem_WindOffshore:.2f} $/kg')
    print(f'Nuclear AEM LCOH = {lcoh_aem_nuclear:.2f} $/kg')    


    plot_graph(lcoh_pem_pv, lcoh_pem_WindOnshore, lcoh_pem_WindOffshore, lcoh_pem_nuclear, lcoh_alk_pv, lcoh_alk_WindOnshore,lcoh_alk_WindOffshore, lcoh_alk_nuclear, 
               lcoh_soec_pv, lcoh_soec_WindOnshore, lcoh_soec_WindOffshore, lcoh_soec_nuclear, lcoh_aem_pv, lcoh_aem_WindOnshore, lcoh_aem_WindOffshore, lcoh_aem_nuclear)
    
    write_txt(lcoh_pem_pv, lcoh_pem_WindOnshore, lcoh_pem_WindOffshore, lcoh_pem_nuclear,
          lcoh_alk_pv, lcoh_alk_WindOnshore, lcoh_alk_WindOffshore, lcoh_alk_nuclear,
          lcoh_soec_pv, lcoh_soec_WindOnshore, lcoh_soec_WindOffshore, lcoh_soec_nuclear,
          lcoh_aem_pv, lcoh_aem_WindOnshore, lcoh_aem_WindOffshore, lcoh_aem_nuclear)

if __name__ == '__main__':
    # os.system('cls' if os.name == 'nt' else 'clear')
    main()