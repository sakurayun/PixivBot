import typing as T
from functools import partial

from graia.application import GraiaMiraiApplication, MessageChain, Source, Friend, Group

from utils.wait_queue import WaitQueue

__reply_queue = WaitQueue()


async def start_reply_queue():
    await __reply_queue.start()


async def stop_reply_queue():
    await __reply_queue.stop()


async def reply(app: GraiaMiraiApplication,
                target: T.Union[Friend, Group],
                message: MessageChain,
                quote: T.Optional[Source] = None) -> T.NoReturn:
    """
    回复消息。若是群组则引用回复，若是好友则普通地回复。
    :param app: Mirai Bot实例
    :param target: 回复的对象
    :param message: 回复的消息
    :param quote: 原消息的Source
    """

    # 因为mirai-api-http的问题，不能并发传图不然容易车祸
    if isinstance(target, Group):
        await __reply_queue.do(partial(app.sendGroupMessage, group=target, message=message, quote=quote))
    elif isinstance(target, Friend):
        await __reply_queue.do(partial(app.sendFriendMessage, target=target, message=message, quote=quote))
