import requests
import json
import os
import sys
import logging
from enum import Enum

#====================const====================#
baseUrl = "http://bvm/"
log = logging.getLogger()
FORMAT = '%(message)s'  #message ONLY
logging.basicConfig(format= FORMAT,stream=sys.stderr,level=logging.INFO)
version = "1.02"

class EntryOperationType(Enum):
  Add = 0
  Remove = 1
  Modify = 2
          

#====================Input field====================#
#//----------Modify Here----------//#
username = "lahan"
password = "*"

# Weekly BIOS
"""
processorName = "ComboAM4 V2 - Family 19h"
platformName = "Combo_AM4_v2_Artic_AMI_EDKII"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "Weekly BIOS"
# baseBIOSType = "User-Generated"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "WA20916N"
# revision = "D:\\temp\\2.FD"
#You can get all available operations by function GetAvailableOperations
operationType = "PSP";
pspConfig = "CZN"
"""

# PI BIOS

processorName = "Rembrandt - Family 19h"
platformName = "Rev_RMB_Mayan_Insyde_EDKII"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "PI BIOS"
# baseBIOSType = "User-Generated"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "TRM1004B_804_804"
# revision = "D:\\temp\\2.FD"
#You can get all available operations by function GetAvailableOperations
operationType = "PSP"
pspConfig = "RMB"


# By Request Id
"""
processorName = "Rembrandt - Family 19h"
platformName = "Rev_RMB_Mayan_Insyde_EDKII"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "By Request Id"
# baseBIOSType = "User-Generated"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "257232"
# revision = "D:\\temp\\2.FD"
#You can get all available operations by function GetAvailableOperations
operationType = "PSP"
pspConfig = "RMB"
"""

# User-Generated
"""
processorName = "Rembrandt - Family 19h"
platformName = "Rev_RMB_Mayan_Insyde_EDKII"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "User-Generated"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "C:\\DropBox\\Documents\\temp\\base\\1.FD"
#You can get all available operations by function GetAvailableOperations
operationType = "PSP"
pspConfig = "RMB"
"""

purpose = "BVMAPI test\nmultiple line"
newName = ""#leave blank for default name
downloadPath = "D:\\temp\\1.FD"
#//----------Modify End----------//#

#Sign not enabled on API currently
signType = "NOSIGN";
signHP = "0";
signUserName = username;
signPassword = password;

replacementList = [
  #Replace Image Entry Example
  {
  "entryType" : "IMAGE_ENTRY",
  "type" : "0x8",
  "romId" : "0x0",
  "instance" : "0x0",
  "subProgram" : "0x0",
  "operation" : EntryOperationType.Modify.value,
  "filename" : "C:\\Users\\lahan\\Desktop\\BVM\\SMU_46.59.0.bin",
  #Directory Level, Available options: 0x1. 0x2, 0x2A, 0x2B
  "level" : "0x2A",
  #For non-AB-recovery BIOS, this field is equal to level-1
  #For AB-recovery BIOS, this field is the index of PSP/BIOS directory
  "dirIndex" : "0x1",
  #Version string, optional
  "detail" : "4.30.18.0 -> 46.59.0",
  #The entry is a PSP entry or a BIOS entry
  "isPspEntry" : True
  #Only for VALUE_ENTRY
  #value = "0x1",
  #Only for signing, type 0x7
  },
  #Replace Point Entry Example
  {
    "entryType": "POINT_ENTRY",
    "type": "0x4",
    "romId": "0x0",
    "instance": "0x0",
    "subProgram": "0x0",
    "operation": EntryOperationType.Modify.value,
    "filename": "C:\\Users\\lahan\\Desktop\\BVM\\SMU_46.59.0.bin",
    "level": "0x2",
    "dirIndex": "0x1",
    "isPspEntry": True,
    # Only for POINT_ENTRY, point entry offset and size
    "offset": "0x855000",
    "size": "0x20000"
  },
  #Replace Value Entry Example
  {
    "entryType" : "VALUE_ENTRY",
    "type" : "0xb",
    "romId" : "0x0",
    "instance" : "0x0",
    "subProgram" : "0x0",
    "operation" : EntryOperationType.Modify.value,
    "filename" : "C:\\Users\\lahan\\Desktop\\BVM\\SMU_46.59.0.bin",
    "level" : "0x2A",
    "dirIndex" : "0x1",
    "isPspEntry" : True,
    #Only for VALUE_ENTRY
    "value" : "0x1",
  },
  #Add Image Entry Example
  {
  "entryType" : "IMAGE_ENTRY",
  "type" : "0x8",
  "romId" : "0x0",
  "instance" : "0x0",
  "subProgram" : "0x2",
  "operation" : EntryOperationType.Add.value,
  "filename" : "C:\\Users\\lahan\\Desktop\\BVM\\SMU_46.59.0.bin",
  "level" : "0x2A",
  "dirIndex" : "0x1",
  "isPspEntry" : True
  },
  #Remove Image Entry Example
  {
  "entryType" : "IMAGE_ENTRY",
  "type" : "0x8",
  "romId" : "0x0",
  "instance" : "0x0",
  "subProgram" : "0x1",
  "operation" : EntryOperationType.Remove.value,
  "filename" : "C:\\Users\\lahan\\Desktop\\BVM\\SMU_46.59.0.bin",
  "level" : "0x2A",
  "dirIndex" : "0x1",
  "isPspEntry" : True
  },
]

#//----------Modify END----------//#
#====================Functions====================#
def login(username, password):
  log.info("Logging in...")
  url = baseUrl + "api/account/Login"
  cre = {
    "userName":username,
    "Password":password
    }
  headers = {"Content-Type" : "application/json"}
  response = requests.post(url, headers=headers, data=json.dumps(cre))
  if(response.status_code == 200):
    log.info("Log in successful")
    return response.json()['token']
  elif(response.status_code == 401):
    log.error("Log in failed. Please check your username and password.")
  else:
    log.error("Log in failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def GetProcessorList(token):
  log.info("Getting processor list...")
  url = baseUrl + "api/bvmmain/GetProcessorList"
  headers = {"Authorization": "Bearer " + token}
  
  response = requests.get(url, headers=headers)
  if(response.status_code == 200):
    log.info("Get processor list successful")
    return json.loads(response.text)
  elif(response.status_code == 401):
    log.error("Get processor list failed. Please check your credential.")
  else:
    log.error("Get processor list failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def GeneratePspRequest(processorList, processorName, platformName, baseBIOSType, revision, operationType, purpose, newName, pspConfig, token):
  log.info("Generating PSP Request...")
  (processorId, processor) = GetProcessorId(processorList, processorName)
  if(processorId == None):
    log.error("Failed to get processor Id")
    return None
  
  (platformId, platform) = GetPlatformId(processor, platformName)
  if(platformId == None):
    log.error("Failed to get platform Id")
    return None
  
  revision = GetRevision(platform, baseBIOSType, revision, token)
  if(revision == None):
    log.error("Failed to get revision")
    return None
  
  operationTypeStr = GetOperationType(operationType)
  if(operationTypeStr == None):
    log.error("Failed to get operation type")
    return None
  
  url = baseUrl + "api/bvmpsp/GeneratePspRequest"
  url = url + "?processorId=" + processorId
  url = url + "&platformId=" + platformId
  url = url + "&baseBIOSType=" + baseBIOSType
  url = url + "&revision=" + revision
  url = url + "&operationType=" + operationTypeStr
  url = url + "&purpose=" + purpose
  url = url + "&newName=" + newName
  url = url + "&isApi=1"
  url = url + "&selectedPspConfig=" + pspConfig
  headers = {"Authorization": "Bearer " + token}
  
  response = requests.get(url, headers=headers)
  if(response.status_code == 200):
    log.info("Generate PSP Request successful")
    return response.text
  else:
    log.error("Generate PSP Request failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def GetProcessorId(processorList, processorName):
  for p in processorList:
    if(p["name"] == processorName):
      return (p["id"], p)
  return (None, None)

def GetPlatformId(processor, platformName):
  for p in processor["platforms"]:
    if(p["name"] == platformName):
      return (p["id"], p)
  return (None, None)

def GetRevision(platform, baseBIOSType, revision, token):
  if(baseBIOSType == "Weekly BIOS"):
    return GetWeeklyBIOSId(platform, revision)
  elif(baseBIOSType == "PI BIOS"):
    return GetPIBIOSId(platform, revision)
  elif(baseBIOSType == "User-Generated"):
    return UploadUserGenBIOS(revision, token)
  elif(baseBIOSType == "By Request Id"):
    return revision
  return None

def GetWeeklyBIOSId(platform, revision):
  for w in platform["weeklyBIOSes"]:
    if(w["name"] == revision):
      return w["id"]
  return None

def GetPIBIOSId(platform, revision):
  for p in platform["piBIOSes"]:
    if(p["name"] == revision):
      return p["id"]
  return None

def UploadUserGenBIOS(revision, token):
  url = baseUrl + "api/bvmmain/UploadBaseBIOS?name=filename"
  headers = {"Authorization": "Bearer " + token}
  files = {"file": ("apibios.bin", open(revision, 'rb'))}
  
  response = requests.post(url, files=files, headers=headers)
  
  if(response.status_code == 200):
    return response.content.decode("ascii")
  else:
    log.error("Upload user-gen BIOS failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def GetOperationType(operationType):
  ao = GetAvailableOperations()
  #check if operation is available
  for key, value in ao.items():
    if(value == operationType):
      return key
  return None

def GetAvailableOperations():
  url = baseUrl + "api/bvmpsp/GetAvailableOperations"
  
  response = requests.get(url)
  if(response.status_code == 200):
    return json.loads(response.text)
  else:
    log.error("Get available operations failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def UpdateName(requestId, updateName, token):
  log.info("Updating name...")
  url = baseUrl + "api/bvmmain/UpdateNewName"
  url = url + "?requestId=" + requestId
  url = url + "&newName=" + updateName
  headers = {"Authorization": "Bearer " + token}
  
  response = requests.post(url, headers=headers)
  
  if(response.status_code != 200):
    log.error("Update name failed. Status code: %d. Reason: %s", response.status_code, response.reason)
    return None
  
  log.info("Update name successful")
  return 1

def UploadReplacement(requestId, replacementList, token):
  log.info("Uploading replaced binary...")
  url = baseUrl + "api/bvmpsp/UploadPspEntry"
  headers = {"Authorization": "Bearer " + token}
  
  for r in replacementList:
    if(r["operation"] == EntryOperationType.Remove.value):
      continue
    url_r = url
    url_r = url_r + "?dirType=" + "PSP" if r["isPspEntry"] else "BIOS"
    url_r = url_r + "&type=" + r["type"]
    url_r = url_r + "&romId=" + r["romId"]
    url_r = url_r + "&instance=" + r["instance"]
    url_r = url_r + "&subProgram=" + r["subProgram"]
    url_r = url_r + "&requestId=" + requestId
    url_r = url_r + "&dirIndexStr=" + r["dirIndex"]

    if r["type"] == "0x4" or r["type"] == "0x54":
      url_r = url_r + "&offset=" + r["offset"]

    files = {"file": ("apifile.bin", open(r["filename"], 'rb'))}
    response = requests.post(url_r, files=files, headers=headers)
    
    if(response.status_code != 200):
      log.error("Upload replaced binary failed. Status code: %d. Reason: %s", response.status_code, response.reason)
      return None
  log.info("Upload replaced binary successful")
  return 1

def SubmitPspRequest(requestId, signType, signHP, signUserName, signPassword, replacementList, token):
  log.info("Submitting PSP Request...")
  url = baseUrl + "api/bvmpsp/SubmitRequestAPI"
  url = url + "?requestId=" + requestId
  url = url + "&signType=" + signType
  url = url + "&signHP=" + signHP
  url = url + "&signUserName=" + signUserName
  url = url + "&signPassword=" + signPassword
  headers = {"Authorization": "Bearer " + token, "Content-Type" : "application/json"}
  
  #Update filename to BVM_apifile.bin
  for r in replacementList:
    r["filename"] = "BVM_apifile.bin"

  response = requests.post(url, data=json.dumps(replacementList), headers=headers)
  if(response.status_code == 200):
    log.info("Submit PSP Request successful")
    return 1
  else:
    log.error("Submit PSP Request failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def DownloadBIOS(requestId, downloadPath):
  log.info("Downloading BIOS...")
  
  try:
    OutputHandle = open (downloadPath,'wb')
  except:
    raise Exception("Error: Opening {}".format(downloadPath))
  
  url = baseUrl + "api/bvmresult/DownloadBIOSByRequestId?requestId=" + requestId
  
  response = requests.get(url)
  if(response.status_code == 200):
    OutputHandle.write(response.content)
    log.info("Download BIOS successful")
    return 1
  else:
    log.error("Download BIOS failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def DownloadTar(requestId, downloadPath):
  log.info("Downloading Tar...")
  
  try:
    OutputHandle = open (downloadPath,'wb')
  except:
    raise Exception("Error: Opening {}".format(downloadPath))
  
  url = baseUrl + "api/bvmresult/DownloadTarByRequestId?requestId=" + requestId
  
  response = requests.get(url)
  if(response.status_code == 200):
    OutputHandle.write(response.content)
    log.info("Download Tar successful")
    return 1
  else:
    log.error("Download Tar failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

#====================Main====================#
def main():

  token = login(username, password)
  if not token:
    return

  processorList = GetProcessorList(token)
  if not processorList:
    return
  
  requestId = GeneratePspRequest(processorList, processorName, platformName, baseBIOSType, revision, operationType, purpose, newName, pspConfig, token)
  if not requestId:
    return
  #Remove " in requestId
  requestId = requestId.replace('"', "")
  
  # updateName = "VXX" + str(requestId) + "N.FD"
  # result = UpdateName(requestId, updateName, token)
  # if not result:
    # return
  
  result = UploadReplacement(requestId, replacementList, token)
  if not result:
    return
  
  result = SubmitPspRequest(requestId, signType, signHP, signUserName, signPassword, replacementList, token)
  if not result:
    return
  
  result = DownloadBIOS(requestId, downloadPath)
  # You may download tar file instead by below command
  # result = DownloadTar(requestId, downloadPath)
  if not result:
      return

if __name__ == "__main__":
  main()