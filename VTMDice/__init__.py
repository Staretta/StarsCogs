from .vtmdice import VTMDice


def setup(bot):
    bot.add_cog(VTMDice(bot))
