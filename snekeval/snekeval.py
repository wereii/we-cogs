import logging

import aiohttp
from redbot.core import Config, checks, commands

logger = logging.getLogger("we_cogs.snekeval")

##
# Borrowed from Retrigger
# https://github.com/TrustyJAID/Trusty-cogs/blob/master/retrigger/triggerhandler.py

listener = getattr(commands.Cog, "listener", None)

if listener is None:

    def listener(name=None):
        return lambda x: x


# --


class SnekEval(commands.Cog):
    """Evaluate your python code right from Discord.```
    - Execution time limited to 2 seconds.
    - Only built-in modules.
    - No filesystem.
    - No enviroment.```"""

    def __init__(self):
        self.conf = Config.get_conf(
            self, identifier=115110101107)  # ord('snek')
        default_global = {"snekbox_url": None}
        self.conf.register_global(**default_global)

    @staticmethod
    async def evaluate(url: str, payload: str) -> dict:
        data = {"input": payload}

        async with aiohttp.ClientSession() as session:  # type: aiohttp.ClientSession
            async with session.post(url, json=data) as resp:
                resp.raise_for_status()
                ret_json = await resp.json()

        return ret_json

    async def test_snekurl(self, url: str):
        ret_json = None
        try:
            ret_json = await self.evaluate(url, "print('hello world')")
        except aiohttp.client_exceptions.ClientError as exc:
            logger.error("Request failed.", exc_info=exc)
        else:
            if ret_json.get("returncode") == 0:
                return True

        return False

    @commands.command(usage="<snekbox_url>")
    @checks.is_owner()
    async def snekurl(self, ctx: commands.Context, url=None):
        """Set URL to your snekbox-box.
        Examples:
        `http://[IP or site][:port]/eval`
        `http://snek.box.com:8060/eval`"""

        if not url:
            current_url = await self.conf.snekbox_url()
            await ctx.send_help()
            return await ctx.send("`Current snekbox URL: {}`".format(current_url))

        async with ctx.typing():
            if await self.test_snekurl(url):
                await self.conf.snekbox_url.set(url)
                return await ctx.send(":white_check_mark: It's working! New url set.")

            await ctx.send(":x: URL doesn't seem to work.")

    @commands.command(usage="<payload>")
    async def snek(self, ctx, *, payload: str = None):
        """Evaluates python code
        Escaping with \" or \' is not needed.
        _Everything after this command is considered code._"""

        url = await self.conf.snekbox_url()
        if not url:
            return await ctx.send("Snekbox URL isn't set.")

        if not payload:
            return await ctx.send_help()

        first_sym, last_sym = payload[0], payload[-1]
        if (first_sym == last_sym == "'") or (first_sym == last_sym == '"'):
            payload = payload[1:-1]

        data = await self.evaluate(url, payload)
        await ctx.send(
            "\n".join(
                (
                    "```",
                    data.get("stdout", ""),
                    " ",
                    "status code: {}".format(data.get("returncode")),
                    "```",
                )
            )
        )
