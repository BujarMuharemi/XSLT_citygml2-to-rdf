from lxml import etree
from io import StringIO, BytesIO
import re
from pathlib import Path

"""
Description: Script for testing the possibility of auto generating XSLT-RDF templates files from the original CityGML files.
This should be possible because XML is a tree structure and thats just a restricted graph. 

TODO:   
    - fix blacklist bug
    - add output to a valid xslt output file with a serialized name (blank-output-template as base)     
    - missing ids for objects: gml:MultiSurface   
    - Building>Solid Linkage ? really necessary ?

    Bugs? gml:MultiSurface ?

"""


# reading spo-temp file
f = open(r'python-spo\templates\spo-temp.xslt', "r")
og_lines = f.readlines() #original template, read from the file
output_file = []

# blank-output-template
blank_output_template = open(r'python-spo\templates\blank-output-template.xslt', "r")
output_template = blank_output_template.readlines() #original template, read from the file
#print(output_template)

# reading input gml file
root = etree.parse(r'gml-simplesolid-test\data\SimpleSolid.gml')
#root = etree.parse(r'/home/bujar/Documents/_HFT/BA_IDP/Data/Meidling/Meidling_citygml/Meilding_building/Meilding_one_building.gml')


# changes the template according to the parameters, so it can later be written to the output flie
def writeToOutputTemplate(matchingRegex,predicate,object):
    #print("-------",matchingRegex,"\t",predicate,"\t",object)
    lines=og_lines[:]
    
    for i in range(len(lines)):               
        if re.search(r"\${{matchingRegex}}", lines[i]): 
            lines[i] = re.sub("\${{matchingRegex}}",matchingRegex,lines[i])
        elif re.search(r"\${{predicate}}", lines[i]): 
            lines[i] = re.sub("\${{predicate}}",predicate,lines[i])
        elif re.search(r"\${{object}}", lines[i]): 
            lines[i] = re.sub("\${{object}}",object,lines[i])

        #print(lines[i])
    #print("lines:\t",lines,"\n\n")
    output_file.append(lines)
    #lines=og_lines
    #print(output_file)

############################################################

# getting all paths of the elements
paths = [root.getpath(d) for d in root.iter()]
output = set() # set for storing just unique triples

# FIXME: exterior>CompositeSurface>surfaceMember is missing because it has a / length of 8 ?
for e in paths:
    #print(e)
    if(e.count("/")%2!=0 and e.count("/")>1):
        array = e.split("/")         
        array.pop(0) # remove first empty element
        #print(array)
        a3 = array[-3:] 
        #print(a3)
        a3[1]=re.sub("\[[0-9]+\]","",a3[1]) 
        a = '/'.join(a3)
        output.add(a)
        #print(e.count("/"),"\t",e)
    #elif(e.count("/")==4): #needs also too look up if this element has any children
        #print("possible attribute:\t",e.count("/"),"\t",e)


#showing found triples
print("\n═══ Number of found SPO Triples: ",len(output),"═══")
output_array=list(output)

for i in range(len(output_array)):
    print(i,":",output_array[i])

blacklist = input("\nEnter number of triples, which should be skipped (like 5,6,7)").split(",") # getting blacklist from user

print("\n═══ Removing choosen triples ═══")
removedCount=0 # counter when removing an element
for i in blacklist:
    print("removed: ",output_array[int(i)-removedCount])
    output_array.remove(output_array[int(i)-removedCount])
    removedCount+=1

print("\n═══ Writing to output file ═══")
writeCount=0
for triples in output_array:
    print(">> to output ",writeCount,": ",triples)
    writeToOutputTemplate(triples, triples.split("/")[1], triples.split("/")[2])
    writeCount+=1

print("Wrote ",writeCount," triples to file.")


#writing to file
with open('python-spo\output\output3.xslt', 'w') as f:
    for item in output_file:
        for i in item:
            i = i.rstrip()
            f.write("%s\n" % i)

