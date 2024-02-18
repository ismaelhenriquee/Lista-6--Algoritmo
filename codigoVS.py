import pandas as pd
import math
from igraph import Graph, plot
import matplotlib.pyplot as plt
import cairo
import pygame
from Botão_classe import Botao

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

pygame.init()

LARGURA, ALTURA = 1200, 700

#Criando botoes
botao_comecar=Botao("Começar", 150, 64, 340, 275 )
botao_visualizar=Botao("Visualizar Grafo", 150, 64, 255, 380)
botao_pular=Botao("Pular Vizualização", 150, 64, 115, 220) #Volta para tela inicial após o player perder todas as vidas
botao_menu_voltar=Botao("Voltar Menu", 150, 64, 145, 275) #Opção de jogar novamente após o player vencer o jogo
botao_encerrar_programa=Botao("Encerrar programa", 150, 64, 330, 275)#Opção de fechar a tela após o player vencer o jogo

#Define o título da JANELA e estabelece a taxa de quadros por segundo.
pygame.display.set_caption("O resgate de Marcelinho")
JANELA = pygame.display.set_mode((LARGURA, ALTURA))
relogio = pygame.time.Clock()
FPS = 60


configuracao = {
    "Menu inicial": True,
    "Selecionar Semaforos": False,
    "Vizualisar":False,
    "Fim do programa":False,
    
}


def haversine(lat1, lon1, lat2, lon2):
    # Raio da Terra em km
    R = 6371.0
    
    # Conversão de graus para radianos
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Diferença das latitudes e longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance
def menor_caminho(grafo, semaforo_inicial, semaforo_final,dicionario_semaforos,mapeamento_ids,distancia_total=0,semaforos_vitados=[]):
    if semaforo_inicial == semaforo_final:
        return grafo,distancia_total
    semaforos_vitados.append(semaforo_inicial)
    menor_distancia = float('inf')
    semaforo_mais_proximo = None
    for outro_semaforo_num, outro_semaforo_data in dicionario_semaforos.items():
        if outro_semaforo_num not in semaforos_vitados:
            distancia = haversine(dicionario_semaforos[semaforo_inicial][1], dicionario_semaforos[semaforo_inicial][2], 
                                  outro_semaforo_data[1], outro_semaforo_data[2])
               
            if distancia < menor_distancia:
                menor_distancia = distancia
                semaforo_mais_proximo = outro_semaforo_num
    grafo.vs[semaforo_mais_proximo-1]["color"] = "blue"
    grafo.add_edge(mapeamento_ids[semaforo_inicial], mapeamento_ids[semaforo_mais_proximo], weight=menor_distancia)
    distancia_total += menor_distancia
    return menor_caminho(grafo, semaforo_mais_proximo, semaforo_final,dicionario_semaforos,mapeamento_ids,distancia_total,semaforos_vitados)
def gerar_gafro(semaforo_inicial,semaforo_final):
    # Carregar os dados dos semáforos
    df = pd.read_csv('semaforos.csv', nrows=100)

    dicionario_semaforos = {}

    for index, row in df.iterrows():
        numero_semaforo = int(row[0])  
        nome_semaforo = row[0]  # Assumindo que o nome do semáforo está na segunda coluna do CSV
        latitude = -(row[4] )
        longitude = row[5]
        nome_bairro=row[3]  
        
        dicionario_semaforos[numero_semaforo] = (nome_semaforo, latitude, longitude,nome_bairro)

    # Criar um grafo representado pelo igraph
    grafo = Graph()

    # Adicionar vértices ao grafo e mapear os identificadores dos vértices para números de 0 a n-1
    mapeamento_ids = {}

    for i, (semaforo_num, (nome, latitude, longitude,nome_bairro)) in enumerate(dicionario_semaforos.items()):
        grafo.add_vertex(name=nome, latitude=latitude, longitude=longitude, bairro=nome_bairro)
        grafo.vs["color"] = "white"

        mapeamento_ids[semaforo_num] = i
        
    # Exibir informações sobre o grafo
    grafo,distancia=menor_caminho(grafo, semaforo_inicial,semaforo_final,dicionario_semaforos,mapeamento_ids)  
    print("Número de vértices:", grafo.vcount())
    print("Número de arestas:", grafo.ecount())
    print("Grafo:", grafo)
    grafo.vs[semaforo_inicial-1]["color"] = "green"
    grafo.vs[semaforo_final-1]["color"] = "red"

    vertex_labels = [f"\n{nome}\n{bairro}" for nome, bairro in zip(grafo.vs['name'], grafo.vs['bairro'])]
    layout = [(v['longitude'], v['latitude']) for v in grafo.vs]
    plot(grafo, layout=layout,  bbox=(1200, 700), margin=50, vertex_label=vertex_labels, vertex_label_size=10 , vertex_size=16,  vertex_color=grafo.vs['color'], edge_width=grafo.es['weight'], edge_color="black", vertex_label_dist=-1).save("social_netwoork.png")
    return distancia

# Adicionar arestas (com as menores distâncias encontradas)
def Menu():
    
    global configuracao
    background_menu = pygame.image.load("./download (2).jpg")
    tamanho_background_menu = pygame.transform.scale(background_menu,(1200, 700))
    menu_final_rodando = True
   
    while menu_final_rodando:
        pygame.time.delay(50)
        relogio.tick(FPS)
        JANELA.fill(PRETO) 
        if botao_comecar.draw():
            menu_final_rodando = False
            configuracao["Menu inicial"]=False
            configuracao["Selecionar Semaforos"]= True
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  
                menu_final_rodando = False
                pygame.quit()
                

        
        pygame.display.update()


def Selecionar():
    
    global configuracao
    background_selecionar = pygame.image.load("./download (2).jpg")
    tamanho_background_selecionar = pygame.transform.scale(background_selecionar,(1200, 700))
    menu_final_rodando = True
    
    while menu_final_rodando:
        JANELA.blit(tamanho_background_selecionar, (0, 0))
        pygame.time.delay(50)
        relogio.tick(FPS)
        
        if botao_visualizar.draw():
            menu_final_rodando = False
            configuracao["Selecionar Semaforos"]= False
            configuracao["Vizualisar"]=True
            distancia_total=gerar_gafro(1,8)
            

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  
                menu_final_rodando = False
                pygame.quit()
                

        pygame.display.update()

def Vizualizar():
    
    global configuracao
    background_grafo = pygame.image.load("./social_netwoork.png")
    tamanho_background_grafo = pygame.transform.scale(background_grafo,(1200, 700))
    menu_final_rodando = True
    
    while menu_final_rodando:
        
        JANELA.blit(tamanho_background_grafo, (0, 0))
        pygame.time.delay(50)
        relogio.tick(FPS)
        
        if botao_menu_voltar.draw():
            menu_final_rodando = False
            configuracao["Vizualisar"]=False
            configuracao["Menu inicial"]=True

        if botao_encerrar_programa.draw():
            menu_final_rodando = False
            configuracao["Vizualisar"]=False
            configuracao["Fim do programa"]=True
           
            

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  
                menu_final_rodando = False
                pygame.quit()
                

        pygame.display.update()

jogo_rodando = True
#Navega pelos menus do jogo
while jogo_rodando:

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    JANELA.fill(PRETO) #Limpa a tela
    if configuracao["Menu inicial"]==True:
        Menu()
    elif configuracao["Vizualisar"]==True:
        Vizualizar()
    elif configuracao["Selecionar Semaforos"]==True:
        Selecionar()
    elif configuracao["Fim do programa"]==True:
        jogo_rodando = False
    

    pygame.display.update()

pygame.quit()









