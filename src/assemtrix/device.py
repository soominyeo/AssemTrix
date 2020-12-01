from assemtrix import instructor as inst


class Register:
    def __init__(self, memory_size):
        self.__value = 0
        self.memory_size = memory_size

    def __int__(self):
        if self.__value > 2 ** (self.memory_size - 1):
            return -self.__value
        else:
            return self.__value

    def __and__(self,other):
        return self.__value & other.read

    def __or__(self,other):
        return self.__value | other.read

    def __neg__(self):
        return 2 ** self.memory_size - self.__value - 1

    def __add__(self, other):
        return self.__value + other.read

    def read(self):
        return self.__value

    def write(self, value):
        flag = 0b0000
        self.__value = value % 2 ** self.memory_size
        # overflow
        if self.__value > 2 ** self.memory_size:
            flag += 0b0100
            value %= 2 ** self.memory_size
        # signed
        if self.__value > 2 ** (self.memory_size - 1):
            flag += 0b0010
        # zero
        if value == 0:
            flag += 0b0001
        return flag

    def reset(self):
        self.__value = 0


class ALU:
    def __init__(self, reg_s: Register, memory_size):
        self.reg_s = reg_s
        self.memory_size = memory_size

    # add reg_b to reg_a
    def calc_add(self, reg_a: Register, reg_b: Register):
        value = reg_a + reg_b
        flag = reg_a.write(value)
        self.reg_s.write(flag)

    def calc_neg(self, reg_a: Register):
        value = -reg_a
        flag = reg_a.write(value)
        self.reg_s.write(flag)

    def calc_and(self, reg_a: Register, reg_b: Register):
        value = reg_a & reg_b
        flag = reg_a.write(value)
        self.reg_s.write(flag)

    def calc_or(self, reg_a: Register, reg_b: Register):
        value = reg_a | reg_b
        flag = reg_a.write(value)
        self.reg_s.write(flag)

    def calc_mov(self, reg_a: Register, reg_b: Register):
        reg_a.write = reg_b.read()


class Device:
    invisible_registers = ["P", "H", "S", "I"]
    visible_registers = ["A", "B", "X", "C"]

    def __init__(self, device_info, memory_map, address_range, memory_size, seed=None):
        # retrieve data from parameter
        self.register_size = device_info.register_size
        self.address_range = address_range

        instructor = inst.Instructor(device_info.instructions, self.register_size, self.address_range, memory_size)

        self.memory_size = instructor.get_memory_size() if instructor.get_memory_size() > memory_size else memory_size
        self.decoder = instructor.get_decoder()
        self.encoder = instructor.get_encoder()
        self.main_map = memory_map
        self.origin = device_info.origin
        self.name = device_info.name

        # initialize registers
        self.register_names = Device.invisible_registers + Device.visible_registers
        for i in range(2 ** self.register_size - 4):
            self.register_names.append("D" + str(i))
        self.registers = {name: Register(memory_size) for name in self.register_names}

        # add ALU
        self.alu = ALU(self.registers["S"], memory_size)

    def get_registers(self):
        return self.registers[4:]

    def get_origin(self):
        return self.origin

    def get_main_map(self):
        return self.main_map

    def step(self):
        data = self.read_current()
        if data == 0:
            self.registers["P"].write(self.encoder.encode_pos(self.origin))
            self.registers["H"].reset()
        else:
            self.run(data)

    def read_current(self):
        pos = self.decoder.get_absolute_pos(self.registers["P"].read())
        return self.main_map.read(pos)

    def run(self, data):
        decoded = self.decoder.decode(data)
        if len(decoded) <= 1:
            decoded[0].execute(self)
        elif len(decoded) == 1:
            decoded[0].execute(self, decoded[1])
        elif len(decoded) == 2:
            decoded[0].execute(self, decoded[1], decoded[2])

    def next(self, data):
        pos = self.read_current()
        d = self.registers["H"].read()
        next_pos = inst.Position(pos.x + tf_pos[d][0], pos.y + tf_pos[d][1])
        self.registers["P"].write(self.encoder.encode_pos(next_pos))

    def interrupt(self, device_num):
        self.main_map.throwinterrupt(device_num)

tf_pos = [[1, 0], [0,- 1], [-1, 0],[0, 1]]


class RegisterNotFoundException(Exception):
    pass
