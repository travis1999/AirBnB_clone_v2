#!/usr/bin/python3
"""command line parser"""
import re
from typing import Dict, Callable, List, Union, Any
from dataclasses import dataclass
from enum import Enum
from cmd import Cmd as BaseCmd


@dataclass
class Token:
    """Token class"""
    type: str
    value: str

    def __str__(self):
        return f"{self.type}: {self.value}"


@dataclass
class Cmd:
    """cmd class"""
    function: Callable
    args: List


class RULE(Enum):
    """Rule Enums"""
    RECURSIVE = 'RECURSIVE'
    SINGLE = 'SINGLE'
    MANY = 'MANY'


def create_match_func(_type: str, match_actions: dict = None) -> Callable:
    """creates a match function that is called when a rule is matched"""
    def match(scanner, matched):
        """match function"""
        if match_actions and _type in match_actions:
            return Token(_type, match_actions[_type](matched))
        return Token(_type, matched)
    return match


def build_scanner(patterns: Dict[str, str],
                  match_actions: dict = None) -> Scanner:
    """builds a Scanner from a dict"""
    new_patterns = [
        (value, create_match_func(key, match_actions))
        for key, value in patterns.items()
    ]
    return re.Scanner(new_patterns)


def create_args(args, match_actions: dict = None) -> List[Rule]:
    """creates args for te inbuilt scanner"""
    pats = {
        RULE.RECURSIVE: r"r<([a-zA-Z_|][a-zA-Z0-9_|]*\s*?)+>",
        RULE.MANY: r"m\|([a-zA-Z_][a-zA-Z0-9_]*\s*?)+\|",
        RULE.SINGLE: r"[a-zA-Z_][a-zA-Z0-9_]*",
        "ignore": r"\s+"
    }

    scan = build_scanner(pats, match_actions)
    scanned, rem = scan.scan(args)
    args = []

    for tok in scanned:
        if tok.type == RULE.RECURSIVE:
            args.append(Rule(RULE.RECURSIVE, tok.value))
        elif tok.type == RULE.SINGLE:
            args.append(Rule(RULE.SINGLE, tok.value))
        elif tok.type == RULE.MANY:
            args.append(Rule(RULE.MANY, tok.value))
        elif tok.type != "ignore":
            raise Exception("Invalid token type")

    return args


class Rule:
    """Class that defines rules"""

    def __init__(self, rule_type: RULE, pattern: str) -> None:
        """init"""
        self.rule = self.build_rule(rule_type, pattern)
        self.rule_type = rule_type

    def build_rule(self, rule_type: RULE, pattern: str) -> None:
        """builds the correct rule"""
        if rule_type == RULE.RECURSIVE:
            return create_args(pattern[2:-1])

        elif rule_type == RULE.SINGLE:
            return pattern

        elif rule_type == RULE.MANY:
            return pattern[2:-1]

        else:
            raise Exception("Invalid rule type")

    def rule_info(self):
        """gets the rule info"""
        if self.rule_type == RULE.RECURSIVE:
            return f"One or more of <{', '.join(x.rule_info() for x in self.rule)}>"
        elif self.rule_type == RULE.SINGLE:
            return self.rule
        elif self.rule_type == RULE.MANY:
            return f"Any of <{', '.join(self.rule.split())}>"
        else:
            raise Exception("Invalid rule type")

    def match_tokens(self, start: int,
                     tokens: List[Token]) -> Union[int, Token]:
        """returns a matched token"""
        if self.rule_type == RULE.RECURSIVE:
            return self.recursive(start, tokens)
        elif self.rule_type == RULE.SINGLE:
            return self.single(start, tokens)
        elif self.rule_type == RULE.MANY:
            return self.match_many(start, tokens)
        else:
            raise Exception("Invalid rule type")

    def recursive(self, start, tokens) -> Union[int, List[Token]]:
        """for recursive rule"""
        rule_l = self.rule.split() if isinstance(self.rule, str) else self.rule
        matched = []

        while (start + len(rule_l) <= len(tokens)):
            count, match = self.match_list(
                tokens[start:start + len(rule_l)], rule_l)
            if count is None:
                break
            matched.append(match)
            start += count

        return start, matched

    def match_list(self, match_list: List, rule_list: List) -> bool:
        """match list"""
        if len(match_list) != len(rule_list):
            return None, None

        return len(rule_list), self.match_func_tokens(match_list, rule_list)

    def match_many(self, start: int,
                   tokens: List[Token]) -> Union[int, List[Token]]:
        """maatch many"""
        tok = tokens[start]
        rules = self.rule.split()

        for rule in rules:
            if tok.type == rule:
                return 1, tok.value
        return None, None

    def single(self, start, tokens) -> Union[int, Token]:
        """matches single"""
        if tokens[start].type == self.rule:
            return 1, tokens[start].value
        return None, None

    @staticmethod
    def match_func_tokens(tokens: List[Token], rules: List[RULE]) -> List[Any]:
        """match function"""
        start = 0
        matched = []

        for rule in rules:
            move, res = rule.match_tokens(start, tokens)

            if not move:
                raise Exception("Invalid token")

            start += move
            matched.append(res)

        return matched

    def __str__(self):
        """str repr"""
        return f"{self.rule_type}: {self.rule}"


class Cmdmaker:
    """cmdmaker class"""

    def __init__(self, patterns):
        """initializer"""
        self.funcs: Dict[str, Callable] = {}
        self.on_match = {}
        self.scanner = build_scanner(patterns, self.on_match)

    def scan_str(self, string):
        """scans string for tokens"""
        tokens, remainder = self.scanner.scan(string)
        if remainder:
            offset = len(string) - len(remainder)
            print(f"Scan error at pos {offset}")
            print(string)
            print(" " * offset + "^")
        return [token for token in tokens if token.type != 'ignore']

    def cmd_loop(self):
        """for testing"""
        while ((read := input(">> ")) not in ["q", "quit", "exit"]):
            try:
                res = read.split(" ", 1)

                if len(res) == 1:
                    self.command_str(res[0], "")
                else:
                    self.command_str(*res)
            except Exception as e:
                print(e)

    def print_help(self, func, cmd):
        """prints help for te command"""
        func_args = func.function.__code__.co_varnames
        cmds = func.args
        usage_strs = [
            f'{arg}: {usage.rule_info()}' for arg,
            usage in zip(
                func_args,
                cmds)]

        print(f"{cmd}:\n    {func.function.__doc__}\n")
        for usage_str in usage_strs:
            print("  " + usage_str)

    def command_str(self, cmd, string):
        """main parsing"""
        if cmd not in self.funcs:
            raise Exception(
                f"Command not found: {cmd}, available commands are {', '.join(self.funcs.keys())}")

        try:
            func = self.funcs[cmd]
            tokens = self.scan_str(string)
            args = Rule.match_func_tokens(tokens, func.args)

            func_args = func.function.__code__.co_varnames[:
                                                           func.function.__code__.co_argcount]
            if len(func_args) != len(args):
                self.print_help(self.funcs[cmd], cmd)
                return

            return self.funcs[cmd].function(*args)

        except Exception as e:
            self.print_help(self.funcs[cmd], cmd)

    def run_cmd(self, cmd_string: str):
        """runnef function after succesful parsing"""
        res = cmd_string.split(" ", 1)
        try:
            if len(res) == 1:
                self.command_str(res[0], "")
            else:
                self.command_str(*res)
        except Exception as e:
            print(e)

    def cmd(self, args):
        """wrapper for  the rules"""
        def cmd_inner(func):
            self.funcs[func.__name__] = Cmd(func, create_args(args))

            def func_inner(*args, **kwargs):
                func(*args, **kwargs)
            return func_inner
        return cmd_inner

    def infect(self, _class):
        """used to add funtionality to the cmd.Cmd class"""
        for _, cmd in self.funcs.items():
            def do_cmd(me, arg):
                arg = f"{cmd.function.__name__} {arg}"
                return self.run_cmd(arg)
            do_cmd.__name__ = f"do_{cmd.function.__name__}"
            do_cmd.__doc__ = cmd.function.__doc__
            setattr(_class, do_cmd.__name__, do_cmd)
        return _class

    def match(self, func):
        """Wrapper for function used after matching a token"""
        self.on_match[func.__name__] = func

        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner
