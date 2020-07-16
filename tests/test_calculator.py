import pytest

from .lib.page import CanvasCalculatorPage


@pytest.fixture(scope="class")
def calc(browser):
    calc = CanvasCalculatorPage(browser)
    calc.get()
    return calc


class TestCalculator:

    def test_clear(self, calc: "CanvasCalculatorPage"):
        calc.clear()

        calc.click_on_button("4")
        assert calc.display_value == "4"
        calc.clear()
        assert calc.display_value == "0"

    @pytest.mark.parametrize('number', ["1", "2", "3", "4", "5",
                                        "6", "7", "8", "9", "0"])
    def test_numbers_ocr(self, calc: "CanvasCalculatorPage", number):
        calc.clear()

        calc.insert_number(number)
        assert calc.display_value == number

    def test_1_plus_2(self, calc: "CanvasCalculatorPage"):
        calc.clear()

        calc.click_on_button("1")
        assert calc.display_value == "1"
        calc.click_on_button("plus")
        calc.click_on_button("2")
        assert calc.display_value == "2"
        calc.click_on_button("equal")
        assert calc.display_value == "3"

    def test_21_plus_15_plus_6(self,
                               calc: "CanvasCalculatorPage"):
        calc.clear()

        calc.insert_number("21")
        assert calc.display_value == "21"
        calc.click_on_button("plus")
        calc.insert_number("15")
        assert calc.display_value == "15"
        calc.click_on_button("plus")
        assert calc.display_value == "36"
        calc.insert_number("6")
        assert calc.display_value == "6"
        calc.click_on_button("equal")
        assert calc.display_value == "42"
