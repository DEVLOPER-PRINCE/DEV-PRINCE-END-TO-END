import requests, json
from _core._utils import formAll, mainRequests, formatResults

def func(dataFB, threadID, idUser, statusChoice=True):
    dataForm = formAll(dataFB, requireGraphql=False)
    dataForm["thread_fbid"] = str(threadID)
    dataForm["admin_ids[0]"] = str(idUser)
    dataForm["add"] = statusChoice

    sendRequests = json.loads(requests.post(**mainRequests("https://www.facebook.com/messaging/save_admins/?dpr=1", dataForm, dataFB["cookieFacebook"])).text.split("for (;;);")[1])

    if sendRequests.get("error"):
        error = sendRequests["error"]
        match error:
            case 1976004:
                return formatResults("error", "Aap admin nahi hain.")
            case 1357031:
                return formatResults("error", "Yeh thread group conversation nahi hai.")
            case _:
             return formatResults("error", "Unknown error.")
    else:
        return formatResults("success", "Admin added to group successfully.")