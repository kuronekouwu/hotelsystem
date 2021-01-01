import uvicorn
import fastapi
import pymongo
import json
import hashlib
import datetime
import os
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field

#Set Path
path_config = "bin/config.json"
path_idcard = "bin/api/idcard"
path_slipbank = "bin/api/slipbank"

with open(path_config,"r",encoding="utf8") as conf :
	d_config = json.loads(conf.read())

#Create APP 
app = FastAPI(
	docs_url=None,
	redoc_url=None,
	secret_key="Fwbh2n4jrQQAqw8PVMv5dQgN4UQTRTwUkecsnQ8g7sLGstqxa6KSfMDvzkB5UbWe"
)

#Set Class 
class requestsdataidcard(BaseModel) :
	uuid : str = Field(...,min_length=1)

class requestsdataslipbank(BaseModel) :
	uuid : str = Field(...,min_length=1)
	uuid_book : str = Field(...,min_length=1)


@app.post("/idcardimage", include_in_schema=False)
def idcardimage(data: requestsdataidcard=None) :
	if not data is None :
		c = __checkreq(uuid=data.uuid)

		if not c is None :
			if os.path.isfile(f"{path_idcard}/{hashlib.md5(c['_id'].__str__().encode()).hexdigest()}.jpg") :
				return FileResponse(f"{path_idcard}/{hashlib.md5(c['_id'].__str__().encode()).hexdigest()}.jpg")

			raise HTTPException(status_code=404,detail={"code" : "ERR_NOTFOUND"})
		
	
	raise HTTPException(status_code=401,detail={"code" : "ERR_AUTHFAIL"})

@app.post("/slipbankimage", include_in_schema=False)
def slipbankimage(data: requestsdataslipbank=None) :
	if not data is None :
		c = __checkreq(uuid=data.uuid)

		if not c is None :
			if os.path.isfile(f"{path_slipbank}/{data.uuid_book}.jpg") :
				return FileResponse(f"{path_slipbank}/{data.uuid_book}.jpg")

			raise HTTPException(status_code=404,detail={"code" : "ERR_NOTFOUND"})
		
	
	raise HTTPException(status_code=401,detail={"code" : "ERR_AUTHFAIL"})

@app.post("/checkidcard", include_in_schema=False)
def checkidcard(data: requestsdataidcard=None) :
	if not data is None :
		c = __checkreq(uuid=data.uuid)
		if  not c is None :
			if os.path.isfile(f"{path_idcard}/{hashlib.md5(c['_id'].__str__().encode()).hexdigest()}.jpg") :
				return {"code" : True} 
			
			return {"code" : False} 
		
	raise HTTPException(status_code=401,detail={"code" : "ERR_AUTHFAIL"})

@app.post("/getuuid", include_in_schema=False)
def getid(data: requestsdataidcard=None) :
	if not data is None :
		c = __checkreq(uuid=data.uuid)
		if  not c is None :
			return {"code" : "%s" % hashlib.md5(c['_id'].__str__().encode()).hexdigest()}

#Function
def __connectdb() :
	try :
		conn = pymongo.MongoClient(__getconnectmongodb(),serverSelectionTimeoutMS=5000)
		conn.server_info()

		return conn
	except Exception as e :
		raise HTTPException(status_code=500,detail={"code" : "ERR_CONNECTFAILED"})

def __getconfigmongodb() :
	global path_config

	with open(path_config,"r",encoding="utf8") as conf :
		d = json.loads(conf.read())

		res = {
			"db" : d["mongodb"]["database"]
		}

		return res

def __getconnectmongodb() :
	global path_config

	with open(path_config,"r",encoding="utf8") as conf :
		d = json.loads(conf.read())
		if d["mongodb"]["srv"] is True :
			res = "mongodb+srv://%s:%s@%s/%s" % (
				d["mongodb"]["username"],
				d["mongodb"]["password"],
				d["mongodb"]["host"],
				d["mongodb"]["database_auth"]
			)
		else :
			res = "mongodb://%s:%s@%s:%s/%s" % (
				d["mongodb"]["username"],
				d["mongodb"]["password"],
				d["mongodb"]["host"],
				d["mongodb"]["port"],
				d["mongodb"]["database_auth"]
			)

		return res

def __checkreq(uuid) :
	conn = __connectdb()

	return conn[__getconfigmongodb()["db"]]["user_members"].find_one({
		"uuid" : "%s" % uuid
	})

if __name__ == "__main__" :
	uvicorn.run(app,host="127.0.0.1",port=8085)

