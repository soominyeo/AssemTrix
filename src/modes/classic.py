from assemtrix import device
from assemtrix import game
from assemtrix import instructor
from modes import mode


class ClassicMode(mode.TemplateMode):
    def set_register_size(self):
        self.register_size = 4

    def set_instructions(self):
        super().set_instructions()

        # main instruction
        instructions = mode.Instructions()
        instructions.add_instruction(lambda _device, o1, o2: [o1.write(o2.read(), _device.next())], "mov", 2)
        instructions.add_instruction(lambda _device, o1, o2: [o1.write(o1 + o2), _device.next()], 'add', 2)
        instructions.add_instruction(lambda _device, o1, o2: [o1.write(o1 - o2), _device.next()], 'sub', 2)
        instructions.add_instruction(lambda _device, o1: [o1.write(-o1), _device.next()], 'neg', 1)
        instructions.add_instruction(lambda _device, o1: [o1.write(o1.read() + 1), _device.next()], 'inc', 1)
        self.instructions_dict["main"] = instructions

    def set_conditions(self):
        super().set_conditions()

    def set_actions(self):
        super().set_actions()

    def set_devices(self):
        super().set_devices()
        self.devices.add_device(name="player", origin=instructor.Position(0, 0),
                                instructions=self.instructions_dict["main"], register_size=self.register_size)

    def set_memory_size(self):
        self.memory_size = mode.TemplateMode.default_memory_size

    def get_default_map(self):
        self.default_map = game.MemoryMap(15, 15, self.memory_size, 0)

    def set_address_range(self):
        self.address_range = 4


