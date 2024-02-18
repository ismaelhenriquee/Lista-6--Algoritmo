import pandas as pd
import math
from igraph import Graph, plot
import cairo
import pygame
import sys
from Botão_classe import Botao

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
distancia_total=0

pygame.init()

LARGURA, ALTURA = 1200, 700
#informações para os inputs dos semáforos
base_font=pygame.font.Font(None, 32)
semaforo_inicial=''
semaforo_final=''
input_react_1=pygame.Rect(800, 480, 200, 30)
input_react_2=pygame.Rect(300, 480, 200, 30)
color_input_1=pygame.Color('black')
color_input_2=pygame.Color('black')

#Criando botoes para as telas
botao_comecar=Botao("Começar", 150, 64, 930, 600 )
botao_visualizar=Botao("Visualizar Grafo", 200, 64, 930, 600)
botao_menu_voltar=Botao("Voltar Menu", 200, 64, 70, 600) 
botao_encerrar_programa=Botao("Encerrar Programa", 250, 64, 930, 600)

#Define o título da JANELA e estabelece a taxa de quadros por segundo.
pygame.display.set_caption("Lista 6 - Algoritmo de Bellman-Ford - Semáforos de Recife")
JANELA = pygame.display.set_mode((LARGURA, ALTURA))
relogio = pygame.time.Clock()
FPS = 60

#Configuração da manipulação de telas
configuracao = {
    "Menu inicial": True,
    "Selecionar Semaforos": False,
    "Vizualisar":False,
    "Fim do programa":False,
    
}

#Parte do codigo que vai definir os metodos do grafo

#Função para verificar se existe ciclo negativo
def verifica_ciclo_negativo(graph, dist):
    for s, d, w in graph:
        if dist[s] != float("inf") and dist[s] + w < dist[d]:
            print("Graph contains negative weight cycle")
            return True
    return False

#Função para calcular o peso/distancia entre dois pontos
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

#Função bellman_ford 
def bellman_ford(grafo, semaforo_inicial, semaforo_final,dicionario_semaforos,mapeamento_ids,distancia_total=0,semaforos_vitados=None):
    if semaforos_vitados==None:
        semaforos_vitados=[]
    if semaforo_inicial == semaforo_final:
        semaforos_vitados=None
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
    grafo.vs[mapeamento_ids[semaforo_mais_proximo]]["color"] = "blue"
    grafo.add_edge(mapeamento_ids[semaforo_inicial], mapeamento_ids[semaforo_mais_proximo], weight=menor_distancia)
    distancia_total += menor_distancia
    return bellman_ford(grafo, semaforo_mais_proximo, semaforo_final,dicionario_semaforos,mapeamento_ids,distancia_total,semaforos_vitados)

#Função para gerar o grafo e manipular o grafo
def gerar_gafro(semaforo_inicial,semaforo_final):
    # Carregar os dados dos semáforos
    print('carregando dados dos semáforos...')
    df = pd.read_csv('semaforos.csv', nrows=100)

    dicionario_semaforos = {}

    # Mapear os semáforos para um dicionário
    for index, row in df.iterrows():
        numero_semaforo = int(row[0])  
        nome_semaforo = row[0]  # Assumindo que o nome do semáforo está na segunda coluna do CSV
        latitude = -(row[4] )
        longitude = row[5]
        nome_bairro=row[3]  
        dicionario_semaforos[numero_semaforo] = (nome_semaforo, latitude, longitude,nome_bairro)

    # Criar um grafo representado pelo igraph
    grafo=Graph()
    if grafo:
        grafo.delete_vertices(v for v in grafo.vs )
    
    
    # Adicionar vértices ao grafo e mapear os identificadores dos vértices para números de 0 a n-1
    mapeamento_ids = {}
    for i, (semaforo_num, (nome, latitude, longitude,nome_bairro)) in enumerate(dicionario_semaforos.items()):
        grafo.add_vertex(name=nome, latitude=latitude, longitude=longitude, bairro=nome_bairro)
        grafo.vs["color"] = "white"
        mapeamento_ids[semaforo_num] = i
    
    
    
    grafo,distancia=bellman_ford(grafo, semaforo_inicial,semaforo_final,dicionario_semaforos,mapeamento_ids)  
    print('Grafo gerado com sucesso!')
    if verifica_ciclo_negativo(grafo.get_edgelist(), distancia):
        print("O grafo contém um ciclo de peso negativo.")
        
    
    # mudar a cor do semáforo inicial e final
    grafo.vs[semaforo_inicial-1]["color"] = "green"
    grafo.vs[semaforo_final-1]["color"] = "red"

    # muda a label dos vértices
    vertex_labels = [f"\n{nome}\n{bairro}" for nome, bairro in zip(grafo.vs['name'], grafo.vs['bairro'])]
    # muda o layout do grafo
    layout = [(v['longitude'], v['latitude']) for v in grafo.vs] 
    # salva o grafo
    print('salvando o grafo...')
    plot(grafo, layout=layout,  bbox=(1200, 700), margin=50, vertex_label=vertex_labels, vertex_label_size=10 , vertex_size=16,  vertex_color=grafo.vs['color'], edge_width=grafo.es['weight'], edge_color="black", vertex_label_dist=-1, edge_arrow_size=0.5,  vertex_label_color="black").save("Grafo.png")
    grafo.delete_vertices(v for v in grafo.vs )
    return distancia

#Função para desenhar texto na tela
def draw_texto(texto,x,y):
    fonte = pygame.font.SysFont(None, 36)  
    texto_renderizado = fonte.render(texto, True, PRETO) 
    JANELA.blit(texto_renderizado, (x,y))  

#Tela de menu inicial  
def Menu():
    
    global configuracao
    background_menu = pygame.image.load("./Fundo_menu.png")
    tamanho_background_menu = pygame.transform.scale(background_menu,(1200, 700))
    menu_final_rodando = True
   
    while menu_final_rodando:
        pygame.time.delay(50)
        relogio.tick(FPS)
        JANELA.blit(tamanho_background_menu, (0, 0))
        if botao_comecar.draw():
            menu_final_rodando = False
            configuracao["Menu inicial"]=False
            configuracao["Selecionar Semaforos"]= True
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  
                menu_final_rodando = False
                pygame.quit()
                

        
        pygame.display.update()

#Tela para selecionar os semáforos
def Selecionar():

    #Variáveis globais
    global configuracao
    global semaforo_inicial
    global semaforo_final
    global color_input_1
    global color_input_2
    global distancia_total

    background_selecionar = pygame.image.load("./Fundo_input.png")
    tamanho_background_selecionar = pygame.transform.scale(background_selecionar,(1200, 700))
    menu_final_rodando = True
    input_incorreto=False
    semaforo_final_ativo=False
    semaforo_inicial_ativo=False
    semaforo_inicial="semáforo inicial"
    semaforo_final="semáforo final"

    while menu_final_rodando:
        JANELA.blit(tamanho_background_selecionar, (0, 0))
        pygame.time.delay(50)
        relogio.tick(FPS)
        
        texto_surface_2=base_font.render(semaforo_inicial,True,PRETO)
        texto_surface_1=base_font.render(semaforo_final,True,PRETO)

        pygame.draw.rect(JANELA,color_input_1,input_react_1,2)
        pygame.draw.rect(JANELA,color_input_2,input_react_2,2)
        
        JANELA.blit(texto_surface_1,(input_react_1.x+5,input_react_1.y+5))
        JANELA.blit(texto_surface_2,(input_react_2.x+5,input_react_2.y+5))

        if botao_visualizar.draw():
            #Verifica se os inputs existem
            if semaforo_inicial!="" and semaforo_final!=""  :
                #Verifica se os inputs são números
                try:
                    semaforo_inicial_data=int(semaforo_inicial)
                    semaforo_final_data=int(semaforo_final)
                    #Verifica se os inputs estão entre 1 e 100

                    if semaforo_inicial_data>0 and semaforo_inicial_data<101 and semaforo_final_data>0 and semaforo_final_data<101:
                        menu_final_rodando = False
                        color_input_1=pygame.Color('black')
                        color_input_2=pygame.Color('black')
                        configuracao["Selecionar Semaforos"]= False
                        configuracao["Vizualisar"]=True
                        distancia_total=gerar_gafro(semaforo_inicial_data,semaforo_final_data)
                        semaforo_final,semaforo_inicial,semaforo_inicial_data,semaforo_final_data="","","","0"
                    else:
                        input_incorreto=True
                except:
                    input_incorreto=True
                
            else:
                input_incorreto=True

        if input_incorreto:
            draw_texto("Digite números de 1-100", 540, 420)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  
                menu_final_rodando = False
                pygame.quit()

            #Verifica se o botão do mouse foi pressionado
            if evento.type==pygame.MOUSEBUTTONDOWN:
                if input_react_1.collidepoint(evento.pos):
                    semaforo_final=""
                    semaforo_inicial_ativo=False
                    semaforo_final_ativo=True
                    color_input_1=pygame.Color('white')
                    color_input_2=pygame.Color('black')
                    
                if input_react_2.collidepoint(evento.pos):
                    semaforo_inicial=""
                    semaforo_final_ativo=False
                    semaforo_inicial_ativo=True
                    
                    color_input_2=pygame.Color('white')
                    color_input_1=pygame.Color('black')

            #Verifica se uma tecla foi pressionada e passa o valor para a variável
            if evento.type==pygame.KEYDOWN:
                if semaforo_final_ativo:
                    if evento.key==pygame.K_BACKSPACE:
                        semaforo_final=semaforo_final[:-1]
                    else:
                        if len(semaforo_final)<3:
                            semaforo_final+=evento.unicode
                
                if semaforo_inicial_ativo:
                    if evento.key==pygame.K_BACKSPACE:
                        semaforo_inicial=semaforo_inicial[:-1]
                    else:
                        if len(semaforo_inicial)<3:
                            semaforo_inicial+=evento.unicode
                

                

        pygame.display.update()

#Tela para visualizar o grafo
def Vizualizar():
    
    global configuracao
    global distancia_total
    texto_final=f"Distância total Percorrida: {distancia_total:.2f} km"
    #Pega a imagem do grafo
    background_grafo = pygame.image.load("./Grafo.png")
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
        draw_texto(texto_final, 440, 10)
           
            

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









