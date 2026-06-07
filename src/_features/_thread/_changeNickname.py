import json, requests
from _core._utils import formAll, mainRequests, formatResults

def func(dataFB, threadID, idUser, NewNickname): # User ka nickname badlo
     
    dataForm = formAll(dataFB, requireGraphql=False)
    dataForm["nickname"] = NewNickname
    dataForm["participant_id"] = idUser
    dataForm["thread_or_other_fbid"] = str(threadID)

    sendRequests = json.loads(requests.post(**mainRequests("https://www.facebook.com/messaging/save_thread_nickname/?source=thread_settings&dpr=1", dataForm, dataFB["cookieFacebook"])).text.split("for (;;);")[1])
    
    
    if sendRequests.get("error"):
        match sendRequests.get("error"):
            case 1545014:
                return formatResults("error", "User group/conversation mein exist nahi karta.")
            case 1357031:
                return formatResults("error", "User exist nahi karta.")
            case _:
                return formatResults("error", "Unknown error.")
    else:
        return formatResults("success", "User nickname successfully changed.")