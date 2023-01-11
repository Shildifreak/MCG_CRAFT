
@register_command("help",0)
def _help(command):
	"""/help"""
	help_texts = []
	command_funcs = type(command).commands.values()
	for command_func in command_funcs:
		# only show commands that user has permission for
		if command.permission_level < command_func.permission_level:
			continue
		help_texts.append(command_func.__doc__)
	#help_texts.append("[showing %i of %i commands]" % (len(help_texts),len(command_funcs)))
	help_text = "\n".join(help_texts)
	command.send_feedback(help_text)

@register_command("goto",2)
def goto(command):
	"""/goto x y z"""
	if not command.entity:
		command.send_feedback("command /goto: don't know which entity to target")
		return
	position = command.arg_text.strip().split(" ")
	if len(position) != 3:
		command.send_feedback("command /goto: wrong number of arguments")
		return
	try:
		position = tuple(map(float, position))
	except ValueError:
		command.send_feedback("command /goto: arguments have to be numbers")
		return
	command.entity["position"] = position

@register_command("skin",1)
def skin(command):
	"""/skin block_name"""
	block_name = command.arg_text.strip()
	if any(map(str.isspace,block_name)):
		command.send_feedback("command /skin: block_name must not contain whitespace characters")
		return
	if not command.entity:
		command.send_feedback("command /skin: don't know which entity to target")
		return
	command.entity["skin"] = block_name

@register_command("give",1)
def give(command):
	"""/give block_name"""
	block_name = command.arg_text.strip()
	if any(map(str.isspace,block_name)):
		command.send_feedback("command /skin: block_name must not contain whitespace characters")
		return
	if not command.entity:
		command.send_feedback("command /skin: don't know which entity to target")
		return
	command.entity["inventory"].append({"id":block_name})

@register_command("entity", 9)
def entity(command):
	"""/entity entity_id subcommand"""
	# extract entity_id and sub_command
	entity_id, subcommand, *_ = command.arg_text.split(" ",1) + [""]
	# find target in universe and set command.target
	for world in command.universe.worlds:
		try:
			entity = world.entities[entity_id]
			break
		except KeyError:
			pass
	else:
		command.send_feedback("command /entity: no entity with id <%s> found" % entity_id)
		return
		
	command.entity = entity
	# execute sub_command
	command.execute_subcommand(subcommand)

@register_command("log",0)
def log(command):
	"""/log message"""

	print(time.strftime("[%Z %Y-%m-%d %T]"), command.arg_text)
