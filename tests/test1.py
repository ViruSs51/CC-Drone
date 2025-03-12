import subprocess
import cv2
import numpy as np
from djitellopy import Tello

drone = Tello()
drone.connect()
drone.streamon()

# Comanda pentru a captura fluxul video de la Tello
command = [
    "C:\\ffmpeg\\bin\\ffmpeg.exe",
    "-probesize",
    "32",
    "-analyzeduration",
    "0",
    "-i",
    "udp://192.168.10.1:11111",
    "-f",
    "image2pipe",
    "-pix_fmt",
    "bgr24",
    "-vcodec",
    "rawvideo",
    "-",
]

# Pornim procesul ffmpeg
pipe = subprocess.Popen(
    command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8
)

while True:
    # Citim un frame din fluxul video
    raw_image = pipe.stdout.read(960 * 720 * 3)  # Ajustează dacă rezoluția e diferită
    if not raw_image:
        break

    # Convertim frame-ul într-o imagine OpenCV
    image = np.frombuffer(raw_image, dtype=np.uint8)
    image = image.reshape((720, 960, 3))  # Asigură-te că rezoluția este corectă

    # Afișăm imaginea
    cv2.imshow("Tello Camera", image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Golim buffer-ul stdout
    pipe.stdout.flush()

# Închidem procesul și ferestrele OpenCV
pipe.terminate()
cv2.destroyAllWindows()
