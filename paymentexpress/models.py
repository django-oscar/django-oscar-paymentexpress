from django.db import models
from xml.dom.minidom import parseString
import re


def pretty_print_xml(xml_string):
    line_regex = re.compile(r'\n\n')
    return line_regex.sub('', parseString(xml_string).toprettyxml())


class OrderTransaction(models.Model):

    # Note we don't use a foreign key as the order hasn't been created
    # by the time the transaction takes place
    order_number = models.CharField(max_length=128, db_index=True, null=True)

    # Transaction type
    txn_type = models.CharField(max_length=12)
    txn_ref = models.CharField(max_length=16)
    amount = models.DecimalField(decimal_places=2,
                                 max_digits=12,
                                 blank=True,
                                 null=True
                                 )

    response_code = models.CharField(max_length=2)
    response_message = models.CharField(max_length=255)

    # For debugging purposes
    request_xml = models.TextField()
    response_xml = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def save(self, *args, **kwargs):
        if not self.pk:
            cc_regex = re.compile(r'\d{12}')
            self.request_xml = cc_regex.sub('XXXXXXXXXXXX', self.request_xml)
            ccv_regex = re.compile(r'<Cvc2>\d+</Cvc2>')

            self.request_xml = ccv_regex.sub('<Cvc2>XXX</Cvc2>',
                                             self.request_xml)

            pw_regex = re.compile(r'<PostPassword>.*</PostPassword>')
            self.request_xml = pw_regex.sub('<PostPassword>XXX</PostPassword>',
                                            self.request_xml)

        super(OrderTransaction, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s txn for order %s - ref: %s, message: %s' % (
            self.txn_type,
            self.order_number,
            self.txn_ref,
            self.response_message,
        )

    @property
    def pretty_request_xml(self):
        return pretty_print_xml(self.request_xml)

    @property
    def pretty_response_xml(self):
        return pretty_print_xml(self.response_xml)
