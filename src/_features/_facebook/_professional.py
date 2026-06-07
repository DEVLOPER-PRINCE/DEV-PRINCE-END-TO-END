import requests, json, random
from _core._utils import formAll, mainRequests

def func(dataFB, statusBusiness=None): # Personal page ka Professional mode on/off karo
          
    # Data liya aur likha gaya: 01:03 Thursday, 06/07/2023. Author: Prince Malhotra
    """Args:
        statusBusiness: Do you want it on or off? (eg. True/False) | typeInput: bool
    """
    
    if ((statusBusiness.lower() == "on") | (statusBusiness.lower() == "bat") | (statusBusiness == True)):
        docID = "6580386111988379"
        friendlyName = "CometProfilePlusOnboardingDialogTransitionMutation"
        variables = json.dumps(
            {
                    "category_id": int(random.random() * 1738263827237839),
                    "surface": None
            }
        )
    elif ((statusBusiness.lower() == "off") | (statusBusiness.lower() == "band") | (statusBusiness == False)):
        docID = "4947853815250139"
        friendlyName = "CometProfilePlusRollbackMutation"
        variables = json.dumps({})
    else:
        return {
            "error": -1,
            "messages": "No valid option was provided."
        }
    
    dataForm = formAll(dataFB, friendlyName, docID)
    dataForm["variables"] = variables
        
    
    sendRequests = json.loads(requests.post(**mainRequests("https://www.facebook.com/api/graphql/", dataForm, dataFB["cookieFacebook"])).text)
        
    if (sendRequests.get("data")):
        return {
            "success": 1,
            "messages": "Professional personal page enabled successfully!" if ((statusBusiness.lower() == "on") | (statusBusiness.lower() == "bat")) else "Professional personal page disabled successfully!",
        }
    else:
        return {
            "error": 1,
            "message": sendRequests["errors"][0]["message"]
        }