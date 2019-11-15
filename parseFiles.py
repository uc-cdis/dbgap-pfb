import glob
import gzip
import json
import uuid
import argparse

def parseOptions():
	parser = argparse.ArgumentParser(description="parse the data dictionaries of unharmonized dbGaP studies")
	parser.add_argument('-d', help="directory of dbGaP study", required=True)
	parser.add_argument('-p', help="phs number of dbGaP study", required=True)
	parser.add_argument('-c', help="consent group number", required=True)
	parser.add_argument('-o', help="output directory for data files", required=True)

	args = parser.parse_args()

	return args


def writeStudyNode(phs, output):
	# writing node for study with one phs number
	studyData = []
	study = {}
	study["type"] = "Study"
	study["submitter_id"] = phs
	studyData.append(study)
	fileName = output + "/Study.json"
	with open(fileName, "w+") as o:
		o.write(json.dumps(studyData))


def parseSubjects(fileName, nodeName, consent, output):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		consent_var = ""
		for line in data:
			try:
				line = line.decode("utf-8")
			except Exception as e:
				print("hey utf-8 didn't work so we are going to try iso")
				line = line.decode('iso-8859-1')
			if line[0] == "#" or len(line) < 2:
				continue
			elif header:
				heads = line.replace('\n',"").split('\t')
				for h in heads:
					if "consent" in h.lower() or h.lower() == "gencons":
						consent_var = h
						break
				heads.append("submitter_id")
				header = False
			else:
				entity = {}
				entity["type"] = "subject"
				data = line.replace('\n',"").split('\t')
				size = len(data)
				for i in range(size):
					entity[heads[i]] = data[i]
				entity["submitter_id"] = str(uuid.uuid4())
				entity["studies"] = {}
				entity["studies"]["submitter_id"] = phs
				if entity[consent_var] == str(consent):
					nodeData.append(entity)

		# write the file for subject
		writeFile = output + "/" + nodeName + ".json"
		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))

		return nodeData

def parseSample(fileName, nodeName, subjects, output):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		subject_var = ""
		for line in data:
			try:
				line = line.decode("utf-8")
			except Exception as e:
				print("hey utf-8 didn't work so we are going to try iso")
				line = line.decode('iso-8859-1')
			if line[0] == "#" or len(line) < 2:
				continue
			elif header:
				heads = line.replace('\n',"").split('\t')
				heads.append("submitter_id")
				header = False
			else:
				entity = {}
				entity["type"] = "sample"
				lineData = line.replace('\n',"").split('\t')
				size = len(lineData)
				for i in range(size):
					entity[heads[i]] = lineData[i]
				entity["submitter_id"] = str(uuid.uuid4())
				entity["studies"] = {}
				entity["studies"]["submitter_id"] = phs
				if entity["dbGaP_Subject_ID"] in subjects:
					nodeData.append(entity)

		print("Number of sample records:", len(nodeData))

		# write the file for sample
		writeFile = output + "/" + nodeName + ".json"
		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))

		return


def parsePedigree(fileName, nodeName, subjects, output):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		for line in data:
			try:
				line = line.decode("utf-8")
			except Exception as e:
				print("hey utf-8 didn't work so we are going to try iso")
				line = line.decode('iso-8859-1')
			if line[0] == "#" or len(line) < 2:
				continue
			elif header:
				heads = line.replace('\n',"").split('\t')
				heads.append("submitter_id")
				header = False
			else:
				entity = {}
				entity["type"] = "pedigree"
				lineData = line.replace('\n',"").split('\t')
				size = len(lineData)
				for i in range(size):
					entity[heads[i]] = lineData[i]
				entity["submitter_id"] = str(uuid.uuid4())
				entity["studies"] = {}
				entity["studies"]["submitter_id"] = phs
				if entity["dbGaP_Subject_ID"] in subjects:
					nodeData.append(entity)

		print("Number of pedigree records:", len(nodeData))

		# write the file for pedigree
		writeFile = output + "/" + nodeName + ".json"
		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))

		return


def parseDataFile(fileName, nodeName, output):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		subject_var = ""
		for line in data:
			try:
				line = line.decode("utf-8")
			except Exception as e:
				print("hey utf-8 didn't work so we are going to try iso")
				line = line.decode('iso-8859-1')
			if line[0] == "#" or len(line) < 2:
				continue
			elif header:
				heads = line.replace('\n',"").split('\t')
				heads.append("submitter_id")
				header = False
			else:
				entity = {}
				entity["type"] = nodeName
				lineData = line.replace('\n',"").split('\t')
				size = len(lineData)
				for i in range(size):
					entity[heads[i]] = lineData[i]
				entity["submitter_id"] = str(uuid.uuid4())
				entity["studies"] = {}
				entity["studies"]["submitter_id"] = phs
				
				nodeData.append(entity)

		# write the file for all the nodes
		writeFile = output + "/" + nodeName + ".json"
		with open(writeFile, "w+") as o:
			for chunk in json.JSONEncoder(indent=2).iterencode(nodeData):
				o.write(chunk)
			# o.write(json.dumps(nodeData))
		return


# parse argumens and return if required ones are not given
args = parseOptions()
location = args.d
phs = args.p
consent = args.c
output = args.o

# use glob to find all files from location that are .txt.gz files
if location.endswith("/"):
	fileFind = location + "*.txt.gz"
else:
	fileFind = location + "/*.txt.gz"
files = glob.glob(fileFind)


print("Outputting to", output, "directory")

# Write initial study node. Only contains one field of submitter id that is the phs of the project
print("Writing data file for: Study")
writeStudyNode(phs, output)


nodes = {}
dataFiles = []

# 
for f in files:
	dataFile = f.replace(location,"")
	thing = dataFile.split('.')
	if "c" + str(consent) in thing[5]:
		file = {}
		file["fileName"] = f
		file["nodeName"] = thing[6]
		dataFiles.append(file)
	elif "Subject" in thing[5] and thing[6] == "MULTI":
		subject = {}
		subject["file"] = f
		subject["name"] = thing[5]
		nodes["subject"] = subject
	elif "Sample" in thing[5] and thing[6] == "MULTI":
		sample = {}
		sample["file"] = f
		sample["name"] = thing[5]
		nodes["sample"] = sample
	elif "Pedigree" in thing[5] and thing[6] == "MULTI":
		pedigree = {}
		pedigree["file"] = f
		pedigree["name"] = thing[5]
		nodes["pedigree"] = pedigree

# parse and write subject file
print("Writing data file for: Subject")
subjects = parseSubjects(nodes["subject"]["file"], nodes["subject"]["name"], consent, output)

# grab the subject ids that are in the consent that we are looking for
subject_ids = []
for s in subjects:
	subject_ids.append(s['dbGaP_Subject_ID'])

# print(subject_ids)

print("Number of subjects with matching consent: ", str(len(subject_ids)))

# parse and write sample file
parseSample(nodes["sample"]["file"], nodes["sample"]["name"], subject_ids, output)

# parse and write pedigree file if it exists
if "pedigree" in nodes.keys():
	parsePedigree(nodes["pedigree"]["file"], nodes["pedigree"]["name"], subject_ids, output)

print("Writing the rest of the data files")
for d in dataFiles:
	parseDataFile(d["fileName"], d["nodeName"], output)
