import numpy as np 
import matplotlib.pyplot as plt 

def plot_graph():
    # Dados
    eletrolisadores = ['PEM', 'ALK', 'SOEC', 'AEM']
    tecnologias = ['Solar', 'Onshore', 'Eólica OffShore', 'Nuclear']
    custo_pem = [3.04, 5, 7.26, 23.78]
    custo_alk = [2.74, 5, 6.84, 22.87]
    custo_soec = [2.54,5, 5.56, 17.39]
    custo_aem = [1.99, 5, 6.41, 20.96]

    # Cores mais sóbrias
    #cores = ['#4B5320', '#1E90FF', '#505050', '#d62728']


    cores = [
        (34/255, 139/255, 34/255),  # Verde
        (138/255, 43/255, 226/255),  # Roxo
        (255/255, 69/255, 0/255),  # Azul claro
        (255/255, 200/255, 0/255)     # Alaranjado
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
    ax.bar(r4, custo_aem, color=cores[3], width=barWidth, label=eletrolisadores[3]) 


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

plot_graph()