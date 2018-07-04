from pymongo import MongoClient
import gridfs

db = MongoClient().gridfs_example
fs = gridfs.GridFS(db)
def write():
	#a = fs.put(b"hello world")
	#print "a is ", a, type(a)
	#print "get a ", fs.get(a).read()
	a = fs.put(open("November.pdf"), filename="Nov" )

def read():
	query = {"filename":"Nov"}
	for i in fs.find(query):
		print i, i.filename, i._id, i.length, i.chunkSize

def delete():
	query = {"filename":"Nov"}
	lst = []
	for i in fs.find(query):
		lst.append(i._id)
	
	for i in lst:
		print "deleting _id:", i
		fs.delete(i)

def drop():
	db.drop_collection('fs.files')
	db.drop_collection('fs.chunks')


def save():
	query = {"filename":"Nov"}
	lst = []
	for i in fs.find(query):
		lst.append(i._id)
	
	for i in lst:
		obj = fs.get(i)
		print "saving obj", obj, "_id=", i
		#fs.put(obj,filename=str(i))  # put to database
		#fd = open("./out.data", "rb")
		with open('gridout.dat', 'wb') as fd:
			fd.write(obj.read()) # call gridfs.grid_file.GridOut read to read binary stream

#delete()
#drop()
#write()
print "read 1"
read()
#print "read 2"
#read()
save()
