
import collections


class Command(object):
	commands = {} # {name: command_func}

	@classmethod
	def register_command(cls, name):
		def _register_command(command):
			cls.commands[name] = command
			return command
		return _register_command

	def __init__(self, originator, command_text):
		self.originator = originator
		self.command_text = command_text
		self.target = self._get_default_target()
		self.permission_level = self._get_permission_level()

	def _get_default_target(self):
		return None

	def _get_permission_level(self):
		return 0
	
	def _get_originator_name(self):
		return repr(originator)

	def _send_feedback(self, feedback):
		pass


	def execute(self):
		print("Command:", command_issuer, "wants to execute", command_text)


@Command.register_command("goto")
def goto(command):
	if not command.target:
		command._send_feedback(command.originator, "missing target for goto command")
		return
	position = command.arg_text.split(" ")


@Command.register_command("say")
def say(command):
	pass

def execute_command(originator, command_text):
	command = Command(originator, command_text)
	command.execute()
