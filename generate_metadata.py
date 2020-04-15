#!/usr/bin/env python3
# generate_metadata.py
import sys,os,argparse,csv

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", nargs="+", help="Input file from which to generate display_name")

args = parser.parse_args()

files = args.input

africa = set(["Algeria","Angola","Benin","Botswana","Burkina Faso","Burundi","Cameroon","Cape Verde","Central African Republic",\
	"Chad","Comoros","Djibouti","Congo","Equatorial Guinea","Eritrea","Ethiopia","Gabon","Gambia","Ghana",\
	"Guinea","Guinea Bissau","Ivory Coast","Kenya","Lesotho","Liberia","Libya","Madagascar","Malawi","Mali",\
	"Mauritania","Mauritius","Mayotte","Morocco","Mozambique","Namibia","Niger","Nigeria","Reunion","Rwanda",\
	"Sao Tome and Principe","Senegal","Seychelles","Sierra Leone","Somalia","South Africa","South Sudan","Sudan","Tanzania", "Togo",\
	"Tunisia","Uganda","Western Sahara","Zambia","Zimbabwe"])
# Excluding: Egypt

asia = set(["Afghanistan","Armenia","Azerbaijan","Bangladesh","Bhutan","Brunei","Cambodia","China","Georgia",\
	"Hong Kong","India","Indonesia","Japan","Kazakhstan","Kyrgystan","Laos","Macau","Malaysia","Maldives",\
	"Mongolia","Myanmar","Nepal","North Korea","Philippines","Singapore","South Korea","Sri Lanka","Taiwan","Tajikistan",\
	"Thailand","Turkmenistan","Uzbekistan", "Vietnam"])
# Excluding: Bahrain,Iran,Iraq,Israel,Jordan,Kuwait,Lebanon,Oman,Pakistan,Palestine,Qatar,Saudi Arabia,Syria,Turkey,United Arab Emirates,Yemen

europe = set(["Albania","Andorra","Armenia","Austria","Azerbaijan","Belarus","Belgium","Bosnia and Herzegovina","Bulgaria",\
	"Croatia","Cyprus","Czechia","Denmark","Estonia","Faroe Islands","Finland","France","Germany","Greece",\
	"Hungary","Iceland","Ireland","Italy","Latvia","Liechtenstein","Lithuania","Luxembourg","Macedonia","Malta",\
	"Moldova","Monaco","Montenegro","The Netherlands","Norway","Poland","Portugal","Romania","Russia","San Marino",\
	"Serbia","Slovakia","Slovenia","Spain","Sweden","Switzerland","Ukraine","United Kingdom","Vatican City"])
# Excluding: Georgia,Kazakhstan,Turkey

middleEast = set(["Afghanistan","Bahrain","Egypt","Iran","Iraq","Israel","Jordan","Kuwait","Lebanon",\
	"Oman","Pakistan","Palestine","Qatar","Saudi Arabia","Syria","Turkey","United Arab Emirates","Yemen"])
# Excluding: Cyprus

northAmerica = set(["Anguilla","Antigua and Barbuda","Aruba","Bahamas","Barbados","Belize","Bermuda","Bonaire","British Virgin Islands",\
	"Canada","Cayman Islands","Clipperton Island","Costa Rica","Cuba","Curacao","Dominica","Dominican Republic","El Salvador","Greenland",\
	"Grenada","Guadeloupe","Guatemala","Haiti","Honduras","Jamaica","Martinique","Mexico","Montserrat","Navassa Island",\
	"Nicaragua","Panama","Puerto Rico","Saba","Saint Barthelemy","Saint Kitts and Nevis","Saint Lucia","Saint Martin","Saint Pierre and Miquelon","Saint Vincent and the Grenadines",\
	"Sint Eustatius","Sint Maarten","Trinidad and Tobago","Turks and Caicos Islands","United States","USA","US Virgin Islands"])

oceania = set(["American Samoa","Australia","Cook Islands","Fiji","French Polynesia","Guam","Kiribati","Micronesia","Nauru",\
	"New Caledonia","New Zealand","Niue","Palau","Papua New Guinea","Samoa","Tokelau","Tonga","Tuvalu","Vanuatu","Wallis and Futuna"])

southAmerica = set(["Argentina","Bolivia","Brazil","Chile","Colombia","Ecuador","Guyana","Paraguay","Peru",\
	"Suriname","Uruguay","Venezuela"])


dndict = dict()

for file in files:
	try:
		infile = open(file, "r")
	except IOError as err:
		sys.stderr.write("Error while opening input file: {}\n".format(str(err)))
		sys.exit(1)

	lines = infile.readlines() # Read entire file, small so OK
	infile.close()
	
	row_num = 1
	
	datamatrix = [[] for i in range(len(lines))]
	datamatrix[0] = lines[0].split("\t")
	
	if datamatrix[0][2] == "display_name":
		sys.stdout.write("\"display_name\" column exists - delete column and try again...\n")
		sys.exit(0)
	
	elif datamatrix[0][-2] == "continent":
		sys.stdout.write("\"continent\" column exists - delete column and try again...\n")
		sys.exit(0)
	
	else:
	
		datamatrix[0].insert(2,"display_name")
		datamatrix[0].insert(6,"continent")
		
		for line in lines[1:]:
			# Setup display_name
			datamatrix[row_num] = line.rstrip().split("\t")
		
			if not datamatrix[row_num][0].startswith("DTU_"):
				datamatrix[row_num].insert(2, dndict[datamatrix[row_num][0]])
	
			else: 
				display_name = datamatrix[row_num][3] + "-" + datamatrix[row_num][0].split("_")[2] # CTR-NUM
				datamatrix[row_num].insert(2, display_name)
	
				dndict[datamatrix[row_num][1]] = display_name
			
			# Annotate continent
			country = datamatrix[row_num][5]
			if country in africa:
				datamatrix[row_num].insert(6,"Africa")
			
			elif country in asia:
				datamatrix[row_num].insert(6,"Asia")

			elif country in europe:
				datamatrix[row_num].insert(6,"Europe")

			elif country in middleEast:
				datamatrix[row_num].insert(6,"Middle East")

			elif country in northAmerica:
				datamatrix[row_num].insert(6,"North America")

			elif country in oceania:
				datamatrix[row_num].insert(6,"Oceania")

			elif country in southAmerica:
				datamatrix[row_num].insert(6, "South America")
			
			else:
				datamatrix[row_num].insert(6, "")

			row_num += 1


# Write data back to file
try:
	with open(file, "w+") as outfile:
		csvwriter = csv.writer(outfile, delimiter="\t")
		csvwriter.writerows(datamatrix)
except IOError as err:
	sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
	sys.exit(1)
