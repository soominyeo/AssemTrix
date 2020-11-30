from assemtrix import device
from assemtrix import game
from assemtrix import instructor
from modes import mode


class ClassicMode(mode.TemplateMode):
    def set_register_size(self):
        self.register_size = 4

    def set_instructions(self):
        self.instructions_dict = {}
        instructions = mode.Instructions()
        instructions.add_instruction(lambda _device, o1, o2: o1.write(o2.read()), "mov", 2)
        instructions.add_instruction(lambda _device, o1, o2: o1.write(o1 + o2), 'add', 2)
        instructions.add_instruction(lambda _device, o1, o2: o1.write(o1 - o2), 'sub', 2)
        instructions.add_instruction(lambda _device, o1: o1.write(-o1), 'neg', 1)
        instructions.add_instruction(lambda _device, o1: o1.write(o1.read() + 1), 'inc', 1)
        self.instructions_dict["main"] = instructions

    def set_conditions(self):
        self.conditions = mode.Conditions()
        self.success_cond = game.Condition("success", None)
        self.failure_cond = game.Condition("failure", None)
        self.conditions.append(self.success_cond)
        self.conditions.append(self.failure_cond)

    def set_actions(self):
        super().set_actions()

    def set_devices(self):
        self.devices = mode.Devices()
        self.devices.add_device(name="player", origin=instructor.Position(0, 0),
                                instructions=self.instructions_dict["main"], register_size=self.register_size)

    def set_memory_size(self):
        self.memory_size = mode.TemplateMode.default_memory_size

    def get_default_map(self):
        self.default_map = game.MemoryMap(25, 25, self.memory_size, 0)


    def set_address_range(self):
        self.address_range = 4


