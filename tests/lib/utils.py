import numpy as np
from cv2 import cv2
from PIL import Image


def cv2_to_pil(img):
    i = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(i)


def pil_to_cv2(img):
    i = np.asarray(img, dtype=np.float32).astype(np.uint8)
    return cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
