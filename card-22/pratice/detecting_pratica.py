import cv2
import numpy as np
from collections import deque

cap = cv2.VideoCapture(0)# abre a webcam

pts = deque(maxlen=100)
# o deque é uma funcao que elimina o valor mais antigo ao adicionar outro, entao no 101° ponto ele elimina da lista o 1°

while True:
    _, frame = cap.read()

    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    low_red = np.array([161,155,84])
    high_red = np.array([179,255,255]) 
    red_mask = cv2.inRange(hsv, low_red, high_red)
    red = cv2.bitwise_and(frame,frame,mask=red_mask)

    low_blue = np.array([94,80,2])
    high_blue = np.array([126,255,255])
    blue_mask = cv2.inRange(hsv,low_blue,high_blue)
    blue = cv2.bitwise_and(frame,frame,mask=blue_mask)

    low_green = np.array([25,52,72])
    high_green = np.array([102,255,255])
    green_mask = cv2.inRange(hsv,low_green,high_green)
    
    kernel = np.ones((5,5), np.uint8)
    # cria uma matriz 5x5 de 1 segundo
    erode = cv2.erode(blue_mask,kernel,iterations=1)
    # tira ruidos brancos
    resultado = cv2.dilate(erode, kernel, iterations=1)
    # volta o ruido para o mesmo tamanho(o que sobrou ele) para nao quebrar a imagemm
    contornos, hierarquia = cv2.findContours(resultado,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # pega os contornos dos objetos presentes no frame
    
    if contornos:
        # se a lista tiver pelo menos 1 elemento, ou seja, se achar pelo menos 1 objeto rastreavel, pega o que tem maior tamanho
        maior_contorno = max(contornos,key=cv2.contourArea)
        
        M = cv2.moments(maior_contorno)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        # calcula o centroide do objeto(contorno)
        pts.append((cx,cy))
        # adiciona a lista a cordenada para traçar a linha

    for i in range(1,len(pts)):
            cv2.line(frame, pts[i-1],pts[i],(34,65,255), 5)
            # pega cada par da lista de coordenadas para desenhar a linha por essas coordenadas

    green = cv2.bitwise_and(frame,frame,mask=resultado)


    low = np.array([0,42,0])
    high = np.array([179,255,255])
    mask = cv2.inRange(hsv,low,high)
    result = cv2.bitwise_and(frame,frame,mask=mask)

    cv2.imshow("Frame",frame)
    #cv2.imshow("Red", red)
    #cv2.imshow("Blue",blue)
    #cv2.imshow("Green", green)

    #cv2.imshow("Result", result)

    
    key = cv2.waitKey(1)
    if key == 27:
        break
    
