from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes

from .serializers import ComputerSerializer, ServerSerializer, SearchSerializer
from .models import Computer, Server

from drf_haystack.generics import HaystackGenericAPIView
from haystack.query import SearchQuerySet
from django.core import serializers

import uuid

# Create your views here.

def index(request):
	return render(request, 'WebCMDBapi/index.html')

class AllSearchGeneric(HaystackGenericAPIView):
	# source: DRF Haystack documentation
	# My old Eenna/WebCMDB
	# Add this to fix Query doesnt look up for 2 modes: HAYSTACK_LIMIT_TO_REGISTERED_MODELS = False
	serializer_class = ServerSerializer
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

	def get_queryset(self, *args, **kwargs):
		queryset = SearchQuerySet().all().filter(content=self.request.GET.get('search'))
		return queryset

	def get(self, request):
		if self.request.accepted_renderer.format == 'json':
			content = []
			for x in self.get_queryset():
				if str(x.object._meta) == 'WebCMDBapi.computer':
					content.append(ComputerSerializer(instance=x.object).data)
				elif str(x.object._meta) == 'WebCMDBapi.server':
					content.append(ServerSerializer(instance=x.object).data)
			print(content)
			return Response(content)
		#return HTML here

class ComputerSearchGeneric(generics.ListAPIView):
	# cdrf.co/3.1/rest_framework.generics/ListAPIView.html
	model = Computer
	queryset = Computer.objects.all()
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/computers.html'
	filter_backends = [filters.SearchFilter]
	search_fields = ['hostname', 'location', 'ipv4']

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())
		if self.request.accepted_renderer.format == 'json':
			return Response((ComputerSerializer(queryset, many=True)).data)
		return Response({'computers':queryset})

class ServerSearchGeneric(generics.ListAPIView):
	# cdrf.co/3.1/rest_framework.generics/ListAPIView.html
	model = Server
	queryset = Server.objects.all()
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/servers.html'
	filter_backends = [filters.SearchFilter]
	search_fields = ['servername', 'location', 'ipv4']

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())
		if self.request.accepted_renderer.format == 'json':
			return Response((ServerSerializer(queryset, many=True)).data)
		return Response({'servers':queryset})

#----------------------------------------------------------------------------
# Show all computers/servers

class ComputerAPIView(generics.ListAPIView):
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/computers.html'
	model = Computer

	def get(self, request):
		queryset = Computer.objects.all()
		serializer_class = ComputerSerializer
		return Response({'computers':queryset})

class ServerAPIView(generics.ListAPIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'WebCMDBapi/servers.html'
	model = Server

	def get(self, request):
		queryset = Server.objects.all().order_by('servername')
		serializer_class = ServerSerializer
		return Response({'servers':queryset})

#----------------------------------------------------------------------------
# Rendering HTML

class ComputerDetailAPIView(APIView):
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/computer_detail.html'
	model = Computer

	def get(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			computer = get_object_or_404(Computer, pk=pk)
			serializer = ComputerSerializer(computer)
			if self.request.accepted_renderer.format == 'json':
				return Response(serializer.data)
			return Response({'serializer': serializer, 'computer': computer})
		else:
			serializer = ComputerSerializer()
			return Response({'serializer': serializer})

	def post(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			computer = get_object_or_404(Computer, pk=pk)
			serializer = ComputerSerializer(computer, data=request.data)
			if not serializer.is_valid():
				return Response({'serializer': serializer, 'computer': computer})
			serializer.save()
			return redirect('WebCMDBapi:computers')
		else:
			serializer = ComputerSerializer(data=request.data)
			if serializer.is_valid():
				computer = serializer.save()
				return redirect('WebCMDBapi:computer_detail', pk=computer.pk)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServerDetailAPIView(APIView):
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/server_detail.html'
	model = Server

	def get(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			server = get_object_or_404(Server, pk=pk)
			serializer = ServerSerializer(server)
			if self.request.accepted_renderer.format == 'json':
				return Response(serializer.data)
			return Response({'serializer': serializer, 'server': server})
		else:
			serializer = ServerSerializer()
			return Response({'serializer': serializer})

	def post(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			server = get_object_or_404(Server, pk=pk)
			serializer = ServerSerializer(server, data=request.data)
			if not serializer.is_valid():
				return Response({'serializer': serializer, 'server': server})
			serializer.save()
			return redirect('WebCMDBapi:servers')
		else:
			serializer = ServerSerializer(data=request.data)
			if serializer.is_valid():
				server = serializer.save()
				return redirect('WebCMDBapi:server_detail', pk=server.pk)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)