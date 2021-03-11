import uuid
from django.db import models

# Create your models here.

class Computer(models.Model):
	"""Laptop/Desktop/NAS-StorageBox"""

	PHYSICAL = 'PHYSICAL'
	VIRTUAL = 'VIRTUAL'

	ACTIVE = 'ACTIVE'
	OFF = 'OFF'
	TEMP = 'TEMP'  # ????????????????????
	SURPLUS = 'SURPLUS'
	STALLED = 'STALLED'
	SPARE = 'SPARE'  # how is this different from surplus?
	RETIRED = 'RETIRED'
	MISSING = 'MISSING'
	IPALIAS = 'IPALIAS'  # ???????????
	FLOATER = 'FLOATER'  # ??????

	IoT_ = 'IoT'  # to format it for future

	# power up priotity variables
	ONE = '1'
	TWO = '2'
	THREE = '3'
	FOUR = '4'
	FIVE = '5'
	UNKNOWN_PRIORITY = 'U'
	UNKNOWN = 'UNKNOWN'

	# power up priority choices
	POWER_UP_PRIORITY_CHOICE = [
		(ONE, ONE),
		(TWO, TWO),
		(THREE, THREE),
		(FOUR, FOUR),
		(FIVE, FIVE),
		(UNKNOWN_PRIORITY, UNKNOWN.title()),
	]

	PHYSICAL_VIRTUAL_CHOICE = [
		(PHYSICAL, PHYSICAL.title()),
		(VIRTUAL, VIRTUAL.title()),
	]

	STATUS_CHOICE = [
		(ACTIVE, ACTIVE.title()),
		(OFF, OFF.title()),
		(TEMP, TEMP.title()),
		(SURPLUS, SURPLUS.title()),
		(STALLED, STALLED.title()),
		(SPARE, SPARE.title()),
		(RETIRED, RETIRED.title()),
		(MISSING, MISSING.title()),
		(IPALIAS, IPALIAS.title()),
		(FLOATER, FLOATER.title()),
	]

	DESKTOP = 'DESKTOP'
	LAPTOP = 'LAPTOP'
	NAS = 'NAS'

	DESKTOP_LAPTOP_NAS_CHOICES = [
		(DESKTOP, DESKTOP.title()),
		(LAPTOP, LAPTOP.title()),
		(NAS, NAS.title()),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	hostname = models.CharField(max_length=100) #unique = True?
	location = models.CharField(max_length=100, blank=True)
	ipv4 = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
	ipv6 = models.GenericIPAddressField(protocol='IPv6', blank=True, null=True)
	desktop_laptop_nas = models.CharField(
		'Desktop/Laptop/NAS',
		max_length=15,
		choices=DESKTOP_LAPTOP_NAS_CHOICES,
		default=DESKTOP,
	)
	os = models.CharField(max_length=100, blank=True)
	# physical_virtual = models.CharField(
	# 	'Physical/Virtual',
	# 	max_length=15,
	# 	choices=PHYSICAL_VIRTUAL_CHOICE,
	# 	default=PHYSICAL,
	# )
	physical_virtual = models.CharField(max_length=100, blank=True)
	owner = models.CharField(max_length=100, blank=True)
	administrator = models.CharField(max_length=100, blank=True)
	uofa_tag_number = models.CharField(max_length=15, blank=True)
	make_model = models.CharField(max_length=100, blank=True)
	cpu = models.CharField(max_length=100, blank=True)
	ram = models.CharField(max_length=15, blank=True)
	storage = models.CharField(max_length=15, blank=True)
	gpu = models.CharField(max_length=100, blank=True)
	serial_number = models.CharField(max_length=15, blank=True)
	status = models.CharField(
		'Status',
		choices=STATUS_CHOICE,
		max_length=15,
		default=ACTIVE,
	)
	rack = models.CharField(max_length=15, blank=True)
	scitech_access = models.BooleanField(null=True)
	power_up_priority = models.CharField(
		max_length=1,
		choices=POWER_UP_PRIORITY_CHOICE,
		default=UNKNOWN_PRIORITY,
	)
	support_team = models.CharField(max_length=100, blank=True)
	department = models.CharField(max_length=100, blank=True)
	comments = models.TextField(blank=True)
	latest_information_update_date = models.DateTimeField(auto_now=True)
	date_added_to_database = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'WebCMDBapi_computer'

class Server(models.Model):
	"""Server"""

	TEACHING_LEARNING = 'TEACHING/LEARNING'
	RESEARCH = 'RESEARCH'
	ADMINISTRATION = 'ADMINISTRATION'
	MULTIPLE = 'MULTIPLE'
	UNKNOWN = 'UNKNOWN'
	SERVICE_CHOICE = [
		(TEACHING_LEARNING, TEACHING_LEARNING.title()),
		(RESEARCH, RESEARCH.title()),
		(ADMINISTRATION, ADMINISTRATION.title()),
		(MULTIPLE, MULTIPLE.title()),
		(UNKNOWN, UNKNOWN.title()),
	]

	LINUX = 'LINUX'
	WINDOWS = 'WINDOWS'
	OTHER = 'OTHER'
	OS_CHOICE = [
		(LINUX, LINUX.title()),
		(WINDOWS, WINDOWS.title()),
		(OTHER, OTHER.title()),
	]

	PHYSICAL = 'PHYSICAL'
	VIRTUAL = 'VIRTUAL'
	CLOUD = 'CLOUD'
	SERVER_TYPE_CHOICE = [
		(PHYSICAL, PHYSICAL.title()),
		(VIRTUAL, VIRTUAL.title()),
		(CLOUD, CLOUD.title()),
	]

	VMWARE = 'VMWARE'
	HYPERV = 'HYPERV'
	OPENSTACK = 'OPENSTACK'
	VIRTUAL_ENVIRONMENT_CHOICE = [
		(VMWARE, VMWARE.title()),
		(HYPERV, HYPERV.title()),
		(OPENSTACK, OPENSTACK.title()),
		(OTHER, OTHER.title()),
	]

	AZURE = 'AZURE'
	AWS = 'AWS'
	GCP = 'GCP'
	CLOUD_PROVIDER_CHOICE = [
		(AZURE, AZURE.title()),
		(AWS, AWS.title()),
		(GCP, GCP.title()),
		(OTHER, OTHER.title()),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	servername = models.CharField(max_length=100)
	fqdn = models.CharField(max_length=100, blank=True)
	used_for = models.CharField(max_length=100, blank=True)
	application = models.CharField(max_length=100, blank=True)
	service = models.CharField(
		'Services support by the server',
		max_length=20,
		choices=SERVICE_CHOICE,
		default=UNKNOWN,
	)
	ipv4 = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
	os = models.CharField(
		'OS',
		max_length=20,
		choices=OS_CHOICE,
		default=OTHER,
	)
	os_version = models.CharField(max_length=100, blank=True)
	cpu_counts = models.CharField(max_length=10, blank=True)
	ram = models.CharField(max_length=10, blank=True)
	storage_installed = models.CharField(max_length=10, blank=True)
	storage_used = models.CharField(max_length=10, blank=True)
	part_of_ActiveDirectoryDomain = models.BooleanField(default=False)
	domain_name = models.CharField(max_length=100, blank=True)
	server_type = models.CharField(
		'Server Type',
		max_length=20,
		choices=SERVER_TYPE_CHOICE,
		blank=True,
		null=True,
	)
	location = models.CharField(max_length=100, blank=True)
	location_access = models.CharField(max_length=100, blank=True)
	virtual_environment = models.CharField(
		'Virtual Environment',
		max_length=50,
		choices=VIRTUAL_ENVIRONMENT_CHOICE,
		blank=True,
		null=True,
	)
	cloud_provider = models.CharField(
		'Cloud Provider',
		max_length=20,
		choices=CLOUD_PROVIDER_CHOICE,
		blank=True,
		null=True,
	)
	firewall = models.BooleanField(null=True)
	firewall_ip = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
	backup = models.BooleanField(null=True)
	backup_type = models.CharField(max_length=20, blank=True)
	backup_system = models.CharField(max_length=20, blank=True)
	retention_period = models.CharField(max_length=20, blank=True)
	monitor = models.BooleanField(null=True)
	monitor_server = models.CharField(max_length=20, blank=True)
	maintenance_windows = models.BooleanField(null=True)
	patching_schedule = models.CharField(max_length=100, blank=True)
	legal_requirements = models.BooleanField(null=True)
	support_hours = models.CharField(max_length=50, blank=True)
	contact_technical = models.TextField(blank=True)
	contact_business = models.TextField(blank=True)
	device_owner = models.CharField(max_length=50, blank=True)
	licensing = models.CharField(max_length=50, blank=True)
	comment_service_application = models.TextField(blank=True)
	comment_server = models.TextField(blank=True)
	comment_issues = models.TextField(blank=True)

	latest_information_update_date = models.DateTimeField(auto_now=True)
	date_added_to_database = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'WebCMDBapi_server'