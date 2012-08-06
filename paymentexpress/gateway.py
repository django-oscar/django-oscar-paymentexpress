from xml.dom.minidom import parseString, Document
from xml.parsers.expat import ExpatError

# Methods

AUTH = 'Auth'
COMPLETE = 'Complete'
PURCHASE = 'Purchase'
REFUND = 'Refund'
VALIDATE = 'Validate'


class Request(object):
    """
    Represents a PaymentExpress request
    """
    def __init__(self, username, password, currency, txn_type, amount):
        self.data = {}
        self.required_keys = [
            'username',
            'password',
            'amount',
            'currency',
            'txn_type',
            'amount',
        ]

        self.field_map = {

            # Required
            'username': 'PostUsername',
            'password': 'PostPassword',
            'amount': 'Amount',
            'currency': 'InputCurrency',
            'txn_type': 'TxnType',

            # Card details
            'card_holder': 'CardHolderName',
            'card_number': 'CardNumber',
            'cvn': 'Cvc2',
            'card_expiry': 'DateExpiry',

            'billing_id': 'BillingId',
            'dps_billing_id': 'DpsBillingId',
            'dps_txn_ref': 'DpsTxnRef',
            'enable_add_bill_card': 'EnableAddBillCard',
            'merchant_ref': 'MerchantReference',
            'txn_data1': 'TxnData1',
            'txn_data2': 'TxnData2',
            'txn_data3': 'TxnData3',
            'enable_avs': 'EnableAvsData',
            'avs_action': 'AvsAction',
            'avs_postcode': 'AvsPostCode',
            'avs_street_address': 'AvsStreetAddress',
            'date_start': 'DateStart',
            'issue_number': 'IssueNumber',
            'track2': 'Track2',
        }

        self.set_auth(username, password)
        self.set_element('currency', currency)
        self.set_element('txn_type', txn_type)
        self.set_element('amount', amount)

    @property
    def request_xml(self):
        """
        Return the string value of the request object
        """
        doc = Document()
        root = doc.createElement('Txn')
        doc.appendChild(root)

        for key, value in self.data.items():
            field = self.field_map.get(key)
            self._create_element(doc, root, field, value)

        return doc.toxml()

    def set_auth(self, username, password):
        self.set_element('username', username)
        self.set_element('password', password)

    def set_element(self, name, value):
        self.data[name] = value

    def _create_element(self, doc, parent, tag, value=None, attributes=None):
        """
        Creates an XML element
        """
        ele = doc.createElement(tag)
        parent.appendChild(ele)
        if value:
            text = doc.createTextNode(str(value))
            ele.appendChild(text)
        if attributes:
            [ele.setAttribute(k, v) for k, v in attributes.items()]
        return ele

    def __unicode__(self):
        return self.request_xml

    def __str__(self):
        return self.__unicode__()


class Response(object):
    """
    Encapsulate a PaymentExpress response
    """

    def __init__(self, request_xml, response_xml):
        self.request_xml = request_xml
        self.response_xml = response_xml
        self.data = self._extract_data(response_xml)

    def _extract_data(self, response_xml):
        if response_xml == '' \
            or response_xml == '<?xml version="1.0" ?>' \
            or response_xml is None:
            return None

        doc = parseString(response_xml)
        data = {
            'success': int(self._get_transaction_attribute(doc, 'success')),
            'response_code': self._get_transaction_attribute(doc, 'reco'),
            'response_text': self._get_transaction_attribute(doc,
                'responseText'),
            'authorised': int(self._get_element_text(doc, 'Authorized')),
            'auth_code': self._get_element_text(doc, 'AuthCode'),
            'txn_ref': self._get_element_text(doc, 'TxnRef'),
            'dps_txn_ref': self._get_element_text(doc, 'DpsTxnRef'),
            'card_holder_help_text': self._get_element_text(doc,
                'CardHolderHelpText'),
            'help_text': self._get_element_text(doc, 'HelpText'),
        }
        return data

    def _try_get_element(self, doc, tag):
        try:
            ele = doc.getElementsByTagName(tag)[0]
        except IndexError:
            return None
        return ele

    def _get_transaction_attribute(self, doc, attr):
        ele = self._try_get_element(doc, 'Transaction')
        if ele is None:
            return None
        if ele.attributes is None:
            return None
        return ele.attributes.get(attr).value

    def _get_element_text(self, doc, tag):
        ele = self._try_get_element(doc, tag)
        if ele is None:
            return None
        if ele.firstChild is None:
            return None
        return ele.firstChild.data

    def get_message(self):
        message = self.data['card_holder_help_text']
        if message is None:
            message = self.data['help_text']
        return message

    def __getitem__(self, key):
        return self.data[key]

    def is_successful(self):
        if self.data is None:
            return False
        return self.data['success'] == 1 and self.data['authorised'] == 1


class Gateway(object):
    """
    Transport class used to send PaymentExpress requests
    """

    def __init__(self, host, username, password, currency):
        self.host = host
        self.username = username
        self.password = password
        self.currency = currency

    def _do_request(self, request):
        """
        Sends the request
        """
        self._check_kwargs(request.data, request.required_keys)

    def _check_kwargs(self, kwargs, required_keys):
        for key in required_keys:
            if key not in kwargs:
                raise ValueError('You must provide a "%s" argument' % key)

    def _get_request(self, txn_type, kwargs, required_keys):
        if 'amount' not in required_keys:
            required_keys.append('amount')

        self._check_kwargs(kwargs, required_keys)
        request = Request(self.username,
                       self.password,
                       self.currency,
                       kwargs.get('txn_type'),
                       kwargs.get('amount'))
        for key in required_keys:
            request.set_element(key, kwargs.get(key))
        return request

    def authorise(self, **kwargs):
        """
        Authorizes a transaction.
        Must be completed within 7 days using the "Complete" TxnType
        """
        request = self._get_request(AUTH, kwargs, [
            'card_holder', 'card_number', 'cvn', 'amount',
        ])
        self._do_request(request)

    def complete(self, **kwargs):
        """
        Completes (settles) a pre-approved Auth Transaction.
        The DpsTxnRef value returned by the original approved Auth transaction
        must be supplied.
        """
        request = self._get_request(COMPLETE, kwargs, ['dps_txn_ref', ])
        self._do_request(request)

    def purchase(self, **kwargs):
        """
        Purchase - Funds are transferred immediately.
        """
        if kwargs.get('billing_id') is None:
            self._purchase_on_new_card(kwargs)
        else:
            self._purchase_on_existing_card(kwargs)

    def _purchase_on_new_card(self, **kwargs):
        request = self._get_request(PURCHASE, kwargs, [
            'card_holder', 'card_number', 'card_expiry', 'cvn',
            'merchant_ref', 'enable_add_bill_card', 'billing_id'
        ])
        self._do_request(request)

    def _purchase_on_existing_card(self, **kwargs):
        request = self._get_request(PURCHASE, kwargs, ['billing_id'])
        self._do_request(request)

    def validate(self, **kwargs):
        """
        Validation Transaction.
        Effects a $1.00 Auth to validate card details including expiry date.
        Often utilised with the EnableAddBillCard property set to 1 to
        automatically add to Billing Database if the transaction is approved.
        """
        request = self._get_request(AUTH, kwargs, [
            'card_holder', 'card_number', 'cvn', 'card_expiry',
        ])
        self._do_request(request)

    def refund(self, **kwargs):
        """
        Refund - Funds transferred immediately.
        Must be enabled as a special option.
        """
        request = self._get_request(REFUND, kwargs, [
            'dps_txn_ref', 'merchant_ref',
        ])
        self._do_request(request)
