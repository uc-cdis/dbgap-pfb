import csv
import os
import json

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
				heads = line.split('\t')
				for h in heads:
					if h == nodes[n]["submitter_id"]:
						heads[ittr] = "submitter_id"
					ittr += 1
				header = False
			else:
				entity = {}
				entity["type"] = n
				data = line.split('\t')
				size = len(data)
				for i in range(size):
					entity[heads[i]] = data[i]
				nodeData.append(entity)


		writeFile = "data/" + n + ".json"

		with open(writeFile, "w+") as o:
			o.write(json.dumps(nodeData))
