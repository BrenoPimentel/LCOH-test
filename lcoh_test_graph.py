import numpy as np 
import matplotlib.pyplot as plt 

class Eletrolisador:
    # Define as caracteristicas do eletrolisadr
    def __init__(self, name, pot, h2, capex, opex, efficiency):
        self.name = name
        self.pot = pot
        self.h2 = h2
        self.capex = capex
        self.opex = opex
        self.ef = efficiency
        
    # Energia para produzir 1kg de hidrogenio
    def energy_prod_1kg(self):
        energy_1kg = self.pot/self.h2
        tot_energy = energy_1kg+energy_1kg*0.1
        return tot_energy
    
    # Total capex e opex do eletrolisador com base na potencia
    # Calcula o capex e opex total, com base na potencia multiplicada pelo preco por kW
    def electrolyser_capex_opex(self):
        if 'AEM' in self.name.upper():
            capex = self.capex
            opex = self.opex
            capex_total = capex*self.pot*0.66
            # Material - 2.5% | Labor - 5.0%   Deionized water - 0.01$/kg | Electrolyte (KOH) 2.75$/kg | Steam 0.01$/kg
            opex_total = (0.025+0.05)*capex_total + (0.01 + 2.75 + 0.01)*(self.h2)
        else:  
            capex = self.capex
            opex = self.opex
            capex_total = capex*self.pot*0.66
            opex_total = opex*capex_total
        
        print('=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
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

    # Total capex e opex da fonte energia com base na potencia do eletrolisador
    # As potencias dos eletrolisadores estao proximas de 1 MW entao o capex e o opex sao similares
    # Essa formula multiplica o capex pelo total de energia que minha planta deve ter com base no fator de capacidade
    # Se meu eletrolisador tem 1MW e cf_sol 0.25, minha planta deve ter 1MW/0.25 = 4 WM
    def energy_total_capex_opex(self,pot,cf, nome):
        tot_capex_energy = self.capex*(pot/cf)
        tot_opex_energy = self.opex*tot_capex_energy
        print('---------------------------------')
        print(f'{self.name} - {nome} Capex total {tot_capex_energy * 10**-6:.2f} M$')
        print(f'{self.name} - {nome} Opex total {tot_opex_energy*10**-6:.2f} M$')
        print('---------------------------------')
        return tot_capex_energy, tot_opex_energy # Ta funcionando


# Calculo do Levelised Cosf Of Hydrogen
def lcoh(tot_capex_el, tot_opex_el, tot_capex_energy, tot_opex_energy, wh2, t, nome, energia_nome, wacc):
    lcoh_h2 = ((tot_capex_el+tot_capex_energy)+(tot_opex_el+tot_opex_energy)*t)/(wh2*t)
    capex_total = tot_capex_el+tot_capex_energy
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

# Calcula a producao anual de energia em kg
def wh2(pot, energy1kg, nome):
    aep = pot*24*365
    wh2 = aep/energy1kg
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print(f'{nome} WH2: {wh2:.2f} kg')
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    return wh2

def plot_graph(lcoh_pem_pv, lcoh_pem_wind, lcoh_pem_nuclear, lcoh_alk_pv, lcoh_alk_wind, lcoh_alk_nuclear, 
               lcoh_soec_pv, lcoh_soec_wind, lcoh_soec_nuclear, lcoh_aem_pv, lcoh_aem_wind, lcoh_aem_nuclear):

    # Dados
    eletrolisadores = ['PEM', 'ALK', 'SOEC', 'AEM']
    tecnologias = ['Solar', 'Eólica OffShore', 'Nuclear']
    custo_pem = [lcoh_pem_pv, lcoh_pem_wind, lcoh_pem_nuclear]
    custo_alk = [lcoh_alk_pv, lcoh_alk_wind, lcoh_alk_nuclear]
    custo_soec = [lcoh_soec_pv, lcoh_soec_wind, lcoh_soec_nuclear]
    custo_aem = [lcoh_aem_pv, lcoh_aem_wind, lcoh_aem_nuclear]

    # Cores mais sóbrias
    cores = ['#333333', '#666666', '#999999', '#CCCCCC']
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
    ax.bar(r3, custo_soec, color=cores[2], width=barWidth, label=eletrolisadores[1]) 
    ax.bar(r4, custo_aem, color=cores[3], width=barWidth, label=eletrolisadores[2]) 

    # Personalização do gráfico
    ax.set_xlabel('Tecnologia', fontweight='bold', fontsize=15) 
    ax.set_ylabel('LCOH ($/kg)', fontweight='bold', fontsize=15) 
    ax.set_xticks(r)
    ax.set_xticklabels(tecnologias)
    ax.legend()

    ax.grid(True, linestyle='--')
    
    # Função para fechar o gráfico ao pressionar 'q'
    def press(event):
        if event.key == 'q' or 'Q':
            plt.close()

    # Conectar a função de pressionar tecla ao gráfico
    plt.connect('key_press_event', press)

    # Mostrar gráfico
    plt.show() 

def main():
    t = 20
    wacc = 8/100
    ########### Energia ################
    ### custos energias
    # Solar
    capex_sol = 3200*0.2 # USD/kW
    opex_sol = 0.02 # %
    cf_sol = 0.25 
    
    # wind offshore
    capex_wind = 12250*0.2 # USD/kW
    opex_wind = 0.04 # %
    cf_wind = 0.4
    
    # Nuclear
    capex_nuclear = 24500
    opex_nuclear = 0.02
    cf_nuclear = 1 



    # Energias
    solar = Energia('Solar', capex_sol, opex_sol, cf_sol)
    wind = Energia('wind', capex_wind, opex_wind, cf_wind)
    nuclear = Energia('Nuclear', capex_nuclear, opex_nuclear, cf_nuclear)

    ######### Eletrolisador ############
    ### Custos e parametros
    # PEM parametros
    capex_pem = 1000 # USD/kW
    opex_pem = 0.02 # %

    pot_pem = 988.68 # kW
    h2_pem = 17.976 # kg/h 
    ef_pem = 0

    # Alkalino parametros
    capex_alk = 650 # $/kW
    opex_alk = 0.02
    
    pot_alk = 1000 # kW
    h2_alk = 200*0.08988 # kg/h # nao to usando pra nada
    ef_alk = 0
    alk_energy_prod1kg = (4.8/0.08988) + (4.8/0.08988)*0.1 # kWh/kg
    # capex_alk = 1500
    # opex_alk = 0.02
    # pot_alk = 17.5
    # h2_alk = 3357

    # Parametros SOEC
    capex_soec = 1800
    opex_soec = 0.02

    pot_soec = 1100 # kW
    h2_soec = 24 # kg/h # nao to usando pra nada
    soec_energy_prod1kg = 39.4 + 39.4*0.1 # kWh/kg
    soec_ef = 0

    # Parametros AEM
    capex_aem = (469.13+258.02) # $/kW
    nao_utilizado_opex = 1

    pot_aem = 1000 # kW
    h2_aem = 453/24 # kg/h
    aem_energy_prod1kg = 53.3 # kWh/kg
    aem_ef = 0.625 

    # Eletrolisadores
    pem = Eletrolisador('PEM-HyLYZER-200', pot_pem, h2_pem, capex_pem, opex_pem, ef_pem)
    alk = Eletrolisador('Alkaline P200', pot_alk, h2_alk, capex_alk, opex_alk, ef_alk)
    soec = Eletrolisador('SOEC FuelCell Energy', pot_soec, h2_soec, capex_soec, opex_soec, soec_ef)
    aem = Eletrolisador('AEM Nexus 1000',pot_aem, h2_aem, capex_aem, nao_utilizado_opex, aem_ef)

    ############# Calculos #################
    ### Total capex opex energias, que é parecido porque as plantas tem apriximadamente 1 MW
    # Energias Capex e Opex PEM
    tot_capex_solar_pem, tot_opex_solar_pem = solar.energy_total_capex_opex(pem.pot,cf_sol, pem.name) # Entro com a potencia pois a potencia instalada é com base na potencia do eletrolisador e do cf
    tot_capex_wind_pem, tot_opex_wind_pem = wind.energy_total_capex_opex(pem.pot, cf_wind, pem.name)
    tot_capex_nuclear_pem, tot_opex_nuclear_pem = nuclear.energy_total_capex_opex(pem.pot, cf_nuclear, pem.name)

    # Energia Capex e Opex AWE
    tot_capex_solar_alk, tot_opex_solar_alk = solar.energy_total_capex_opex(pot_alk, cf_sol, alk.name)
    tot_capex_wind_alk, tot_opex_wind_alk = wind.energy_total_capex_opex(pot_alk, cf_wind, alk.name)
    tot_capex_nuclear_alk, tot_opex_nuclear_alk = nuclear.energy_total_capex_opex(alk.pot, cf_nuclear, alk.name)

    # Energia Capex e Opex SEOC
    tot_capex_solar_soec, tot_opex_solar_soec = solar.energy_total_capex_opex(soec.pot, cf_sol, soec.name)
    tot_capex_wind_soec, tot_opex_wind_soec = wind.energy_total_capex_opex(soec.pot, cf_wind, soec.name)
    tot_capex_nuclear_soec, tot_opex_nuclear_soec = nuclear.energy_total_capex_opex(soec.pot, cf_nuclear, soec.name)

    # Energia capex opex AEM
    tot_capex_solar_aem, tot_opex_solar_aem = solar.energy_total_capex_opex(aem.pot, cf_sol, aem.name)    
    tot_capex_wind_aem, tot_opex_wind_aem = wind.energy_total_capex_opex(aem.pot, cf_wind, aem.name)
    tot_capex_nuclear_aem, tot_opex_nuclear_aem = nuclear.energy_total_capex_opex(aem.pot, cf_nuclear, aem.name)

    #########
    ####### Eletrolisador Capex e opex ##### Busco na classe o valor do meu capex e opex total
    tot_cap_pem, tot_op_pem = pem.electrolyser_capex_opex()
    tot_cap_alk, tot_op_alk = alk.electrolyser_capex_opex()
    tot_cap_soec, tot_op_soec = soec.electrolyser_capex_opex()
    tot_cap_aem, tot_op_aem = aem.electrolyser_capex_opex()

    ## producao de H2
    wh2_pem = wh2(pem.pot, pem.energy_prod_1kg(), pem.name)
    wh2_alk = wh2(alk.pot, alk_energy_prod1kg, alk.name)
    wh2_soec = wh2(soec.pot, soec_energy_prod1kg, soec.name)
    wh2_aem = wh2(aem.pot, aem_energy_prod1kg, aem.name)


    ### Calculo lcoh
    # Pem
    lcoh_pem_pv = lcoh(tot_cap_pem, tot_op_pem, tot_capex_solar_pem, tot_opex_solar_pem, wh2_pem, t, pem.name, solar.name, wacc)
    lcoh_pem_wind = lcoh(tot_cap_pem, tot_op_pem, tot_capex_wind_pem, tot_opex_wind_pem, wh2_pem, t, pem.name, wind.name, wacc)
    lcoh_pem_nuclear = lcoh(tot_cap_pem, tot_op_pem, tot_capex_nuclear_pem, tot_opex_nuclear_pem, wh2_pem, t, pem.name, nuclear.name, wacc)


    # Alkalino
    lcoh_alk_pv = lcoh(tot_cap_alk, tot_op_alk, tot_capex_solar_alk, tot_opex_solar_alk, wh2_alk, t, alk.name, solar.name, wacc)
    lcoh_alk_wind = lcoh(tot_cap_alk, tot_op_alk, tot_capex_wind_alk, tot_opex_wind_alk, wh2_alk,t, alk.name, wind.name, wacc)
    lcoh_alk_nuclear = lcoh(tot_cap_alk, tot_op_alk, tot_capex_nuclear_alk, tot_opex_nuclear_alk, wh2_alk,t, alk.name, nuclear.name, wacc)

    # SOEC
    lcoh_soec_pv = lcoh(tot_cap_soec, tot_op_soec, tot_capex_solar_soec, tot_opex_solar_soec, wh2_soec, t, soec.name, solar.name, wacc)
    lcoh_soec_wind = lcoh(tot_cap_soec, tot_op_soec, tot_capex_wind_soec, tot_opex_wind_soec, wh2_soec, t, soec.name, wind.name, wacc)
    lcoh_soec_nuclear = lcoh(tot_cap_soec, tot_op_soec, tot_capex_nuclear_soec, tot_opex_nuclear_soec, wh2_soec, t, soec.name, nuclear.name, wacc)
    
    # AEM
    lcoh_aem_pv = lcoh(tot_cap_aem, tot_op_aem, tot_capex_solar_aem, tot_opex_solar_aem, wh2_soec, t, aem.name, solar.name, wacc)
    lcoh_aem_wind = lcoh(tot_cap_aem, tot_op_aem, tot_capex_wind_aem, tot_opex_wind_aem, wh2_aem, t, aem.name, wind.name, wacc)
    lcoh_aem_nuclear = lcoh(tot_cap_aem, tot_op_aem, tot_capex_nuclear_aem, tot_opex_nuclear_aem, wh2_aem, t, aem.name, nuclear.name, wacc)


    print('\n')
    print(f'Solar PEM LCOH = {lcoh_pem_pv:.2f} $/kg')
    print(f'wind PEM LCOH = {lcoh_pem_wind:.2f} $/kg')
    print(f'Nuclear PEM LCOH = {lcoh_pem_nuclear:.2f} $/kg')
    print('\n')
    print(f'Solar AWE LCOH = {lcoh_alk_pv:.2f} $/kg')
    print(f'wind AWE LCOH = {lcoh_alk_wind:.2f} $/kg')
    print(f'Nuclear AWE LCOH = {lcoh_alk_nuclear:.2f} $/kg')
    print('\n')
    print(f'Solar SOEC LCOH = {lcoh_soec_pv:.2f} $/kg')
    print(f'wind SOEC LCOH = {lcoh_soec_wind:.2f} $/kg')
    print(f'Nuclear SOEC LCOH = {lcoh_soec_nuclear:.2f} $/kg')
    print('\n')
    print(f'Solar AEM LCOH = {lcoh_aem_pv:.2f} $/kg')
    print(f'wind AEM LCOH = {lcoh_aem_wind:.2f} $/kg')
    print(f'Nuclear AEM LCOH = {lcoh_aem_nuclear:.2f} $/kg')    

    plot_graph(lcoh_pem_pv, lcoh_pem_wind, lcoh_pem_nuclear, lcoh_alk_pv, lcoh_alk_wind, lcoh_alk_nuclear, 
               lcoh_soec_pv, lcoh_soec_wind, lcoh_soec_nuclear, lcoh_aem_pv, lcoh_aem_wind, lcoh_aem_nuclear)
    
if __name__ == '__main__':
    main()