from django.test import TestCase
from mock import patch, Mock
from paymentexpress.gateway import Request, Response, Gateway, AUTH
from xml.dom.minidom import parseString, Document
from tests import (XmlTestingMixin,
                   SAMPLE_PURCHASE_REQUEST,
                   SAMPLE_DECLINED_RESPONSE,
                   SAMPLE_SUCCESSFUL_RESPONSE,
                   CARD_VISA,
                   )


class MockedResponseTestCase(TestCase):

    def create_mock_response(self, body, status_code=200):
        response = Mock()
        response.content = body
        response.text = body
        response.status_code = status_code
        return response


class RequestTests(XmlTestingMixin, TestCase):

    def test_request_returns_valid_xml(self):
        r = Request('TangentSnowball', 's3cr3t', 'AUD', 'Auth', 12.3)
        self.assertIsInstance(parseString(r.request_xml), Document)
        self.assertIsInstance(parseString(str(r)), Document)

    def test_request_has_correct_root(self):
        r = Request('TangentSnowball', 's3cr3t', 'AUD', 'Auth', 12.3)
        doc = parseString(r.request_xml)
        self.assertEquals('Txn', doc.documentElement.tagName)

    def test_can_add_element(self):
        r = Request('TangentSnowball', 's3cr3t', 'AUD', 'Auth', 12.3)
        r.set_element('card_holder', 'Frankie')
        doc = parseString(r.request_xml)

        self.assertXmlElementEquals(doc, 'Frankie', 'Txn.CardHolderName')

    def test_has_required_fields(self):
        r = Request('TangentSnowball', 's3cr3t', 'AUD', 'Purchase', 12.3)
        doc = parseString(r.request_xml)
        self.assertXmlElementEquals(doc, 'TangentSnowball', 'Txn.PostUsername')
        self.assertXmlElementEquals(doc, 's3cr3t', 'Txn.PostPassword')
        self.assertXmlElementEquals(doc, 'AUD', 'Txn.InputCurrency')
        self.assertXmlElementEquals(doc, '12.3', 'Txn.Amount')
        self.assertXmlElementEquals(doc, 'Purchase', 'Txn.TxnType')

    def test_auth_present_in_xml(self):
        r = Request('TangentSnowball', 's3cr3t', 'AUD', 'Auth', 12.3)
        doc = parseString(r.request_xml)
        self.assertXmlElementEquals(doc, 'TangentSnowball', 'Txn.PostUsername')
        self.assertXmlElementEquals(doc, 's3cr3t', 'Txn.PostPassword')


class ResponseTests(TestCase):

    def test_is_successful_returns_false_on_empty_response(self):
        r = Response('', '')
        self.assertFalse(r.is_successful())

        r = Response('', '<?xml version="1.0" ?>')
        self.assertFalse(r.is_successful())

    def test_is_declined_returns_false_on_empty_response(self):
        r = Response('', '')
        self.assertFalse(r.is_declined())

        r = Response('', '<?xml version="1.0" ?>')
        self.assertFalse(r.is_declined())

    def test_is_declined_returns_true_on_declined_response(self):
        r = Response('', SAMPLE_DECLINED_RESPONSE)
        self.assertTrue(r.is_declined())

    def test_element_text_returns_blank_on_none(self):
        r = Response('', '<Txn><Transaction success="1" reco="00"' +
                     ' responseText="APPROVED" pxTxn="true" /></Txn>')
        self.assertEquals(r['authorised'], 0)

    def test_get_message_returns_help_text(self):
        r = Response('', """
            <Txn>
            <Transaction success="1" reco="00"
                responseText="APPROVED" pxTxn="true">
                <CardHolderHelpText />
            </Transaction>
            <HelpText>Transaction Approved</HelpText>
             </Txn>
             """)
        self.assertEquals('Transaction Approved', r.get_message())

    def test_get_message_returns_generic_message_when_no_response(self):
        r = Response('', '')
        message = r.get_message()
        self.assertTrue(message is not None and message != '')


class SuccessfulResponseTests(TestCase):

    def setUp(self):
        self.response = Response('', SAMPLE_SUCCESSFUL_RESPONSE)

    def test_is_successful_returns_true(self):
        self.assertTrue(self.response.is_successful())

    def test_get_message_is_not_empty(self):
        self.assertTrue(self.response.get_message() is not None)
        self.assertTrue(self.response.get_message() != '')

    def test_response_data_has_dict_access(self):
        self.assertEquals(1, self.response['authorised'])
        self.assertEquals(1, self.response['success'])

    def test_response_text_is_approved_when_transaction_is_successful(self):
        self.assertEquals('APPROVED', self.response['response_text'])


class ApiResponseTests(MockedResponseTestCase):

    def setUp(self):
        self.gateway = Gateway(
            post_url='https://sec.paymentexpress.com/pxpost.aspx',
            username='TestUsername',
            password='TestPassword',
            currency='AUD')

    def test_authorise_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE
            )
            self.assertIsInstance(
                self.gateway.authorise(card_holder='Frankie',
                                       card_number=CARD_VISA,
                                       cvc2='123',
                                       amount=1.23), Response
            )

    def test_complete_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE)
            self.assertIsInstance(
                self.gateway.complete(dps_txn_ref='1234', amount=1.23, ),
                Response)

    def test_purchase_with_billing_id_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE
            )
            self.assertIsInstance(
                self.gateway.purchase(billing_id='123', amount=1.23), Response
            )

    def test_purchase_with_bankcard_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE
            )
            self.assertIsInstance(
                self.gateway.purchase(card_holder='Frankie',
                                      card_number=CARD_VISA,
                                      card_expiry='1015',
                                      cvc2='123',
                                      merchant_ref='abc123',
                                      enable_add_bill_card=1,
                                      amount=1.23), Response
                )

    def test_refund_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE
            )
            self.assertIsInstance(
                self.gateway.refund(dps_txn_ref='1234',
                                    merchant_ref='abc123',
                                    amount=1.23), Response
                )

    def test_validate_returns_response(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                SAMPLE_SUCCESSFUL_RESPONSE
            )
            self.assertIsInstance(
                self.gateway.validate(card_holder='Frankie',
                                      card_number=CARD_VISA,
                                      cvc2='123',
                                      card_expiry='1015',
                                      amount=1.23), Response
                )


class DeclinedResponseTests(TestCase):

    def setUp(self):
        self.response = Response('', SAMPLE_DECLINED_RESPONSE)

    def test_is_successful_returns_false(self):
        self.assertFalse(self.response.is_successful())

    def test_response_text_not_approved(self):
        self.assertNotEquals('APPROVED', self.response['response_text'])


class GatewayTests(TestCase):
    gateway = None

    def setUp(self):
        self.gateway = Gateway('http://localhost/', 'TangentSnowball',
            's3cr3t', 'AUD')

    def test_raises_error_on_missing_fields(self):
        with self.assertRaises(ValueError):
            self.gateway.authorise(
                card_holder='Frankie',
                card_number='5111222233334444',
                amount=1.23
            )

    def test_does_not_raise_error_when_all_fields_set(self):
        r = Request('TangentSnowball', 's3cr3t', 'AUD', 'Purchase', 1.23)
        doc = parseString(r.request_xml)
        self.assertIsInstance(doc, Document)

    def test_authorise_fields_set(self):
        self.gateway.authorise(
            card_holder='Frankie',
            card_number='5111222233334444',
            cvc2='123',
            amount=1.23
        )
        with self.assertRaises(ValueError):
            self.gateway.authorise()

    def test_amount_is_always_required(self):
        r = self.gateway._get_request(AUTH, {'card_holder': 'Frankie',
                                         'amount': 1.23
                                        }, ['amount', ], )
        self.assertIsInstance(r, Request)
        with self.assertRaises(ValueError):
            self.gateway._get_request(AUTH, {'card_holder': 'Frankie'}, [],)

    def test_get_message_returns_help_text(self):
        r = Response(SAMPLE_PURCHASE_REQUEST, SAMPLE_SUCCESSFUL_RESPONSE)
        self.assertTrue(r.get_message() is not None)

    def test_complete_requires_dps_txn_ref(self):
        with self.assertRaises(ValueError):
            self.gateway.complete()

    def test_amount_always_greater_than_zero(self):
        self.gateway.complete(dps_txn_ref="1234", amount=1.23)
        with self.assertRaises(ValueError):
            self.gateway.authorise(card_holder="Frankie",
                                   card_number=CARD_VISA,
                                   cvc2="123",
                                   amount=0.00)
            self.gateway.complete(dps_txn_ref="1234", amount=0)

    def test_card_expiry_has_four_digits(self):
        self.gateway.validate(card_holder="Frankie",
                              card_number=CARD_VISA,
                              cvc2="123",
                              card_expiry="1015",
                              amount=1.00)
        with self.assertRaises(ValueError):
            self.gateway.validate(card_holder="Frankie",
                                  card_number=CARD_VISA,
                                  cvc2="123",
                                  card_expiry="10/15",
                                  amount=1.00)

    def test_currency_code_has_three_characters(self):
        gateway = Gateway('http://localhost/', 'TangentSnowball',
            's3cr3t', 'au')
        with self.assertRaises(ValueError):
            gateway.refund(dps_txn_ref="abc", merchant_ref="123", amount=1.23)
