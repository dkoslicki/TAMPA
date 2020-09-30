import sys
f=open(sys.argv[1],"r")
lines=f.readlines()
software_result=[]
for x in lines:
	if x.startswith('19'):
		software_result.append(x.split())
f.close()
f2=open(sys.argv[2], "w")
f2.write('##fileformat=VCFv4.2\n##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant detected">\n##INFO=<ID=SVLEN,Number=1,Type=Integer,Description="Length of structural variant">\n##INFO=<ID=END,Number=1,Type=Integer,Description="End position of structural variant">\n#CHROM POS     ID     REF    ALT     QUAL  FILTER  INFO\n')
for i in range(len(software_result)): 
	if(software_result[j][7].split(";")[0].split("=")[1] == "DEL"):
		length= int( (software_result[j][7].split(";")[1]).split("=")[1] )
		print(length)
		if(length<51):
			start=software_result[j][1]
			f2.write('19      ')
			f2.write(start)
			f2.write(' .      .      <DEL>  .      PASS   SVTYPE=DEL;SVLEN=')
			f2.write(str(length) )
			f2.write(";END=")
			f2.write((software_result[j][7].split(";")[2]).split("=")[1] )
			f2.write('\n')