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
        instructions.add_instruction('back', lambda _device: _device.back(), 0)
        instructions.add_instruction("mov", lambda _device, o1, o2: [o1.write(o2.read(), _device.next())], 2)
        instructions.add_instruction('add', lambda _device, o1, o2: [o1.write(o1 + o2), _device.next()], 2)
        instructions.add_instruction('sub', lambda _device, o1, o2: [o1.write(o1 - o2), _device.next()], 2)
        instructions.add_instruction('neg', lambda _device, o1: [o1.write(-o1), _device.next()], 1)
        instructions.add_instruction('inc', lambda _device, o1: [o1.write(o1.read() + 1), print(o1.read()), _device.next()], 1)
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
        self.memory_size = 12

    def get_default_map(self):
        self.default_map = game.MemoryMap(15, 15, self.memory_size, 0)

    def set_address_range(self):
        self.address_range = 4


