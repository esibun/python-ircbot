import re, select, socket, traceback

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

		self._eventlist = {}

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

	def user_array(self, user):
		nick = user.split('!')[0]
		username = user.split('!')[1].split('@')[0]
		address = user.split('@')[1]
		return (nick, username, address)

	def _hook_generic(self, command, channel, match, func):
		try:
			self._eventlist[''.join([command, '.', channel])].append((re.compile(match), func))
		except:
			self._eventlist[''.join([command, '.', channel])] = []
			self._eventlist[''.join([command, '.', channel])].append((re.compile(match), func))

	def hook_join(self, channel, user, func): self._hook_generic('JOIN', channel, user, func)
	def hook_msg(self, channel, message, func):	self._hook_generic('PRIVMSG', channel, message, func)
	def hook_part(self, channel, user, func): self._hook_generic('PART', channel, user, func)
	def hook_quit(self, user, func): self._hook_generic('QUIT', '*', '.*', func)

	def join(self, channel):
		self._send('JOIN %s' % channel)

	def msg(self, channel, message):
		self._send('PRIVMSG %s :%s' % (channel, message))

	def _process_event(self, line):
		if len(line) > 0:
			command = line.split(' ')[1]
			if command == 'JOIN':
				self._process_join(line)
			elif command == 'PART':
				self._process_part(line)
			elif command == 'PRIVMSG':
				self._process_privmsg(line)
			elif command == 'QUIT':
				self._process_quit(line)
			else:
				self._process_generic(line)

	def _process_join(self, line):
		source = line.split(' ')[0][1:]
		channel = line.split(' ')[2][1:].rstrip()
		args = {'line': line, 'source': source, 'channel': channel}
		self._fire_event('JOIN', args, channel, channel=channel)

	def _process_part(self, line):
		source = line.split(' ')[0][1:]
		channel = line.split(' ')[2].rstrip()
		if len(line.split(' ')) > 2:
			msg = ' '.join(line.split(' ')[3:])[1:].rstrip()
		else:
			msg = ''
		args = {'line': line, 'source': source, 'channel': channel, 'message': msg}
		self._fire_event('PART', args, channel, channel=channel)

	def _process_privmsg(self, line):
		source = line.split(' ')[0][1:]
		channel = line.split(' ')[2]
		msg = ' '.join(line.split(' ')[3:])[1:]
		args = {'line': line, 'source': source, 'channel': channel, 'message': msg}
		self._fire_event('PRIVMSG', args, msg, channel=channel)

	def _process_generic(self, line):
		command = line.split(' ')[1]
		args = {'line': line}
		self._fire_event(command, args, line)

	def _fire_event(self, event, args, match, **kwargs):
		try:
			for event in self._eventlist[''.join([event, '.*'])]:
				if re.match(event[0], match):
					try:
						event[1](self, args)
					except Exception:
						traceback.print_exc()
						pass
		except Exception as err:
			pass
		try:
			for event in self._eventlist[''.join([event, '.', kwargs['channel']])]:
				if re.match(event[0], match):
					try:
						event[1](self, args)
					except Exception:
						traceback.print_exc()
						pass
		except Exception as err:
			pass

	def loop(self):
		while True:
			data = self._recv()
			dataArray = data.split('\n')
			for line in dataArray:
				self._process_event(line)

					