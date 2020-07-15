import pytesseract
import typing
from io import BytesIO

import numpy as np
from cv2 import cv2
from libs.utils import pil_to_cv2, cv2_to_pil
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if typing.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401


class CanvasCalculatorPage(object):
    URL = r"https://livecode.com/demo/html5/calculator/"

    def __init__(self, driver: "WebDriver"):
        self.driver = driver
        self._canvas_dom = None

    def get(self):
        self.driver.get(self.URL)

    def wait_until_canvas_is_loaded(self, timeout=60):
        # Once the spinner is hidden, the canvas has finished loading
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "spinner"))
        )

    @property
    def canvas(self):
        return self.driver.find_element_by_id("canvas")

    @staticmethod
    def _compute_element_contour_and_center(el) -> np.array:
        el["contour"] = np.array([
            [el["x"], el["y"]],
            [el["x"] + el["w"], el["y"]],
            [el["x"] + el["w"], el["y"] + el["h"]],
            [el["x"], el["y"] + el["h"]],
        ], dtype=np.int32)

        # compute the center of the contour
        m = cv2.moments(el["contour"])
        el["center"] = {
            "x": int(m["m10"] / m["m00"]),
            "y": int(m["m01"] / m["m00"])
        }

    @property
    def canvas_dom(self):

        if self._canvas_dom is not None:
            return self._canvas_dom

        # Hardcoded. TODO replace with an automatic segmentation
        el_w = self.canvas.size["width"] / 4
        el_h = self.canvas.size["height"] / 6

        self._canvas_dom = {
            "x": self.canvas.location["x"], "y": self.canvas.location["y"],
            "w": self.canvas.size["width"], "h": self.canvas.size["height"],
            "children": {
                "display": {
                    "x": 0,
                    "y": 0,
                    "w": 4,
                    "h": 1
                },
                "btn_0": {
                    "x": 0,
                    "y": 5,
                    "w": 2,
                    "h": 1
                },
                "btn_1": {
                    "x": 0,
                    "y": 4,
                    "w": 1,
                    "h": 1
                },
                "btn_2": {
                    "x": 1,
                    "y": 4,
                    "w": 1,
                    "h": 1
                },
                "btn_3": {
                    "x": 2,
                    "y": 4,
                    "w": 1,
                    "h": 1
                },
                "btn_4": {
                    "x": 0,
                    "y": 3,
                    "w": 1,
                    "h": 1
                },
                "btn_5": {
                    "x": 1,
                    "y": 3,
                    "w": 1,
                    "h": 1
                },
                "btn_6": {
                    "x": 2,
                    "y": 3,
                    "w": 1,
                    "h": 1
                },
                "btn_7": {
                    "x": 0,
                    "y": 2,
                    "w": 1,
                    "h": 1
                },
                "btn_8": {
                    "x": 1,
                    "y": 2,
                    "w": 1,
                    "h": 1
                },
                "btn_9": {
                    "x": 2,
                    "y": 2,
                    "w": 1,
                    "h": 1
                },
                "btn_dot": {
                    "x": 2,
                    "y": 5,
                    "w": 1,
                    "h": 1
                },
                "btn_plus": {
                    "x": 3,
                    "y": 4,
                    "w": 1,
                    "h": 1
                },
                "btn_minus": {
                    "x": 3,
                    "y": 3,
                    "w": 1,
                    "h": 1
                },
                "btn_multiply": {
                    "x": 3,
                    "y": 2,
                    "w": 1,
                    "h": 1
                },
                "btn_divide": {
                    "x": 3,
                    "y": 1,
                    "w": 1,
                    "h": 1
                },
                "btn_sign": {
                    "x": 1,
                    "y": 1,
                    "w": 1,
                    "h": 1
                },
                "btn_percent": {
                    "x": 2,
                    "y": 1,
                    "w": 1,
                    "h": 1
                },
                "btn_clear": {
                    "x": 0,
                    "y": 1,
                    "w": 1,
                    "h": 1
                },
                "btn_equal": {
                    "x": 3,
                    "y": 5,
                    "w": 1,
                    "h": 1
                }
            }
        }

        for child in self._canvas_dom["children"].values():
            child["x"] *= el_w
            child["y"] *= el_h
            child["w"] *= el_w
            child["h"] *= el_h

        for el in self._canvas_dom["children"].values():
            self._compute_element_contour_and_center(el)

        return self._canvas_dom

    def debug_draw_buttons_contour(self):

        dom = self.canvas_dom

        scr = self.canvas.screenshot_as_png
        calc_img = Image.open(BytesIO(scr))
        scr_cv2 = pil_to_cv2(calc_img)
        scr_cv2 = cv2.resize(scr_cv2, (int(self.canvas.size["width"]),
                                       int(self.canvas.size["height"])))

        cv2.imshow("Screenshot", scr_cv2)
        cv2.waitKey()

        scr_rois = scr_cv2.copy()

        # loop over the contours
        for b in dom["children"].values():
            c = b["contour"]
            c_x = b["center"]["x"]
            c_y = b["center"]["y"]

            # draw the contour and center of the shape on the image
            cv2.drawContours(scr_rois, [c], -1, (0, 255, 0), 3)
            cv2.circle(scr_rois, (c_x, c_y), 7, (0, 255, 0), -1)
            cv2.putText(scr_rois, "center", (c_x - 20, c_y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # show the image
            cv2.imshow("Contours", scr_rois)
            cv2.waitKey()

    def _click_on_button(self, el):

        if isinstance(el, str):
            el = self.canvas_dom["children"][f"btn_{el}"]

        ac = ActionChains(self.driver)
        ac.move_to_element_with_offset(self.canvas,
                                       el["center"]["x"],
                                       el["center"]["y"])
        ac.click()
        ac.perform()

    def click_on_button(self, btn):
        self._click_on_button(btn)

    def clear(self):
        self.click_on_button("clear")

    @property
    def display_value(self):

        dom = self.canvas_dom

        scr = self.canvas.screenshot_as_png
        calc_img = Image.open(BytesIO(scr))
        scr_cv2 = pil_to_cv2(calc_img)
        scr_cv2 = cv2.resize(scr_cv2, (int(self.canvas.size["width"]),
                                       int(self.canvas.size["height"])))

        x, y, w, h = cv2.boundingRect(dom["children"]["display"]["contour"])
        display_img = scr_cv2[y:y+h, x:x+w]

        # cv2.imshow("debug", display_img)
        # cv2.waitKey(0)
        display_img = cv2.bitwise_not(display_img)

        custom_config = r"--oem 3 --psm 6 outputbase digits"
        val = pytesseract.image_to_string(display_img, config=custom_config)

        return float(val)

    def debug_get_display_screenshot(self):

        dom = self.canvas_dom

        scr = self.canvas.screenshot_as_png
        calc_img = Image.open(BytesIO(scr))
        scr_cv2 = pil_to_cv2(calc_img)
        scr_cv2 = cv2.resize(scr_cv2, (int(self.canvas.size["width"]),
                                       int(self.canvas.size["height"])))

        x,y,w,h = cv2.boundingRect(dom["children"]["display"]["contour"])
        display_img = scr_cv2[y:y+h, x:x+w]

        cv2.imshow("Display", display_img)
        cv2.waitKey()
