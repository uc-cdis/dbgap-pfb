import json
import xml.etree.ElementTree as ET
import glob
import argparse


def parseOptions():
	parser = argparse.ArgumentParser(description="parse the data dictionaries of unharmonized dbGaP studies")
	parser.add_argument('-d', help="directory of dbGaP study", required=True)
	parser.add_argument('-o', help="output file for pfb schema", required=True)
	args = parser.parse_args()

	return args


def parse_dbgap_dictionary(name, dictionary, filename):
	with open(filename, "r") as f:
		# initial parse of xml
		tree = ET.parse(f)
		root = tree.getroot()

		tableName = filename.split('/')[-1]
		nodeName = filename.split(".")[4]

		# create dictionary structure
		props = {}
		props["id"] = name
		props["title"] = name
		props["validators"] = None
		props["term"] = {}
		props["term"]["$ref"] = "_terms.yaml#/" + nodeName
		props["$schema"] = "http://json-schema.org/draft-04/schema#"
		props["type"] = "object"
		props["category"] = "clinical"
		props["project"] = "*"
		props["program"] = "*"
		props["additionalProperties"] = False
		props["properties"] = {}


		# setting up table values in metadata
		dictionary["_terms.yaml"][nodeName] = {}
		dictionary["_terms.yaml"][nodeName]["termDef"] = {}
		for i in root.attrib:
			dictionary["_terms.yaml"][nodeName]["termDef"][i] = root.attrib[i]

		# initializing a dictionary to hold variable names and phv key pairs
		variables = {}

		for child in root:
			# Get table descriptions
			if child.tag == "description" and child.text != None:
				dictionary["_terms.yaml"][nodeName]["termDef"]["description"] = child.text

			# Get variable PHV values
			if child.tag == "variable":
				for c in child:
					if c.tag == "name":
						variables[c.text] = child.attrib["id"]
						dictionary["_terms.yaml"][c.text] = {}
						dictionary["_terms.yaml"][c.text]["termDef"] = {} 
						dictionary["_terms.yaml"][c.text]["termDef"]["id"] = child.attrib["id"] 


		# parse xml structure
		for item in root.findall('./variable'):
			# get the name of the variable in dictionary
			props["properties"][item[0].text] = {}
			
			# need to handle enumerated values if need be
			enums = {}

			# loop through the variable properties
			for child in item:
				attribute = None
				tag = child.tag

				# if tag is name we can skip
				if tag == "name":
					continue
				
				# if we have a value tag then we know that we will have enumerated vaules 
				if tag == "value" and child.attrib != {}:
					# print(child.attrib['code'])
					enums[child.attrib["code"]] = child.text

				if child.attrib != {}:
					attribute = child.attrib
				value = child.text
				
				props["properties"][item[0].text][tag] = value
			if enums != {}:
				enums[""] = "Null"
				enums[" "] = "Null"
				enums["NEVER DONE BEFORE"] = "Null"
				enums["-9"] = "Null"
				# props["properties"][item[0].text]["enum"] = list(enums.keys())
				# props["properties"][item[0].text]["enumDef"] = []
				dictionary["_terms.yaml"][item[0].text]["termDef"]["enumerated_values"] = []
				for e in enums:
					enum = {}
					enum["enumeration"] = e
					enum["value"] = enums[e]
					dictionary["_terms.yaml"][item[0].text]["termDef"]["enumerated_values"].append(enum)

				# del props["properties"][item[0].text]["type"]
				# del props["properties"][item[0].text]["value"]

			props["properties"][item[0].text]["type"] = "string"

			props["properties"][item[0].text]["term"] = {}
			props["properties"][item[0].text]["term"]["$ref"] = "_terms.yaml#/"+item[0].text

			if props["properties"][item[0].text]["description"]:
				dictionary["_terms.yaml"][item[0].text]["termDef"]["description"] = props["properties"][item[0].text]["description"]



		props["properties"]["dbGaP_Subject_ID"] = {}
		props["properties"]["dbGaP_Subject_ID"]["description"] = "dbGaP subject variable"
		props["properties"]["dbGaP_Subject_ID"]["type"] = "string"

		props["properties"]["dbGaP_Sample_ID"] = {}
		props["properties"]["dbGaP_Sample_ID"]["description"] = "dbGaP sample variable"
		props["properties"]["dbGaP_Sample_ID"]["type"] = "string"

		props["properties"]["BioSample Accession"] = {}
		props["properties"]["BioSample Accession"]["description"] = "dbGaP BioSample Accession variable"
		props["properties"]["BioSample Accession"]["type"] = "string"

		dictionary[name] = props

	return dictionary


# parse the arguments for the directory of the dbGaP data
args = parseOptions()
location = args.d
outputSchema = args.o

# use glob to find all the data dictionary files
if location.endswith("/"):
	fileFind = location + "*.data_dict.xml"
else:
	fileFind = location + "/*.data_dict.xml"
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


with open(outputSchema, "w+") as w:
	print("Writing to " + outputSchema)
	w.write(json.dumps(dictionary))


