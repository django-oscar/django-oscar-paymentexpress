# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'OrderTransaction'
        db.create_table('paymentexpress_ordertransaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order_number', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_index=True)),
            ('txn_type', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('txn_ref', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('response_code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('response_message', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('request_xml', self.gf('django.db.models.fields.TextField')()),
            ('response_xml', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('paymentexpress', ['OrderTransaction'])


    def backwards(self, orm):
        
        # Deleting model 'OrderTransaction'
        db.delete_table('paymentexpress_ordertransaction')


    models = {
        'paymentexpress.ordertransaction': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'OrderTransaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_index': 'True'}),
            'request_xml': ('django.db.models.fields.TextField', [], {}),
            'response_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'response_message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'response_xml': ('django.db.models.fields.TextField', [], {}),
            'txn_ref': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'txn_type': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        }
    }

    complete_apps = ['paymentexpress']
