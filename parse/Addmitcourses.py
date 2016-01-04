from neo4jrestclient.client import GraphDatabase
import parseMIT

import json

with open('../config.json') as data_file:
    config = json.load(data_file)


db = GraphDatabase("http://localhost:" + config['neo4jPort'], username=config['neo4jUser'], password=config['neo4jPassword'])

subjectmap = {
    '1': 'Civil and Environmental Engineering',
    '2': 'Mechanical Engineering',
    '3': 'Materials Science and Engineering',
    '4': 'Architecture',
    '5': 'Chemistry',
    '6': 'Electrical Engineering and Computer Science',
    '7': 'Biology',
    '8': 'Physics',
    '9': 'Brain and Cognitive Sciences',
    '10': 'Chemical Engineering',
    '11': 'Urban Studies and Planning',
    '12': 'Earth, Atmospheric, and Planetary Sciences',
    '14': 'Economics',
    '15': 'Management',
    '16': 'Aeronautics and Astronautics',
    '17': 'Political Science',
    '18': 'Mathematics',
    '20': 'Biological Engineering'
}


(courses, nameToNumber) = parseMIT.gimmelists()
print len(courses)


t = 0
for coursename in courses.keys():
    prerequisitelist = courses[coursename]
    courseno = nameToNumber[coursename]

    num = courseno[0].split('.')[0]
    try:
        subjectmap[num]
    except:
        continue
    t = t + 1
    print "name: " + coursename + "   number: " + courseno[0]
    for prereqOrGroup in prerequisitelist:
        for prereqName in prereqOrGroup:
            prereqno = nameToNumber[prereqName]
            print "name: " + prereqName + "   number: " + prereqno[0]
            query = ""
            query = query + "MERGE (c:MITcourse {name:\""+coursename+"\",coursenum:\""+courseno[0]+"\"})"
            query = query + "MERGE (p:MITcourse {name:\""+prereqName+"\",coursenum:\""+prereqno[0]+"\"})"
            query = query + "MERGE (c) <- [:prereq] - (p)"
            query = query + ";"
            results = db.query(query)
            for r in results:
                print(r)
print t
query = 'match (n:MITcourse) optional match n -[:prereq] -> (b) return n.name, n.coursenum, count(b)'
results = db.query(query)
for r in results:
    name = r[0]
    num = r[1]
    subjectno = str(num).split('.')[0]
    subject = ""
    try:
        subject = subjectmap[subjectno]
    except:
        subject = "?"
    edges = r[2]
    print name + ",   edges: " + str(edges)+ "     subject: " + subject + "        subjectno: " + str(subjectno)
    query = 'match (n:MITcourse) where n.name = \''+name+'\' set n.outedges = '+str(edges)+' set n.subject = \''+subject + '\''
    results = db.query(query)
    for r in results:
        print r
