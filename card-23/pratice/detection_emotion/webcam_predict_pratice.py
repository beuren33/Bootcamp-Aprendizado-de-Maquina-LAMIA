import cv2
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import load_model


# json_file = open('card-23/pratice/hand_gesture.json', 'r')
# loaded_model_json = json_file.read()
# json_file.close()
#  carrega o modelo e os pesos da rede treinada

# loaded_model = model_from_json(loaded_model_json)
# loaded_model.load_weights("card-23/pratice/hand_gesture.h5")

modelo_carregado = load_model('/home/beuren/Documentos/Bootcamp-LAMIA/card-23/pratice/detection_emotion/modelo_01.h5')
# carrega o modelo e seus pesos ja treinados

face_cascade = cv2.CascadeClassifier('/home/beuren/Documentos/Bootcamp-LAMIA/card-23/pratice/detection_emotion/haarcascade_frontalface_default.xml')
# carrega o classificador Haar Cascade para detecção de faces

expressoes = ['Surpresa', 'Medo', 'Nojo', 'Feliz', 'Triste', 'Raiva', 'Neutro']
# labels do dataset

cap = cv2.VideoCapture(0)
# abre a captura de video da webcam
while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # tira a esplhagem do cv2
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # tranforma a imagem em escala de cinza
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # detecta as faces na imagem

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        # redimensiona o ROI para o tamanho do modelo (64,64)
        roi_gray = cv2.resize(roi_gray, (64, 64))
        roi_gray = roi_gray.astype('float32') / 255.0
        # normaliza a imagem para 0-1
        roi_gray = np.expand_dims(roi_gray, axis=0)
        roi_gray = np.expand_dims(roi_gray, axis=-1)
        #adicina dimensoes para a que o modelo espera

        predictions = modelo_carregado.predict(roi_gray)
        # faz a predição da emoção
        max_index = int(np.argmax(predictions))
        # pega a maior probabilidade de predição
        predicted_emotion = expressoes[max_index]
        # escreve a emoção com base na maior probabilidade de predição

        cv2.putText(frame, predicted_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        # coloca o testo da emoção na tela
        cv2.rectangle(frame, (x, y), (x + w, y + h), (36, 255, 12), 2)
        # desenha um retangulo em volta da face detectada

    cv2.imshow('Reconhecimento de emocoes', frame)
    # mostra a imagem com a detecção de emoção

    if cv2.waitKey(1) & 0xFF == ord('q'):
        # sai do loop quando aperta a tecla q
        break
cap.release()
cv2.destroyAllWindows()
# libera a captura de video e fecha todas as janelas