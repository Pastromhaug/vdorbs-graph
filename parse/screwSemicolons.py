import sys, datetime, csv, urllib2, string, json, re
from collections import defaultdict

f = open('../data/Mit Courses 16th Dec 14_44.json', 'r')
j = f.read()
l = json.loads(j)

groups = {
	'Physics I (GIR)' : ['8.011', '8.012', '8.01L'],
	'Pysics II (GIR)' : ['8.02', '8.021', '8.022'],
	'Calculus I (GIR)' : ['18.01', '18.014', '18.01A'],
	'Calculus II (GIR)' : ['18.02', '18.022', '18.044', '18.02A'],
	'Biology (GIR)' : ['7.012', '7.013', '7.014', '7.015', '7.016'],
	'Chemistry (GIR)' : ['3.091', '5.111', '5.112']
}

results = []
for page in l['pages']:
	results += page['results']

#create a map of MIT syllabus numbers to sullabus names, as well as names no numbers
courseno = re.compile("^.*\..\S*")
syllabus_num_to_name = {}
syllabus_name_to_num  = {}
for result in results:
	full = result['my_column']
	result = courseno.match(full)
	num = result.group(0)
	num_list = [num]
	name = full.replace(num + ' ', '');
	if "," in num:
		num_list = num.split(",")
	for num in num_list:
		#update syllabus_num_to_name
		if num in syllabus_num_to_name.keys():
			l = []
			names = syllabus_num_to_name.get(num)
			l += names
			l.append(name)
			syllabus_num_to_name[num] = l
		else: 
			syllabus_num_to_name[num] = [name]
		#update syllabus_name_to_num
		if name in syllabus_name_to_num.keys():
			l = []
			nums = syllabus_name_to_num.get(name)
			l += nums
			l.append(num)
			syllabus_name_to_num[name] = l
		else:
			syllabus_name_to_num[name] = [num]

#construct dictionaries from MIT Courseware data
courseware_num_to_name = {}
courseware_name_to_num = {}
courseware_num_to_link = {}
with open('../data/mit_courseware_data.csv') as f:
	reader = csv.DictReader(f)
	for row in reader:
		num = row.get('course_num/_text')
		name = row.get('course_name/_text')
		link = row.get('course_num/_source')
		if num in courseware_num_to_name.keys():
			l = []
			names = courseware_num_to_name.get(num)
			l += names
			l.append(name)
			courseware_num_to_name[num] = l
		else:
			courseware_num_to_name[num] = [name]
		if name in courseware_name_to_num.keys():
			l = []
			nums = courseware_name_to_num.get(name)
			l += nums
			l.append(num)
			courseware_num_to_name[name] = l
		else:
			courseware_name_to_num[name] = [num]
		if link in courseware_num_to_link.keys():
			l = []
			linkes = courseware_num_to_link.get(num)
			l += linkes
			l.append(link)
			courseware_num_to_link[num] = l;
		else:
			courseware_num_to_link[num] = [link]

#construct dictionary of course to pre-reqs, subbing with Courseware names
course_dictionary = defaultdict(list)
for result in results:
	full = result['my_column']
	r = courseno.match(full)
	num = r.group(0)
	name = full.replace(num + ' ', '');
	course_nums = syllabus_name_to_num[name]
	course_name = ''
	for n in course_nums:
		if (courseware_num_to_name.get(n) != None):
			course_name = courseware_num_to_name.get(n)[0];
			break;
	#print course_name;
	if course_name == '':
		continue
	elif (result.get('prerequisites') == None):
		course_dictionary[course_name] = [];
		continue
	req_full = result['prerequisites'].replace("Prereq: ", '').replace("\"", "\'")
	c = req_full.split('Coreq: ');
	if (len(c) > 1):
		coreq = c[1]
	prereqs = c[0]
	req_parts = re.split('; ', prereqs);
	req_list = []
	for part in req_parts:
		ors = part.split(" or ");
		orlist = []
		if (len(ors) > 0):
			for o in ors:
				courses = o.split(",");
				for course in courses:
					if ('permission of instructor' not in course and 'Permission of Instructior' not in course
						and 'None' not in course and course != ''):
						if groups.get(course) != None:
								part = part.replace(course, '')
								orlist += groups.get(course)
						else:
							orlist.append(course);
							part = part.replace(course, '')
			req_list.append(orlist)
		ands = part.split("and")
		if (len(ands) > 0):
			for a in ands:
				courses = a.split(",")
				for course in courses:
					if ('permission of instructor' not in course and 'Permission of Instructior' not in course
						and 'None' not in course and course != ''):
						if groups.get(course) != None:
								part = part.replace(course, '')
								group = groups.get(course)
								for g in group:
									req_list.append([g])
						else:
							part = part.replace(course, '')
							req_list.append([course])
		if (len(ands) == 0 and len(ors) == 0):
			courses = part.split(",")
			for course in courses:
					if ('permission of instructor' not in course and 'Permission of Instructior' not in course
						and 'None' not in course and course != ''):
						if groups.get(course) != None:
								group = groups.get(course)
								for g in group:
									req_list.append([g])
						else:
							req_list.append([course])
	course_dictionary[course_name] = req_list;

for course in course_dictionary.keys():
	l = []
	pre_rex = course_dictionary[course]
	for rec in pre_rex:
		l2 = []
		for r in rec:
			#print r.strip()
			if (courseware_num_to_name.get(r.strip()) != None):
				l2.append(courseware_num_to_name[r.strip()])
		l+=l2
	course_dictionary[course] = l

return (course_dictionary, courseware_name_to_num)







