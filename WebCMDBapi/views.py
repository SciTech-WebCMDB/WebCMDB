from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from .serializers import ComputerSerializer, ServerSerializer
from .models import Computer, Server

# Create your views here.

def index(request):
	return render(request, 'WebCMDBapi/index.html')

class ComputerSearchGeneric(generics.ListAPIView):
	# cdrf.co/3.1/rest_framework.generics/ListAPIView.html
	model = Computer
	queryset = Computer.objects.all()
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'WebCMDBapi/computers.html'
	filter_backends = [filters.SearchFilter]
	search_fields = ['hostname', 'location', 'ipv4']

	def list(self, request):
		return Response({'computers':self.filter_queryset(self.get_queryset())})

#----------------------------------------------------------------------------
# Show all computers/servers

class ComputerAPIView(generics.ListAPIView):
	renderer_classes = [TemplateHTMLRenderer]
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
# Returning JSON for whatever purpose you have #

class ComupterDetailAPIView_JSON(APIView):
	def get(self, request, pk):
		computer = get_object_or_404(Computer, pk=pk)
		serializer = ComputerSerializer(computer).data
		return Response({'serializer':serializer})

class ServerDetailAPIView_JSON(APIView):
	def get(self, request, pk):
		server = get_object_or_404(Server, pk=pk)
		serializer = ComputerSerializer(server).data
		return Response({'serializer':serializer})

#----------------------------------------------------------------------------
# Rendering HTML

class ComputerDetailAPIView(APIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'WebCMDBapi/computer_detail.html'
	model = Computer

	def get(self, request, pk):
		computer = get_object_or_404(Computer, pk=pk)
		serializer = ComputerSerializer(computer)
		return Response({'serializer': serializer, 'computer': computer})

	def post(self, request, pk):
		computer = get_object_or_404(Computer, pk=pk)
		serializer = ComputerSerializer(computer, data=request.data)
		if not serializer.is_valid():
			return Response({'serializer': serializer, 'computer': computer})
		serializer.save()
		return redirect('WebCMDBapi:computers')

class ServerDetailAPIView(APIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'WebCMDBapi/server_detail.html'
	model = Server

	def get(self, request, pk):
		server = get_object_or_404(Server, pk=pk)
		serializer = ComputerSerializer(server)
		return Response({'serializer': serializer, 'server': server})

	def post(self, request, pk):
		server = get_object_or_404(Server, pk=pk)
		serializer = ComputerSerializer(server, data=request.data)
		if not serializer.is_valid():
			return Response({'serializer': serializer, 'server': server})
		serializer.save()
		return redirect('WebCMDBapi:servers')