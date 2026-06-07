import json, requests, time, json, random
from _core._utils import formAll, mainRequests

def func(dataFB, newContents, attachmentID=None): # Facebook par post banao
    
    # Data liya aur likha gaya: 09:40 Wednesday, 05/07/2023. Author: Prince Malhotra
    """Args:
        newContents: post ka content (jaise: Prince Malhotra ne naya post banaya!) | typeInput: str
        attachmentID: Coming soon....
    """
    
    dataForm = formAll(dataFB, "ComposerStoryCreateMutation", 6534257523262244)
    dataForm["variables"] = json.dumps(
        {
            "input": {
                    "composer_entry_point": "inline_composer",
                    "composer_source_surface": "timeline",
                    "source": "WWW",
                    "attachments": [],
                    "audience": {
                        "privacy": {
                            "allow": [],
                            "base_state": "EVERYONE",
                            "deny": [],
                            "tag_expansion_state": "UNSPECIFIED"
                        }
                    },
                    "message": {
                        "ranges": [],
                        "text": newContents
                    },
                    "with_tags_ids": [],
                    "inline_activities": [],
                    "explicit_place_id": "0",
                    "text_format_preset_id": "0",
                    "logging": {
                        "composer_session_id": dataFB["sessionID"]
                    },
                    "navigation_data": {
                        "attribution_id_v2": f"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,tap_bookmark,{int(time.time() * 1000)},{dataFB['jazoest']},{dataFB['FacebookID']}"
                    },
                    "tracking": "[null]",
                    "actor_id": dataFB["FacebookID"],
                    "client_mutation_id": "1"
            },
            "displayCommentsFeedbackContext": None,
            "displayCommentsContextEnableComment": None,
            "displayCommentsContextIsAdPreview": None,
            "displayCommentsContextIsAggregatedShare": None,
            "displayCommentsContextIsStorySet": None,
            "feedLocation":"TIMELINE",
            "focusCommentID": None,
            "scale": str(round(random.random() * 1024)),
            "privacySelectorRenderLocation":"COMET_STREAM",
            "renderLocation":"timeline",
            "useDefaultActor": False,
            "inviteShortLinkKey": None,
            "isFeed": False,
            "isFundraiser": False,
            "isFunFactPost": False,
            "isGroup": False,
            "isEvent": False,
            "isTimeline": True,
            "isSocialLearning":False,
            "isPageNewsFeed": False,
            "isProfileReviews": False,
            "isWorkSharedDraft": False,
            "UFI2CommentsProvider_commentsKey":"ProfileCometTimelineRoute",
            "hashtag": None,
            "canUserManageOffers": False,
            "__relay_internal__pv__IsWorkUserrelayprovider": False,
            "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
            "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": False,
            "__relay_internal__pv__StoriesRingrelayprovider":False
        }
    )
                    
    sendRequests = json.loads(requests.post(**mainRequests("https://www.facebook.com/api/graphql/", dataForm, dataFB["cookieFacebook"])).text)
    
    if (sendRequests.get("data")):
        return {
            "success": 1,
            "messages": "Post successfully created!",
            "urlPost": sendRequests["data"]["story_create"]["story"]["url"]
        }
    else:
        return {
            "error": 1,
            "messages": sendRequests["errors"][0]["message"]
        }