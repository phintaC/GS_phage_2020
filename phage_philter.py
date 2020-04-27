#!/usr/bin/env python3 
# phage_philter.py
import sys, argparse, os

# Setup program parser
parser = argparse.ArgumentParser()

parser.add_argument("-i", help="Input file", required=True)
parser.add_argument("-acc", "--accessory", nargs="?", help="Accessory file containing metadata (imgvr) or genera (virus)")
parser.add_argument("-gbk", "--genbank", help="File containing GenBank accession numbers")
parser.add_argument("-nc", "--refseq", help="File containing RefSeq accession numbers (NC_)")

args = parser.parse_args()

#######################################################################################################
# Setup various variables
delim = "\t"

phage_families = list(["Ackermannviridae","Myoviridae","Siphoviridae","Podoviridae", "Lipothrixviridae",\
 "Clavaviridae", "Corticoviridae", "Cystoviridae","Guttaviridae", "Inoviridae", "Leviviridae", "Microviridae",\
 "Plasmaviridae", "Pleolipoviridae", "Portogloboviridae", "Sphaerolipoviridae", "Spiraviridae", "Tectiviridae",\
 "Tristromaviridae", "Turriviridae"])
# Archaeal phage families: Ampullaviridae; Bicaudaviridae; Fuselloviridae; Globuloviridae; Rudiviridae; ~Tectiviridae (shared)

phages = ("phage", "PHAGE", "Phage")
#######################################################################################################
# Identify database
database = ((args.i).split("/")[-1]).split("_")[0]
taxon = (args.i).split("_")[1] # Not relevant for imgvr, which will just return "id" = UViG

#######################################################################################################
# Open input file from which phages will be extracted
try:
	infile = open(args.i, "r")
except IOError as err: 
	sys.stderr.write("Error while loading file: {}\n".format(str(err)))
	sys.exit(1)

#######################################################################################################
# Acquire column names and index for row ([0]) 
header = (infile.readline().rstrip()).split(delim)
phage_list = list() # List storing index of phages
virus_list = list() # List storing index of other viruses
phage_list.append(0) # Add "sample" to phageset, automatically added to virus_list


#######################################################################################################
# Use detected database to retrieve relevant information
if database == "virus" or database == "kvit":
	sys.stdout.write("\"{}\" file is queried for filtering..\n".format(database))
	
#	genus_list = set()
#	identity = str.maketrans("","", "\"'[]") # used to clean names

	# Detects taxonomical level
	if taxon == "id": # Strain level 
		sys.stdout.write("Detected strain level file... Filtering on accession numbers.\n")
		 
		if args.refseq is not None:
			ncfile = open(args.refseq, "r")
		else: 
			sys.stderr.write("RefSeq accession numbers required for strain detection...\nTerminating!")
			sys.exit(1)

		accessions = set()
		# The file from RefSeq contains only accession numbers (NC_XXXX)
		for line in ncfile:
			accession_num = (line.rstrip()).split()[0] 
			accessions.add(accession_num)
		ncfile.close()

		if database == "kvit":
			try:
				if args.genbank is not None:
					gbkfile = open(args.genbank, "r")
				else:
					sys.stdout.write("Both RefSeq and GenBank accession numbers required for strain detection...\nTerminating!")
					sys.exit(1)

			except IOError as err:
				sys.stderr.write("Error while opening file: {}\n".format(str(err)))
				sys.exit(1)

			# The file from GenBank contains metadata
			for line in gbkfile:
				contents = line.strip().split(delim)
				accession_num = contents[0].split(".")[0] # Accession number excluding version
				accessions.add(accession_num)
			gbkfile.close()
			

		# Compare inputs
		for i,item in enumerate(header):
			item = item.split(".")[0] # Discard the accession version
			if item in accessions:
				#print("Phage: ", item)
				phage_list.append(i)
			elif item not in accessions:
				#print("Not phage: ", item)
				virus_list.append(i)

#	# Not used in project
#	if taxon == "species":
#		sys.stdout.write("Detected species level file...\n")
#
#		# for hte vira
#		if args.accessory is not None:
#			# Extracts all genera (and other stuff) from a taxonomy file. 
#			sys.stdout.write("Trying to find phages from bacterial genera...\n")
#			try:
#				taxfile = open(args.accessory, "r")
#			except IOError as err:
#				sys.stderr.write("Error while opening file: {}\n".format(str(err)))
#				sys.exit(1)
#			
#			# Only difference is naming of species
#			if database == "virus":
#				for line in taxfile:
#					genus_virus = (line.split(" ")[0]).translate(identity) + " virus"
#					genus_list.add(genus_virus)
#			
#			elif database == "kvit":
#				for line in taxfile:
#					genus_virus = (line.split(" ")[0]).translate(identity) + "virus"
#					genus_list.add(genus_virus)
#
#		for i,item in enumerate(header):
#			# Check for phage in entry
#			for phage in phages:
#				if phage in item:
#					phage_list.append(i)
#		
#			# Check for bacterial "<genus> virus" in entry 
#			for genus in genus_list:
#				if genus in item:
#					phage_list.append(i)
#
#
#	# Not used in project
#	if taxon == "family":
#		sys.stdout.write("Detected family level file...\n")
#
#		for i,item in enumerate(header):
#			for phage_fam in phage_families:
#				if phage_fam in item:
#					phage_list.append(i)


#######################################################################################################
elif database == "imgvr":
	sys.stdout.write("\"{}\" file is being filtered...\n".format(database))
	
	if args.accessory is None:
		sys.stderr.write("### Error! Filtering IMG/VR requires a file containing metadata using flag \"-acc\"! ###\nTerminating...\n")
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
		
		# Query header items against the UViG set; fast lineook-up
		sys.stdout.write("Filtering bacterial phage UViGs from {}...\n".format((args.i).split("/")[-1]))
		for i,item in enumerate(header):
			if item in uvig_set:
				phage_list.append(i)
			else:
				virusset.append(i)

#######################################################################################################
# Define output name
#filter_path = os.path.dirname(args.i) + "/filtered/"
filter_path = os.getcwd() + "/filtered/"
if not os.path.exists(filter_path):
	os.mkdir(filter_path)

# Default output name derived from input name
outname_phage = filter_path + ((args.i).split("/")[-1]).split(".")[0] + ".phages.txt"
outname_virus = filter_path + ((args.i).split("/")[-1]).split(".")[0] + ".virus.txt"

sys.stdout.write("Writing phage file to:\t{}\n".format(outname_phage))
sys.stdout.write("Writing virus file to:\t{}\n".format(outname_virus))

outfile_phage = open(outname_phage, "w+")
outfile_virus = open(outname_virus, "w+")

#######################################################################################################
# Write data to file
infile.seek(0)
for line in infile:
	line = line.rstrip().split("\t")

	for index in phage_list: 
		outfile_phage.write(line[index] + "\t")
	outfile_phage.write("\n")
	
	for index in virus_list: 
		outfile_virus.write(line[index] + "\t")
	outfile_virus.write("\n")

infile.close()
outfile_phage.close()
outfile_virus.close()

#######################################################################################################
