import csv
import os
import json
import uuid
import glob

files = glob.glob("files/*.txt")

for f in files:
	dataFile = f.replace("files/","")
	thing = dataFile.split('.')
	print(thing[5])



# write data for study with just submitter id of PHS# of project
studyData = []
study = {}
study["type"] = "Study"
study["submitter_id"] = "phs000007.v30"
studyData.append(study)
print("writing data file for: Study")
with open("data/Study.json", "w+") as o:
	o.write(json.dumps(studyData))

nodes = {}
with open("nodes.json", "r") as n:
	nodes = json.loads(n.read())

for n in nodes:
	print("writing data file for:", n)
	with open(nodes[n]["file"], "r") as f:
		header = True
		nodeData = []
		ittr = 0
		for line in f:
			if line[0] == "#" or len(line) < 2:
				continue
			elif header:
				heads = line.replace('\n',"").split('\t')
				heads.append("submitter_id")
				header = False
			else:
				entity = {}
				entity["type"] = n
				data = line.replace('\n',"").split('\t')
				size = len(data)
				for i in range(size):
					entity[heads[i]] = data[i]
				entity["submitter_id"] = str(uuid.uuid4())
				entity["studies"] = {}
				entity["studies"]["submitter_id"] = "phs001062.v3"
				nodeData.append(entity)

		writeFile = "data/" + n + ".json"

		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))
