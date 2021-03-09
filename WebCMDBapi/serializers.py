from rest_framework import serializers

from .models import Computer, Server

from drf_haystack.serializers import HaystackSerializer
from .search_indexes import ComputerIndex, ServerIndex

class ComputerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Computer
		fields = '__all__'

class ServerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Server
		fields = '__all__'

class SearchSerializer(HaystackSerializer):
	class Meta:
		index_classes = [ComputerIndex, ServerIndex]
		fields = ["hostname", "ipv4", "location", "servername"]