import requests, json
from _core._utils import Headers, parse_cookie_string, formAll
     
def func(dataFB, typeAdded, messageID, emojiChoice):

     dataForm = formAll(dataFB, docID=1491398900900362)
     dataForm["variables"] = json.dumps({"data": {
          "action": "ADD_REACTION" if (typeAdded == "add") else "REMOVE_REACTION",
          "client_mutation_id": "1",
          "actor_id": dataFB["FacebookID"],
          "message_id": str(messageID),
          "reaction": emojiChoice # random.choice(["🥺","😏", "✅","😎","😭", "🫥", "✈️", "✅", "🌚", "😵", "😮‍💨", "😷", "🥹", "😒", "🐧", "💩", "🍦", "👀", "💀", "🐣", "💔", "🫶🏻", "🪐", "🙈", "🐈‍⬛", "🦆", "🔪", "⚙️", "🧭", "📡", "💌", "⁉️", "💀"])
     }})
     dataForm["dpr"] = 1
     
     mainRequests = {
               "headers": Headers(dataFB["cookieFacebook"], dataForm),
               "timeout": 60000,
               "url": "https://www.facebook.com/webgraphql/mutation/",
               "data": dataForm,
               "cookies": parse_cookie_string(dataFB["cookieFacebook"]),
               "verify": True
     }
               
     sendRequests = requests.post(**mainRequests)
     return sendRequests
     

""" Istemal ka tarika (Tutorial)

 * Zaroori arguments (args):

     - dataFB: _core._session.dataGetHome(setCookies) se lo
     - typeAdded: "add" message mein reaction add karo. "remove" reaction hatao
     - messageID: message ka messageID
     - emojiChoice: message par reaction karne wala emoji (jaise: 👍, 😭, 😎,...)(All emoji)

* Return result:

     - Koi data nahi
     - Note: alag-alag cases mein error code aur details alag ho sakte hain!

* Author ki info:
     Github: PrinceMalhotra

✓ Prince Malhotra dwara banaya gaya
✓ Fbchat Python se remake (https://fbchat.readthedocs.io/en/stable/)
✓ Tum author ki izzat karo ❤️
"""
