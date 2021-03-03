import re
import sys
from typing import List


class SymbolTable:
    INIT_TABLE = {
        "R0": 0,
        "R1": 1,
        "R2": 2,
        "R3": 3,
        "R4": 4,
        "R5": 5,
        "R6": 6,
        "R7": 7,
        "R8": 8,
        "R9": 9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,
        "SCREEN": 16384,
        "KBD": 24576,
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
    }

    def __init__(self):
        self.table = SymbolTable.INIT_TABLE
        self.empty_address = 16

    def add_entry(self, symbol: str, address: int = None) -> None:
        if not address:
            self.table[symbol] = self.empty_address
            self.empty_address += 1
        else:
            self.table[symbol] = address

    def contains(self, symbol: str) -> bool:
        return symbol in self.table

    def get_address(self, symbol: str) -> int:
        return self.table.get(symbol)


class ParseHelper:

    @staticmethod
    def c_parser(instruction: str) -> str:
        """
        Converts a type C instruction to it's binary representation.
        Each method divide the instruction to it's suitable part: (comp, dest, jump).
        """

        comp_dict = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "!D": "0001101",
            "!A": "0110001",
            "-D": "0001111",
            "-A": "0110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "D|A": "0010101",
            "M": "1110000",
            "!M": "1110001",
            "-M": "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "D|M": "1010101",
        }

        dest_dict = {
            None: "000",
            "M": "001",
            "D": "010",
            "DM": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "ADM": "111",

            "MD": "011",
            "MA": "101",
            "DA": "110",
            "MDA": "111",
            "MAD": "111",
            "AMD": "111",
            "DMA": "111",
            "DAM": "111",
        }

        jump_dict = {
            None: "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111",
        }

        def comp(line: str) -> str:
            """
            Returns the computation part of the line, using '=' and ';' as an indicators.
            """
            equal_operator = line.find("=")
            semicolon = line.find(";")

            if equal_operator != -1 and semicolon != -1:
                return instruction.split('=')[1].split(';')[0]

            elif equal_operator != -1:
                return instruction.split('=')[1]

            elif semicolon != -1:
                return instruction.split(';')[0]

        def dest(line: str) -> str:
            """
            Returns the destination part of the line, using '=' as an indicator.
            """
            if line.find("=") != -1:
                return line.split("=")[0]

        def jump(line: str) -> str:
            """
            Returns the jump part of the line, using ';' as an indicator.
            """
            if line.find(";") != -1:
                return line.split(";")[1]

        return "111" + comp_dict[comp(instruction)] + dest_dict[dest(instruction)] + jump_dict[jump(instruction)] + '\n'

    @staticmethod
    def a_parser(instruction: str) -> str:
        """
        Converts a type A instruction to it's 16-bit binary representation
        """
        return "{0:016b}".format(int(instruction[1:])) + '\n'
        # TODO: 15bit?

    @staticmethod
    def a_symbol_parser(instruction: str, symbol_table: SymbolTable) -> str:
        symbol = instruction[1:]
        if not symbol_table.contains(symbol):
            symbol_table.add_entry(symbol)
        return ParseHelper.a_parser('@' + str(symbol_table.get_address(symbol)))

    @staticmethod
    def l_symbol_parser(instruction: str, line_num: int, symbol_table: SymbolTable) -> None:
        symbol = instruction.split("(")[1].split(")")[0]
        if not symbol_table.contains(symbol):
            symbol_table.add_entry(symbol, line_num)


class Parser:
    def __init__(self, file, symbol_table: SymbolTable):
        """
        Creates a Parser instance that holds the main file, the current line and it's order number.
        """
        self.file = file
        self.symbol_table = symbol_table
        self.current_line_num = 0
        self.current_line = self.file.readline()

        self.first_pass_arr = []

    def first_pass(self) -> None:
        """
        In the first pass, the Parser iterate over the file to:
        1. clean each line (from white spaces, comments, indentations, etc...)
        2. storing the label's addresses in the symbol table, where label instruction is a form of (Xxx)
        """
        first_parse = []

        while self.has_more_lines():
            self.clean_line()
            if self.current_line == "":
                self.advance(count=False)
                continue

            elif self.instruction_type() == "L":
                ParseHelper.l_symbol_parser(self.current_line, self.current_line_num, self.symbol_table)
                self.advance(count=False)
                continue

            # Append cleaned lines for next parses
            first_parse.append(self.current_line)
            self.advance()

        # saving the cleaned line's array as an instance variable
        self.first_pass_arr = first_parse

    def second_pass(self) -> List[str]:
        """
        Returns an array of hack instructions, by parsing the cleaned lines array of the first pass.
        """
        binary_repr = []

        for line in self.first_pass_arr:

            if self.instruction_type(line) == "A" and re.search('[A-z]', line):
                binary_repr.append(ParseHelper.a_symbol_parser(line, self.symbol_table))

            elif self.instruction_type(line) == "A":
                binary_repr.append(ParseHelper.a_parser(line))

            elif self.instruction_type(line) == "C":
                binary_repr.append(ParseHelper.c_parser(line))

        return binary_repr

    def clean_line(self) -> None:
        """
        Cleans the current line from whitespaces, comments and empty lines.
        """
        # blank line
        if self.current_line == "":
            return
        self.current_line = self.current_line.rstrip()
        # clean line break at the end
        if self.current_line.endswith("\n"):
            self.current_line = self.current_line[:-1]

        # indentation handling
        self.current_line = self.current_line.lstrip()

        # ignore comments
        if self.current_line.startswith("//"):
            self.current_line = ""

        # comments in-line handling
        if self.current_line.find("//") != -1:
            self.current_line = self.current_line[:self.current_line.find("//")].rstrip()

    def instruction_type(self, line: str = None) -> str:
        """
        Returns the instruction type:
        A - @Xxx
        L - (Xxx)
        C - dest=comp;jump
        """
        if line:
            if line.startswith("@"):
                return "A"
            return "C"
        else:
            if self.current_line.startswith("("):
                return "L"
            elif self.current_line.startswith("@"):
                return "A"
            return "C"

    def has_more_lines(self) -> bool:
        return not self.current_line == ''

    def advance(self, count: bool = True) -> None:
        """
        Overrides the current line with the next line,
        and keeping track of the line number (not including empty cleaned lines & labels).
        """
        self.current_line = self.file.readline()
        if count:
            self.current_line_num += 1


# assume the given file is '.asm'
asm_file = open(sys.argv[1], "r")
parser = Parser(asm_file, SymbolTable())

parser.first_pass()
hack_commands = parser.second_pass()

hack_file = open(f"{asm_file.name.split('.')[0]}.hack", "w")
hack_file.writelines(hack_commands)

asm_file.close()
hack_file.close()
