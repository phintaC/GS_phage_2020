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
# Acquire column names and index for row names ([0]) 
header = (infile.readline().rstrip()).split(delim)
dataset = set() # set to store tuple of phages
virusset = set() # set to store tuple of other viruses
dataset.add((0,header[0]))
virusset.add((0,header[0]))

#######################################################################################################
# Use detected database to retrieve relvant information
if database == "virus" or database == "kvit":
	sys.stdout.write("\"{}\" file is queried for filtering..\n".format(database))
	
	genus_list = set()
	identity = str.maketrans("","", "\"'[]")
	
	# Detects taxonomical level
	if taxon == "id": # Strain level 
		sys.stdout.write("Detected strain level file... Filtering on accession numbers.\n")
		 


		if database == "kvit":
			try:
				if args.genbank is not None:
					gbkfile = open(args.genbank, "r")
				if args.refseq is not None:
					ncfile = open(args.refseq, "r")
				else:
					sys.stdout.write("Both RefSeq and GenBank accession numbers required for strain detection...\nTerminating!")
					sys.exit(1)

			except IOError as err:
				sys.stderr.write("Error while opening file: {}\n".format(str(err)))
				sys.exit(1)


			# Make sets of GenBank accession and RefSeq accessions
			accessions = set()
			# The file from GenBank contains metadata
			for line in gbkfile:
				contents = line.strip().split(delim)
				accession_num = contents[0].split(".")[0] # Accession number excluding version
				accessions.add(accession_num)
			gbkfile.close()
			
			# The file from RefSeq contains only accession numbers 
			for line in ncfile:
				accession_num = (line.rstrip()).split()[0] 
				accessions.add(accession_num)
			ncfile.close()
		


		elif database =="virus":
			try:
				ncfile = open(args.refseq, "r")

			except IOError as err:
				sys.stderr.write("Error while opening {}: {}\n".format((args.accessory).split("/")[-1], str(err)))
				sys.exit(1)

			accessions = set()
			for line in ncfile:
				accession_num = (line.rstrip()).split()[0]
				accessions.add(accession_num)
			ncfile.close()


		# Compare inputs
		for i,item in enumerate(header):
			item = item.split(".")[0]
			if item in accessions:
				#print("Phage: ", item)
				dataset.add((i,item))
			elif item not in accessions:
				#print("Not phage: ", item)
				virusset.add((i,item))

	# Not used in project
	if taxon == "species":
		sys.stdout.write("Detected species level file...\n")

		# for hte vira
		if args.accessory is not None:
			# Extracts all genera (and other stuff) from a taxonomy file. 
			sys.stdout.write("Trying to find phages from bacterial genera...\n")
			try:
				taxfile = open(args.accessory, "r")
			except IOError as err:
				sys.stderr.write("Error while opening file: {}\n".format(str(err)))
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

		for i,item in enumerate(header):
			# Check for phage in entry
			for phage in phages:
				if phage in item:
					dataset.add((i,item))
		
			# Check for bacterial "<genus> virus" in entry 
			for genus in genus_list:
				if genus in item:
					dataset.add((i,item))


	# Not used in project
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
		
		# Query header items against the UViG set; fast look-up
		sys.stdout.write("Filtering bacterial phage UViGs from {}...\n".format((args.i).split("/")[-1]))
		for i,item in enumerate(header):
			if item in uvig_set:
				dataset.add((i,item))
			else:
				virusset.add((i,item))

#######################################################################################################
# Define output name
filter_path = os.path.dirname(args.i) + "/filtered/"
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
# Create lists to store column names and indices
colnames = [[] for i in range(2)]
indices = [[] for i in range(2)]

# Fill lists with data
# Phages; at index = 0
for tup in sorted(dataset):
	indices[0].append(tup[0])
	colnames[0].append(tup[1])
dataset.clear()

# Other viruses; at index = 1
for tup in sorted(virusset):
	indices[1].append(tup[0])
	colnames[1].append(tup[1])
virusset.clear()

# Write first row to file containing phage information
outfile_phage.write("\t".join(colnames[0]) + "\n")
outfile_virus.write("\t".join(colnames[1]) + "\n")
colnames.clear()

# Write remaining data to file
for line in infile:
	line = line.rstrip().split("\t")

	for index in indices[0]: 
		outfile_phage.write(line[index] + "\t")
	
	for index in indices[1]: 
		outfile_virus.write(line[index] + "\t")
	
	outfile_phage.write("\n")
	outfile_virus.write("\n")


infile.close()
outfile_phage.close()
outfile_virus.close()

#######################################################################################################
