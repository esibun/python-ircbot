# python-ircbot
*More complete documetation to come soon.*

Setup
---
```python
import ircbot

bot = ircbot.IRCBot('some ip/url', 6667, 'nickname')
```

Hook Methods
---
**bot.hook_join(channel, nick, func)**:  
**bot.hook_part(channel, nick, func)**:  
**bot.hook_quit(nick, func)**:  
channel - channel to listen for, or * for all channels  
nick - nick to match on (regex)  
func - function to execute

**bot.hook_msg(channel, msg, func)**:  
channel - channel to listen for, or * for all channels  
msg - message to match on (regex)  
func - function to execute

**bot.hook_generic(command, func)**:  
command - raw numeric or command to hook  
func - function to execute

Hook Function Parameters
---
**hookfunc(self, args)**:  
self - contains a reference to the bot for executing commands on an event  
args - contains the following depending on the event type:
```
line - ALL - raw IRC line triggering the event
source - JOIN, PART, QUIT, MSG - source of the event, can be parsed with helper function user_array (see below)
channel - JOIN, PART, MSG - origin channel
message - PART, QUIT, MSG - message accompanying event
```

Utility Functions
---
**user_array(user)**:  
Returns a tuple containing:  
nick - nickname of the user  
username - username (the part after the ! but before the @)  
address - possibly cloaked IP address of the user  
