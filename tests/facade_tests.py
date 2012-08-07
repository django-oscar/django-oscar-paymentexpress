from django.test import TestCase
from mock import Mock, patch

from paymentexpress.facade import Facade
from paymentexpress.gateway import Response, AUTH
from paymentexpress.models import OrderTransaction
from tests import XmlTestingMixin, CARD_VISA, SAMPLE_SUCCESSFUL_RESPONSE

from oscar.apps.payment.utils import Bankcard
from oscar.apps.payment.exceptions import UnableToTakePayment


class MockedResponseTestCase(TestCase):

    def create_mock_response(self, body, status_code=200):
        response = Mock()
        response.content = body
        response.text = body
        response.status_code = status_code
        return response


class FacadeTests(TestCase, XmlTestingMixin):

    def setUp(self):
        self.facade = Facade()

    def test_zero_amount_raises_exception(self):
        card = Bankcard(
            card_number=CARD_VISA, expiry_date='1015',
            name="Frankie", cvv="123", start_date="1010"
        )
        with self.assertRaises(UnableToTakePayment):
            self.facade.authorise('1000', 0, card)

    def test_zero_amount_for_complete_raises_exception(self):
        with self.assertRaises(UnableToTakePayment):
            self.facade.complete('1000', 0, '1234')

    def test_zero_amount_for_purchase_raises_exception(self):
        with self.assertRaises(UnableToTakePayment):
            self.facade.purchase('1000', 0)

    def test_purchase_without_billing_id_or_card_raises_exception(self):
        with self.assertRaises(ValueError):
            self.facade.purchase('1000', 1.23)

    def test_zero_amount_for_refund_raises_exception(self):
        with self.assertRaises(UnableToTakePayment):
            self.facade.refund('1000', 0, '1234')

    def test_merchant_reference_format(self):
        merchant_ref = self.facade.merchant_reference('1000', AUTH)
        self.assertRegexpMatches(merchant_ref, r'^\d+_[A-Z]+_\d+_\d{4}$')


class SuccessfulResponseTests(MockedResponseTestCase):

    def setUp(self):
        self.facade = Facade()

    def test_authorise_returns_response(self):
        card = Bankcard(
            card_number=CARD_VISA, expiry_date='1015',
            name="Frankie", cvv="123", start_date="1010"
        )
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                    SAMPLE_SUCCESSFUL_RESPONSE
                )
            self.assertIsInstance(
                    self.facade.authorise('1000', 1.23, card),
                    Response
                )

    def test_complete_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                    SAMPLE_SUCCESSFUL_RESPONSE
                )
            self.assertIsInstance(
                    self.facade.complete('1000', 1.23, '123'),
                    Response
                )

    def test_purchase_with_billing_id_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                    SAMPLE_SUCCESSFUL_RESPONSE
                )
            self.assertIsInstance(
                    self.facade.purchase('1000', 1.23, '123'),
                    Response
                )

    def test_purchase_with_bankcard_returns_response(self):
        with patch('requests.post') as post:
            card = Bankcard(
                card_number=CARD_VISA, expiry_date='1015',
                name="Frankie", cvv="123", start_date="1010"
            )
            post.return_value = self.create_mock_response(
                    SAMPLE_SUCCESSFUL_RESPONSE
                )
            self.assertIsInstance(
                    self.facade.purchase('1000', 1.23, None, card),
                    Response
                )

    def test_refund_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                    SAMPLE_SUCCESSFUL_RESPONSE
                )
            self.assertIsInstance(
                    self.facade.refund('1000', 1.23, '123'),
                    Response
                )

    def test_validate_returns_response(self):
        with patch('requests.post') as post:
            card = Bankcard(
                card_number=CARD_VISA, expiry_date='1015',
                name="Frankie", cvv="123", start_date="1010"
            )
            post.return_value = self.create_mock_response(
                    SAMPLE_SUCCESSFUL_RESPONSE
                )
            self.assertIsInstance(
                    self.facade.validate(card),
                    Response
                )
