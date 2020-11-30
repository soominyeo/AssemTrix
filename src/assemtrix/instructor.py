import math
from assemtrix import device

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def flip(self):
        temp = self.x
        self.x = self.y
        self.y = temp

    @classmethod
    def toMapData(cls, pos, address_range, issigned=True):
        if issigned:
            range = address_range // 2 - 1
            x = ("0" if pos.x >= 0 else "1") + format(abs(pos.x), f"0{range}b")
            y = ("0" if pos.y >= 0 else "1") + format(abs(pos.y), f"0{range}b")
            return int(y[::-1] + x[::-1], 2)
        else:
            range = address_range // 2
            x = format(abs(pos.x), f"0{range}b")
            y = format(abs(pos.y), f"0{range}b")
            return int(y[::-1] + x[::-1], 2)

    @classmethod
    def toLineData(cls, dist, address_range, issigned=True):
        if issigned:
            range = address_range - 1
            x = ("0" if dist >= 0 else "1") + format(abs(dist), f"0{range}b")
        else:
            range = address_range
            x = format(abs(dist), f"0{range}b")
        return int(x[::-1], 2)

    @classmethod
    def toColumnData(cls, dist, address_range, issigned=True):
        if issigned:
            range = address_range - 1
            x = ("0" if dist >= 0 else "1") + format(abs(dist), f"0{range}b")
        else:
            range = address_range
            x = format(abs(dist), f"0{range}b")
        return int(x[::-1], 2)

    @classmethod
    def toMapPosition(cls, data, address_range, issigned=True):
        if issigned:
            range = address_range // 2 - 1
            binary = format(data, f"0{2 * (range+1)}b")[:-2 * (range + 1) - 1: -1]
            x = int(binary[1:range + 1], 2) if binary[0] == "0" else -int(binary[1:range + 1], 2)
            y = int(binary[range + 2:], 2) if binary[range + 1] == "0" else -int(binary[range + 2:], 2)
        else:
            range = address_range // 2
            binary = format(data, f"0{2 * range}b")[:-2 * range - 1:-1]
            x = int(binary[:range], 2)
            y = int(binary[range:2 * range], 2)
        return Position(x, y)

    @classmethod
    def toLinePosition(cls, data, address_range: int, issigned=True):
        if issigned:
            range = address_range - 1
            binary = format(data, f"0{address_range}b")[:-address_range - 1:-1]
            x = abs(int(binary[1:range + 1], 2)) if binary[0] == "0" else -abs(int(binary[1:range + 1], 2))
        else:
            range = address_range
            binary = format(data, f"0{address_range}b")[:-address_range - 1: -1]
            x = int(binary, 2)
        return Position(x, 0)

    @classmethod
    def toColumnPosition(cls, data, address_range, issigned=True):
        return Position.toLinePosition(data, address_range, issigned).flip()

class Address:
    def get_source(self, _device):
        pass

# by source
# determine source
class MemoryAddress(Address):
    def __init__(self, data):
        self.data = data

    def get_source(self, _device):
        pass


class RegisterAddress(Address):
    def __init__(self, reg):
        super().__init__()
        self.reg = reg

    def get_reg(self, _device):
        return _device.registers[self.reg]


# by addressing
# determine get_pos
class RelativeAddress(Address):
    def __init__(self, origin, memory_size):
        super().__init__()
        self.origin = origin
        self.memory_size = memory_size

    def calc_dist(self, _device):
        return 0

    def get_pos(self, _device):
        return Position.toMapPosition(_device.registers[self.origin].read(), self.memory_size, False) + self.calc_dist(_device)

# by shape
# determine calc_pos
class ShapeAddress(Address):
    def __init__(self, address_range):
        self.address_range = address_range

class LineAddress(ShapeAddress):
    def calc_pos(self, _device):
        return Position.toLinePosition(self.get_data(_device), self.address_range)

class ColumnAddress(ShapeAddress):
    def calc_pos(self, _device):
        return Position.toColumnPosition(self.get_data(_device), self.address_range)

class MapAddress(ShapeAddress):
    def calc_pos(self, _device):
        return Position.toMapPosition(self.get_data(_device), self.address_range)

class LineRelativeMemoryAddress(LineAddress, RelativeAddress, MemoryAddress):
    def __init__(self, origin, data, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeAddress.__init__(self, origin, memory_size)
        MemoryAddress.__init__(self, data)

    def calc_dist(self, _device):
        return self.calc_pos(_device)

    def get_source(self, _device):
        return _device.main_map[self.get_pos(_device)]

class ColumnRelativeMemoryAddress(ColumnAddress, RelativeAddress, MemoryAddress):
    def __init__(self, origin, data, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeAddress.__init__(self, origin, memory_size)
        MemoryAddress.__init__(self, data)

    def calc_dist(self, _device):
        return self.calc_pos(_device)

    def get_source(self, _device):
        return _device.main_map[self.get_pos(_device)]

class MapRelativeMemoryAddress(MapAddress, RelativeAddress, MemoryAddress):
    def __init__(self, origin, data, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeAddress.__init__(self, origin, memory_size)
        MemoryAddress.__init__(self, data)

    def calc_dist(self, _device):
        return self.calc_pos(_device)

    def get_source(self, _device):
        return _device.main_map[self.get_pos(_device)]

class LineRelativeRegisterAddress(LineAddress, RelativeAddress, RegisterAddress):
    def __init__(self, origin, reg, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeAddress.__init__(self, origin, memory_size)
        RegisterAddress.__init__(self, reg)

    def calc_dist(self, _device):
        return self.calc_pos(_device)

    def get_source(self, _device):
        return self.get_reg()

class ColumnRelativeRegisterAddress(ColumnAddress, RelativeAddress, RegisterAddress):
    def __init__(self, origin, reg, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeAddress.__init__(self, origin, memory_size)
        RegisterAddress.__init__(self, reg)

    def calc_dist(self, _device):
        return self.calc_pos(_device)

    def get_source(self, _device):
        return self.get_reg()


class MapRelativeRegisterAddress(MapAddress, RelativeAddress, RegisterAddress):
    def __init__(self, origin, reg, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeAddress.__init__(self, origin, memory_size)
        RegisterAddress.__init__(self, reg)

    def calc_dist(self, _device):
        return self.calc_pos(_device)

    def get_source(self, _device):
        return self.get_reg()


class Instruction:
    def __init__(self, operator, name):
        self.operator = operator
        self.name = name

    def __str__(self):
        return self.name


class NullaryInstruction(Instruction):
    def execute(self, _device):
        self.operator(_device)

class UnaryInstruction(Instruction):
    def execute(self, _device, address):
        self.operator(_device, address.get_source(_device))


class BinaryInstruction(Instruction):
    def execute(self, _device, address_a, address_b):
        self.operator(_device, address_a.get_source(_device), address_b.get_source(_device))


class Encoder:
    def __init__(self, instructions, op_size, address_size, address_range, total_size, memory_size):
        self.instructions = instructions
        self.op_size = op_size
        self.address_size = address_size
        self.address_range = address_range
        self.total_size = total_size
        self.memory_size = memory_size

    def encoded(self, _device, instruction, *addresses):
        if instruction not in self.instructions:
            raise InstructionNotFoundException(f"There is no instruction {instruction} in {_device}!")

        op = format(self.instructions.index(instruction), f"0{self.op_size}b")

        addr = ""

        for address in addresses:
            prefix = address[:3]
            index = Instructor.prefix.index(prefix)
            if index == -1:
                raise AddressTypeNotFoundException(f"Cannot find address type: {prefix}")
            addresser = Instructor.addressers[index]

            addr += format(index, f"0{abs(math.log2(len(Instructor.addressers)))}b")

            if isinstance(addresser[0], RegisterAddress):
                register_id = _device.registers[4:].index(address[3:])
                if register_id == -1:
                    raise device.RegisterNotFoundException(f"Register{address[3:]} not found or not accessible.")
                addr += format(max(register_id - 4, 0), f"0{_device.register_size}b")
            elif isinstance(addresser[0], MemoryAddress):
                temp = address[3:].split(',')
                if isinstance(addresser[0], MapAddress):
                    pos = Position(temp[0], temp[1])
                    if pos.x > self.address_range or pos.y > self.address_range:
                        raise
                    addr += format(Position.toMapData(pos=pos, address_range=self.address_range, issigned=True))
                else:
                    addr += temp[0]


        return int(addr[::-1] + op[::-1], 2)

    def encode_pos(self, data):
        return Position.toMapPosition(data, self.memory_size, True)


class Decoder:
    def __init__(self, instructions, op_size, address_size, address_range, total_size, memory_size):
        self.instructions = instructions
        self.op_size = op_size
        self.address_size = address_size
        self.address_range = address_range
        self.total_size = total_size
        self.memory_size = memory_size if memory_size > total_size else total_size
        self.binary = ""

    def decoded(self, _device, data):
        self.binary = reversed(format(data, format(f"0{self.total_size}b")))

        instruction = self.get_op()

        if isinstance(instruction, NullaryInstruction):
            return (instruction)
        elif isinstance(instruction, UnaryInstruction):
            address = self.get_address(_device)
            return instruction, address
        else:
            address_a = self.get_address(_device)
            address_b = self.get_address(_device)
            return instruction, address_a, address_b

    def get_sub(self, size):
        value = int(self.binary[:size], 2)
        self.binary = self.binary[size:]
        return value

    def get_op(self):
        return self.get_sub(self.op_size)

    def get_address(self, _device):
        type = self.get_sub(abs(math.log2(len(Instructor.addressers))))
        address = Address()
        base = device.Register()

        address_type = Instructor.addressers[type]
        # if relative addressing, get base register
        if isinstance(address_type, tuple):
            base = _device.registers[address_type[1]]
            address_type = address_type[0]

            # if register addressing or not
            if isinstance(address_type, RegisterAddress):
                reg = _device.registers[self.get_sub(self.address_size)]
                address = address_type(origin=base, reg=reg, memory_size=self.memory_size, address_range=self.address_range)
            else:
                data = self.get_sub(self.address_size)
                address = address_type(origin=base, data=data, memory_size=self.memory_size, address_range=self.address_range)

        return address

    def get_absolute_pos(self, data):
        return Position.toMapPosition(data, self.memory_size, issigned=False)


class Instructor:
    address_types = [LineRelativeMemoryAddress, ColumnRelativeMemoryAddress, MapRelativeMemoryAddress,
                     LineRelativeRegisterAddress, ColumnRelativeRegisterAddress, MapRelativeRegisterAddress]
    register_base = ["P", "B"]
    prefix = ["PL#", "BL#", "PC#", "BC#", "PM#", "BM#", "PL&", "BL&", "PC&", "BC&", "PM&", "BM&"]

    addressers = [(LineRelativeMemoryAddress, "P"), (LineRelativeMemoryAddress, "B"),
                  (ColumnRelativeMemoryAddress, "P"), (ColumnRelativeMemoryAddress,"B"),
                  (MapRelativeRegisterAddress, "P"), (MapRelativeRegisterAddress, "B"),
                  (LineRelativeRegisterAddress, "P"), (LineRelativeRegisterAddress, "B"),
                  (ColumnRelativeRegisterAddress, "P"), (ColumnRelativeRegisterAddress, "B"),
                  (MapRelativeRegisterAddress, "P"), (MapRelativeRegisterAddress, "B")]

    def __init__(self, instructions, register_size, address_range, memory_size=None):
        self.instructions = instructions
        op_size = Instructor.get_min_op_size(instructions)

        address_size = Instructor.get_min_address_size(address_range, register_size)
        total_size = op_size + address_size * 2

        self.memory_size = memory_size if memory_size > total_size else total_size

        self.decoder = Decoder(instructions, op_size, address_size, address_range, total_size, self.memory_size)
        self.encoder = Encoder(instructions, op_size, address_size, address_range, total_size, self.memory_size)


    def get_memory_size(self):
        return self.memory_size

    def get_decoder(self):
        return self.decoder

    def get_encoder(self):
        return self.encoder

    @classmethod
    def get_min_address_size(cls, address_range, register_size):
        address = math.ceil(max(math.log2(address_range), register_size))
        type = math.ceil(math.log2(len(Instructor.addressers)))
        return address + type

    @classmethod
    def get_min_op_size(cls, instructions: list):
        return math.ceil(math.log2(len(instructions)))


class InstructionNotFoundException(Exception):
    pass

class AddressTypeNotFoundException(Exception):
    pass

class AddressRangeExceedException(Exception):
    pass

if __name__=="__main__":
    data = Position.toMapData(Position(1,3), 8, True)
    pos = Position.toMapPosition(data, 8, True)
    print(data, pos.x, pos.y)