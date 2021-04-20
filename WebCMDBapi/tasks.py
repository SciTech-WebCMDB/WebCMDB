from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .models import Computer, Server
from datetime import datetime
from django.core.management import call_command

@shared_task(bind=True)
def import_csv_computer_task(self, data, overwrite):
	progress_recorder = ProgressRecorder(self)
	result = 0
	empty = 0
	total_work = len(data)
	log = ''
	for i, row in enumerate(data):
		if i != 0:
			try:
				if overwrite:
					computer, created = Computer.objects.update_or_create(
							id = str(row[20]),
							defaults = {
								'hostname': str(row[0]),
								'location': str(row[1]),
								'ipv4': str(row[2]),
								'os' :str(row[3]),
								'os_version': str(row[4]),
								'physical_virtual' :str(row[5]),
								'owner': str(row[6]),
								'administrator' :str(row[7]),
								'uofa_tag_number' :str(row[8]),
								'make_model' :str(row[9]),
								'serial_number': str(row[11]),
								'host_id': str(row[12]),
								'host_status': str(row[13]),
								'status': str(row[14]).upper(),
								'firewall': str(row[15]),
								'trustlevel': str(row[16]),
								'rack': str(row[17]),
								'power_up_priority': str(row[18]),
								'support_team': str(row[19]),
								'comments' :str(row[21]),
							},
						)
					result += 1
				else:
					computer, created = Computer.objects.get_or_create(
							id = str(row[20]),
							defaults = {
								'hostname': str(row[0]),
								'location': str(row[1]),
								'ipv4': str(row[2]),
								'os' :str(row[3]),
								'os_version': str(row[4]),
								'physical_virtual' :str(row[5]),
								'owner': str(row[6]),
								'administrator' :str(row[7]),
								'uofa_tag_number' :str(row[8]),
								'make_model' :str(row[9]),
								'serial_number': str(row[11]),
								'host_id': str(row[12]),
								'host_status': str(row[13]),
								'status': str(row[14]).upper(),
								'firewall': str(row[15]),
								'trustlevel': str(row[16]),
								'rack': str(row[17]),
								'power_up_priority': str(row[18]),
								'support_team': str(row[19]),
								'comments' :str(row[21]),
							},
						)
					result += 1
			except Exception as e:
				log += f'Row:{i}; Error:{e}\n'
		progress_recorder.set_progress(i, total_work)
	f = open(f"log_celery/log{datetime.now()}.txt", "w")
	f.write(log)
	f.close()
	if overwrite:
		call_command('rebuild_index', '--noinput')
	else:
		call_command('update_index', '--remove')
	return f'{result}/{total_work-1} added; {empty} empty hostname entries; {total_work-1-result-empty} errors'