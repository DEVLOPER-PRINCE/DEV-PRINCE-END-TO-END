import requests, json, random
from _core._utils import formAll, mainRequests  

def func(dataFB, idUser, choiceInteract): # User ko block ya unblock karo

    # Data liya aur likha gaya: 03:12 Thursday, 06/07/2023. Author: Prince Malhotra
    """Args:
        idUser: ID of the user to block/unblock (eg. 4) | typeInput: str/int
        choiceInteract: Do you want to block or unblock? (eg. block/unblock) | typeInput: str
    """

    if (choiceInteract == "block"):
        
        friendlyName = "ProfileCometActionBlockUserMutation"
        docID = "6305880099497989"
        variables = json.dumps(
            {
                    "collectionID": None,
                    "hasCollectionAndSectionID": False,
                    "input": {
                        "blocksource": "PROFILE",
                        "should_apply_to_later_created_profiles": False,
                        "user_id": int(idUser),
                        "actor_id": dataFB["FacebookID"],
                        "client_mutation_id": str(round(random.random() * 1024))
                    },
                    "scale": 3,
                    "sectionID": None,
                    "isPrivacyCheckupContext": False
            }
        )
    
    elif (choiceInteract == "unblock"):
    
        friendlyName = "BlockingSettingsBlockMutation"
        docID = "6009824239038988"
        variables = json.dumps(
            {
                    "input": {
                        "block_action": "UNBLOCK",
                        "setting": "USER",
                        "target_id": idUser, 
                        "actor_id": dataFB["FacebookID"],
                        "client_mutation_id": "1"
                    },
                    "profile_picture_size": 36
            }
        )
        
    else:
    
        return {
            "error": 1,
            "messages": "This command does not exist."
        }
    
    dataForm = formAll(dataFB, friendlyName, docID)
    dataForm["variables"] = variables
    
    sendRequests = json.loads(requests.post(**mainRequests("https://www.facebook.com/api/graphql/", dataForm, dataFB["cookieFacebook"])).text)
    
    if (choiceInteract == "block"):
        
        if (sendRequests.get("data")):
            return {
                    "success": 1,
                    "messages": "User successfully blocked!"
            }
        else:
            return {
                    "error": 1,
                    "messages": "Failed to block user!"
            }
    
    elif (choiceInteract == "unblock"):
        
        if (sendRequests.get("data")):
            return {
                    "success": 1,
                    "messages": "User successfully unblocked!"
            }
        else:
            return {
                    "error": 1,
                    "messages": "Failed to unblock user!"
            } 