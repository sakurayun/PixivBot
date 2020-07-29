import traceback
import typing as T

from graia.application import GraiaMiraiApplication, Source, Group, MessageChain, Friend
from graia.application.protocol.entities.message.elements.internal import Plain

from pixiv import PixivResultError
from utils import reply, log


class AbstractMessageHandler:
    def __init__(self, tag: str, settings: dict):
        self.tag = tag
        self.settings = settings

    def __getattr__(self, item: str):
        return self.settings[item]

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain,
                             source: Source) -> T.AsyncGenerator[MessageChain, T.Any]:
        raise NotImplementedError
        yield

    async def receive(self, app: GraiaMiraiApplication,
                      subject: T.Union[Group, Friend],
                      message: MessageChain,
                      source: Source) -> T.NoReturn:
        """
        接收消息
        :param app: Mirai Bot实例
        :param source: 消息的Source
        :param subject: 消息的发送对象
        :param message: 消息
        """
        try:
            async for msg in self.generate_reply(app, subject, message, source):
                await reply(app, subject, msg, source)
        except PixivResultError as exc:
            log.info(f"{self.tag}: {exc.error()}")
            await reply(app, subject, MessageChain(__root__=[
                Plain(exc.error()[:128])
            ]), source)
        except Exception as exc:
            traceback.print_exc()
            await reply(app, subject, MessageChain(__root__=[
                Plain(str(exc)[:128])
            ]), source)
