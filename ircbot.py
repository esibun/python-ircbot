import re, select, socket

class IRCBot:
	def __init__(self, ip, port, nick, **kwargs):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.connect((ip, port))
		self._recv()
		ready = select.select([self._socket], [], [], 1)
		if ready[0]:
			self._recv()

		self.nick = nick

		if 'realname' in kwargs:
			self.realname = kwargs['realname']
		else:
			self.realname = 'Python IRCBot'

		if 'username' in kwargs:
			self.username = kwargs['username']
		else:
			self.username = self.nick

		if 'password' in kwargs:
			self._password = kwargs['password']
			self._send('PASS %s' % self._password)

		self._send('NICK %s' % self.nick)
		self._send('USER %s 8 * :%s' % (self.username, self.realname))
		ping = self._recv()
		self._send('PONG %s' % ping.split(' ')[1])

		self._eventlist = {'PRIVMSG.*': []}

	def __setattr__(self, name, value):
		if name == 'nick':
			pass
		elif name == 'realname':
			pass
		self.__dict__[name] = value

	def _send(self, raw):
		print('> %s' % raw.rstrip())
		self._socket.send(bytes(''.join([raw, '\n']), 'UTF-8'))

	def _recv(self):
		data = self._socket.recv(4096).decode('UTF-8')
		for line in data.split('\n'):
			if len(line) > 0:
				print('< %s' % line.rstrip())
		return data

	# def _convert_wildcard(self, search):
	# 	search = search.replace('\\', '\\\\')
	# 	search = re.escape(search)
	# 	return search.replace('\\*', '.+').replace('\\?', '.')

	def hook_msg(self, channel, message, func):
		try:
			self._eventlist[''.join(["PRIVMSG.", channel])].append((re.compile(message), func))
		except:
			self._eventlist[''.join(['PRIVMSG.', channel])] = []
			self._eventlist[''.join(["PRIVMSG.", channel])].append((re.compile(message), func))

	def join(self, channel):
		self._send('JOIN %s' % channel)

	def msg(self, channel, message):
		self._send('PRIVMSG %s :%s' % (channel, message))

	def loop(self):
		while True:
			data = self._recv()
			dataArray = data.split('\n')
			for line in dataArray:
				if len(line) > 0:
					command = line.split(' ')[1]
					if command == 'PRIVMSG':
						channel = line.split(' ')[2]
						msg = ' '.join(line.split(' ')[3:])[1:]
						for event in self._eventlist['PRIVMSG.*']:
							if re.match(event[0], msg):
								event[1](self, line)
						try:
							for event in self._eventlist[''.join(['PRIVMSG.', channel])]:
								if re.match(event[0], msg):
									event[1](self, line)
						except:
							pass