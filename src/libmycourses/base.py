import user
import requests
import re
import course
import os
import pickle
from bs4 import BeautifulSoup

class mycourses:
	def __init__(self):
		self.__mycourses_domain = "https://mycourses2.mcgill.ca"
		self.__mycourses_index_page = "https://mycourses2.mcgill.ca/"
		self.__shibboleth_domain = "https://shibboleth.mcgill.ca"
		self.__shibboleth_login_page = "https://mycourses2.mcgill.ca/Shibboleth.sso/Login?entityID=https://shibboleth.mcgill.ca/idp/shibboleth&target=https%3A%2F%2Fmycourses2.mcgill.ca%2Fd2l%2FshibbolethSSO%2Flogin.d2l"
		self.__useragent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7"
		self.__request_header = {'user-agent':self.__useragent }
		self.session = requests.Session()
		self.session.headers.update(self.__request_header)
		self.__course_match_pattern = re.compile("(\w{4,6}) (\d{4}) - (\w{3,4})-(\d{3})-(\d{3}) - (.+)")
		self.__course_id_match_pattern = re.compile("""\\\/home\\\/(\d+)""")
		self.__datadir = os.environ['HOME']+"/.libmycourses"
		if not os.path.exists(self.__datadir):
			os.mkdir(self.__datadir)
	def login(self, user):
		self.user = user
		self.__do_login()
		if self.loginsuccess:
			with open(self.__datadir+"/"+self.user.username, 'w') as f:
				pickle.dump(self.session, f)
			
	def __parse(self,source):
		res = BeautifulSoup(source)
		courses_containing_nodes = res.find_all("li", class_="d2l-itemlist-simple d2l-itemlist-arrow d2l-itemlist-short")
		ids = self.__course_id_match_pattern.finditer(source)
		for course_containing_node in courses_containing_nodes:
			strings = course_containing_node.stripped_strings
			m = self.__course_match_pattern.match(strings.next())
			if m != None:
				c = course.course(m.group(1),m.group(2),m.group(3),m.group(4),m.group(5),m.group(6),ids.next().group(1), self.session)
				self.user.courses.append(c)
			

	def __do_login(self):
		# try loading previous session
		try:
			with open(self.__datadir+"/"+self.user.username, 'r') as f:
				self.session = pickle.load(f)
		except:
			pass
		r = self.session.get("https://mycourses2.mcgill.ca/d2l/m/home")
		if "Home - myCourses" in r.text:
			self.loginsuccess = True
			self.__parse(r.text)
			return

		# first get the index page of mycourses
		r = self.session.get(self.__mycourses_index_page)
		# then go to shibboleth login page
		r = self.session.get(self.__shibboleth_login_page)
		# make login payload data
		payload = {'j_username': self.user.username,
					'j_password': self.user.password}
		r = self.session.post(self.__shibboleth_domain + '/idp/Authn/UserPassword', data=payload)

		res = BeautifulSoup(r.text)
		# continue button must be pressed manually
		continue_form_url = "https://mycourses2.mcgill.ca/Shibboleth.sso/SAML2/POST"
		# use beautiful soup to find RelayState and SAMLResponse
		try:
			RelayState = res.find(attrs={"name": "RelayState"})['value']
			SAMLResponse = res.find(attrs={"name": "SAMLResponse"})['value']
		except:
			self.loginsuccess = False
			raise LoginError("Cannot retrieve SAMLResponse, username and password are probably wrong")
		# build new payload
		payload = {'RelayState': RelayState,
					'SAMLResponse': SAMLResponse}
		r = self.session.post(continue_form_url, data=payload)
		r = self.session.get("https://mycourses2.mcgill.ca/d2l/lp/auth/login/ProcessLoginActions.d2l")
		result = r.text
		if not "Home - myCourses" in result:
			self.loginsuccess = False
			raise LoginError("Cannot complete final login step")
		self.loginsuccess = True
		self.__parse(result)
		
		
class LoginError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)	
