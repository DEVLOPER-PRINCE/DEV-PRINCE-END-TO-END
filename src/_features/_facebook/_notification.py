import requests, json
from _core._utils import formAll, mainRequests

def func(dataFB): # Facebook notifications lo
    
    # Data liya aur likha gaya: 02:32 Thursday, 06/07/2023. Author: Prince Malhotra
    
    dataForm = formAll(dataFB, "CometNotificationsDropdownQuery", 6770067089747450)
    dataForm["variables"] = json.dumps(
        {
            "count":15,
            "environment":"MAIN_SURFACE",
            "scale":3
        }
    )
    
    listNotificationResults = []
    
    sendRequests = json.loads(requests.post(**mainRequests("https://www.facebook.com/api/graphql/", dataForm, dataFB["cookieFacebook"])).text)
    
    try:
        getDataResultNotificationFacebook = sendRequests["data"]["viewer"]["notifications_page"]["edges"]
        for dataResults, sttCount in zip(getDataResultNotificationFacebook, range(1, len(getDataResultNotificationFacebook) + 1)):
            try:
                    listNotificationResults.append(str(sttCount) + "." + dataResults["node"]["notif"]["body"]["text"])
            except (KeyError, TypeError):   
                    pass
    except Exception as errLog:
        return {
            "error": 1,
            "messages": "ERR: " + str(errLog)
        }
    return {
        "success": 1,
        "NotificationResults": listNotificationResults
    }