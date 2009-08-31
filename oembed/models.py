import datetime
from django.db import models
try:
    import simplejson
except ImportError:
    from django.utils import simplejson

JSON = 1
XML = 2
FORMAT_CHOICES = (
    (JSON, "JSON"),
    (XML, "XML"),
)

class ProviderRule(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    regex = models.CharField(max_length=2000)
    endpoint = models.CharField(max_length=2000)
    format = models.IntegerField(choices=FORMAT_CHOICES)
    
    def __unicode__(self):
        return self.name or self.endpoint

class StoredOEmbed(models.Model):
    match = models.TextField()
    max_width = models.IntegerField()
    max_height = models.IntegerField()
    response_json = models.TextField()
    date_added = models.DateTimeField(default=datetime.datetime.now)
    
    @property
    def response(self):
        return simplejson.loads(self.response_json)

    def __unicode__(self):
        return self.match