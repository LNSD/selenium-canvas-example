import pytest
from libs.page import CanvasCalculatorPage


@pytest.fixture(scope="class")
def calc(browser):
    calc = CanvasCalculatorPage(browser)
    calc.get()
    calc.wait_until_canvas_is_loaded(timeout=240)
    return calc


class TestCalculator:

    def test_clear(self, calc):
        calc.clear()
        calc.click_on_button("7")
        assert calc.display_value == 7
        calc.clear()
        assert calc.display_value == 0

    @pytest.mark.parametrize('number', ["1", "2", "3", "4", "5",
                                        "6", "7", "8", "9", "0"])
    def test_numbers_ocr(self, calc, number):
        calc.clear()
        calc.click_on_button(number)
        assert calc.display_value == int(number)

    def test_one_plus_two(self, calc):
        calc.clear()
        calc.click_on_button("1")
        assert calc.display_value == 1
        calc.click_on_button("plus")
        calc.click_on_button("2")
        assert calc.display_value == 2
        calc.click_on_button("equal")
        assert calc.display_value == 3
