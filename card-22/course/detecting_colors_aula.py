import cv2
import numpy as np

cap = cv2.VideoCapture(0)# abre a webcam

while True:
    _, frame = cap.read()# le cada frame que a webcam captura
    # read retorna em frame o estad de captura(True se deu certo e None cas falhe)
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    # converte BGR para HSV
    # HSV é como RGB, porem o HSV captura apenas a cor em si
    # H = codigo da cor
    # S = Saturação
    # V = brilho

    low_red = np.array([161,155,84])# pega o limite inferior da cor vermelha
    high_red = np.array([179,255,255]) # limite superior da cor vermelha
    red_mask = cv2.inRange(hsv, low_red, high_red)# verifica se os valores de HSV estao dentro do intervalo low_red e high_red
    red = cv2.bitwise_and(frame,frame,mask=red_mask)
    # faz com que somente os pixels vermelhos apareçam na tela

    low_blue = np.array([94,80,2])
    high_blue = np.array([126,255,255])
    blue_mask = cv2.inRange(hsv,low_blue,high_blue)
    blue = cv2.bitwise_and(frame,frame,mask=blue_mask)

    low_green = np.array([25,52,72])
    high_green = np.array([102,255,255])
    green_mask = cv2.inRange(hsv,low_green,high_green)
    green = cv2.bitwise_and(frame,frame,mask=green_mask)

    low = np.array([0,42,0])
    high = np.array([179,255,255])
    mask = cv2.inRange(hsv,low,high)
    result = cv2.bitwise_and(frame,frame,mask=mask)

    cv2.imshow("Frame",frame)
    # abre a visualização da imagem original
    #cv2.imshow("Red", red)
    #cv2.imshow("Blue",blue)
    cv2.imshow("Green", green)
    # mostra a visualização da imagem somente com os pixels verde

    #cv2.imshow("Result", result)
    
    key = cv2.waitKey(1)
    # atualiza o imshow para sempre ficar atualizando os frames
    if key == 27:
        # codigo ASCII da tecla 27
        break
    
