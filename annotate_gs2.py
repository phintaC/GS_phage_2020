#!/usr/bin/env python3
# renaming.py
import sys,os,argparse,re,csv

parser = argparse.ArgumentParser()

parser.add_argument("-g", "--geo_file", help="File containing metadata on mapped sample names")
parser.add_argument("-i", "--input", nargs="+", help="Input file to have sample names replaced")
parser.add_argument("-o", "--output", help="Output directory")
parser.add_argument("-s", "--sort", help="When selected, sorts the dataset on region", action="store_true")

args = parser.parse_args()
###################################################################################
# Setup replacement dict
replacements = dict()
regions = dict()

try: 
	with open(args.geo_file, "r") as infile:
		line = infile.readline() # 0: sample name; 1: country_alpha2; 2: country_alpha3; 3: country; 4: continent; 5: comment
		# Metadata lines
		for line in infile:
			contents = line.rstrip().split("\t")

			if "missing" in contents[-1]:
				pass
			elif "excluded" in contents[-1]:
				pass
			elif "remapped" in contents[-1]:
				pass

			else:
				if contents[0] not in replacements:
					replacements[contents[0]] = contents[2]
				else:
					sys.stdout.write("### {} already logged in dict, with value(s): {}\n>>> Overwriting with entry: {}\n".format(contents[1], replacements[contents[1]], contents[0]))
					replacements[contents[0]] = contents[2]

				if contents[0] not in regions:
					regions[contents[0]] = contents[6]
				else: 
					sys.stdout.write("### {} is already annotated with region: {}\n".format(contents[0], regions[contents[0]]))

except IOError as err:
	sys.stderr.write("Error while opening geo file: {}\n".format(str(err)))
	sys.exit(1)

# Replace old sample names with new
files = args.input

for file in files:
	sys.stdout.write("######### Working on {} #########\n".format(os.path.basename(file)))
	try:
		infile = open(file, "r")
	except IOError as err:
		sys.stderr.write("Error while loading input file: {}\n".format(str(err)))
		sys.exit(1)
	
	# Read entire file to memory
	lines = infile.readlines()
	row_num = 1
	discarded_num = 0
	# Setup datamatrix to store the data
	datamatrix = [[] for i in range(len(lines))]
	# Add the first line of the file to the datamatrix
	datamatrix[0] = lines[0].rstrip().split("\t")
	# Annotate region 
	datamatrix[0].insert(1,"region")

	for line in lines[1:]:
		
		# Insert the line in the datamatrix as a list of data
		datamatrix[row_num] = line.rstrip().split("\t")
		
		### Add regional annotation ### 
		if datamatrix[row_num][0] in regions:
			datamatrix[row_num].insert(1,regions[datamatrix[row_num][0]])

		else:
			key = re.sub(r"(DTU\d{4}_MG_\d{1,3}(_\w\D{1,2}){2,3}(_\w)?(_\d{1,3}){0,2}(_re_\d{1,2})?)(_.+)$",r"\1", datamatrix[row_num][0])
			
			if key in regions: 
				datamatrix[row_num].insert(1,regions[key])

		
		### Change display name ###
		# Check if the sample name is in the dictionary; if True, replace the name
		if datamatrix[row_num][0] in replacements:
			datamatrix[row_num][0] = replacements[datamatrix[row_num][0]]

		else:
			# The mapped samples may contain "_R1"
			key = re.sub(r"(DTU\d{4}_MG_\d{1,3}(_\w\D{1,2}){2,3}(_\w)?(_\d{1,3}){0,2}(_re_\d{1,2})?)(_.+)$",r"\1", datamatrix[row_num][0])

			if key in replacements:
				datamatrix[row_num][0] = replacements[key]
		row_num += 1
	infile.close()

	print("Number of samples: {}".format(len(datamatrix)-1))

	if args.sort:
		print("Sorting relative abundance on region for PCoA...")
		# Sort the output according to region (for PCoA analysis)
		head = datamatrix[0]
		datamatrix = sorted(datamatrix[1:], key=lambda x: x[1])
		datamatrix.insert(0,head)

	# Write data to file
	if args.output is None:
		outname = os.path.dirname(file) + "/" + os.path.basename(args.geo_file).split("_")[0] + "_" + os.path.basename(file)
	else: 
		outname = args.output + "/" + os.path.basename(args.geo_file).split("_")[0] + "_" + os.path.basename(file)

	try:
		sys.stdout.write("Writing data to: {}\n".format(outname))
		with open(outname, "w+") as outfile:
			csvwriter = csv.writer(outfile, delimiter="\t")
			csvwriter.writerows(datamatrix)

	except IOError as err:
		sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
		sys.exit(1)

# Print number of samples from each region; relevant for PCoA analysis annotation
if args.sort:
	africa, asia, europe, mideast, oceania, namerica, samerica = 0,0,0,0,0,0,0
	for row in datamatrix:
		if row[1] == "Africa":
			africa += 1
		elif row[1] == "Asia":
			asia += 1
		elif row[1] == "Europe":
			europe += 1
		elif row[1] == "Middle East":
			mideast += 1
		elif row[1] == "Oceania":
			oceania += 1
		elif row[1] == "North America":
			namerica += 1
		elif row[1] == "South America":
			samerica += 1

	sys.stdout.write("# samples from Africa:\t{}\n\
# samples from Asia:\t{}\n\
# samples from Europe:\t{}\n\
# samples from Middle East:\t{}\n\
# samples from North America:\t{}\n\
# samples from Oceania:\t{}\n\
# samples from South America:\t{}\n".format(africa,asia,europe,mideast,namerica,oceania,samerica))