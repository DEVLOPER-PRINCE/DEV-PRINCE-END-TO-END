import requests, json
from _core._utils import formAll, mainRequests, formatResults

def func(dataFB, threadID, newEmoji): # Group ka emoji badlo
    dataForm = formAll(dataFB, requireGraphql=False)
    dataForm["emoji_choice"] = newEmoji
    dataForm["thread_or_other_fbid"] = threadID

    sendRequests = json.loads(requests.post(**mainRequests("https://www.facebook.com/messaging/save_thread_emoji/?source=thread_settings&__pc=EXP1%3Amessengerdotcom_pkg", dataForm, dataFB["cookieFacebook"])).text.split("for (;;);")[1])

    if (sendRequests.get("error")):
        error = sendRequests.get("error")
        if error == 1357031:
            return formatResults("error", "Jo conversation exist nahi karta uska emoji status change nahi ho sakta.")
        else:
            return formatResults("error", "Unknown error.")
    else:
            return formatResults("success", "Quick emoji successfully changed.")