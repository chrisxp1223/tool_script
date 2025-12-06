import requests
import json
import sys
import logging


#====================const====================#
baseUrl = "http://bvm/"
log = logging.getLogger()
FORMAT = '%(message)s'  #message ONLY
logging.basicConfig(format= FORMAT,stream=sys.stderr,level=logging.INFO)
version = "1.03"


#====================Input field====================#
#//----------Modify Here----------//#
username = "boyachen"
password = "***"

# By Request Id

processorName = "Phoenix - Family 19h"
platformName = "Rev_PHX_Mayan_AMD_EDKII"
# Available base BIOS types: Weekly BIOS, PI BIOS,  By Request Id
baseBIOSType = "By Request Id"
revision = "697408"
cbsConfigProgram = "Rev_PHX_Mayan_AMD_EDKII"


"""
# Weekly BIOS
processorName = "Phoenix - Family 19h"
platformName = "Rev_PHX_Mayan_AMD_EDKII"
# Available base BIOS types: Weekly BIOS, PI BIOS,  By Request Id
baseBIOSType = "Weekly BIOS"
revision = "W2M3524N"
cbsConfigProgram = "Rev_PHX_Mayan_AMD_EDKII"

# PI BIOS

processorName = "Phoenix - Family 19h"
platformName = "Rev_PHX_Mayan_AMD_EDKII"
# Available base BIOS types: Weekly BIOS, PI BIOS,  By Request Id
baseBIOSType = "PI BIOS"
# baseBIOSType = "User-Generated"
#Available base BIOS types: "WQX9403N", "TQX1004M", "D:\\temp\\myBIOS.FD", "1023"
revision = "T2M1001D_151"
cbsConfigProgram = "Rev_PHX_Mayan_AMD_EDKII"

"""



#0 means CBS Override function, 1 means GBS modification. GBS modification is not supported by API
isGbs = "0"
purpose = "BVMAPI test\n # multiple line"
newName = ""#leave blank for default name
downloadPath = "D:\\temp\\1.FD"

#Sign function parameters
signType = "NOSIGN";#NOSIGN => sign disabled, PK => sign enabled
signUserName = username;
signPassword = password;
signSpFunction = "SIGN REMBRANDT BIOS (4K)";#You need to know the SP Function for the platform. You may get available SP Functions at below servers.
"""
https://atlkds-proxy01.amd.com/pspsp
https://atlkds-proxy02.amd.com/pspsp
https://cybkds-proxy01.amd.com/pspsp
https://cybkdsweb02/pspsp
https://atlkdsappv02/pspsp
https://atlkdsapp04.amd.com/pspsp
https://atlkdsappdev01/pspsp
"""
signHP = "0";

replacementList = [
  {
    "CbsCmnCpuSmuPspDebugMode":"0"
  },
  {
    "CbsDbgRomArmorSupport": "0"
  }
#==========required only if sign enabled end==========#
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

def GenerateCbsRequest(processorList, processorName, platformName, baseBIOSType, revision, cbsConfigProgram, purpose,  isGbs, newName, token):
  log.info("Generating CBS Request...")
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

  url = baseUrl + "api/bvmcbsoverride/GenerateConstructedRequest"

  headers = {"Authorization": "Bearer " + token}

  parameter_dict = {"processorId": processorId,
                    "platformId": platformId,
                    "baseBIOSType": baseBIOSType,
                    "revision": revision,
                    "cbsConfigProgram": cbsConfigProgram,
                    "purpose": purpose,
                    "isGbs": isGbs,
                    "newName": newName,
                    "isApi": 1
                    }
  
  response = requests.get(url, params = parameter_dict, headers=headers)
  if(response.status_code == 200):
    log.info("Generate CBS Request successful")
    return response.text
  else:
    log.error("Generate CBS Request failed. Status code: %d. Reason: %s", response.status_code, response.reason)
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
    if(revision in w["name"]):
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

def SubmitCbsRequest(requestId, replacementList, token):
  log.info("Submitting CBS request......")
  url = baseUrl + "api/bvmcbsoverride/SubmitRequest"
  headers = {"Authorization": "Bearer " + token}
  argument_dict = dict()
  CBSModifyCollection = list()
  argument_dict.update({"RequestId": requestId})
  for each_dict in replacementList:
    for option_name, option_value in each_dict.items():
      SingleCBSModifyNode = dict()
      SingleCBSModifyNode.update({"OptionName": "",
                                  "OptionOldValue": "",
                                  "OptionNewValue": "nvStorage: " + option_value,
                                  "NvStorage": option_value,
                                  "VariableName": option_name
                                  })
      CBSModifyCollection.append(SingleCBSModifyNode)

  argument_dict.update({"CBSModifyCollection": CBSModifyCollection})

  response = requests.post(url, json=argument_dict, headers=headers)
    
  if(response.status_code != 200):
      log.error("Submit CBS Request failed. Status code: %d. Reason: %s", response.status_code, response.reason)
      return None
  log.info("Submit CBS Request successful")
  log.info("Please Wait 30~60 minutes to build BIOS. You will receive an Email when the build finished.")
  return 1



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

  requestId = GenerateCbsRequest(processorList, processorName, platformName, baseBIOSType, revision, cbsConfigProgram, purpose, isGbs, newName, token)
  if not requestId:
    return
  # Remove " in requestId
  requestId = requestId.replace('"', "")
  
  # updateName = "VXX" + str(requestId) + "N.FD"
  # result = UpdateName(requestId, updateName, token)
  # if not result:
    # return
  
  result = SubmitCbsRequest(requestId, replacementList, token)
  if not result:
    return

if __name__ == "__main__":
  main()