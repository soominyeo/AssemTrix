import math
import regex
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
            x = ("0" if pos.x >= 0 else "1") + format(abs(pos.x % range), f"0{range}b")
            y = ("0" if pos.y >= 0 else "1") + format(abs(pos.y % range), f"0{range}b")
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
            dist %= 2 ** range
            x = ("0" if dist >= 0 else "1") + format(abs(dist), f"0{range}b")
        else:
            range = address_range
            dist %= 2 ** range
            x = format(abs(dist), f"0{range}b")
        return int(x[::-1], 2)

    @classmethod
    def toColumnData(cls, dist, address_range, issigned=True):
        if issigned:
            range = address_range - 1
            dist %= 2 ** range
            x = ("0" if dist >= 0 else "1") + format(abs(dist), f"0{range}b")
        else:
            range = address_range
            dist %= 2 ** range
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

    def get_data(self, _device):
        return data


class RegisterAddress(Address):
    def __init__(self, reg):
        super().__init__()
        self.reg = reg

    def get_data(self, _device):
        return _device.registers[self.reg].read()


# by addressing
# determine get_pos
class RelativeAddress(Address):
    def __init__(self, origin, memory_size):
        self.origin = origin
        self.memory_size = memory_size

    def get_pos(self, _device):
        return Position.toMapPosition(_device.registers[self.origin].read(), self.memory_size, False) + self.get_dist(_device)


# by shape
# determine calc_pos
class ShapeAddress(Address):
    def __init__(self, address_range):
        self.address_range = address_range


class LineAddress(ShapeAddress):
    def get_dist(self, _device):
        return Position.toLinePosition(self.get_data(_device), self.address_range)


class ColumnAddress(ShapeAddress):
    def get_dist(self, _device):
        return Position.toColumnPosition(self.get_data(_device), self.address_range)


class MapAddress(ShapeAddress):
    def get_dist(self, _device):
        return Position.toMapPosition(self.get_data(_device), self.address_range)


class RelativeMemoryAddress(RelativeAddress, MemoryAddress):
    def __init__(self, origin, data, memory_size):
        RelativeAddress.__init__(self, origin, memory_size)
        MemoryAddress.__init__(self, data)


class RelativeRegisterAddress(RelativeAddress, RegisterAddress):
    def __init__(self, origin, reg, memory_size):
        RelativeAddress.__init__(self, origin, memory_size)
        RegisterAddress.__init__(self, reg)


class LineRelativeMemoryAddress(LineAddress, RelativeMemoryAddress):
    def __init__(self, origin, data, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeMemoryAddress.__init__(self, origin, data, memory_size)


class ColumnRelativeMemoryAddress(ColumnAddress, RelativeMemoryAddress):
    def __init__(self, origin, data, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeMemoryAddress.__init__(self, origin, data, memory_size)


class MapRelativeMemoryAddress(MapAddress, RelativeMemoryAddress):
    def __init__(self, origin, data, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeMemoryAddress.__init__(self, origin, data, memory_size)


class LineRelativeRegisterAddress(LineAddress, RelativeRegisterAddress):
    def __init__(self, origin, reg, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeRegisterAddress.__init__(self, origin, reg, memory_size)


class ColumnRelativeRegisterAddress(ColumnAddress, RelativeRegisterAddress):
    def __init__(self, origin, reg, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeRegisterAddress.__init__(self, origin, reg, memory_size)


class MapRelativeRegisterAddress(MapAddress, RelativeRegisterAddress):
    def __init__(self, origin, reg, memory_size, address_range):
        ShapeAddress.__init__(self, address_range)
        RelativeRegisterAddress.__init__(self, origin, reg, memory_size)


class Instruction:
    def __init__(self, operator, name):
        self.operator = operator
        self.name = name

    def execute(self, _device, *addresses):
        pass

    def __str__(self):
        return self.name


class NullaryInstruction(Instruction):
    def execute(self, _device, *addresses):
        self.operator(_device)


class UnaryInstruction(Instruction):
    def execute(self, _device, *addresses):
        self.operator(_device, addresses[0].get_source(_device))


class BinaryInstruction(Instruction):
    def execute(self, _device, *addresses):
        self.operator(_device, addresses[0].get_source(_device), addresses[0].get_source(_device))


class Encoder:
    def __init__(self, instructions, op_size, address_size, address_range, total_size, memory_size):
        self.instructions = instructions
        self.op_size = op_size
        self.address_size = address_size
        self.address_range = address_range
        self.total_size = total_size
        self.memory_size = memory_size

    def encoded(self, _device, text):
        pattern = regex.compile(Instructor.pattern)
        match = pattern.match(text)
        if not match:
            raise InvalidFormatException()
        grouped = match.capturesdict()

        i_name = grouped["instruct"][0]
        instructions = [i for i, value in enumerate(self.instructions) if value.name == i_name]
        if not instructions:
            raise InstructionNotFoundException()
        op = format(instructions[0], f"0{self.op_size}b")
        addr = ""

        for index in range(len(grouped["address_type"])):
            address_type = grouped["address_type"][index]
            try:
                i = Instructor.prefix.index(address_type)
                addresser = Instructor.addressers[i][0]
            except ValueError:
                raise AddressTypeNotFoundException(f"Cannot find address type: {address_type}")

            addr = format(i, f"0{int(math.ceil(abs(math.log2(len(Instructor.addressers)))))}b")[::-1] + addr
            print('*', addresser, addr)
            # if register accessing
            if issubclass(addresser, RegisterAddress):
                register = grouped["address"][index]
                try:
                    register_id = _device.register_names.index(register)
                except ValueError:
                    raise device.RegisterNotFoundException(f"Register{register} not found or not accessible.")
                addr = format(max(register_id - 4, 0), f"0{_device.register_size}b")[::-1] + addr

            # if memory accessing
            elif issubclass(addresser, MemoryAddress):
                data = grouped["address"][index]

                # if map addressing
                if issubclass(addresser, MapAddress):
                    temp = data.split(',')
                    if len(temp) < 2:
                        raise InvalidFormatException()
                    pos = Position(int(temp[0]), int(temp[1]))
                    addr = format(Position.toMapData(pos, address_range=self.address_range, issigned=True), f"0{self.address_range}b")[::-1] + addr

                # if line addressing
                elif issubclass(addresser, LineAddress):
                    try:
                        dist = int(data)
                    except ValueError:
                        raise InvalidFormatException
                    addr = format(Position.toLineData(dist, address_range=self.address_range, issigned=True), f"0{self.address_range}b")[::-1] + addr
                elif issubclass(addresser, ColumnAddress):
                    try:
                        dist = int(data)
                    except ValueError:
                        raise InvalidFormatException
                    addr = format(Position.toColumnData(dist, address_range=self.address_range, issigned=True), f"0{self.address_range}b")[::-1] + addr
        print(addr)
        return int(addr + op[::-1], 2)
        # return int(addr[::-1] + op[::-1], 2)

    def encode_pos(self, pos):
        return Position.toMapData(pos, self.address_range, False)


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
        self.binary = format(data, f"0{self.total_size}b")[::-1]
        instruction = self.instructions[self.get_op()]

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
        if len(self.binary) < size:
            raise InvalidFormatException()
        value = int(self.binary[:size], 2)
        self.binary = self.binary[size:]
        return value

    def get_op(self):
        return self.get_sub(self.op_size)

    def get_address(self, _device):
        type = self.get_sub(math.ceil(abs(math.log2(len(Instructor.addressers)))))
        address = None
        base = device.Register(self.memory_size)

        addresser = Instructor.addressers[type]
        address_type = addresser[0]
        # if relative addressing, get base register
        if issubclass(address_type, RelativeAddress):
            base = _device.registers[addresser[1]]

            # if register addressing or not
            if issubclass(address_type, RegisterAddress):
                reg_id = self.get_sub(self.address_size)
                reg = _device.registers[_device.register_names[reg_id]]
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
    pattern = "^(?:[\\s]*)(?<instruct>[a-z]+)(?:[\\s]*)((?<address_type>[BP][LCM][#&])(?<address>([A-Z][0-9]*)|([0-9]+,[0-9]+)|([0-9]+))(?:[\\s])*)*"
    addressers = [(LineRelativeMemoryAddress, "P"), (LineRelativeMemoryAddress, "B"),
                  (ColumnRelativeMemoryAddress, "P"), (ColumnRelativeMemoryAddress,"B"),
                  (MapRelativeMemoryAddress, "P"), (MapRelativeMemoryAddress, "B"),
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
        _type = math.ceil(math.log2(len(Instructor.addressers)))

        return address + _type

    @classmethod
    def get_min_op_size(cls, instructions: list):
        return math.ceil(math.log2(len(instructions)))


class InstructionNotFoundException(Exception):
    pass


class AddressTypeNotFoundException(Exception):
    pass


class AddressRangeExceedException(Exception):
    pass


class InvalidFormatException(Exception):
    pass


if __name__=="__main__":
    data = Position.toMapData(Position(1,3), 8, True)
    pos = Position.toMapPosition(data, 8, True)
    print(data, pos.x, pos.y)

    from modes import classic
    classic_mode = classic.ClassicMode()
    _device = device.Device(classic_mode.devices[0], memory_map=classic_mode.default_map, memory_size=10, address_range=10)
    address = MapRelativeMemoryAddress(origin="P", data=data, memory_size=10, address_range=5)
    print(address.get_source(_device))

    print(_device.encoder.instructions)
    code = _device.encoder.encoded(_device, "inc BL#1025")
    print(code)
    instruction, address = _device.decoder.decoded(_device, code)
    print(instruction.name, type(address), address.get_source)

    pattern = regex.compile(Instructor.pattern)
    grouped = pattern.match("inc PL#1").capturesdict()