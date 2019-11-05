import logging
from typing import Dict

import aiohttp
from redbot.core import Config, checks, commands

logger = logging.getLogger("snekeval")


class SnekEval(commands.Cog):

    def __init__(self):
        self.conf = Config.get_conf(
            self, identifier=115110101107)  # ord('snek')
        default_global = {"snekbox_url": None}
        self.conf.register_global(**default_global)

    @staticmethod
    async def _evaluate(url: str, payload: str) -> Dict:
        data = {"input": payload}

        async with aiohttp.ClientSession() as session:  # type: aiohttp.ClientSession
            async with session.post(url, json=data) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _test_snekurl(self, url: str):
        ret_json = None
        try:
            ret_json = await self.evaluate(url, "print('hello world')")
        except aiohttp.client_exceptions.ClientError as exc:
            logger.error("Request failed.", exc_info=exc)
        else:
            if ret_json.get("returncode") == 0:
                return True

        return False

    @staticmethod
    def _remove_escapes(text: str):
        while text.startswith(('"', '\'')) and text.endswith(('"', '\'')):
            text = text[1:-1]
        return text

    @staticmethod
    def _parse_code_block(text: str):
        return text.lstrip('```python').rstrip('```')
    
    @staticmethod
    def _escape_backticks(text: str, escpe_with='\u200b'):
        return text.replace('`', escpe_with)

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
            if await self._test_snekurl(url):
                await self.conf.snekbox_url.set(url)
                return await ctx.send(":white_check_mark: It's working! New url set.")

            await ctx.send(":x: URL doesn't seem to work.")

    @commands.command(usage="<payload>")
    async def snek(self, ctx, *, payload: str = None):
        """Evaluate your python code right from Discord.```
        - Execution time limited to 2 seconds.
        - Only built-in modules.
        - No filesystem.
        - No enviroment.```
        _Everything after this command is considered code._
        Code blocks supported."""

        url = await self.conf.snekbox_url()
        if not url:
            return await ctx.send("Snekbox URL isn't set.")

        if not payload:
            return await ctx.send_help()

        first_sym, last_sym = payload[0], payload[-1]
        if (first_sym == last_sym == "'") or (first_sym == last_sym == '"'):
            payload = payload[1:-1]
        try:
            data = await self._evaluate(url, payload)
        except Exception as exc:
            await ctx.send(f"Something went wrong when contacting Snekbox: `{exc}`")
            return

        if data.get('returncode') == 137:
            await ctx.send(":timer: Execution timeout. _Maximum running time is 2 seconds._")
            return

        stdout = data.get('stdout', "").strip()

        # detect code block
        if stdout.startswith(("```python ", "```python\n")) and stdout.endswith("```"):
            stdout = self._parse_code_block(stdout)
        else:
            stdout = self._remove_escapes(stdout)

        stdout = self._escape_backticks(stdout)

        await ctx.send(
            "\n".join(
                (
                    "```",
                    stdout,
                    " ",
                    "status code: {}".format(data.get("returncode")),
                    "```",
                )
            )
        )
