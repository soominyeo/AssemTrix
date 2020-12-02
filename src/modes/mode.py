from assemtrix import instructor
from assemtrix import game

class Instructions(list):
    def add_instruction(self, name, operator, operand):
        if operand == 0:
            instruction = instructor.NullaryInstruction(name, operator)
        elif operand == 1:
            instruction = instructor.UnaryInstruction(name, operator)
        else:
            instruction = instructor.BinaryInstruction(name, operator)
        self.append(instruction)


class Conditions(list):
    def add_memory_condition(self, cond_name, pos, value):
        self.append(game.MemoryCondition(cond_name, pos, value))

    def add_register_condition(self, cond_name, device_name, register_name, value):
        self.append(game.DeviceRegisterCondition(cond_name, device_name, register_name, value))


class Actions(dict):
    def add_system_action(self, cond_name, method):
        self[cond_name] = game.SystemAction(method)

    def add_device_action(self, cond_name, index, method):
        self[cond_name] = game.DeviceAction(index, method)

class DeviceInfo:
    def __init__(self, name, origin, instructions, register_size):
        self.name = name
        self.origin = origin
        self.instructions = instructions
        self.register_size = register_size

class Devices(list):
    def add_device(self, name, origin, instructions, register_size):
        self.append(DeviceInfo(name, origin, instructions, register_size))



class ModeInfo:
    name = ""
    version = "x.x"
    description = ""
    author = ""


class TemplateMode:
    default_memory_size = 0
    def __init__(self):
        self.set_register_size()
        self.set_instructions()
        self.set_conditions()
        self.set_actions()
        self.set_devices()
        self.set_memory_size()
        self.set_address_range()
        self.get_default_map()

    def set_register_size(self):
        self.register_size = 4

    def set_instructions(self):
        self.instructions_dict = {}

    def set_conditions(self):
        self.conditions = Conditions()
        self.success_cond = game.Condition("success", None)
        self.failure_cond = game.Condition("failure", None)
        self.conditions.append(self.success_cond)
        self.conditions.append(self.failure_cond)

    def set_actions(self):
        self.actions = Actions()
        self.actions.add_system_action("success", game.AssemTrixGame.on_success)
        self.actions.add_system_action("failure", game.AssemTrixGame.on_failure)

    def bind(self):
        self.success_cond.connect(self.actions["success"])
        self.failure_cond.connect(self.actions["failure"])

    def set_devices(self):
        self.devices = Devices()

    def set_memory_size(self):
        self.memory_size = TemplateMode.default_memory_size

    def get_default_map(self):
        self.default_map = game.MemoryMap(self.memory_size)

    def set_address_range(self):
        self.address_range = 4