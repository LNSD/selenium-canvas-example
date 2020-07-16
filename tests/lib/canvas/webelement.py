import typing
from io import BytesIO

import numpy as np
import pytesseract
from cv2 import cv2
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from ..utils import pil_to_cv2

if typing.TYPE_CHECKING:
    from typing import Dict, Optional  # noqa: F401


class CanvasWebElement(WebElement):

    def __init__(self, parent, id_):
        super(CanvasWebElement, self).__init__(parent, id_)

        self._location: 'Optional[Dict]' = None
        self._size: 'Optional[Dict]' = None

    @property
    def location(self):
        if self._location is None:
            raise AttributeError("Element location not set")
        return self._location

    @location.setter
    def location(self, loc):
        self._location = {"x": loc[0], "y": loc[1]}

    @property
    def size(self):
        if self._size is None:
            raise AttributeError("Element size not set")
        return self._size

    @size.setter
    def size(self, size):
        self._size = {"width": size[0], "height": size[1]}

    @property
    def contour(self):
        if self._size is None or self._location is None:
            raise ValueError("Element contour cannot be calculated")

        return np.array([
            [
                self.location["x"],
                self.location["y"]
            ],
            [
                self.location["x"] + self.size["width"],
                self.location["y"]
            ],
            [
                self.location["x"] + self.size["width"],
                self.location["y"] + self.size["height"]
            ],
            [
                self.location["x"],
                self.location["y"] + self.size["height"]
            ],
        ], dtype=np.int32)

    @property
    def center(self):
        try:
            cont = self.contour
        except ValueError:
            raise ValueError("Element center cannot be calculated")

        # Compute the center of the contour
        m = cv2.moments(cont)
        return {
            "x": int(m["m10"] / m["m00"]),
            "y": int(m["m01"] / m["m00"])
        }

    @property
    def screenshot_as_png(self):

        # Get canvas screenshot
        scr = self.parent.screenshot_as_png
        scr_pil = Image.open(BytesIO(scr))
        scr_cv2 = pil_to_cv2(scr_pil)

        # Scale canvas screenshot to actual canvas size
        scr_cv2 = cv2.resize(scr_cv2, (int(self.parent.size["width"]),
                                       int(self.parent.size["height"])))

        # Correct bounding rectangle
        x, y, w, h = cv2.boundingRect(self.contour)

        # Crop the screenshot
        return scr_cv2[y:y + h, x:x + w]

    @property
    def text(self):
        img = self.screenshot_as_png

        # Binarize the image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        custom_config = r"--oem 3 --psm 6 outputbase digits"
        return pytesseract.image_to_string(img, config=custom_config)

    def click(self):
        ac = ActionChains(self.parent.parent)
        ac.move_to_element_with_offset(self.parent,
                                       self.center["x"],
                                       self.center["y"])
        ac.click()
        ac.perform()
