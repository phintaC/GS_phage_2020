#!/usr/bin/env python3 
# phage_philter.py
import sys, argparse, os

# Setup program parser
parser = argparse.ArgumentParser()

parser.add_argument("-i", help="Input file", required=True)
parser.add_argument("-o", nargs="?", help="Output file")
parser.add_argument("-acc", "--accessory", nargs="?", help="Accessory file containing metadata (imgvr) or genera (virus)")

args = parser.parse_args()

#######################################################################################################
# Setup various variables
delim = "\t"

phage_families = list(["Ackermannviridae","Myoviridae","Siphoviridae","Podoviridae", "Lipothrixviridae",\
 "Rudiviridae", "Ampullaviridae", "Bicaudaviridae", "Clavaviridae", "Corticoviridae", "Cystoviridae",\
 "Fuselloviridae", "Globuloviridae", "Guttaviridae", "Inoviridae", "Leviviridae", "Microviridae",\
 "Plasmaviridae", "Pleolipoviridae", "Portogloboviridae", "Sphaerolipoviridae", "Spiraviridae",\
 "Tectiviridae", "Tristromaviridae", "Turriviridae"])

phages = ("phage", "PHAGE", "Phage")
#######################################################################################################
# Identify database
database = ((args.i).split("/")[-1]).split("_")[0]
taxon = (args.i).split("_")[1] # Not relevant for imgvr, which will just return "id"

#######################################################################################################
# Open input file from which phages will be extracted
try:
	infile = open(args.i, "r")
except IOError as err: 
	sys.stderr.write("Error while loading file: {}\n".format(str(err)))
	sys.exit(1)

#######################################################################################################
# Acquire column names and index for row names ([0]) 
header = (infile.readline().rstrip()).split(delim)
dataset = set()
dataset.add((0,header[0]))

#######################################################################################################
# Use detected database to retrieve relvant information
if database == "virus" or database == "kvit":
	sys.stdout.write("\"{}\" file is being filtered..\n".format(database))
	
	genus_list = list()
	identity = str.maketrans("","", "\"'[]")
	# for hte vira
	if args.accessory is not None:
		# Extracts all genera (and other stuff) from a taxonomy file. 
		try:
			taxfile = open(args.accessory, "r")
		except IOError as err:
			sys.stderr.write("Can't open file {}: {}".format(args.accessory, str(err)))
			sys.exit(1)
		
		# Only difference is naming of species
		if database == "virus":
			for line in taxfile:
				genus_virus = (line.split(" ")[0]).translate(identity) + " virus"
				genus_list.add(genus_virus)
		elif database == "kvit":
			for line in taxfile:
				genus_virus = (line.split(" ")[0]).translate(identity) + "virus"
				genus_list.add(genus_virus)

	# Detects taxonomical level
	if taxon == "species":
		sys.stdout.write("Detected species level file...\n")
		
		for i,item in enumerate(header):
			# Check for phage in entry
			for phage in phages:
				if phage in item:
					dataset.add((i,item))
		
			# Check for bacterial "<genus> virus" in entry 
			for genus in genus_list:
				if genus in item:
					dataset.add((i,item))
	
	if taxon == "family":
		sys.stdout.write("Detected family level file...\n")

		for i,item in enumerate(header):
			for phage_fam in phage_families:
				if phage_fam in item:
					dataset.add((i,item))

#######################################################################################################
elif database == "imgvr":
	sys.stdout.write("\"{}\" file is being filtered...\n".format(database))
	
	if args.accessory is None:
		sys.stderr.write("Error! Metadata file (flag: -acc) required to perform filtering... Exiting...\n")
		sys.exit(1)
	
	else:
		sys.stdout.write("Acquiring data on bacterial phages from IMG/VR metadata...\n")
		acc_file = open(args.accessory, "r") # args.accessory = IMGVR_all_Sequence_information.tsv
		acc_header = acc_file.readline().split(delim)

		# Find index which indicate bacterial host origin
		for i,item in enumerate(acc_header):
			if item == "Host_domain":
				index = i
				break
		
		print("Creating UViG set...")
		uvig_set = set() # Entries of IMG/VR are denoted UViG (uncultivated viral genomes)

		# Make set of phage UViGs
		for line in acc_file:
			line = line.split(delim)
			if line[index] == "Bacteria":
				uvig_set.add(line[0])
		
		acc_file.close()
		
		# Query header items against the UViG set; fast look-up
		sys.stdout.write("Filtering bacterial phage UViGs from {}...\n".format((args.i).split("/")[-1]))
		for i,item in enumerate(header):
			if item in uvig_set:
				dataset.add((i,item))

#######################################################################################################
# Define output name
if args.o is not None:
	# User defined output name
	outname = args.o

else:
	abs_path = os.path.dirname(args.i) + "/phages/"

	if not os.path.exists(abs_path):
		os.mkdir(abs_path)

	# Default output name derived from input name
	outname = abs_path + ((args.i).split("/")[-1]).split(".")[0] + ".phages.txt"

sys.stdout.write("Writing file to:\t{}\n".format(outname))
outfile = open(outname, "w+")

#######################################################################################################
# Sort species and indices in different lists 
indices = list()
col_names = list()

for tup in sorted(dataset):
	col_names.append(tup[1])
	indices.append(tup[0])
dataset.clear()

# Write the first line to file
outfile.write("\t".join(col_names) + "\n")
col_names.clear()
tup_counter = 0
# Write remaining data to file
for line in infile:
	line = line.rstrip().split("\t")
	for index in indices: 
		outfile.write(line[index] + "\t")
	outfile.write("\n")

infile.close()
outfile.close()

#######################################################################################################
