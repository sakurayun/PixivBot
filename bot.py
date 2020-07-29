import asyncio
import typing as T

from graia.application import GraiaMiraiApplication, Session, Source, Friend, Group, MessageChain, FriendMessage, \
    GroupMessage
from graia.application.protocol.entities.event.lifecycle import ApplicationShutdowned, ApplicationLaunched
from graia.broadcast import Broadcast

from handler import *
from pixiv import start_auto_auth, start_search_helper, start_illust_cacher, stop_illust_cacher, stop_search_helper
from utils import settings, log, start_reply_queue, stop_reply_queue

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
session = Session(
    host=f"""http://{settings["mirai"]["host"]}:{settings["mirai"]["port"]}""",
    authKey=settings["mirai"]["auth_key"],
    account=settings["mirai"]["qq"],
    websocket=settings["mirai"]["enable_websocket"]
)
app = GraiaMiraiApplication(broadcast=bcc, connect_info=session)
log.info("Connect to " + str(session))

handlers = {
    "ranking":
        PixivRankingQueryHandler("ranking query", settings["ranking"]),
    "illust":
        PixivIllustQueryHandler("illust query", settings["illust"]),
    "random_illust":
        PixivRandomIllustQueryHandler("random illust query", settings["random_illust"]),
    "random_user_illust":
        PixivRandomUserIllustQueryHandler("random user illust query", settings["random_user_illust"]),
    "random_bookmark":
        PixivRandomBookmarkQueryHandler("random bookmark query", settings["random_bookmarks"])
}


async def on_receive(function_switch: dict,
                     app: GraiaMiraiApplication,
                     subject: T.Union[Group, Friend],
                     message: MessageChain):
    if (function_switch["listen"] is not None) and (subject.id not in function_switch["listen"]):
        return

    src = message.get(Source)[0]

    for key in handlers:
        if function_switch[key]:
            await handlers[key].receive(app, subject, message, src)


@bcc.receiver(GroupMessage)
async def group_receiver(app: GraiaMiraiApplication, message: MessageChain, sender: Group):
    await on_receive(settings["function"]["group"], app, sender, message)


@bcc.receiver(FriendMessage)
async def friend_receiver(app: GraiaMiraiApplication, message: MessageChain, sender: Friend):
    await on_receive(settings["function"]["friend"], app, sender, message)


@bcc.receiver(ApplicationLaunched)
async def prepare_bot():
    start_auto_auth()
    await start_reply_queue()
    await start_search_helper()
    await start_illust_cacher()


@bcc.receiver(ApplicationShutdowned)
async def shutdown_bot():
    await stop_reply_queue()
    await stop_search_helper()
    await stop_illust_cacher()


app.launch_blocking()
