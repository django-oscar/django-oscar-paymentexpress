from unittest import TestCase
from tests import (XmlTestingMixin,
                   SAMPLE_PURCHASE_REQUEST,
                   SAMPLE_SUCCESSFUL_RESPONSE)
from xml.dom.minidom import parseString
from paymentexpress.models import OrderTransaction


class TransactionModelTests(TestCase, XmlTestingMixin):

    def setUp(self):
        self.txn = OrderTransaction.objects.create(
            order_number=1000,
            txn_type='Purchase',
            txn_ref='0000000600fdd28e',
            amount=1.23,
            response_code='00',
            response_message='The Transaction was approved',
            request_xml=SAMPLE_PURCHASE_REQUEST,
            response_xml=SAMPLE_SUCCESSFUL_RESPONSE,
            date_created=None
            )

    def test_unicode(self):
        self.assertTrue('Purchase txn for order 1000 - ref: 0000000600fdd28e,',
            ' message: The Transaction was approved' in str(self.txn))

    def test_cc_numbers_are_not_saved_in_xml(self):
        doc = parseString(self.txn.request_xml)
        self.assertXmlElementEquals(doc, 'XXXXXXXXXXXX1111', 'Txn.CardNumber')

    def test_cvn_numbers_are_not_saved_in_xml(self):
        doc = parseString(self.txn.request_xml)
        self.assertXmlElementEquals(doc, 'XXX', 'Txn.Cvc2')

    def test_password_is_not_saved_in_xml(self):
        doc = parseString(self.txn.request_xml)
        self.assertXmlElementEquals(doc, 'XXX', 'Txn.PostPassword')

    def test_pretty_request_xml(self):
        self.assertTrue('\n\t<PostUsername>' in
            str(self.txn.pretty_request_xml))
        self.assertTrue('\n\t<PostPassword>' in
            str(self.txn.pretty_request_xml))

    def test_pretty_response_xml(self):
        self.assertTrue('\n\t<Transaction' in
            str(self.txn.pretty_response_xml))
        self.assertTrue('\n\t\t<Authorized' in
            str(self.txn.pretty_response_xml))
        self.assertTrue('\n\t<Transaction' in
            str(self.txn.pretty_response_xml))
