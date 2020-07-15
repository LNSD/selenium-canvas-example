import sys

import pytest
import selenium.webdriver


@pytest.fixture(scope="class", params=["firefox", "chrome", "safari"])
def browser(request):

    # Initialize WebDriver
    if request.param == "firefox":
        driver = selenium.webdriver.Firefox()
    elif request.param == "chrome":
        driver = selenium.webdriver.Chrome()
    elif request.param == "safari" and sys.platform == "darwin":
        driver = selenium.webdriver.Safari()
    else:
        raise ValueError(request.param)

    # Maximize browser window
    driver.maximize_window()

    # Wait implicitly for elements to be ready before attempting interactions
    driver.implicitly_wait(10)

    # Return the driver object at the end of setup
    yield driver

    # For cleanup, quit the driver
    driver.quit()
