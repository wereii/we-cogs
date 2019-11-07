import re

import discord
from redbot.core import commands
from urllib.parse import quote

# Copyright 2018 Kixiron
# Edits 2019: Cog rebooted for v3 by Wereii
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#


class StackOverflow(commands.Cog):
    """ Ask questions from the mystical being which all knowledge flows from """

    @commands.command()
    async def stackoverflow(self, ctx: commands.Context, *, question: str = None):
        """ Enlighten yourself """

        if not question:
            await ctx.send_help()
            return

        url_encoded = quote(question)

        baseURL = "https://stackoverflow.com/search?q="
        finallURL = baseURL + url_encoded

        embed = discord.Embed(color=0x1e2dd4)
        embed.set_author(
            name="StackOverflow on question '{}' says...".format(
                question[:15]),
            url=finallURL)
        embed.set_footer(text='click me to find out ;)')

        await ctx.send(embed=embed)
