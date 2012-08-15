from django.test import TestCase
from mock import Mock, patch

from paymentexpress.facade import Facade
from paymentexpress.gateway import AUTH, PURCHASE
from paymentexpress.models import OrderTransaction
from tests import (XmlTestingMixin, CARD_VISA, SAMPLE_SUCCESSFUL_RESPONSE,
                   SAMPLE_DECLINED_RESPONSE, SAMPLE_ERROR_RESPONSE)

from oscar.apps.payment.utils import Bankcard
from oscar.apps.payment.exceptions import (UnableToTakePayment,
    InvalidGatewayRequestError)


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
        card = Bankcard(card_number=CARD_VISA,
                        expiry_date='1015',
                        name="Frankie", cvv="123",
                        start_date="1010")
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
        merchant_ref = self.facade._get_merchant_reference('1000', AUTH)
        self.assertRegexpMatches(merchant_ref, r'^\d+_[A-Z]+_\d+_\d{4}$')


class FacadeSuccessfulResponseTests(MockedResponseTestCase):

    dps_txn_ref = '000000030884cdc6'
    dps_billing_id = '0000080023225598'

    def setUp(self):
        self.facade = Facade()
        self.card = Bankcard(card_number=CARD_VISA,
                             expiry_date='1015',
                             name="Frankie", cvv="123",
                             start_date="1010")

    def test_successful_call_returns_valid_dict(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE)

            auth_dict = self.facade.authorise('1000', 1, self.card)
            complete_dict = self.facade.complete('1000', 1.23,
                                                 self.dps_txn_ref)
            refund_dict = self.facade.refund('1000', 1.23, '000000030884cdc6')
            validate_dict = self.facade.validate(self.card)
            response_dicts = (auth_dict, complete_dict, refund_dict,
                validate_dict)

            for response_dict in response_dicts:
                self.assertEquals(self.dps_txn_ref,
                    response_dict['txn_reference'])
                self.assertEquals(self.dps_billing_id,
                    response_dict['partner_reference'])

    def test_purchase_with_billing_id_returns_valid_dict(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE)

            txn_ref = self.facade.purchase('1000', 1.23, 'abc123')
            self.assertEquals(self.dps_txn_ref, txn_ref['txn_reference'])

    def test_purchase_with_bankcard_returns_valid_dict(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE)
            txn_ref = self.facade.purchase('1000', 1.23, None, self.card)
            self.assertEquals(self.dps_txn_ref, txn_ref['txn_reference'])

    def test_successful_call_is_recorded(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE)
            self.facade.authorise('10001', 10.25, self.card)
            txn = OrderTransaction.objects.filter(order_number='10001')[0]
            self.assertEquals(AUTH, txn.txn_type)

    def test_empty_issue_date_is_allowed(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE)
            card = Bankcard(card_number=CARD_VISA,
                            expiry_date='1015',
                            name="Frankie", cvv="123")
            txn_ref = self.facade.authorise('1000', 1.23, card)
            self.assertEquals(self.dps_txn_ref, txn_ref['txn_reference'])


class FacadeDeclinedResponseTests(MockedResponseTestCase):

    def setUp(self):
        self.facade = Facade()
        self.card = Bankcard(card_number=CARD_VISA,
                            expiry_date='1015',
                            name="Frankie", cvv="123",
                            start_date="1010")

    def test_declined_call_raises_an_exception(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_DECLINED_RESPONSE)

            with self.assertRaises(UnableToTakePayment):
                self.facade.authorise('1000', 1, self.card)

            with self.assertRaises(UnableToTakePayment):
                self.facade.complete('1000', 1.23, '000000030884cdc6')

            with self.assertRaises(UnableToTakePayment):
                self.facade.purchase('1000', 1.23, 'abc123')

            with self.assertRaises(UnableToTakePayment):
                self.facade.purchase('1000', 1.23, None, self.card)

            with self.assertRaises(UnableToTakePayment):
                self.facade.refund('1000', 1.23, '000000030884cdc6')

            with self.assertRaises(UnableToTakePayment):
                self.facade.validate(self.card)

    def test_declined_call_is_recorded(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_DECLINED_RESPONSE)
            try:
                self.facade.purchase('1001', 10.24, None, self.card)
            except Exception:
                pass
            txn = OrderTransaction.objects.filter(order_number='1001')[0]
            self.assertIsNotNone(txn)
            self.assertEquals(PURCHASE, txn.txn_type)


class FacadeErrorResponseTests(MockedResponseTestCase):

    def setUp(self):
        self.facade = Facade()
        self.card = Bankcard(card_number=CARD_VISA,
                            expiry_date='1015',
                            name="Frankie", cvv="123",
                            start_date="1010")

    def test_error_response_raises_invalid_gateway_request_exception(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_ERROR_RESPONSE)
            with self.assertRaises(InvalidGatewayRequestError):
                self.facade.purchase('1000', 10.24, None, self.card)
