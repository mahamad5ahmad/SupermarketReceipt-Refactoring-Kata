import pytest
from model_objects import Product, SpecialOfferType, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog
import approvaltests
import pytest
from model_objects import SpecialOfferType
from receipt_printer import ReceiptPrinter
from unittest.mock import Mock, patch
from model_objects import Product, ProductUnit


# ✅ Tests different scenarios that should PASS under current code

def test_empty_basket(teller, cart, toothbrush, apples):
    receipt = teller.checks_out_articles_from(cart)
    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))

def test_no_discount(teller, cart, toothbrush, apples):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
    cart.add_item_quantity(apples, 2.5)
    
    receipt = teller.checks_out_articles_from(cart)
    
    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))


def test_ten_percent_discount(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
    cart.add_item_quantity(toothbrush, 2)

    receipt = teller.checks_out_articles_from(cart)

    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))


def test_three_for_two_discount(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 10.0)
    cart.add_item_quantity(toothbrush, 3)

    receipt = teller.checks_out_articles_from(cart)

    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))

def test_three_for_two_discount_too_few(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 10.0)
    cart.add_item_quantity(toothbrush, 2)

    receipt = teller.checks_out_articles_from(cart)

    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))


def test_five_for_amount_discount(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothbrush, 4.0)
    cart.add_item_quantity(toothbrush, 5)

    receipt = teller.checks_out_articles_from(cart)

    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))

def test_five_for_amount_discount_bought_too_few(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothbrush, 4.0)
    cart.add_item_quantity(toothbrush, 4)

    receipt = teller.checks_out_articles_from(cart)

    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))

def test_two_for_amount_discount(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, toothbrush, 1.80)
    cart.add_item_quantity(toothbrush, 5)

    receipt = teller.checks_out_articles_from(cart)

    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))

def test_two_for_amount_discount_bought_too_few(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, toothbrush, 1.80)
    cart.add_item_quantity(toothbrush, 1)

    receipt = teller.checks_out_articles_from(cart)

    approvaltests.verify(ReceiptPrinter().print_receipt(receipt))

def test_ten_percent_discount(teller, cart, toothbrush , apples):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
    cart.add_item_quantity(apples, 2.5)

    receipt = teller.checks_out_articles_from(cart)

    assert 4.975 == pytest.approx(receipt.total_price(), 0.01)
    assert [] == receipt.discounts
    assert 1 == len(receipt.items)
    receipt_item = receipt.items[0]
    assert apples == receipt_item.product
    assert 1.99 == receipt_item.price
    assert 2.5 * 1.99 == pytest.approx(receipt_item.total_price, 0.01)
    assert 2.5 == receipt_item.quantity


def test_very_large_quantity( cart, apples):
    """Test handling very large quantities."""
    large_quantity = 999999.999
    cart.add_item_quantity(apples, large_quantity)
    assert cart.product_quantities[apples] == large_quantity


def test_feature_checkout_with_mixed_items_and_one_discount(teller, cart, toothbrush, apples):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, None) 
    cart.add_item_quantity(toothbrush, 3)
    cart.add_item_quantity(apples, 1.5)
    
    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(4.965)
    assert len(receipt.items) == 2
    assert len(receipt.discounts) == 1
    discount = receipt.discounts[0]
    assert discount.product == toothbrush
    assert discount.description == "3 for 2"
    assert discount.discount_amount == pytest.approx(-0.99)

def test_three_for_two_discount_more_items(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, None)
    cart.add_item_quantity(toothbrush, 7)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(4.95)
    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == pytest.approx(-1.98) 


def test_two_for_amounr_more_even_items(teller, cart, toothbrush, apples, catalog):
    banana = Product("banana", ProductUnit.KILO)
    catalog.add_product(banana, 2.5)

    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, banana, 4.00)
    cart.add_item_quantity(banana, 4)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(8)


# ❌ Tests designed to expose missing validation or incorrect behavior in current code

def test_two_for_amounr_more_non_even_items(teller, cart, toothbrush, apples, catalog):
    banana = Product("banana", ProductUnit.KILO)
    catalog.add_product(banana, 2.5)

    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, banana, 4.00)
    cart.add_item_quantity(banana, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(6.5)

def test_negative_quantity_should_raise_error(teller, cart, toothbrush):
    #will pass which is incorrect
    cart.add_item_quantity(toothbrush, -1)

    receipt = teller.checks_out_articles_from(cart)
    assert -0.99 == pytest.approx(receipt.total_price() )
 
    
      