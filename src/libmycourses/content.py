class folder:
	def __init__(self, name, cid, mid):
		self.name = name
		self.mid = mid
		self.url = 'https://mycourses2.mcgill.ca/d2l/m/le/content/' + cid + '/toc/moduleList/' + mid
		self.files = []

class file_:
	def __init__(self, name, fid, url):
		self.name = name
		self.fid = fid
		self.url = url
