import ircbot, re

bot = ircbot.IRCBot('127.0.0.1', 6667, 'esibot')
bot.join('#esibun')
bot.hook_msg('#esibun', re.escape('!test'), lambda self, args: self.msg(args['channel'], 'hi'))
bot.hook_join('#esibun', '.*', lambda self, args: self.msg(args['channel'], ''.join(['hey, ', self.user_array(args['source'])[0]])))
bot.loop()