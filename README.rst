=======================================
PaymentExpress package for django-oscar
=======================================

This package provides integration with the payment gateway, PaymentExpress using their `PX POST API`_. It is designed to work seamlessly with the e-commerce framework `django-oscar`_ but can be used without it.

.. _`PX Post API`: http://sec.paymentexpress.com/technical_resources/ecommerce_nonhosted/pxpost.html
.. _`django-oscar`: https://github.com/tangentlabs/django-oscar

Installation
------------

From PyPi::

    pip install django-oscar-paymentexpress

or from Github::

    pip install git+git://github.com/tangentlabs/django-oscar-paymentexpress.git#egg=django-oscar-paymentexpress

Add ``'paymentexpress'`` to ``INSTALLED_APPS`` and run::

    ./manage.py migrate paymentexpress

to create the appropriate database tables.

Configuration
-------------

Edit your ``settings.py`` to set the following settings::

    PAYMENTEXPRESS_POST_URL = 'https://sec.paymentexpress.com/pxpost.aspx'
    PAYMENTEXPRESS_USERNAME = '…'
    PAYMENTEXPRESS_PASSWORD = '…'
    PAYMENTEXPRESS_CURRENCY = 'AUD'

Integration into checkout
-------------------------

You'll need to use a subclass of ``oscar.apps.checkout.views.PaymentDetailsView`` within your own
checkout views.  See `oscar's documentation`_ on how to create a local version of the checkout app.

.. _`oscar's documentation`: http://django-oscar.readthedocs.org/en/latest/index.html

Override the ``handle_payment`` method (which is blank by default) and add your integration code.  An example
integration might look like::

    # myshop.checkout.views
    from django.conf import settings

    from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView
    from oscar.apps.payment.forms import BankcardForm
    from paymentexpress.facade import Facade
    from paymentexpress import PAYMENTEXPRESS

    ...

    class PaymentDetailsView(OscarPaymentDetailsView):

        def get_context_data(self, **kwargs):
            ...
            ctx['bankcard_form'] = BankcardForm()
            ...
            return ctx

        def post(self, request, *args, **kwargs):
            """
            This method is designed to be overridden by subclasses which will
            validate the forms from the payment details page.  If the forms are valid
            then the method can call submit()
            """
            # Check bankcard form is valid
            bankcard_form = BankcardForm(request.POST)
            if not bankcard_form.is_valid():
                ctx = self.get_context_data(**kwargs)
                ctx['bankcard_form'] = bankcard_form
                return self.render_to_response(ctx)

            bankcard = bankcard_form.get_bankcard_obj()

            # Call oscar's submit method, passing through the bankcard object so it gets
            # passed to the 'handle_payment' method
            return self.submit(request.basket, payment_kwargs={'bankcard': bankcard})

        def handle_payment(self, order_number, total, **kwargs):
            # Make request to PaymentExpress - if there any problems (eg bankcard
            # not valid / request refused by bank) then an exception would be
            # raised and handled) within oscar's PaymentDetails view.
            bankcard = kwargs['bankcard']
            response_dict = Facade().purchase(order_number, total, None, bankcard)

            source_type, _ = SourceType.objects.get_or_create(name=PAYMENTEXPRESS)
            source = Source(source_type=source_type,
                            currency=settings.PAYMENTEXPRESS_CURRENCY,
                            amount_allocated=total,
                            amount_debited=total,
                            reference=response_dict['partner_reference'])

            self.add_payment_source(source)

            # Also record payment event
            self.add_payment_event(PURCHASE, total)

Oscar's view will handle the various exceptions that can get raised.

Package structure
=================

There are two key components:

Gateway
-------

The class ``paymentexpress.gateway.Gateway`` provides fine-grained access to the PaymentExpress API, which involve constructing XML requests and decoding XML responses.  All calls return a ``paymentexpress.gateway.Response`` instance which provides dictionary-like access to the attributes of the response.

Example calls::

    # Authorise a transaction.
    # The funds are not transferred from the cardholder account.
    response = gateway.authorise(card_holder='John Smith',
                                 card_number='4500230021616301',
                                 cvc2='123',
                                 amount=50.23)

    # Completes (settles) a pre-approved Auth Transaction.
    response = gateway.complete(amount=50.23,
                                dps_txn_ref='0000000809b61753')


    # Purchase on a new card - funds are transferred immediately
    response = gateway.purchase(card_holder='Frankie',
                                card_number=CARD_VISA,
                                card_expiry='1015',
                                cvc2='123',
                                merchant_ref='100001_PURCHASE_1_2008',
                                enable_add_bill_card=1,
                                amount=29.95)

    # Purchase on a previously used card
    response = gateway.purchase(amount=29.95,
                                billing_id='0000080023748351')


    # Refund a transaction - funds are transferred immediately
    response = gateway.refund(dps_txn_ref='0000000809b61753',
                              merchant_ref='abc123',
                              amount=50.23)

Facade
------

The class ``paymentexpress.facade.Facade`` wraps the above gateway object and provides a less granular API, as well as saving instances of ``paymentexpress.models.OrderTransaction`` to provide an audit trail for PaymentExpress activity.


Contributing
============

To work on ``django-oscar-paymentexpress``, clone the repo, set up a virtualenv and install in develop mode::

    python setup.py develop

then install the testing dependencies::

    pip install -r requirements.txt

The test suite can then be run using::

    ./run_tests.py

Magic card numbers are available on the PaymentExpress site:
http://www.paymentexpress.com/knowledge_base/faq/developer_faq.html#Testing%20Details

Sample VISA vard:

    4111111111111111

Settings
========

* ``PAYMENTEXPRESS_POST_URL`` - PX POST URL

* ``PAYMENTEXPRESS_USERNAME`` - Username

* ``PAYMENTEXPRESS_PASSWORD`` - Password

* ``PAYMENTEXPRESS_CURRENCY`` - Currency to use for transactions