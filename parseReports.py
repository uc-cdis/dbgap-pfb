import json
import xml.etree.ElementTree as ET
import glob
import argparse
import xmltodict

def parseOptions():
	parser = argparse.ArgumentParser(description="parse the data dictionaries of unharmonized dbGaP studies")
	parser.add_argument('-d', help="directory of dbGaP study", required=True)
	parser.add_argument('-c', help="consent group value, in the files this is something like c1 or c2. Just put the number", required=True)
	parser.add_argument('-o', help="output file for pfb schema", required=True)

	args = parser.parse_args()

	return args


def parse_var_report(filename, dictionary, consent):
	print("Parsing ", filename)
	with open(filename , "r") as f:
		parsedDict = xmltodict.parse(f.read(),  attr_prefix='', dict_constructor=dict)

		i = 0
		while i < len(parsedDict["data_table"]["variable"]):
			var_id = parsedDict["data_table"]["variable"][i]["id"]
			if ".c" in var_id and ".c" + consent not in var_id:
				del parsedDict["data_table"]["variable"][i]
			else:
				i += 1

		dictionary[parsedDict["data_table"]["name"]] = parsedDict

	return


args = parseOptions()
location = args.d
output_file = args.o
consent_val = args.c

# grab all the variable report files from the given directory
if location.endswith("/"):
	fileFind = location + "*.var_report.xml"
else:
	fileFind = location + "/*.var_report.xml"

files = glob.glob(fileFind)

var_report_dictionary = {}

for f in files:
	parse_var_report(f, var_report_dictionary, consent_val)

# output the parsed report to the output_file
with open(output_file, "w+") as w:
	w.write(json.dumps(var_report_dictionary))

