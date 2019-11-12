import json
import xml.etree.ElementTree as ET
import glob
import argparse


def parseOptions():
	parser = argparse.ArgumentParser(description="parse the data dictionaries of unharmonized dbGaP studies")
	parser.add_argument('-d', help="directory of dbGaP study", required=True)
	args = parser.parse_args()

	return args


def parse_dbgap_dictionary(name, dictionary, filename):
	with open(filename, "r") as f:
		# initial parse of xml
		tree = ET.parse(f)
		root = tree.getroot()

		# create dictionary structure
		props = {}
		props["id"] = name
		props["title"] = name
		props["validators"] = None
		props["$schema"] = "http://json-schema.org/draft-04/schema#"
		props["type"] = "object"
		props["category"] = "clinical"
		props["project"] = "*"
		props["program"] = "*"
		props["additionalProperties"] = False
		props["properties"] = {}

		# parse xml structure
		for item in root.findall('./variable'):
			# get the name of the variable in dictionary
			props["properties"][item[0].text] = {}
			
			# loop through the variable properties
			for child in item:
				attribute = None
				tag = child.tag
				if tag == "name":
					continue
				if child.attrib != {}:
					attribute = child.attrib
				value = child.text
				
				props["properties"][item[0].text][tag] = value
			props["properties"][item[0].text]["type"] = "string"

		dictionary[name] = props
	return dictionary


# parse the arguments for the directory of the dbGaP data
args = parseOptions()
location = args.d

# use glob to find all the data dictionary files
fileFind = location + "*.data_dict.xml"
files = glob.glob(fileFind)

# load the default dictionary schema with study 
dictionary = ""
with open("default-schema.json", "r") as schema:
	print("Reading default schema")
	dictionary = json.loads(schema.read())

print("Parsing dictionaries")
for f in files:
	# split the file name to get the node name
	fileSections = f.replace(location,"").split('.')
	nodeName = fileSections[4]

	# set up the dictionary with all of the properties from the data dictionary files
	dictionary = parse_dbgap_dictionary(nodeName, dictionary, f)
	
	# set up submitter id's and links
	dictionary[nodeName]["properties"]["submitter_id"] = {}
	dictionary[nodeName]["properties"]["submitter_id"]["description"] = "submitter_id"
	dictionary[nodeName]["properties"]["submitter_id"]["type"] = "string"

	# in the manifest we establish links between node. Simplest way is with the submitter_id
	dictionary[nodeName]["properties"]["studies"] = {}
	dictionary[nodeName]["properties"]["studies"]["submitter_id"] = {}
	dictionary[nodeName]["properties"]["studies"]["submitter_id"]["type"] = "string"
	dictionary[nodeName]["properties"]["studies"]["submitter_id"]["description"] = "submitter_id"

	# linking every
	dictionary[nodeName]["links"] = []
	dictLink = {}
	dictLink["backref"] = str(nodeName) + "s"
	dictLink["name"] = "studies"
	dictLink["multiplicity"] = "one_to_one"
	dictLink["required"] = True
	dictLink["target_type"] = "Study"
	dictLink["label"] = "member_of"

	# append the links to the dictionary
	dictionary[nodeName]["links"].append(dictLink)


with open("dbgap-schema.json", "w+") as w:
	print("Writing to dbgap-schema.json")
	w.write(json.dumps(dictionary))
# print(json.dumps(dictionary))


