import typing
from io import BytesIO

import numpy as np
import pytesseract
from cv2 import cv2
from libs.utils import pil_to_cv2
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

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


class CanvasDom:

    def __init__(self, parent):
        self._parent = parent
        self._dom = None

    @property
    def dom(self):
        """
        Canvas DOM

        :return: Canvas DOM elements
        """
        if self._dom is not None:
            return self._dom

        # TODO Segmentation and DOM construction
        self._dom = {}

        d = {
            "display": {"x": 0.065, "y": 0.055, "w": 0.87, "h": 0.09},
            "buttons": {"x": 0.05, "y": 0.2, "w": 0.9, "h": 0.725},
            "btn_7": {"x": 0, "y": 1, "w": 1, "h": 1},
            "btn_8": {"x": 1, "y": 1, "w": 1, "h": 1},
            "btn_9": {"x": 2, "y": 1, "w": 1, "h": 1},
            "btn_4": {"x": 0, "y": 2, "w": 1, "h": 1},
            "btn_5": {"x": 1, "y": 2, "w": 1, "h": 1},
            "btn_6": {"x": 2, "y": 2, "w": 1, "h": 1},
            "btn_1": {"x": 0, "y": 3, "w": 1, "h": 1},
            "btn_2": {"x": 1, "y": 3, "w": 1, "h": 1},
            "btn_3": {"x": 2, "y": 3, "w": 1, "h": 1},
            "btn_0": {"x": 0, "y": 4, "w": 1, "h": 1},
            "btn_plus": {"x": 3, "y": 4, "w": 1, "h": 1},
            "btn_equal": {"x": 4, "y": 4, "w": 1, "h": 1},
            "btn_clear": {"x": 4, "y": 0, "w": 1, "h": 1}
        }

        b_w = d["buttons"]["w"] / 5
        b_h = d["buttons"]["h"] / 5

        # Update buttons
        for id_, el in d.items():
            if not id_.startswith("btn_"):
                continue

            d[id_] = {
                "x": d["buttons"]["x"] + el["x"] * b_w,
                "y": d["buttons"]["y"] + el["y"] * b_h,
                "w": el["w"] * b_w,
                "h": el["h"] * b_h
            }

        # Build canvas dom
        for id_, el in d.items():
            self._dom[id_] = CanvasWebElement(self._parent, id_)
            self._dom[id_].location = (
                int(el["x"] * self._parent.size["width"]),
                int(el["y"] * self._parent.size["height"])
            )
            self._dom[id_].size = (
                int(el["w"] * self._parent.size["width"]),
                int(el["h"] * self._parent.size["height"])
            )

        return self._dom

    def debug_dom(self):
        scr = self._parent.screenshot_as_png
        calc_img = Image.open(BytesIO(scr))
        scr_cv2 = pil_to_cv2(calc_img)
        scr_cv2 = cv2.resize(scr_cv2, (int(self._parent.size["width"]),
                                       int(self._parent.size["height"])))

        for el in self.dom.values():
            # Draw the contour and center of the shape on the image
            cv2.drawContours(scr_cv2, [el.contour], -1, (0, 255, 0), 3)
            cv2.circle(scr_cv2, (el.center["x"],
                                 el.center["y"]), 7, (0, 255, 0), -1)
            cv2.putText(scr_cv2, "center", (el.center["x"] - 20,
                                            el.center["y"] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Show the image
            cv2.imshow("Contours", scr_cv2)
            cv2.waitKey()

    def find_element_by_id(self, id_):
        return self.dom.get(id_)
