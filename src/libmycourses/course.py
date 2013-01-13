import re
import content
from bs4 import BeautifulSoup

class course:
	def __init__(self,semester, year, subject, course_number, section_number, name, cid, session):
		self.semester = semester
		self.year = year
		self.subject = subject
		self.course_number = course_number
		self.section_number = section_number
		self.name = name
		self.cid = cid
		self.url = {}
		self.url['domain'] = 'https://mycourses2.mcgill.ca'
		self.url['base'] = 'https://mycourses2.mcgill.ca/d2l/m'
		self.url['content'] = self.url['base'] + \
				"/le/content/"+ self.cid + \
				"/toc/list"
		self.url['home'] =  self.url['base'] + \
				"/home/"+ \
				self.cid
		self.url['discussion'] =  self.url['base'] + \
				"/le/" + \
				self.cid + \
				"/discussions/list"
		self.session = session
		self.folders = []
		pass
	def __str__(self):
		return self.semester + " " + \
				self.year + " - " +\
				self.subject + "-" +\
				self.course_number + "-" +\
				self.section_number + " - " +\
				self.name
	def load_content(self):
		content_folder_pattern = re.compile('(\d+)".+"\\\/d2l\\\/m\\\/le\\\/content\\\/\d+\\\/toc\\\/moduleList\\\/(\d+)')
		source = self.session.get(self.url['content']).text

		matches = content_folder_pattern.finditer(source)	
		for match in matches:
			mid = match.group(2)
			f = content.folder('', self.cid, mid)
			r = self.session.get(f.url)
			res = BeautifulSoup(r.text)
			f.name = res.find(name="li", class_='\\"d2l-cardstack-item\\"').contents[1].contents
			filenodes = res.find_all(name="li", class_='\\"d2l-itemlist-simple')
			for filenode in filenodes:
				ahref = filenode.find("a")
				url = self.url['base'] + ahref['href'].replace('\\"',"").replace("/d2l/m","")
				name = ahref.find("span").contents
				fid = re.search("/view/(\d+)", url).group(1)


				s = self.session.get(url)
				fileres = BeautifulSoup(s.text)
				url = self.url['domain'] + fileres.find(name="a", class_="topiclink")["href"]
				print url
				file_ = content.file_(name, fid, url)
				f.files.append(file_)
				
			self.folders.append(f)
		
