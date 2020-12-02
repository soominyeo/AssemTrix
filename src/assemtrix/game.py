from assemtrix import device
from assemtrix import instructor

class MemoryMap:
    def __init__(self, x, y, memory_size, default=0):
        # initialize a memory map
        self.memory = [[device.Register(memory_size) for j in range(y)] for i in range(x)]

        for i in self.memory:
            for j in i:
                j.write(default)
        self.device_table = []
        self.origins = []
        self.memory_size = memory_size
        self.x = x
        self.y = y

    def read_raw(self, x, y):
        return self.read(instructor.Position(x, y))

    def get_memory(self, pos):
        return self.memory[pos.y % self.y][pos.x % self.x]

    def read(self, pos):
        memory = self.get_memory(pos)
        return memory.read()

    def add(self, sub_device):
        self.device_table.append(sub_device)
        self.origins.append(sub_device.origin)

    def throwinterrupt(self, device_number):
        _device = self.device_table[device_number]
        _device.registers["P"].write(_device.encoder.encode_pos(_device.origin))

    def write(self, pos, data):
        self.memory[pos.x][pos.y].write(data)
        if pos in self.origins:
            self.throwinterrupt(self.origins.index(pos))


class Condition:
    def __init__(self, cond_name, value):
        self.cond_name = cond_name
        self.value = value
        self.action = None

    def connect(self, action):
        self.action = action

    def check_cond(self, game):
        return False

    def check(self, game):
        if self.check_cond(game):
            self.action.run()


class MemoryCondition(Condition):
    def __init__(self, cond_name, pos, value):
        super().__init__(cond_name, value)
        self.pos = pos

    def check_cond(self, game):
        return game.game_map.read(self.pos) == self.value


class DeviceRegisterCondition(Condition):
    def __init__(self, cond_name, device_name, register_name, value):
        super().__init__(cond_name, value)
        self.device_name = device_name
        self.register_name = register_name

    def check_cond(self, game):
        isComplete = False
        for device in game.device_table:
            if device.name == self.device_name:
                if self.register_name not in device.registers.keys():
                    raise device.RegisterNotFoundException(f"Register {self.register_name} not found in {device.name}.")
                elif device.registers[self.register_name] == self.value:
                    isComplete = True
                    break
        return isComplete

class Action:
    def __init__(self, method):
        self.method = method
        self.instance = None

    def __str__(self):
        return str(self.method)

    def bind(self, instance):
        self.instance = instance

    def run(self):
        if self.instance is None:
            raise ActionNotBindedException(f"Action not binded: {self}")
        self.method(self.instance)

class SystemAction(Action):
    pass

class DeviceAction(Action):
    def __init__(self, index, method):
        super().__init__(method)
        self.index = index

class AssemTrixGame:
    def __init__(self, mode, seed=None, game_map=None):
        self.seed = seed

        # initialize game map
        if game_map is None:
            self.game_map = mode.default_map
        else:
            self.game_map = game_map

        self.device_table = []
        self.memory_size = mode.memory_size
        self.address_range = mode.address_range

        # initialize devices
        for d_info in mode.devices:
            _device = device.Device(d_info, self.game_map, self.address_range, self.memory_size, seed)
            self.game_map.add(_device)
            self.device_table.append(_device)


        # initialize conditions and actions
        self.success_cond = mode.success_cond
        self.failure_cond = mode.failure_cond
        self.conditions = mode.conditions

        self.actions = mode.actions
        for action in self.actions.values():
            if isinstance(action, SystemAction):
                action.bind(self)
            elif isinstance(action, DeviceAction):
                action.bind(self.device_table[action.index])


        # connect conditions
        for cond in self.conditions:
            cond.connect(self.actions[cond.cond_name])

        # initialize count
        self.step_count = 0
        self.input_count = 0


    def step(self):
        self.step_each()
        self.check_cond()
        self.step_count += 1

    def step_until(self, condition: Condition, max_step=0):
        if max_step == 0:
            while not condition.check():
                self.step()
        else:
            while not condition.check() and self.step_count < max_step:
                self.step()

    def step_each(self):
        for d in self.device_table:
            d.step()

    def check_cond(self):
        for c in self.conditions:
            c.check(self)

    def inst_input(self, id, text):
        if id not in range(len(self.device_table)):
            raise NameNotFoundException(f"No device [{id}] found.")
        _device = self.device_table[id]
        code = _device.encoder.encoded(_device, text)
        self.game_map.write(_device.origin, code)
        self.input_count += 1
        return code

    def raw_input(self, id, text):
        pass

    def on_success(self):
        return True

    def on_failure(self):
        return False


class NameNotFoundException(Exception):
    pass

class ActionNotBindedException(Exception):
    pass


if __name__=="__main__":
    from modes import classic
    mode = classic.ClassicMode()
    game = AssemTrixGame(mode)
    game.inst_input(0, "inc BC#1")
    game.step()
