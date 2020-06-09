#!/usr/bin/env python3
#group_amr.py
import argparse,sys,os,re,numpy as np
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", help="Input file to be grouped")
parser.add_argument("-a", "--accessory", nargs="+", help="Accessory file to help grouping")

args = parser.parse_args()
###################################################################################
try:
	infile = open(args.input, "r")

except IOError as err:
	sys.stderr.write(str(err))
	sys.exit(1)

# Setup dict of AMR genes linked to classes
amrDict = dict()
files = args.accessory
for file in files:
	amrfile = open(file, "r")
	for line in amrfile:
		if line.startswith("#"):
			pass
		else:
			line = line.rstrip().split(":")
			if len(line) > 2:
				alt_gene = line[2]
				if alt_gene != "":
					if alt_gene.startswith("Alternate name;"):
						alt_gene = re.sub("Alternate name; ","",alt_gene)
						if alt_gene not in amrDict:
							amrDict[alt_gene] = [line[1]]
	
			# Update to not contain "resistance" and prettify "metronidazole (5-nitroimidazole)"
			resistance = line[1]
			
			if "Aminoglycoside resistance" in resistance:
				resistance = "Aminoglycoside"
			elif "resistance" in resistance:
				resistance = re.sub(" resistance", "",resistance)	
			elif "metronidazole (5-nitroimidazole)" in resistance:
				resistance = "Nitroimidazole"
			elif "Folate pathway antagonist" in resistance:
				# Look at gene and its phenotype
				resistance = line[2]
			elif "Polymyxin" in resistance:
				resistance = line[2]
			
			if line[0] not in amrDict:
				amrDict[line[0]] = [resistance]
			else:
				if resistance in amrDict[line[0]]:
					pass
				else:
					sys.stdout.write("Warning, {} has multiple AMR class annotations\n".format(line[0]))
					amrDict[line[0]] += [resistance]

# Setup initial datamatrix
inlines = infile.readlines()
datamatrix = [[] for i in range(len(inlines))]

for i,line in enumerate(inlines):
	line = line.rstrip().split("\t")
	datamatrix[i] = line

# Time to map the AMR classes
unmapped_file = open("unmapped_amr.txt", "w+")
amr_map = dict()
unmapped,mapped = 0,0
for i,amr_gene in enumerate(datamatrix[0][1:]):
	gene = "'".join(amr_gene.split("_")[:-2]) # Exclude _1_"Accession number"
	gene = re.sub(r"'\d","",gene) # Because have remnants
	if gene in amrDict:
		if amrDict[gene][0] not in amr_map:
			amr_map[amrDict[gene][0]] = [i+1]
		else:
			amr_map[amrDict[gene][0]] += [i+1]
		mapped += 1
		
	else:
		if "Unclassified" not in amr_map:
			amr_map["Unclassified"] = [i+1]
		else:
			amr_map["Unclassified"] += [i+1]
		unmapped_file.write(gene + "\n")
		unmapped += 1

#  Setup newmatrix
newmatrix = [[] for i in range(len(inlines))]
newmatrix[0].append("sample")
for i,amr_class in enumerate(amr_map):
	newmatrix[0].append(amr_class)

# Aggregate data in newmatrix
for i,row in enumerate(datamatrix[1:]): # Skip first row
	newmatrix[i+1].append(row[0]) 
	for j,col in enumerate(newmatrix[0][1:]):
		newmatrix[i+1].insert(j+1,0)

		for pos in amr_map[col]:
			pass
			newmatrix[i+1][j+1] += float(datamatrix[i+1][pos])

# Update Unclassifed to contain number of unclassified genes and percentage of dataset
for i,amr_class in enumerate(newmatrix[0]):
	if amr_class == "Unclassified":
		newmatrix[0][i] = "Unclassified: {} ({:.2f}%)".format(unmapped,100*unmapped/(unmapped+mapped))

unmapped_file.close()
# Write to file
npmatrix = np.asmatrix(newmatrix)
outname = os.path.splitext(os.path.basename(args.input))[0] + ".class.tsv"
np.savetxt(outname, npmatrix, delimiter="\t",newline="\n",fmt="%s")
print(">>> Class file saved to: {}".format(outname))
print(">>> Number of AMR classes identified: {}".format(len(newmatrix[0])-2))
print(">>> {} gene(s) could not be linked to any known AMR class from metafile constituting {:.2f}% of dataset\n>>> {} was mapped to known AMR classes".format(unmapped,100*unmapped/(unmapped+mapped),mapped))