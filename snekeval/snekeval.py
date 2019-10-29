from httpx import AsyncClient, exceptions
from redbot.core import Config, checks, commands
import logging

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
    """Description of the cog visible with [p]help MyFirstCog"""

    def __init__(self):
        self.conf = Config.get_conf(self, identifier=115110101107)  # ord('snek')
        default_global = {"snekbox_url": None}
        self.conf.register_global(**default_global)

    @staticmethod
    async def evaluate(url: str, payload: str) -> dict:
        data = {"input": payload}

        ret = None
        async with AsyncClient() as aclient:
            ret = await aclient.post(url, json=data)
            aclient.raise_for_status()

        return ret.json()

    async def test_snekurl(self, url: str):
        ret_json = None
        try:
            ret_json = await self.evaluate(url, "print('hello world')")
        except exceptions.HTTPError as exc:
            logger.error("Request failed.", exc_info=exc)
        else:
            if ret_json.get("returncode") == 0:
                return True

        return False

    @commands.group()
    async def snekeval(self, ctx):
        """Evaluate your python code right from Discord.\n"""
        """```\n- Time limited to 2 seconds.\n"""
        """- Only built-in modules.\n"""
        """- No filesystem.\n"""
        """- No enviroment.\n```"""
        pass

    @snekeval.command()
    @checks.is_owner()
    async def url(self, ctx: commands.Context, url=None, usage="<snekbox_url>"):
        """Set URL to your snekbox-box.\nExample url:"""
        """ `http://[IP or site][:port]/eval` | `http://snek.box.com:8060/eval`"""

        if not url:
            return await ctx.send_help()

        async with ctx.typing():
            if self.test_snekurl(url):
                self.conf.snekbox_url.set(url)
                await ctx.send(":white_check_mark: It's working! New url set.")
            else:
                await ctx.send(":x: URL doesn't seem to work.")

    @commands.command()
    async def eval(self, ctx, *, payload: str = None):
        """Description of myfirstcom visible with [p]help myfirstcom"""
        if not payload:
            return await ctx.send_help()

        first_sym, last_sym = payload[0], payload[-1]
        if (first_sym == last_sym == "'") or (first_sym == last_sym == '"'):
            payload = payload[1:-1]

        data = await self.evaluate(self.conf.snekbox_url(), payload)
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
