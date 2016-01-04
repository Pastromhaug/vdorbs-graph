import csv, parseMIT

courseHomeLinks = open("courseHomeLinks.txt", "w")
courseSyllabusLinks = open("courseSyllabusLinks.txt", "w")
courseExamLinks = open("courseExamLinks.txt", "w")
courseLectureNotesLinks = open("courseLectureNotesLinks.txt", "w")
courseRecitationLinks = open("courseRecitationLinks.txt", "w")

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
goodCourseNames = courses.keys()

namesofar = []
with open('../data/mit_courseware_data.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        num = row.get('course_num/_text')
        name = row.get('course_name/_text')
        link = row.get('course_num/_source')

        if name in goodCourseNames and name not in namesofar:
            courseno = nameToNumber[name]
            num = courseno[0].split('.')[0]
            try:
                subjectmap[num]
            except:
                continue

            namesofar += name
            print link

            courseHomeLinks.write("http://ocw.mit.edu" +  link)
            courseHomeLinks.write('\n')

            courseSyllabusLinks.write("http://ocw.mit.edu" +  link + "/syllabus")
            courseSyllabusLinks.write('\n')



