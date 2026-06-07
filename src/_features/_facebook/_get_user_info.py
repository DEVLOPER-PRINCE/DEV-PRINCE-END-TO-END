import json, requests
from _core._utils import parse_cookie_string, Headers, formAll

def func(dataFB, userID):
     
     dataForm = formAll(dataFB, requireGraphql=False)
     dataForm["ids[0]"] = userID


     mainRequests = {
        "headers": Headers(dataFB["cookieFacebook"], dataForm),
        "timeout": 5,
        "url": "https://www.facebook.com/chat/user_info/",
        "data": dataForm,
        "cookies": parse_cookie_string(dataFB["cookieFacebook"]),
        "verify": True
    }
     
     sendRequests = requests.post(**mainRequests)
     try:
        jsonData = json.loads(sendRequests.text.split("for (;;);")[1])["payload"]["profiles"][str(userID)]
        
        idUser = jsonData.get("id")
        nameUser = jsonData.get("name")
        firstName = jsonData.get("firstName")
        Username = jsonData.get("vanity")
        thumbSrc = jsonData.get("thumnSrc")
        urlProfile = jsonData.get("uri")
        genderUser = jsonData.get("gender")
        alternateName = jsonData.get("alternateName")
        chatWithUSerIsNonFriend = jsonData.get("is_nonfriend_messenger_contact")

        if (genderUser == 1): genderUser = "Female"
        elif (genderUser == 2): genderUser = "Male"
        else: genderUser = "Unknown"

        return {
            "idUser": idUser,
            "nameUser": nameUser,
            "firstName": firstName,
            "Username": Username,
            "thumbSrc": thumbSrc,
            "urlProfile": urlProfile,
            "genderUser": genderUser,
            "alternateName": alternateName,
            "chatWithUSerIsNonFriend": chatWithUSerIsNonFriend
        }
     except (IndexError, KeyError, TypeError, json.JSONDecodeError):
          return {
               "err": 0
          }


""" Istemal ka tarika (Tutorial)

 * Zaroori arguments (args):
 
     - dataFB: _core._session.dataGetHome(setCookies) se lo
     - userID: jis user ki info chahiye uska ID
     
* Return result:
     
     - Jab data successfully mila:

        {'idUser': '1...', 'nameUser': 'Priscilla......', ........}
     
     - Jab data fetch fail hua:

        {'err': 0}
     
     - Note: koi bhi sawaal ho toh GitHub par issue kholo.

* Author ki info:
     Github: PrinceMalhotra

✓ Prince Malhotra dwara banaya gaya
✓ Fbchat Python se remake (https://fbchat.readthedocs.io/en/stable/)
✓ Tum author ki izzat karo ❤️
"""
