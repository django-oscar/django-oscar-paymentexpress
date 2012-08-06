from unittest import TestCase
from paymentexpress.gateway import Request, Response, Gateway
from xml.dom.minidom import parseString, Document

SAMPLE_SUCCESSFUL_RESPONSE = """
<Txn>
    <Transaction success="1" reco="00" responseText="APPROVED" pxTxn="true">
        <Authorized>1</Authorized>
        <ReCo>00</ReCo>
        <RxDate>20090610225432</RxDate>
        <RxDateLocal>20090611105432</RxDateLocal>
        <LocalTimeZone>NZT</LocalTimeZone>
        <MerchantReference>Test Transaction</MerchantReference>
        <CardName>Visa</CardName>
        <Retry>0</Retry>
        <StatusRequired>0</StatusRequired>
        <AuthCode>105430</AuthCode>
        <AmountBalance>0.00</AmountBalance>
        <Amount>1.23</Amount>
        <CurrencyId>840</CurrencyId>
        <InputCurrencyId>840</InputCurrencyId>
        <InputCurrencyName>USD</InputCurrencyName>
        <CurrencyRate>1.00</CurrencyRate>
        <CurrencyName>USD</CurrencyName>
        <CardHolderName>A ANDERSON</CardHolderName>
        <DateSettlement>20090611</DateSettlement>
        <TxnType>Purchase</TxnType>
        <CardNumber>411111........11</CardNumber>
        <TxnMac>BD43E619</TxnMac>
        <DateExpiry>1010</DateExpiry>
        <ProductId/>
        <AcquirerDate>20090611</AcquirerDate>
        <AcquirerTime>105430</AcquirerTime>
        <AcquirerId>9001</AcquirerId>
        <Acquirer>Undefined</Acquirer>
        <AcquirerReCo/>
        <AcquirerResponseText/>
        <TestMode>0</TestMode>
        <CardId>2</CardId>
        <CardHolderResponseText>APPROVED</CardHolderResponseText>
        <CardHolderHelpText>The Transaction was approved</CardHolderHelpText>
        <CardHolderResponseDescription>
            The Transaction was approved
        </CardHolderResponseDescription>
        <MerchantResponseText>APPROVED</MerchantResponseText>
        <MerchantHelpText>The Transaction was approved</MerchantHelpText>
        <MerchantResponseDescription>
            The Transaction was approved
        </MerchantResponseDescription>
        <UrlFail/>
        <UrlSuccess/>
        <EnablePostResponse>0</EnablePostResponse>
        <AcquirerPort>100000000000-18270000</AcquirerPort>
        <AcquirerTxnRef>486310</AcquirerTxnRef>
        <GroupAccount>9997</GroupAccount>
        <DpsTxnRef>000000030884cdc6</DpsTxnRef>
        <AllowRetry>1</AllowRetry>
        <DpsBillingId/>
        <BillingId/>
        <TransactionId>0884cdc6</TransactionId>
        <PxHostId>00000003</PxHostId>
        <RmReason/>
        <RmReasonId>0000000000000000</RmReasonId>
        <RiskScore>-1</RiskScore>
        <RiskScoreText/>
    </Transaction>
    <ReCo>00</ReCo>
    <ResponseText>APPROVED</ResponseText>
    <HelpText>Transaction Approved</HelpText>
    <Success>1</Success>
    <DpsTxnRef>000000030884cdc6</DpsTxnRef>
    <TxnRef>inv1278</TxnRef>
</Txn>
"""

SAMPLE_DECLINED_RESPONSE = """
<Txn>
    <Transaction success="0" reco="05" responseText="DO NOT HONOUR"
        pxTxn="true">
        <Authorized>0</Authorized>
        <ReCo>05</ReCo>
        <RxDate>20120802050625</RxDate>
        <RxDateLocal>20120802150625</RxDateLocal>
        <LocalTimeZone>AEST</LocalTimeZone>
        <MerchantReference>25dc87c1be3053207d27003a5c2ccc7f</MerchantReference>
        <CardName>Visa</CardName>
        <Retry>0</Retry>
        <StatusRequired>0</StatusRequired>
        <AuthCode/>
        <AmountBalance>0.00</AmountBalance>
        <Amount>23.99</Amount>
        <CurrencyId>36</CurrencyId>
        <InputCurrencyId>36</InputCurrencyId>
        <InputCurrencyName>AUD</InputCurrencyName>
        <CurrencyRate>1.00</CurrencyRate>
        <CurrencyName>AUD</CurrencyName>
        <CardHolderName>CLARE WATER</CardHolderName>
        <DateSettlement>20120802</DateSettlement>
        <TxnType>Purchase</TxnType>
        <CardNumber>456472........83</CardNumber>
        <TxnMac>A595F807</TxnMac>
        <DateExpiry>0714</DateExpiry>
        <ProductId/>
        <AcquirerDate>20120802</AcquirerDate>
        <AcquirerTime>170627</AcquirerTime>
        <AcquirerId>5</AcquirerId>
        <Acquirer>ANZ AU</Acquirer>
        <AcquirerReCo>04</AcquirerReCo>
        <AcquirerResponseText>DECLINED 04</AcquirerResponseText>
        <TestMode>0</TestMode>
        <CardId>2</CardId>
        <CardHolderResponseText>DECLINED (05)</CardHolderResponseText>
        <CardHolderHelpText>
            The transaction was not approved
        </CardHolderHelpText>
        <CardHolderResponseDescription>
            The transaction was not approved
        </CardHolderResponseDescription>
        <MerchantResponseText>DO NOT HONOUR</MerchantResponseText>
        <MerchantHelpText>The transaction was not approved</MerchantHelpText>
        <MerchantResponseDescription>
            The transaction was not approved
        </MerchantResponseDescription>
        <UrlFail/>
        <UrlSuccess/>
        <EnablePostResponse>0</EnablePostResponse>
        <Cvc2ResultCode>NotUsed</Cvc2ResultCode>
        <AcquirerPort>1375112-00010027</AcquirerPort>
        <AcquirerTxnRef>12005</AcquirerTxnRef>
        <GroupAccount>0</GroupAccount>
        <DpsTxnRef>000000080985f6b6</DpsTxnRef>
        <AllowRetry>1</AllowRetry>
        <DpsBillingId>0000080023225598</DpsBillingId>
        <BillingId/>
        <TransactionId>0985f6b6</TransactionId>
        <PxHostId>00000008</PxHostId>
        <RmReason/>
        <RmReasonId>0000000000000000</RmReasonId>
        <RiskScore>-1</RiskScore>
        <RiskScoreText/>
    </Transaction>
    <ReCo>05</ReCo>
    <ResponseText>DO NOT HONOUR</ResponseText>
    <HelpText>The transaction was not approved</HelpText>
    <Success>0</Success>
    <DpsTxnRef>000000080985f6b6</DpsTxnRef>
    <TxnRef/>
    <RmReason/>
    <RmReasonId>0000000000000000</RmReasonId>
    <RiskScore>-1</RiskScore>
    <RiskScoreText/>
</Txn>
"""


class XmlTestingMixin(object):
    """
    Used to compare an expected field value against an xml element
    """

    def assertXmlElementEquals(self, doc, value, element_path):
        elements = element_path.split('.')
        parent = doc
        for element_name in elements:
            sub_elements = parent.getElementsByTagName(element_name)
            if len(sub_elements) == 0:
                self.fail("No element matching '%s' found using XML string "
                          "'%s'" % (element_name, element_path))
                return
            parent = sub_elements[0]
        self.assertEqual(value, parent.firstChild.data)


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


class SuccessfulResponseTests(TestCase):

    def setUp(self):
        self.response = Response('', SAMPLE_SUCCESSFUL_RESPONSE)

    def test_is_successful_returns_true(self):
        self.assertTrue(self.response.is_successful())

    def test_get_message(self):
        self.assertTrue(self.response.get_message() is not None)
        self.assertTrue(self.response.get_message() != '')

    def test_dict_access(self):
        self.assertEquals(1, self.response['authorised'])
        self.assertEquals(1, self.response['success'])

    def test_response_text_approved(self):
        self.assertEquals('APPROVED', self.response['response_text'])


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
        self.gateway = Gateway('hostname', 'TangentSnowball', 's3cr3t', 'AUD')

    def test_raises_error_on_missing_fields(self):
        with self.assertRaises(ValueError):
            self.gateway.authorise(card_holder='Frankie',
                                   card_number='5111222233334444',
                                   amount=1.23)

    def test_does_not_raise_error_when_all_fields_set(self):
        r = Request('TangentSnowball', 's3cr3t', 'AUD', 'Purchase', 1.23)
        doc = parseString(r.request_xml)
        self.assertIsInstance(doc, Document)

    def test_authorise_fields_set(self):
        self.gateway.authorise(card_holder='Frankie',
                               card_number='5111222233334444',
                               cvn='123',
                               amount=1.23)
        with self.assertRaises(ValueError):
            self.gateway.authorise()
