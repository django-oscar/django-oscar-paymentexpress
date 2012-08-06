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

SAMPLE_PURCHASE_REQUEST = """
<Txn>
    <PostUsername>TestUsername</PostUsername>
    <PostPassword>TestPassword</PostPassword>
    <CardHolderName>A Anderson</CardHolderName>
    <CardNumber>4111111111111111</CardNumber>
    <Amount>1.23</Amount>
    <DateExpiry>1010</DateExpiry>
    <Cvc2>3456</Cvc2>
    <InputCurrency>NZD</InputCurrency>
    <TxnType>Purchase</TxnType>
    <TxnId>inv1278</TxnId>
    <MerchantReference>Test Transaction</MerchantReference>
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
