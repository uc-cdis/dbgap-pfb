import json
import xml.etree.ElementTree as ET

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
				
				if attribute:
					# if the xml has attributes the property is an enumerated value
					if not props["properties"][item[0].text].__contains__("enum"):
						props["properties"][item[0].text]["enum"] = []
						del(props["properties"][item[0].text]["type"])

					props["properties"][item[0].text]["enum"].append(attribute["code"])
				else:
					# if not then it is a single value property
					if value == "Numeric":
						value = "string"
					props["properties"][item[0].text][tag] = value

		dictionary[name] = props
	return dictionary

dicts = {}
with open("dicts.json", "r") as d:
	dicts = json.loads(d.read())

dictionary = json.loads(r'{"_definitions.yaml":{"datetime":{"oneOf":[{"type":"string","format":"date-time"},{"type":"null"}],"term":{"$ref":"_terms.yaml#/datetime"}},"UUID":{"pattern":"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$","term":{"$ref":"_terms.yaml#/UUID"},"type":"string"},"to_one":{"anyOf":[{"items":{"minItems":1,"maxItems":1,"$ref":"#/foreign_key"},"type":"array"},{"$ref":"#/foreign_key"}]},"foreign_key":{"additionalProperties":true,"type":"object","properties":{"id":{"$ref":"#/UUID"},"submitter_id":{"type":"string"}}}},"_terms.yaml":{"datetime":{"description":"A combination of date and time of day in the form [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm]\n"},"UUID":{"termDef":{"term_url":"https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&version=16.02d&ns=NCI_Thesaurus&code=C54100","source":"NCIt","term":"Universally Unique Identifier","cde_version":null,"cde_id":"C54100"},"description":"A 128-bit identifier. Depending on the mechanism used to generate it, it is either guaranteed to be different from all other UUIDs/GUIDs generated until 3400 AD or extremely likely to be different. Its relatively small size lends itself well to sorting, ordering, and hashing of all sorts, storing in databases, simple allocation, and ease of programming in general.\n"}}}')

for d in dicts:
	dictionaryFile = dicts[d]["file"]
	# set up the dictionary with all of the properties from the data dictionary files
	dictionary = parse_dbgap_dictionary(d, dictionary, dictionaryFile)
	
	# set up submitter id's and links
	dictionary[d]["properties"]["submitter_id"] = {}
	dictionary[d]["properties"]["submitter_id"]["description"] = "submitter_id"
	dictionary[d]["properties"]["submitter_id"]["type"] = "string"

	if dicts[d]["link"]:
		# in the manifest we establish links between node. Simplest way is with the submitter_id
		link = dicts[d]["link"]
		dictionary[d]["properties"][link] = {}
		dictionary[d]["properties"][link]["submitter_id"] = {}
		dictionary[d]["properties"][link]["submitter_id"]["type"] = "string"
		dictionary[d]["properties"][link]["submitter_id"]["description"] = "submitter_id"

		dictionary[d]["links"] = []
		dictLink = {}
		dictLink["backref"] = link
		dictLink["name"] = str(d) + "s"
		dictLink["multiplicity"] = "one_to_one"
		dictLink["required"] = True
		dictLink["target_type"] = "program"
		dictLink["label"] = "member_of"
		# append the links to the dictionary
		dictionary[d]["links"].append(dictLink)

	else:
		dictionary[d]["links"] = []

with open("dbgap-schema-new.json", "w+") as w:
	w.write(json.dumps(dictionary))
# print(json.dumps(dictionary))


