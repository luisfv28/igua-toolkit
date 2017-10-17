Assume you stored that dictionary in a variable called values. To get id in to a variable, do:

idValue = values['criteria'][0]['id']
If that json is in a file, do the following to load it:

import json
jsonFile = open('your_filename.json', 'r')
values = json.load(jsonFile)
jsonFile.close()
If that json is from a URL, do the following to load it:

import urllib, json
f = urllib.urlopen("http://domain/path/jsonPage")
values = json.load(f)
f.close()
To print ALL of the criteria, you could:

for criteria in values['criteria']:
    for key, value in criteria.iteritems():
        print key, 'is:', value
    print ''
