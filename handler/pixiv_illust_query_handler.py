import asyncio
import re
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Source, Friend

from pixiv import make_illust_message, papi, PixivResultError
from utils import log, launch
from .abstract_message_handler import AbstractMessageHandler


class PixivIllustQueryHandler(AbstractMessageHandler):
    def __check_triggered(self, message: MessageChain) -> bool:
        """
        返回此消息是否触发
        """
        content = message.asDisplay()
        for x in self.trigger:
            if x in content:
                return True
        return False

    async def make_msg(self, illust_id) -> MessageChain:
        result = await launch(papi.illust_detail, illust_id=illust_id)
        if "error" in result:
            raise PixivResultError(result["error"])
        else:
            log.info(f"""{self.tag}: [{result["illust"]["id"]}] ok""")
            return await make_illust_message(result["illust"])

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain,
                             source: Source) -> T.AsyncGenerator[MessageChain, T.Any]:
        if self.__check_triggered(message):
            content = message.asDisplay()

            regex = re.compile("[1-9][0-9]*")
            ids = [int(x) for x in regex.findall(content)]
            log.info(f"{self.tag}: {ids}")

            tasks = []
            for x in ids:
                tasks.append(asyncio.create_task(self.make_msg(x)))

            while tasks:
                done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    yield task.result()
