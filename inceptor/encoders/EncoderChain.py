import traceback
from collections import OrderedDict
from pydoc import locate

from config.Config import Config
from encoders.Encoder import Encoder, EncoderTypes
from enums.Language import Language


class EncoderChain:
    def __init__(self):
        self.chain = OrderedDict()
        self.current = 0

    def is_empty(self):
        return len(self.chain) == 0

    def to_string(self):
        return "->".join([e.__class__.__name__ for e in self.chain.values()])

    @property
    def last(self):
        return max(self.current - 1, 0)

    @property
    def last_element(self):
        try:
            return self.chain[max(self.current - 1, 0)]
        except KeyError:
            return None

    def prepend(self, value: Encoder):
        value.order = 0
        for e in self.chain.values():
            e.order += 1
        self.chain[self.current] = value
        self.chain.move_to_end(self.current, last=False)
        self.current += 1

    def push(self, value: Encoder):
        value.order = self.current
        self.chain[self.current] = value
        self.current += 1

    def pop(self) -> Encoder:
        self.current -= 1
        return self.chain.popitem()[1]

    def delete(self, index) -> bool:
        if index not in self.chain.keys():
            return False
        self.chain.move_to_end(index)
        self.chain.popitem()

    def encode(self, data):
        for k, v in self.chain.items():
            data = v.encode(data)
        return data

    def validate(self, language=Language.CSHARP):
        for e in list(self.chain.values()):
            if not e.is_supported(language):
                return False
        current_in, current_out, previous_out = None, None, None
        if len(self.chain) == 0:
            return True
        if self.chain[0].decoder_out[0] != bytes:
            return False
        #if self.chain[self.last].decoder_in[0] != str and language == Language.CSHARP:
        #    return False
        # if self.chain[self.last].decoder_in[0] != bytes and language == Language.POWERSHELL:
        #    return False
        if self.chain[0].decoder_in[0] != bytes and language == Language.POWERSHELL:
            return False
        for k in list(self.chain.keys())[::-1]:
            current_in = self.chain[k].decoder_in
            current_out = self.chain[k].decoder_out[0]
            if previous_out and (previous_out != current_in[0] or previous_out not in current_in):
                if Config().get("DEBUG", "encoders"):
                    print(f"Node mismatch: {previous_out} -> {current_in}")
                return False
            previous_out = current_out
        return True

    def translate(self, language=Language.CSHARP):
        modules = []
        chain = EncoderChain()
        chain.chain = self.chain.copy()
        chain.current = self.current
        call = ""
        if language == Language.CSHARP:
            call = Config().get("PLACEHOLDERS", "SHELLCODE_VARIABLE")
        elif language == Language.POWERSHELL:
            call = "$" + Config().get("PLACEHOLDERS", "SHELLCODE_VARIABLE")
        prefix, suffix = "", ""
        if language == Language.CSHARP:
            prefix = "byte[] decoded = "
            suffix = ";"
        elif language == Language.CPP:
            prefix = ""
            suffix = "\n"
        elif language == Language.POWERSHELL:
            prefix = "[byte[]] $decoded = "
            suffix = ";"

        while not chain.is_empty():
            encoder = chain.pop()
            encoder_module = encoder.translate(language=language)
            call = encoder_module.call_component.as_function_call(call, language=language)
            modules.append(encoder_module)

        call = f"{prefix}{call}{suffix}"

        return modules, call

    @staticmethod
    def from_list(encoders: list = None):
        chain = EncoderChain()
        if not encoders or len(encoders) == 0:
            return chain
        for e in encoders:
            try:
                if e == "":
                    continue
                for et in EncoderTypes.to_list():
                    try:
                        encoder_class_string = f"encoders.{str(e).capitalize()}{et}.{str(e).capitalize()}{et}"
                        # print(encoder_class_string)
                        encoder_class = locate(encoder_class_string)
                        encoder_instance = encoder_class()
                        chain.push(encoder_instance)
                        break
                    except:
                        pass
            except Exception as ex:
                print(ex)
                continue
        return chain
