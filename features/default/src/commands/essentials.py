from resources import *

@register_command("help",0)
def _help(context, command:Command.COMMAND):
	"""print a commands docstring to chat"""
	context.send_feedback(command.__doc__)

@register_command("list",0)
def _list(context):
	"""print list of commands"""
	text = "\n".join(command_name
		for command_name, command_func in Command.commands.items()
		if context.permission_level >= command_func.permission_level
	)
	context.send_feedback(text)

@register_command("goto",4.1)
def goto(context, x : Command.FLOAT, y : Command.FLOAT, z : Command.FLOAT):
	"""teleport entity to the given position"""
	context.entity["position"] = x,y,z

@register_command("skin",1)
def skin(context, block_name : Command.BLOCKNAME):
	"""change the skin of an entity to a new block"""
	context.entity["skin"] = block_name

@register_command("give",4.2)
def give(context, item_name : Command.ITEMNAME, count : Command.INT(default=1)):
	"""give an entity count items of type item_name"""
	context.entity.pickup_item({"id":item_name, "count":count})

@register_command("entity", 9)
def entity(context, entity : Command.ENTITY, subcommand : Command.SUBCOMMAND):
	"""/entity entity_id subcommand"""
	context.entity = entity
	context.execute(subcommand)

@register_command("at", 9)
def goto(context, x : Command.FLOAT, y : Command.FLOAT, z : Command.FLOAT, subcommand : Command.SUBCOMMAND):
	"""execute subcommand at given position"""
	context.position = Vector(x,y,z)
	context.execute(subcommand)

@register_command("log",0)
def log(context, message : Command.FREETEXT):
	"""add timestamp and message to the server log"""
	print(time.strftime("[%Z %Y-%m-%d %T]"), message)

@register_command("gamemode",4.9)
def gamemode(context, gamemode : Command.GAMEMODE):
	"""set gamemode of player"""
	context.player.gamemode = gamemode

@register_command("damage",2)
def damage(context, amount:Command.INT(1)):
	"""damage entity"""
	context.entity.take_damage(amount)

@register_command("spawnpoint",4.0)
def spawnpoint(context):
	world_index = context.world.universe.worlds.index(context.world)
	position = context.position
	context.entity["spawn"] = (world_index, position)
	context.send_feedback("new spawnpoint was set")

@register_command("spawn",2)
def spawn(context, entity_type: Command.ENTITYNAME):
	context.send_feedback(f"spawning {entity_type}")
	e = EntityFactory(entity_type)
	w = context.world
	p = context.position
	if context.entity:
		p += context.entity.get_sight_vector()*2
	e.set_world(w, p)
