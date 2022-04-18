import requests
import datetime

class Student:
    def __init__(self, uid, name, surname, number):
        self.uid = uid
        self.name = name
        self.surname = surname
        self.number = number

    def __str__(self):
        return str((self.uid, self.number, self.name, self.surname))

class Exam:
    def __init__(self, course, name, start, end):
        self.course = course
        self.name = name
        self.start = int(datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").timestamp()*1000)
        self.end = int(datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ").timestamp()*1000)

    def __str__(self):
        return str((self.course, self.name, self.start, self.end))

class DB:
    DB_URL = "https://firestore.googleapis.com/v1/projects/exam-guard/databases/(default)/documents/"

    def stripCourse(url):
        return url.replace("projects/exam-guard/databases/(default)/documents/courses/", '')

    def stripExam(url):
        return url.replace("projects/exam-guard/databases/(default)/documents/courses/.*/exams", '')

    def getDocuments(url):
        return requests.get(url).json().get('documents')
    
    def getStudent(auth):
        data = DB.getDocuments(DB.DB_URL + "students?access_token=" + auth.jwt)
        
        s = list(filter(lambda x: x['fields']['uid']['stringValue'] == auth.getUid(), data))[0]['fields']
        
        return Student(s['uid']['stringValue'], s['name']['stringValue'], s['surname']['stringValue'], s['number']['stringValue'])
    
    def getExams(auth, number):
        access = "access_token=" + auth.jwt
        data = DB.getDocuments(DB.DB_URL + "courses?" + access)

        courses = [DB.stripCourse(d['name']) for d in data]
        courseStudents = {c: DB.getDocuments(DB.DB_URL + "courses/" + c + "/courseStudents?access_token=" + auth.jwt) for c in courses}
        courseList = []
        for c, d in courseStudents.items():
            for s in d:
                if s['fields']['number']['stringValue'] == number:
                    courseList.append(c)
        
        exams = []
        
        for c in courseList:
            for e in DB.getDocuments(DB.DB_URL + "courses/" + c + "/exams"):
                exams.append(Exam(c, DB.stripExam(e['name']), e['fields']['examStartDate']['timestampValue'], e['fields']['examEndDate']['timestampValue']))

        return exams

    def __init__(self, auth):
        self.auth = auth
        self.student = DB.getStudent(self.auth)
        self.exams = DB.getExams(self.auth, self.student.number)

if __name__ == "__main__":
    class A:
        def __init__(self):
            self.jwt = ""

        def getUid(self):
            return "bthn"
    
    auth = A()
    db = DB(auth)
    print(db.student)
    for e in db.exams:
        print(e)