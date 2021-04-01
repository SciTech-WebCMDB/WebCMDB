from haystack import indexes
from .models import Computer, Server

class ComputerIndex(indexes.SearchIndex, indexes.Indexable,):
	text = indexes.NgramField(document=True, use_template=True)
	hostname = indexes.CharField(model_attr='hostname')
	ipv4 = indexes.CharField(model_attr='ipv4', null=True)
	location = indexes.CharField(model_attr='location')

	def get_model(self):
		return Computer

	def index_queryset(self, using=None):
		return self.get_model().objects.all()

class ServerIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.NgramField(document=True, use_template=True)
	servername = indexes.CharField(model_attr='servername')
	ipv4 = indexes.CharField(model_attr='ipv4', null=True)
	location = indexes.CharField(model_attr='location')

	def get_model(self):
		return Server

	def index_queryset(self, using=None):
		return self.get_model().objects.all()