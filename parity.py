from codecs import open
from ConfigParser import ConfigParser
from os import path, mkdir
from random import randint
from re import sub
from shutil import rmtree
from string import ascii_letters, digits
from subprocess import call
from sys import argv
from time import sleep
from urllib2 import Request, urlopen, HTTPError, quote

def process_ignore_patterns(text, ignore_patterns):
	s = text
	for pattern in ignore_patterns:
		s = sub(pattern, '', s)
	return s

def fetch_url(url, headers=None, data=None):
	if data:
		headers['Content-Length'] = len(data)
	attempt = 0
	while attempt < 5:
		try:
			request = Request(url, headers=headers, data=data)
			response = urlopen(request, timeout=300).read().decode('utf-8')
			return response
			attempt += 1
		except HTTPError:
			sleep(randint(1, 10))
	return None

def escape_filename(raw_filename):
	valid_chars = '-_.()' + ascii_letters + digits
	filename = ''.join(c if c in valid_chars else '_' for c in raw_filename)
	return filename

def compare_responses(control_url, control_response, treatment_url, treatment_response, fields):
	output_path_prefix = path.join(output_directory, escape_filename('_'.join(fields)))
	output_file = open(output_path_prefix+'.control.txt', mode='w', encoding='utf-8')
	output_file.write(control_url + '\n\n')
	output_file.write((control_response if control_response else 'No response') + '\n')
	output_file.close()
	output_file = open(output_path_prefix+'.treatment.txt', mode='w', encoding='utf-8')
	output_file.write(treatment_url + '\n\n')
	output_file.write((treatment_response if treatment_response else 'No response') + '\n')
	output_file.close()
	output_file = open(output_path_prefix+'.diff.txt', mode='w', encoding='utf-8')
	call('diff {0}.control.txt {0}.treatment.txt'.format(output_path_prefix), stdout=output_file)
	output_file.close()

if __name__ == '__main__':
	# Clear output directory.
	output_directory = path.join(path.dirname(path.realpath(__file__)), 'output')
	if path.exists(output_directory):
		rmtree(output_directory)
	mkdir(output_directory)
	
	# Parse settings.
	if len(argv) > 1:
		settings_filename = argv[1]
	else:
		settings_filename = path.join(path.dirname(path.realpath(__file__)), 'SimpleParity.ini')
	settings_file = open(settings_filename, mode='r', encoding='utf-8')
	settings = ConfigParser()
	settings.readfp(settings_file)
	settings_file.close()
	control_url_format = settings.get('Settings', 'ControlUrlFormat')
	treatment_url_format = settings.get('Settings', 'TreatmentUrlFormat')
	post_data_format = settings.get('Settings', 'PostDataFormat') if settings.has_option('Settings', 'PostDataFormat') else None
	query_filename = settings.get('Settings', 'QueryFilename')
	headers = {k:v for (k,v) in settings.items('Headers')} if settings.has_section('Headers') else {}
	ignore_patterns = [v.strip() for (k,v) in settings.items('Ignore')] if settings.has_section('Ignore') else []
	
	# Process queries.
	query_count = 0
	match_count = 0
	query_file = open(query_filename, mode='r', encoding='utf-8')
	for line in query_file:
		line = line.strip()
		if not line:
			continue
		query_count += 1
		if query_count % 100 == 0:
			print('Processing query {0}.'.format(query_count))
		fields = [quote(x) for x in line.split('\t')]
		control_url = control_url_format.format(*fields)
		treatment_url = treatment_url_format.format(*fields)
		post_data = post_data_format.format(*fields) if post_data_format else None
		control_response = fetch_url(control_url, headers, post_data)
		control_response = process_ignore_patterns(control_response, ignore_patterns)
		treatment_response = fetch_url(treatment_url, headers, post_data)
		treatment_response = process_ignore_patterns(treatment_response, ignore_patterns)
		if not control_response or control_response != treatment_response:
			compare_responses(control_url, control_response, treatment_url, treatment_response, fields)
		else:
			match_count += 1
	query_file.close()

	print('{0}/{1} queries matched.'.format(match_count, query_count))
