=======================================
PaymentExpress package for django-oscar
=======================================

This package provides integration with the payment gateway, PaymentExpress using their PX POST API. It is designed to work seamlessly with the e-commerce framework `django-oscar` but can be used without it.

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

[ to be added ]


Package structure
=================

[ to be added ]


Settings
========

* ``PAYMENTEXPRESS_POST_URL`` - PX POST URL

* ``PAYMENTEXPRESS_USERNAME`` - Username

* ``PAYMENTEXPRESS_PASSWORD`` - Password

* ``PAYMENTEXPRESS_CURRENCY`` - Currency to use for transactions