import collections
import time
import typing

from .canvas.dom import CanvasDom

if typing.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401


class CanvasCalculatorPage(object):
    URL = r"https://www.online-calculator.com/html5/online-calculator/index.php"

    def __init__(self, driver: "WebDriver"):
        self.driver = driver
        self._canvas_dom = None

    def get(self):
        self.driver.get(self.URL)

    @property
    def canvas(self):
        return self.driver.find_element_by_id("canvas")

    @property
    def canvas_dom(self):
        if self._canvas_dom is None:
            self._canvas_dom = CanvasDom(self.canvas)
        return self._canvas_dom

    def click_on_button(self, btn):
        if isinstance(btn, str):
            btn = self.canvas_dom.find_element_by_id(f"btn_{btn}")
        btn.click()

        # Click takes time to perform. Wait to avoid race conditions
        time.sleep(0.2)

    def clear(self):
        self.click_on_button("clear")

    @property
    def display_value(self):
        display = self.canvas_dom.find_element_by_id("display")
        return display.text

    def insert_number(self, num):
        num = str(num)
        num = collections.deque(num)
        while num:
            n = num.popleft()
            self.click_on_button(n)
