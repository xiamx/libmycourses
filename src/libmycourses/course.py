class course:
	def __init__(self,semester, year, subject, course_number, section_number, name, cid):
		self.semester = semester
		self.year = year
		self.subject = subject
		self.course_number = course_number
		self.section_number = section_number
		self.name = name
		self.cid = cid
		pass
	def __str__(self):
		return self.semester + " " + \
				self.year + " - " +\
				self.subject + "-" +\
				self.course_number + "-" +\
				self.section_number + " - " +\
				self.name
