import random
import discord
import copy
import redbot.core.utils.chat_formatting
from redbot.core import commands


class VTMDice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx: commands.Context, pool: int, hunger: int, difficulty: int):
        # todo throw an error if hunger is greater than the pool.
        dice_pool = self.roll_dice(pool, 10)
        embed = discord.Embed(title=f"{ctx.message.author.name}'s Roll")
        # status of the roll
        status = self.roll_status(dice_pool, hunger, difficulty)
        embed.add_field(name=f"{status[1]}", value=f"({status[0]})", inline=True)
        # normal dice
        embed.add_field(name="Normal Dice", value=self.format_dice(dice_pool, pool, hunger, False), inline=False)
        # hunger dice
        embed.add_field(name="Hunger Dice", value=self.format_dice(dice_pool, pool, hunger, True), inline=False)
        # show dice
        # some kind of image generation wizardry here
        # I don't know how to do the optional comment thing. x.x
        # comment, if available.
        # embed.add_field(name="Comment", value="-", inline=False)
        await ctx.send(mention_author=True, embed=embed)

    @staticmethod
    def roll_status(dice_pool, hunger, difficulty):
        # we want to preserve the array, so lets make a deep copy. I probably don't need to do this.
        array = copy.deepcopy(dice_pool)

        total_successes = 0
        successes = 0
        criticals = 0
        bestial_failures = 0
        hunger_criticals = 0

        count = 0
        for d in array:
            if count < len(dice_pool) - hunger:
                if d == 10:
                    criticals += 1
                elif d >= 6:
                    successes += 1
            else:
                if d == 10:
                    hunger_criticals += 1
                elif d >= 6:
                    successes += 1
                elif d == 1:
                    bestial_failures += 1
            count += 1

        # I'm sure there is a more efficient way to do this
        total_crits = criticals + hunger_criticals
        if total_crits % 2 == 1:
            total_successes += ((total_crits - 1) * 2) + 1
        else:
            total_successes += total_crits * 2

        total_successes += successes

        # If our total crits are more than 1, we know there is a pair of them, but not where.
        if total_crits > 1:
            # If we have at least 1 hunger crit, then the whole thing is a messy crit. V5 pg 205-206
            if hunger_criticals > 0:
                status = "Messy Critical"
            else:
                status = "Critical Success"
        elif total_successes >= difficulty:
            status = "Success"
        else:
            # At this point, if it's not a success, or a crit, it's a failure. What kind of failure?
            # Check if it's a Bestial Failure. V5 pg 207
            if bestial_failures > 0:
                status = "Bestial Failure"
            else:
                status = "Failure"

        return [total_successes, status]

    @staticmethod
    def roll_dice(amount, maximum):
        dice_array = []
        for _ in range(amount):
            dice_array.append(random.randint(1, maximum))
        return dice_array

    @staticmethod
    def format_dice(dice_pool, total, hunger, is_hunger):
        cf = redbot.core.utils.chat_formatting
        # we want to preserve the array, so lets make a deep copy to reverse if we need to.
        array = copy.deepcopy(dice_pool)
        string = ""

        # reverse the array to get and display our hunger dice.
        if is_hunger:
            array.reverse()
            loop_num = hunger
        else:
            loop_num = total - hunger
        for n in range(loop_num):
            if array[n] == 10:
                string += cf.underline("10")
            elif array[n] >= 6:
                string += f'{array[n]}'
            elif array[n] == 1:
                string += cf.bold("1")
            else:
                string += cf.strikethrough(f'{array[n]}')
            if n < loop_num - 1:
                string += ','

        # if for some reason the Hunger Dice are 0, or the Pool is 0, return a dash.
        if string == "":
            string += "—"
        return string
