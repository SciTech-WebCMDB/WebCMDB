from rest_framework import serializers

from .models import Computer, Server

class ComputerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Computer
		fields = '__all__'

class ServerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Server
		fields = '__all__'