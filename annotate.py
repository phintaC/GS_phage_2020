#!/usr/bin/env python3
# annotate.py
import sys,os,csv,argparse,re
###############################################################################################
#@author Josephine Strange
#@date	08May2020
#@version	2.0
# Generalized sorting to include sample when region is not being annotated. 
###############################################################################################
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", nargs="+", help="Query file", required=True)
parser.add_argument("-m", "--metadata", help="Flag for metadata file")
parser.add_argument("-o", "--output", help="Output directory")
parser.add_argument("-s", "--species", nargs="+", help="Files to annotate species")
parser.add_argument("--sort", help="Select to sort output", action="store_true")
parser.add_argument("--region", help="Select to annotate region", action="store_true")
parser.add_argument("--country", help="Select to annotate country", action="store_true")
parser.add_argument("--sample", help="Select to update sample names", action="store_true")
parser.add_argument("--pilot", help="Select to indicate PILOT study", action="store_true")


args = parser.parse_args()

files = args.input
###############################################################################################
# Define functions
def setupMatrix(file):
	''' Setup a datamatrix from tab separated  file '''
	try:
		infile = open(file, "r")
	except IOError as err:
		sys.stderr.write("Error while opening file: {}\n".format(str(err)))
		sys.exit(1)
		
	lines = infile.readlines()
	infile.close()
	
	# Setup datamatrix
	datamatrix = [[] for i in range(len(lines))]
	row = 0
	for line in lines:
		datamatrix[row] = line.rstrip().split("\t")
		row+=1

	return datamatrix

def regionCount(datamatrix):
	''' Count number of samples from each region '''
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
		elif row[1] == "North America":
			namerica += 1
		elif row[1] == "Oceania":
			oceania += 1
		elif row[1] == "South America":
			samerica += 1

	return africa,asia,europe,mideast,namerica,oceania,samerica

def sort(datamatrix,col):
	# Sort the output alphabetically on region
	head = datamatrix[0]
	datamatrix = sorted(datamatrix[1:], key=lambda x: x[col])
	datamatrix.insert(0,head)	
	return datamatrix

def fileWrite(directory, file, datamatrix):
	'''Writes the annotated datamatrix to file'''
	if not os.path.exists(directory):
		os.mkdir(directory)
	
	outname = directory + "/" + os.path.basename(os.path.splitext(file)[0]) + ".tsv"

	try:
		with open(outname,"w+") as outfile:
			sys.stdout.write("Writing to file: {}\n".format(outname))
			csvwriter = csv.writer(outfile, delimiter="\t")
			csvwriter.writerows(datamatrix)
	except IOError as err:
		sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
		sys.exit(1)

def setupSpcDict(file):
	''' Setup dict of species linked to accession numbers '''
	try:
		speciesfile = open(file,"r")
	except IOError as err: 
		sys.stderr.write("Error while loading metadata file: {}\n".format(str(err)))
		sys.exit(1)
	
	speciesdata = speciesfile.readlines()
	
	# Create dict of accession:species
	spcDict = dict()
	if "taxid" in file:
		for line in speciesdata[2:]: 
			line = line.rstrip().split("\t")
			
			if line[0].startswith(r" "):
				species = re.search(r"\b\w+\s\w+\s(\w)*(\d)*\b",line[0]).group()
				accession = re.search(r"NC_\d{1,9}",line[0]).group()
			else:
				species = line[0].rstrip()
				accession = line[1].rstrip()
			
			if accession not in spcDict:
				if accession == "-": # Then the phage has multiple accessions 
					pass 
				spcDict[accession] = [species]
				
#			else:
#				sys.stdout.write("###  Warning!  ###\n\"{}\" annotated with:\n".format(accession))
#				for item in spcDict[accession]:
#					sys.stdout.write(item + "\n")
#				sys.stdout.write("##################\n\n")
#				spcDict[accession] += [species]

	if "nuccore" in file:
		for line in speciesdata:
			# Stateful parsing to find each segment of nuccore file
			if line == "":
				pass
			
			if re.match(r"\d{1,4}\.\s(\w+\s){1,5}.+", line):
				species = re.search(r"\d{1,5}\.\s(((?!complete)(?!partial)(?!proviral)(?!genome)\w+(\d$)?\s(converting\s)?){1,5}((?!complete)(?!partial)(?!proviral)(?!genome)[A-Za-z0-9-_]+))", line).group(1)
			if line.startswith("NC_"):
				accession = re.search(r"NC_\d{4,9}",line).group(0)
				# Create dict
				if accession not in spcDict:
					spcDict[accession] = [species]
#				else:
#					sys.stdout.write("### Warning! ###\n\"{}\" annotated with:\n".format(accession))
#					for item in spcDict[accession]:
#						sys.stdout.write(item + "\n")
#					sys.stdout.write("################\n\n")
#					spcDict[accession] += [species]

	return spcDict

def updateDisplayName(matrix,displayNameDict):
	''' Updates the display name of a datamatrix given the input dictionary '''
	for i,row in enumerate(datamatrix[1:]):
		if row[0] in displayNameDict:
			datamatrix[i+1][0] = displayNameDict[row[0]]
		else:
			key = re.sub(r"(DTU\d{4}_MG_\d{1,3}(_\w\D{1,2}){2,3}(_\w)?(_\d{1,3}){0,2}(_re_\d{1,2})?)(_.+)$",r"\1", datamatrix[i+1][0])

			if key in displayNameDict:
				datamatrix[i+1][0] = displayNameDict[key]

			else:
				sys.stdout.write("Could not update {}\n".format(row[0]))
	return datamatrix

def annotateSpecies(datamatrix,startcol,spcDict):
	''' Annotates a given datamatrix'''
	for i,accession in enumerate(datamatrix[0][startcol:]):
		accession = accession.split(".")[0] # Remove version numbers
		if accession in spcDict:
			datamatrix[0][startcol+i] = spcDict[accession][0]
		else:
			if accession.startswith("NC_"):
				sys.stdout.write("### Warning! Could not annotate {} with species...\n".format(accession))

	return datamatrix

def annotateRegion(datamatrix,ctryRegDict):
	''' Annotates a given sample with region '''
	if datamatrix[0][1] != "region":
		datamatrix[0].insert(1, "region")
		for row in datamatrix[1:]:
			row.insert(1, ctryRegDict[row[0][:3]][1])
	else: 
		sys.stdout.write("Region already annotated... Skipping!\n")

	return datamatrix

def annotateCountry(datamatrix, ctryRegDict):
	''' Annotates datamatrix with country '''
	# If region is already annotated
	if datamatrix[0][1] == "region":
		sys.stdout.write("Annotating country in column 3\n")
		if datamatrix[0][2] != "country":
			datamatrix[0].insert(2,"country")
			for row in datamatrix[1:]:
				row.insert(2, ctryRegDict[row[0][:3]][0])
		else:
			sys.stdout.write("Country already annotated... Skipping!\n")
	# If region is not already annotated
	else:
		if datamatrix[0][1] != "country":
			sys.stdout.write("Annotating country in column 2\n")
			datamatrix[0].insert(1,"country")
			for row in datamatrix[1:]:
				row.insert(1,ctry_reg[row[0][:3]][0])
		else:
			sys.stdout.write("Country already annotated... Skipping!\n")

	return datamatrix
###############################################################################################
# Dict containing country [0] and region [1] annotation
ctryRegDict = dict({"ALB":["Albania","Europe"],"ARE":["United Arab Emirates","Middle East"],"ARG":["Argentina","South America"],"AUS":["Australia","Oceania"],"AUT":["Austria","Europe"],\
	"BEL":["Belgium","Europe"],"BEN":["Benin","Africa"],"BFA":["Burkina Faso","Africa"],"BGD":["Bangladesh","Asia"],"BGR":["Bulgaria","Europe"],"BIH":["Bosnia and Herzegovina","Europe"],\
	"BOL":["Bolivia","South America"],"BRA":["Brazil","South America"],"BRB":["Barbados","North America"],"BWA":["Botswana","Africa"],\
	"CAN":["Canada","North America"],"CHE":["Switzerland","Europe"],"CHL":["Chile","South America"],"CHN":["China","Asia"],"CIV":["Ivory Coast","Africa"],"CMR":["Cameroon", "Africa"],\
	"COD":["Democratic Republic of Congo","Africa"],"COL":["Colombia","South America"],"CZE":["Czech Republic","Europe"],\
	"DEU":["Germany","Europe"],"DNK":["Denmark", "Europe"],\
	"ECU":["Ecuador","South America"],"ESP":["Spain","Europe"],"EST":["Estonia","Europe"],"ETH":["Ethiopia","Africa"],\
	"FIN":["Finland","Europe"],"FRA":["France", "Europe"],\
	"GBR":["United Kingdom","Europe"],"GEO":["Georgia","Europe"],"GHA":["Ghana","Africa"],"GRC":["Greece", "Europe"],"GRL":["Greenland","North America"],"GTM":["Guatemala","North America"],\
	"HKG":["Hong Kong","Asia"],"HRV":["Croatia","Europe"],"HUN":["Hungary","Europe"],\
	"IND":["India","Asia"],"IRL":["Ireland","Europe"],"IRN":["Islamic Republic of Iran","Middle East"],"ISL":["Iceland","Europe"],"ISR":["Israel","Middle East"],"ITA":["Italy","Europe"],\
	"JPN":["Japan", "Asia"],\
	"KAZ":["Kazakhstan","Asia"],"KEN":["Kenya","Africa"],"KHM":["Cambodia","Asia"],"KOR":["South Korea","Asia"],"KWT":["Kuwait","Middle East"],\
	"LBN":["Lebanon","Middle East"],"LCA":["Saint Lucia","North America"],"LKA":["Sri Lanka","Asia"],"LTU":["Lithuania","Europe"],"LUX":["Luxembourg","Europe"],"LVA":["Latvia", "Europe"],\
	"MAR":["Morocco","Africa"],"MDA":["Moldova","Europe"],"MDG":["Madagascar","Africa"],"MKD":["Republic of Macedonia","Europe"],"MLT":["Malta","Europe"],"MNE":["Montenegro","Europe"],"MOZ":["Mozambique","Africa"],\
	"MUS":["Mauritius","Africa"],"MWI":["Malawi","Africa"],"MYS":["Malaysia","Asia"],\
	"NGA":["Nigeria","Africa"],"NIC":["Nicaragua","North America"],"NLD":["Netherlands","Europe"],"NOR":["Norway","Europe"],"NPL":["Nepal","Asia"],"NZL":["New Zealand","Oceania"],\
	"PAK":["Pakistan","Asia"],"PER":["Peru","South America"],"PHL":["Phillippines","Asia"],"POL":["Poland","Europe"],"PRT":["Portugal","Europe"],"PRY":["Paraguay","South America"],\
	"SAU":["Saudi Arabia", "Middle East"],"SEN":["Senegal","Africa"],"SGP":["Singapore","Asia"],"SRB":["Serbia","Europe"],"SVK":["Slovakia","Europe"],"SVN":["Slovenia","Europe"],"SWE":["Sweden","Europe"],\
	"VNM":["Viet Nam","Asia"],\
	"TCD":["Chad","Africa"],"TGO":["Togo","Africa"],"THA":["Thailand","Asia"],"TUR":["Turkey","Middle East"],"TWN":["Taiwan","Asia"],"TZA":["Tanzania","Africa"],\
	"UGA":["Uganda","Africa"],"USA":["United States of America","North America"],"URY":["Uruguay", "South America"],\
	"XK-":["Kosova", "Europe"],\
	"ZAF":["South Africa","Africa"],"ZMB":["Zambia","Africa"]})

# Is Nicaragua, Guatemala North America?
###############################################################################################
# Pilot study
if args.pilot:
	displayNameDict = dict({"BWA":"BWA-19", "CIV":"CIV-13", "ETH":"ETH-24", "GHA":"GHA-4",\
	"KEN":"KEN-72", "KHM":"KHM-21", "NGA":"NGA-50", "SEN":"SEN-8", "TGO":"TGO-44", \
	"TZA":"TZA-15", "ZAF":"ZAF-39", "CHN":"CHN-64", "IND":"IND-11", "KAZ":"KAZ-6",\
	"LKA":"LKA-40", "MYS":"MYS-54", "NPL":"NPL-33", "PAK":"PAK-7", "SGP":"SGP-52",\
	"VNM":"VNM-48", "ALB":"ALB-17", "AUT":"AUT-70", "BGR":"BGR-66", "CHE":"CHE-67",\
	"CZE":"CZE-23", "DEU":"DEU-27", "ESP":"ESP-75", "FIN":"FIN-25", "GEO":"GEO-59",\
	"HRV":"HRV-68", "HUN":"HUN-61", "IRL":"IRL-69", "ISL":"ISL-28", "ITA":"ITA-30",\
	"LUX":"LUX-32", "LVA":"LVA-31", "MDA":"MDA-65", "MKD":"MKD-62", "MLT":"MLT-63",\
	"NLD":"NLD-43", "NOR":"NOR-34", "POL":"POL-36", "SRB":"SRB-37", "SVK":"SVK-9",\
	"SVN":"SVN-38", "XK":"XK-60", "IRN":"IRN-12", "ISR":"ISR-29", "TUR":"TUR-46",\
	"NZL":"NZL-56", "COL":"COL-2", "PER":"PER-35"})

	###############################################################################################
	for file in files:
		sys.stdout.write("######### Working on {} #########\n".format(os.path.basename(file)))
		sys.stdout.write(">>> Setting up datamatrix...\n")
		datamatrix = setupMatrix(file)

		###############################################################################################
		# Update sample name to display name
		if args.sample:
			sys.stdout.write(">>> Updating sample names...\n")
			datamatrix = updateDisplayName(datamatrix, displayNameDict)

		###############################################################################################
		# Annotate region		
		if args.region:
			sys.stdout.write(">>> Annotating region...\n")
			datamatrix = annotateRegion(datamatrix,ctryRegDict)

		###############################################################################################
		# Annotate country
		if args.country:
			sys.stdout.write(">>> Annotating country...\n")
			datamatrix = annotateCountry(datamatrix, ctryRegDict)

	
		###############################################################################################
		# Annotate accession numbers with species
		if args.species is not None:
			sys.stdout.write(">>> Annotating species...\n")
			# File handle
			speciesfiles = args.species
			for file in speciesfiles:
				spcDict = setupSpcDict(file)
	
			# Update matrix head with species
			if datamatrix[0][1] == "region" or datamatrix[0][1] == "country":
				if datamatrix[0][2] == "country":
					datamatrix = annotateSpecies(datamatrix,3,spcDict)
				else:
					datamatrix = annotateSpecies(datamatrix,2,spcDict)
			else:
				datamatrix = annotateSpecies(datamatrix,1,spcDict)

		###############################################################################################
		# Sort the datamatrix according to region
		if args.sort:
			if args.region:
				sys.stdout.write(">>> Sorting matrix on region...\n")
				if datamatrix[0][1] == "region":
					datamatrix = sort(datamatrix,1)
				else:
					sys.stdout.write("Region not annotated... Skipping!\n")
			else:
				# Sort on sample name
				sys.stdout.write(">>> Sorting matrix on sample...\n")
				datamatrix = sort(datamatrix,0)


		###############################################################################################
		# Write to file
		sys.stdout.write(">>> Writing to file...\n")
		if args.output:
			fileWrite(args.output, file, datamatrix)
		else:
			fileWrite(os.getcwd(), file, datamatrix)


###############################################################################################
# Study is from GS2
else:

	for file in files:
		# File handle
		sys.stdout.write("######### Working on {} #########\n".format(os.path.basename(file)))
		sys.stdout.write(">>> Setting up datamatrix...\n")
		datamatrix = setupMatrix(file)

		###############################################################################################
		# Update sample name
		if args.sample:
			sys.stdout.write(">>> Updating sample names...\n")
			
			if not args.metadata:
				sys.stdout.write("Cannot update sample names - missing dependency \"-m\"... Terminating!\n")
				sys.exit(0)
			
			else:		
				# Setup display name dict: 
				displayNameDict = dict()
				
				# File handle 
				try: 
					metafile = open(args.metadata, "r")
					meta = metafile.readlines()
					metafile.close()

				except IOError as err:
					sys.stderr.write("Error while opening metafile: {}\n".format(str(err)))
					sys.exit(1)			

				for line in meta[1:]:
					contents = line.rstrip().split("\t")
					if "missing" in contents[-1]:
						pass
					elif "excluded" in contents[-1]:
						pass
					elif "remapped" in contents[-1]:
						pass
					
					# Create display name dict
					else:
						cnt = contents[0].replace("\"","")
						if cnt not in displayNameDict:
							displayNameDict[cnt] = contents[2].replace("\"","")
						else:
							sys.stdout.write("### {} already logged in dict, with value(s): {}\n>>> Overwriting with entry: {}\n".format(contents[1], displayNameDict[contents[1]], contents[0]))
							displayNameDict[cnt] = contents[2].replace("\"","")

			# Update matrix
			datamatrix = updateDisplayName(datamatrix, displayNameDict)

			print("Number of samples: {}".format(len(datamatrix)-1))
		###############################################################################################
		# Annotate with region
		if args.region:
			if re.match(r"\w{3}-\d{1,3}",datamatrix[1][0]):
				sys.stdout.write(">>> Annotating region...\n")
				# Annotate region 
				datamatrix = annotateRegion(datamatrix, ctryRegDict)
			else:
				sys.stdout.write("### Warning... File does not contain recognised samplename ({})... Terminating!\n".format(datamatrix[1]))
				sys.exit(1)				

		###############################################################################################
		# Annotate with country
		if args.country:
			if re.match(r"\w{3}-\d{1,3}",datamatrix[1][0]):
				sys.stdout.write(">>> Annotating country...\n")
				datamatrix = annotateCountry(datamatrix, ctryRegDict)
			else:
				sys.stdout.write("### Warning... File does not contain recognised samplename ({})... Terminating!\n".format(datamatrix[1]))
				sys.exit(1)
		###############################################################################################
		# Annotate with species
		if args.species:
			sys.stdout.write(">>> Annotating species...\n")
			speciesfiles = args.species
			for spcfile in speciesfiles:
				sys.stdout.write("Annotating species with file: {}\n".format(os.path.basename(spcfile)))
				spcDict = setupSpcDict(spcfile)

				# Update matrix head with species
				if datamatrix[0][1] == "region" or datamatrix[0][1] == "country":
					if datamatrix[0][2] == "country":
						datamatrix = annotateSpecies(datamatrix,3,spcDict)
					else:
						datamatrix = annotateSpecies(datamatrix,2,spcDict)
				else:
					datamatrix = annotateSpecies(datamatrix,1,spcDict)
		###############################################################################################
		# Sort the datamatrix
		if args.sort:
			if args.region:
				sys.stdout.write(">>> Sorting matrix on region...\n")
				if datamatrix[0][1] == "region":
					datamatrix = sort(datamatrix,1)
				else:
					sys.stdout.write("Region not annotated... Skipping!\n")
			else:
				sys.stdout.write(">>> Sorting on sample...\n")
				datamatrix = sort(datamatrix,0)
		###############################################################################################
		# Write to file
		sys.stdout.write(">>> Writing to file...\n")
		if args.output:
			fileWrite(args.output, file, datamatrix)
		else:
			fileWrite(os.getcwd(), file, datamatrix)

###############################################################################################
# Print the numbers if region is annotated or if matrix is being sorted on region
if args.sort or args.region: 
	rCounts = regionCount(datamatrix)

	sys.stdout.write("# samples from Africa:\t{}\n\
# samples from Asia:\t{}\n\
# samples from Europe:\t{}\n\
# samples from Middle East:\t{}\n\
# samples from North America:\t{}\n\
# samples from Oceania:\t{}\n\
# samples from South America:\t{}\n".format(rCounts[0],rCounts[1],rCounts[2],rCounts[3],rCounts[4],rCounts[5],rCounts[6]))
