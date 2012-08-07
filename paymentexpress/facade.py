from django.conf import settings
from paymentexpress.gateway import (
        AUTH, COMPLETE, PURCHASE, REFUND, VALIDATE, Gateway
    )
from paymentexpress.models import OrderTransaction

from oscar.apps.payment.utils import Bankcard
from oscar.apps.payment.exceptions import UnableToTakePayment
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

    def merchant_reference(self, order_number, txn_type):
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

    def authorise(self, order_number, amount, bankcard):
        """
        Authorizes a transaction.
        Must be completed within 7 days using the "Complete" TxnType
        """
        self._check_amount(amount)
        return self.gateway.authorise(
                card_holder=bankcard.card_holder_name,
                card_number=bankcard.card_number,
                card_expiry=bankcard.expiry_date,
                card_issue_date=bankcard.start_date,
                cvc2=bankcard.cvv,
                amount=amount,
                merchant_ref=self.merchant_reference(order_number, AUTH)
            )

    def complete(self, order_number, amount, dps_txn_ref):
        """
        Completes (settles) a pre-approved Auth Transaction.
        The DpsTxnRef value returned by the original approved Auth transaction
        must be supplied.
        """
        self._check_amount(amount)
        return self.gateway.complete(
                amount=amount,
                dps_txn_ref=dps_txn_ref,
                merchant_ref=self.merchant_reference(order_number, COMPLETE)
            )

    def purchase(self, order_number, amount, billing_id=None, bankcard=None):
        """
        Purchase - Funds are transferred immediately.
        """
        self._check_amount(amount)
        res = None
        if billing_id:
            res = self.gateway.purchase(
                    amount=amount,
                    billing_id=billing_id,
                    merchant_ref=self.merchant_reference(
                            order_number, PURCHASE
                        )
                )
        elif bankcard:
            res = self.gateway.purchase(
                    amount=amount,
                    card_holder=bankcard.card_holder_name,
                    card_number=bankcard.card_number,
                    card_expiry=bankcard.expiry_date,
                    card_issue_date=bankcard.start_date,
                    cvc2=bankcard.cvv,
                    merchant_ref=self.merchant_reference(
                            order_number, PURCHASE
                        ),
                    enable_add_bill_card=1
                )
        else:
            raise ValueError("You must specify either a billing id or ",
                "a merchant reference")
        return res

    def refund(self, order_number, amount, dps_txn_ref):
        """
        Refund - Funds transferred immediately.
        Must be enabled as a special option.
        """
        self._check_amount(amount)
        return self.gateway.refund(
                amount=amount,
                dps_txn_ref=dps_txn_ref,
                merchant_ref=self.merchant_reference(order_number, REFUND)
            )

    def validate(self, bankcard):
        """
        Validation Transaction.
        Effects a $1.00 Auth to validate card details including expiry date.
        Often utilised with the EnableAddBillCard property set to 1 to
        automatically add to Billing Database if the transaction is approved.
        """
        return self.gateway.validate(
                    amount=1.00,
                    card_holder=bankcard.card_holder_name,
                    card_number=bankcard.card_number,
                    card_expiry=bankcard.expiry_date,
                    card_issue_date=bankcard.start_date,
                    cvc2=bankcard.cvv,
                    enable_add_bill_card=1
                )
