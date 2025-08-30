import pytest
from model_objects import Product, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog
from approvaltests.approvals import set_default_reporter
from approvaltests.reporters.python_native_reporter import PythonNativeReporter

@pytest.fixture(scope="session", autouse=True)
def configure_approvaltests_reporter():
    """
    This fixture runs automatically for all tests and sets a default
    reporter that prints the diff to the console.
    This guarantees that you never get the 'no reporter' error.
    """
    set_default_reporter(PythonNativeReporter())


@pytest.fixture
def catalog():
    """Create a fake catalog with products."""
    catalog = FakeCatalog()
    return catalog


@pytest.fixture
def toothbrush(catalog):
    """Create a toothbrush product and add it to catalog."""
    toothbrush = Product("toothbrush", ProductUnit.EACH)
    catalog.add_product(toothbrush, 0.99)
    return toothbrush


@pytest.fixture
def apples(catalog):
    """Create an apples product and add it to catalog."""
    apples = Product("apples", ProductUnit.KILO)
    catalog.add_product(apples, 1.99)
    return apples


@pytest.fixture
def teller(catalog):
    """Create a teller with the catalog."""
    return Teller(catalog)


@pytest.fixture
def cart():
    """Create an empty shopping cart."""
    return ShoppingCart()