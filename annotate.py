#!/usr/bin/env python3
# annotate.py
import sys,os,csv
# Dictionary to update sample names appropriately 
upd_dict = dict({"BWA":"BWA-19", "CIV":"CIV-13", "ETH":"ETH-24", "GHA":"GHA-4",\
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

# Sets for quick regional identification
africa = set(["BWA-19","CIV-13","ETH-24","GHA-4","KEN-72",\
"KHM-21","NGA-50","SEN-8","TGO-44","TZA-15",\
"ZAF-39","ZMB-49","ZMB-49b"])

asia = set(["CHN-64","IND-11","KAZ-6","LKA-40","MYS-54",\
"NPL-33","PAK-7","SGP-52","VNM-48"])

europe = set(["ALB-17","AUT-70","BGR-66","CHE-67","CZE-23",\
"DEU-27","DNK-71-RA","DNK-71-RD","DNK-71-RL","ESP-75",\
"FIN-25","GEO-59","HRV-68","HUN-61","IRL-69",\
"ISL-28","ITA-30","LUX-32","LVA-31","MDA-65",\
"MKD-62","MLT-63","NLD-43","NOR-34","POL-36",\
"SRB-37","SVK-9","SVN-38","SWE-41","SWE-41a",\
"XK-60"])

middleEast = set(["IRN-12","ISR-29","TUR-46"])

northAmerica = set(["CAN-22","CAN-22a","CAN-22b","CAN-22c","USA-74",\
"USA-74a","USA-74b","USA-74c","USA-74d","USA-74e",\
"USA-74f","USA-74g","USA-74h","USA-74i"])

oceania = set(["AUS-18","AUS-18a","NZL-56"])

southAmerica = set(["BRA-53","BRA-53a","COL-2","ECU-14","ECU-14a","PER-35"])

if len(sys.argv) != 3:
	sys.stdout.write("Usage: annotate.py <summary file> <output directory>\n")
	sys.exit(1)
else:
	file = sys.argv[1]
	outdir = sys.argv[2]

try:
	infile = open(file, "r")
except IOError as err:
	sys.stderr.write("Error while opening file: {}\n".format(str(err)))
	sys.exit(1)

lines = infile.readlines()
infile.close()

datamatrix = [[] for i in range(len(lines))]
datamatrix[0] = lines[0].rstrip().split("\t")

if datamatrix[0][1] != "region":
	datamatrix[0].insert(1, "region")
else:
	sys.stdout.write(">>> File already annotated!")
	sys.exit(1)

row = 1
africa_ct,asia_ct,europe_ct,middleEast_ct,na_ct,oceania_ct,sa_ct = 0,0,0,0,0,0,0
for line in lines[1:]:
	datamatrix[row] = line.rstrip().split("\t")
	
	# Update sample name to appropriate name
	if datamatrix[row][0] in upd_dict:
		datamatrix[row][0] = upd_dict[datamatrix[row][0]]

	# Annotate country
	
	country = datamatrix[row][0]
	if country in africa:
		datamatrix[row].insert(1,"Africa")
		africa_ct += 1

	elif country in asia:
		datamatrix[row].insert(1,"Asia")
		asia_ct += 1

	elif country in europe:
		datamatrix[row].insert(1,"Europe")
		europe_ct += 1

	elif country in middleEast:
		datamatrix[row].insert(1,"Middle East")
		middleEast_ct += 1

	elif country in northAmerica:
		datamatrix[row].insert(1,"North America")
		na_ct += 1

	elif country in oceania:
		datamatrix[row].insert(1,"Oceania")
		oceania_ct += 1

	elif country in southAmerica:
		datamatrix[row].insert(1, "South America")
		sa_ct += 1

	else:
		datamatrix[row].insert(1, "")

	row += 1

# Sort the datamatrix according to region
if "relabundance" in file:
	print("Sorting relative abundance on region for PCoA...")
	# Sort the output according to region (for PCoA analysis)
	head = datamatrix[0]
	datamatrix = sorted(datamatrix[1:], key=lambda x: x[1])
	datamatrix.insert(0,head)


if not os.path.exists(outdir):
	os.mkdir(outdir)

outfilename = outdir + "pilot_" + os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".csv"

try:
	with open(outfilename,"w+") as outfile:
		csvwriter = csv.writer(outfile, delimiter="\t")
		csvwriter.writerows(datamatrix)
except IOError as err:
	sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
	sys.exit(1)


sys.stdout.write("# samples from Africa:\t{}\n\
# samples from Asia:\t{}\n\
# samples from Europe:\t{}\n\
# samples from Middle East:\t{}\n\
# samples from North America:\t{}\n\
# samples from Oceania:\t{}\n\
# samples from South America:\t{}\n".format(africa_ct,asia_ct,europe_ct,middleEast_ct,na_ct,oceania_ct,sa_ct))