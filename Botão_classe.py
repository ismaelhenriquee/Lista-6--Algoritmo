import pygame
pygame.init()

LARGURA, ALTURA = 640, 480
JANELA = pygame.display.set_mode((LARGURA, ALTURA))
fonte_textos = pygame.font.SysFont('arial', 30)

#A classe botão define formato, cor e fonte dos botões que serão usados ao longo do código. Bem como, verifica se o botão está sendo pressionado.
class Botao:

    def __init__(self, texto, largura, altura, x, y):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_botao = 255, 152, 30
        self.pressionado = False
        self.texto_flutuante = fonte_textos.render(texto, True, (0, 0, 0))
        self.texto_rect = self.texto_flutuante.get_rect(center=self.rect.center)

    def draw(self):

        pygame.draw.rect(JANELA, (self.cor_botao), self.rect, border_radius=12)
        JANELA.blit(self.texto_flutuante, self.texto_rect)
        return self.click_verif()

    def click_verif(self):

        self.click = False
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.cor_botao= 228, 96, 0
            if pygame.mouse.get_pressed()[0]:
                self.pressionado = True
            else:
                if self.pressionado == True:
                    self.click = True

                    self.pressionado = False
        else:
            self.cor_botao = 255, 152, 30

        return self.click