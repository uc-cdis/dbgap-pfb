import glob
import gzip
import json
import uuid
import argparse

def parseOptions():
	parser = argparse.ArgumentParser(description="parse the data dictionaries of unharmonized dbGaP studies")
	parser.add_argument('-d', help="directory of dbGaP study", required=True)
	parser.add_argument('-p', help="phs number os dbGaP study", required=True)
	args = parser.parse_args()

	return args


def writeStudyNode(phs):
	# writing node for study with one phs number
	studyData = []
	study = {}
	study["type"] = "Study"
	study["submitter_id"] = phs
	studyData.append(study)
	with open("data/Study.json", "w+") as o:
		o.write(json.dumps(studyData))


def parseSubjects(fileName, nodeName):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		consent_var = ""
		for line in data:
			line = line.decode("utf-8")
			if line[0] == "#" or len(line) < 2:
				continue
			elif header:
				heads = line.replace('\n',"").split('\t')
				for h in heads:
					if "consent" in h:
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
				nodeData.append(entity)
		ittr = 0
		while ittr < len(nodeData):
			if nodeData[ittr][consent_var] != "2":
				del nodeData[ittr]
			else:
				ittr += 1

		# write the file for subject
		writeFile = "data/" + nodeName + ".json"
		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))

		return nodeData

def parseSample(fileName, nodeName, subjects):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		subject_var = ""
		for line in data:
			line = line.decode("utf-8")
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

		print("number of sample records:")
		print(len(nodeData))

		# write the file for sample
		writeFile = "data/" + nodeName + ".json"
		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))

		return


def parsePedigree(fileName, nodeName, subjects):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		for line in data:
			line = line.decode("utf-8")
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

		print("number of pedigree data")
		print(len(nodeData))

		# write the file for pedigree
		writeFile = "data/" + nodeName + ".json"
		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))

		return


def parseDataFile(fileName, nodeName):
	with gzip.open(fileName, "r") as data:
		header = True
		nodeData = []
		subject_var = ""
		for line in data:
			line = line.decode("utf-8")
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
		writeFile = "data/" + nodeName + ".json"

		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))
		return


# parse argumens and return if required ones are not given
args = parseOptions()
location = args.d
phs = args.p

# use glob to find all files from location that are .txt.gz files
fileFind = location + "*.txt.gz"
files = glob.glob(fileFind)

# Write initial study node. Only contains one field of submitter id that is the phs of the project
print("Writing data file for: Study")
writeStudyNode(phs)


nodes = {}
dataFiles = []

# 
for f in files:
	dataFile = f.replace(location,"")
	thing = dataFile.split('.')
	if "c2" in thing[5]:
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
subjects = parseSubjects(nodes["subject"]["file"], nodes["subject"]["name"])

# grab the subject ids that are in the consent that we are looking for
subject_ids = [] 
for s in subjects:
	subject_ids.append(s['dbGaP_Subject_ID'])

# print(subject_ids)

print("Number of subjects with matching consent: ", str(len(subject_ids)))

# parse and write sample file
parseSample(nodes["sample"]["file"], nodes["sample"]["name"], subject_ids)

# parse and write pedigree file if it exists
if "pedigree" in nodes.keys():
	parsePedigree(nodes["pedigree"]["file"], nodes["pedigree"]["name"], subject_ids)

print("Writing the rest of the data files")
for d in dataFiles:
	parseDataFile(d["fileName"], d["nodeName"])
