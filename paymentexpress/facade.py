from django.conf import settings
from paymentexpress.gateway import (
    AUTH, COMPLETE, PURCHASE, REFUND, VALIDATE, Gateway
)
from paymentexpress.models import OrderTransaction

from oscar.apps.payment.exceptions import (UnableToTakePayment,
                                           InvalidGatewayRequestError)
import random


class Facade(object):
    """
    A bridge between oscar's objects and the core gateway object
    """

    def __init__(self):
        self.gateway = Gateway(
            settings.PAYMENTEXPRESS_POST_URL,
            settings.PAYMENTEXPRESS_USERNAME,
            settings.PAYMENTEXPRESS_PASSWORD,
            getattr(settings, 'PAYMENTEXPRESS_CURRENCY', 'AUD')
        )

    def _check_amount(self, amount):
        if amount == 0 or amount is None:
            raise UnableToTakePayment("Order amount must be non-zero")

    def _get_merchant_reference(self, order_number, txn_type):
        num_previous = OrderTransaction.objects.filter(
            order_number=order_number,
            txn_type=txn_type).count()

        # Get a random number to append to the end.  This solves the problem
        # where a previous request crashed out and didn't save a model instance
        # Hence we can get a clash of merchant references.
        rand = "%04.f" % (random.random() * 10000)
        return u'%s_%s_%d_%s' % (
            order_number, txn_type.upper(), num_previous + 1, rand
        )

    def _get_friendly_decline_message(self):
        return ('The transaction was declined by your bank - ' +
            'please check your bankcard details and try again')

    def _handle_response(self, txn_type, order_number, amount, response):

        OrderTransaction.objects.create(
            order_number=order_number,
            txn_type=txn_type,
            txn_ref=response['dps_txn_ref'],
            amount=amount,
            response_code=response['response_code'],
            response_message=response.get_message(),
            request_xml=response.request_xml,
            response_xml=response.response_xml
            )

        if response.is_successful():
            return {
                'txn_reference': response['dps_txn_ref'],
                'partner_reference': response['dps_billing_id'],
                }

        elif response.is_declined():
            raise UnableToTakePayment(self._get_friendly_decline_message())

        else:
            raise InvalidGatewayRequestError(response.get_message())

    def _format_card_date(self, str_date):
        # Dirty hack so that Oscar's BankcardForm doesn't need to be overridden
        if str_date is None:
            return None
        return str_date.replace('/', '')

    def authorise(self, order_number, amount, bankcard):
        """
        Authorizes a transaction.
        Must be completed within 7 days using the "Complete" TxnType
        """
        self._check_amount(amount)

        card_issue_date = self._format_card_date(bankcard.start_date)
        card_expiry_date = self._format_card_date(bankcard.expiry_date)

        merchant_ref = self._get_merchant_reference(order_number, AUTH)
        res = self.gateway.authorise(card_holder=bankcard.card_holder_name,
                                     card_number=bankcard.card_number,
                                     card_issue_date=card_issue_date,
                                     card_expiry=card_expiry_date,
                                     cvc2=bankcard.cvv,
                                     amount=amount,
                                     merchant_ref=merchant_ref)
        return self._handle_response(AUTH, order_number, amount, res)

    def complete(self, order_number, amount, dps_txn_ref):
        """
        Completes (settles) a pre-approved Auth Transaction.
        The DpsTxnRef value returned by the original approved Auth transaction
        must be supplied.
        """
        self._check_amount(amount)
        merchant_ref = self._get_merchant_reference(order_number, COMPLETE)
        res = self.gateway.complete(amount=amount,
                                    dps_txn_ref=dps_txn_ref,
                                    merchant_ref=merchant_ref)
        return self._handle_response(COMPLETE, order_number, amount, res)

    def purchase(self, order_number, amount, billing_id=None, bankcard=None):
        """
        Purchase - Funds are transferred immediately.
        """
        self._check_amount(amount)

        res = None
        merchant_ref = self._get_merchant_reference(order_number, PURCHASE)

        if billing_id:
            res = self.gateway.purchase(amount=amount,
                                        dps_billing_id=billing_id,
                                        merchant_ref=merchant_ref)
        elif bankcard:
            card_issue_date = self._format_card_date(bankcard.start_date)
            card_expiry_date = self._format_card_date(bankcard.expiry_date)
            res = self.gateway.purchase(amount=amount,
                                        card_holder=bankcard.card_holder_name,
                                        card_number=bankcard.card_number,
                                        card_issue_date=card_issue_date,
                                        card_expiry=card_expiry_date,
                                        cvc2=bankcard.cvv,
                                        merchant_ref=merchant_ref,
                                        enable_add_bill_card=1)
        else:
            raise ValueError("You must specify either a billing id or " +
                "a merchant reference")

        return self._handle_response(PURCHASE, order_number, amount, res)

    def refund(self, order_number, amount, dps_txn_ref):
        """
        Refund - Funds transferred immediately.
        Must be enabled as a special option.
        """
        self._check_amount(amount)
        merchant_ref = self._get_merchant_reference(order_number, REFUND)
        res = self.gateway.refund(amount=amount,
                                  dps_txn_ref=dps_txn_ref,
                                  merchant_ref=merchant_ref)
        return self._handle_response(REFUND, order_number, amount, res)

    def validate(self, bankcard):
        """
        Validation Transaction.
        Effects a $1.00 Auth to validate card details including expiry date.
        Often utilised with the EnableAddBillCard property set to 1 to
        automatically add to Billing Database if the transaction is approved.
        """
        amount = 1.00
        card_issue_date = self._format_card_date(bankcard.start_date)
        card_expiry_date = self._format_card_date(bankcard.expiry_date)

        res = self.gateway.validate(amount=amount,
                                    card_holder=bankcard.card_holder_name,
                                    card_number=bankcard.card_number,
                                    card_issue_date=card_issue_date,
                                    card_expiry=card_expiry_date,
                                    cvc2=bankcard.cvv,
                                    enable_add_bill_card=1)
        return self._handle_response(VALIDATE, None, amount, res)
