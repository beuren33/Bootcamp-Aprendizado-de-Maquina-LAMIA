import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier('/home/beuren/Documentos/Bootcamp-LAMIA/card-23/pratice/haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (36, 255, 12), 2)

    cv2.imshow('Deteccao de Face', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()