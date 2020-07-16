from io import BytesIO

from cv2 import cv2
from PIL import Image

from ..utils import pil_to_cv2
from .webelement import CanvasWebElement


class CanvasDom:

    def __init__(self, parent):
        self._parent = parent
        self._dom = None

    @property
    def dom(self):
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
