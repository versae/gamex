import csv
import json

f = open( 'barroco.csv', 'r' )
reader = csv.DictReader( f )
out = json.dumps( [ row for row in reader ],sort_keys=True,indent=4)
print out
