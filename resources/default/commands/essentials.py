
@register_command("help",0)
def _help(context, command:Command.COMMAND):
	"""print a commands docstring to chat"""
	context.send_feedback(command.__doc__)

@register_command("goto",2)
def goto(context, x : Command.FLOAT, y : Command.FLOAT, z : Command.FLOAT):
	"""teleport entity to the given position"""
	context.entity["position"] = x,y,z

@register_command("skin",1)
def skin(context, block_name : Command.BLOCKNAME):
	"""change the skin of an entity to a new block"""
	context.entity["skin"] = block_name

@register_command("give",1)
def give(context, block_name : Command.BLOCKNAME):
	"""give an entity one item of type block_name"""
	context.entity["inventory"].append({"id":block_name})

@register_command("entity", 9)
def entity(context, entity : Command.ENTITY, subcommand : Command.SUBCOMMAND):
	"""/entity entity_id subcommand"""
	context.entity = entity
	context.execute(subcommand)

@register_command("log",0)
def log(context, message : Command.FREETEXT):
	"""add timestamp and message to the server log"""
	print(time.strftime("[%Z %Y-%m-%d %T]"), message)
