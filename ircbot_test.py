import ircbot, re

bot = ircbot.IRCBot('your.irc.ip', 6667, 'esibot')
bot.join('#esibun')
bot.hook_msg('#esibun', re.escape('!test'), lambda self, line: self.msg('#esibun', 'hi'))
bot.loop()