import requests
import json
import sys
import logging

#====================const====================#
baseUrl = "http://bvm/"
# baseUrl = "https://localhost:44379/"
log = logging.getLogger()
FORMAT = '%(message)s'  #message ONLY
logging.basicConfig(format= FORMAT,stream=sys.stderr,level=logging.INFO)
version = "1.00"

#====================Input field====================#
#//----------Modify Here----------//#
username = ""
password = ""

purpose = "BVMAPI test\nmultiple line"
# leave blank for default name
newName = ""
downloadPath = "D:\\Output\\BVM\\1.FD"

# Weekly BIOS
"""
processorName = "StrixPoint - Family 1Ah"
platformName = "Rev_STX_BirmanPlus_AMD_EDKII_64M"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "Weekly BIOS"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "WXB4110N_312"
"""

# PI BIOS
"""
processorName = "StrixPoint - Family 1Ah"
platformName = "Rev_STX_BirmanPlus_AMD_EDKII_64M"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "PI BIOS"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "TXB0076C_313"
"""

# By Request Id
"""
processorName = "StrixPoint - Family 1Ah"
platformName = "Rev_STX_BirmanPlus_AMD_EDKII_64M"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "By Request Id"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "862589"
"""

# User-Generated

processorName = "StrixPoint - Family 1Ah"
platformName = "Rev_STX_BirmanPlus_AMD_EDKII_64M"
#Available base BIOS types: Weekly BIOS, PI BIOS, User-Generated, By Request Id
baseBIOSType = "User-Generated"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = r"D:\Input\BCT_Binary\for_option_rom\\VXB1512N.FD"


replacementList = [
  {
  "guid" : "348C4D62-BFBD-4882-9ECE-C80BB1C4783B",
  "file" : r"D:\Input\BCT_Binary\for_option_rom\OptionRom3.bin",
  },
  {
    "guid" : "61F0BA73-93A9-419D-BD69-ADE3C5D5217B",
    "file": r"D:\Input\BCT_Binary\for_option_rom\OptionRom5.bin",
  }
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
  response = requests.post(url, headers=headers, data=json.dumps(cre), verify=False)
  if(response.status_code == 200):
    log.info("Log in successfully")
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
  
  response = requests.get(url, headers=headers, verify=False)
  if(response.status_code == 200):
    log.info("Get processor list successfully")
    return json.loads(response.text)
  elif(response.status_code == 401):
    log.error("Get processor list failed. Please check your credential.")
  else:
    log.error("Get processor list failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def GenerateOptionRomRequest(processorList, processorName, platformName, baseBIOSType, revision,  purpose, newName, token):
  log.info("Generating Option Rom Request...")
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

  url = baseUrl + "api/bvmoptionrom/GenerateOptionRomRequest"

  headers = {"Authorization": "Bearer " + token}
  parameter_dict = {"processorId": processorId,
                    "platformId": platformId,
                    "baseBIOSType": baseBIOSType,
                    "revision": revision,
                    "purpose": purpose,
                    "newName": newName
                    }

  response = requests.get(url, params=parameter_dict, headers=headers, verify=False)
  if(response.status_code == 200):
    log.info("Generate Option Rom Request successfully")
    return response.text
  else:
    log.error("Generate Option Rom failed. Status code: %d. Reason: %s", response.status_code, response.reason)
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
  
  response = requests.post(url, files=files, headers=headers, verify=False)
  
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
  
  log.info("Update name successfully")
  return 1

def UploadReplacement(requestId, replacementList, token):
  log.info("Uploading replaced binary...")
  url = baseUrl + "api/bvmoptionrom/UploadOptionRomAPI"
  headers = {"Authorization": "Bearer " + token}
  
  for r in replacementList:
    url_r = url
    url_r = url_r + "?requestId=" + requestId
    url_r = url_r + "&guid=" + str(r["guid"])

    files = {"file": ("apifile.bin", open(r["file"], 'rb'))}
    response = requests.post(url_r, files=files, headers=headers, verify=False)
    
    if(response.status_code != 200):
      log.error("Upload replaced binary failed. Status code: %d. Reason: %s", response.status_code, response.reason)
      return None
  log.info("Upload replaced binary successfully")
  return 1


def SubmitOptionRomRequest(requestId,replacementList, token):
  log.info("Submitting Option Rom Request...")
  url = baseUrl + "api/bvmoptionrom/SubmitOptionRomRequestAPI"
  url = url + "?requestId=" + requestId
  headers = {"Authorization": "Bearer " + token, "Content-Type" : "application/json"}
  guid_list = list()
  for r in replacementList:
    guid_list.append(r["guid"])
    #r["file"] = "\\".join(["E:\\Tools\\BVM_V4\\requests", requestId, str(r["index"]), "BVM_apifile.bin"])
  response = requests.post(url, data=json.dumps(guid_list), headers=headers, verify=False)
  if(response.status_code == 200):
    log.info("Submit Option Rom Request successfully")
    return 1
  else:
    log.error("Submit Option Rom Request failed. Status code: %d. Reason: %s", response.status_code, response.reason)
  return None

def DownloadBIOS(requestId, downloadPath):
  log.info("Downloading BIOS...")
  
  try:
    OutputHandle = open (downloadPath,'wb')
  except:
    raise Exception("Error: Opening {}".format(downloadPath))
  
  url = baseUrl + "api/bvmresult/DownloadBIOSByRequestId?requestId=" + requestId
  
  response = requests.get(url, verify=False)
  if(response.status_code == 200):
    OutputHandle.write(response.content)
    log.info("Download BIOS successfully")
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
    log.info("Download Tar successfully")
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
  
  requestId = GenerateOptionRomRequest(processorList, processorName, platformName, baseBIOSType, revision,  purpose, newName, token)
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
  
  result = SubmitOptionRomRequest(requestId, replacementList, token)
  if not result:
    return
  
  result = DownloadBIOS(requestId, downloadPath)
  # You may download tar file instead by below command
  # result = DownloadTar(requestId, downloadPath)
  if not result:
      return

if __name__ == "__main__":
  main()