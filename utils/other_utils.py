from pyparsing import Forward, Word, alphas, alphanums, nums, Literal, Group, Optional, Suppress, ZeroOrMore, oneOf, \
    infixNotation, opAssoc, ParseException, Regex


class OutputParser():
    def __init__(self,TOSPN):
        self.TOSPN=TOSPN
        self.update_parsing_element()

    def update_parsing_element(self):
        self.name_list=self.TOSPN.placeNameDic.keys()
        self.lparen = Literal("(").suppress()
        self.rparen = Literal(")").suppress()


        self.operator_list=["AND", "OR"]
        self.operator = oneOf(self.operator_list)

        self.symbol_list=["==", "<=", ">=", "<", ">", "!="]
        self.symbol = oneOf(self.symbol_list)
        self.integer = Regex(r'[0-9][0-9]*')

        self.func_ind = oneOf(["FM", "FD"])
        self.place_name = oneOf(self.name_list)  # Function name or variable
        self.marking = Group(self.place_name + self.symbol + self.integer)

        self.operand_with_function = Forward()
        self.operand_without_function = Forward()

        self.function = Forward()
        self.expr_without_function = Forward()
        self.expr_with_function = Forward()

        self.operand_with_function << self.function | self.marking | Group(self.lparen + self.operand_with_function + self.rparen) | self.operand_without_function
        self. operand_without_function << self.marking | Group(self.lparen + self.operand_without_function + self.rparen)

        self.arg_with_function = Group(self.operand_with_function | self.function | self.marking | self.operand_without_function)
        self.arg_without_function = Group(self.marking | self.operand_without_function)

        self.function << (self.func_ind + self.lparen + self.place_name + self.rparen)

        self.expr_without_function <<= infixNotation(self.arg_without_function, [(self.operator, 2, opAssoc.LEFT)])
        self.expr_with_function <<= infixNotation(self.arg_with_function, [(self.operator, 2, opAssoc.LEFT)])

    def tryParsing(self, text_to_parse):
        try:
            result = self.expr_with_function.parseString(text_to_parse)

            text_to_parse_without_space=text_to_parse.replace(" ","")

            text_to_parse_without_space=text_to_parse_without_space.replace(")", "")
            text_to_parse_without_space = text_to_parse_without_space.replace("(", "")

            reconstructed_text=self.reformat_txt(result.asList())

            reconstructed_text_without_space=reconstructed_text.replace(" ","")
            reconstructed_text_without_space = reconstructed_text_without_space.replace("(", "")
            reconstructed_text_without_space = reconstructed_text_without_space.replace(")", "")

            if reconstructed_text_without_space==text_to_parse_without_space:
                return (True, result)
            else:
                print(text_to_parse_without_space)
                print(reconstructed_text_without_space)
                RED = '\033[31m'
                RESET = '\033[0m'
                print(f"{RED}error parsing whole txt{RESET}")
                return (False, result)
        except ParseException as pe:
            return (False, pe)

    def reformat_txt(self,parsed):
        # If the parsed result is a single number, return it as a string
        if isinstance(parsed, str):
            return parsed
        elif isinstance(parsed, list):
            # Handle cases where it's a list of components
            if len(parsed) == 1:
                return self.reformat_txt(parsed[0])  # Simple case: just return the inner value
            elif len(parsed) == 2:
                left = parsed[0]
                right = self.reformat_txt(parsed[1])
                return f"{left}({right})"
            elif len(parsed) == 3:
                operator = parsed[1]
                if operator in self.symbol_list:
                    left = self.reformat_txt(parsed[0])
                    right = self.reformat_txt(parsed[2])
                    return f"{left}{operator}{right}"
                else:
                    left = self.reformat_txt(parsed[0])
                    right = self.reformat_txt(parsed[2])
                    return f"({left} {operator} {right})"
            elif len(parsed)%2==1:
                txt="("+self.reformat_txt(parsed[0])
                k = 1
                while k < len(parsed)-1:
                    txt+=" "+self.reformat_txt(parsed[k])+" "+self.reformat_txt(parsed[k+1])
                    k+=2
                txt+=")"
                return(txt)
            else:
                raise ValueError(f"Unexpected structure in parsed result: {parsed}")
        else:
            print("error_type_list")
        return str(parsed)

    def reformat_id_txt(self,parsed):
        # If the parsed result is a single number, return it as a string
        if isinstance(parsed, str):
            if parsed in self.name_list:
                name = parsed
                id = self.TOSPN.placeNameDic[name].id
                return "P.{}".format(id)
            else:
                return parsed
        elif isinstance(parsed, list):
            # Handle cases where it's a list of components
            if len(parsed) == 1:
                return self.reformat_id_txt(parsed[0])  # Simple case: just return the inner value
            elif len(parsed) == 2:
                left = parsed[0]
                right = self.reformat_id_txt(parsed[1])
                return f"{left}({right})"
            elif len(parsed) == 3:
                operator = parsed[1]
                if operator in self.symbol_list:
                    left = self.reformat_id_txt(parsed[0])
                    right = self.reformat_id_txt(parsed[2])
                    return f"{left}{operator}{right}"
                else:
                    left = self.reformat_id_txt(parsed[0])
                    right = self.reformat_id_txt(parsed[2])
                    return f"({left} {operator} {right})"
            elif len(parsed)%2==1:
                txt="("+self.reformat_id_txt(parsed[0])
                k = 1
                while k < len(parsed)-1:
                    txt+=" "+self.reformat_id_txt(parsed[k])+" "+self.reformat_id_txt(parsed[k+1])
                    k+=2
                txt+=")"
                return(txt)
            else:
                raise ValueError(f"Unexpected structure in parsed result: {parsed}")
        else:
            print("error_type_list")
        return str(parsed)

    def reformat_math_expression(self, parsed):
        # If the parsed result is a single number, return it as a string
        if isinstance(parsed, str):
            if parsed  in self.name_list:
                name=parsed
                id=self.TOSPN.placeNameDic[name].id
                return "P.{}".format(id)
            else:
                return parsed
        elif isinstance(parsed, list):
            # Handle cases where it's a list of components
            if len(parsed) == 1:
                return self.reformat_math_expression(parsed[0])  # Simple case: just return the inner value
            elif len(parsed) == 2:
                left = parsed[0]
                right = self.reformat_math_expression(parsed[1])
                return f"self.{left}(last_marking,new_marking,str({right}))"
            elif len(parsed) == 3:
                operator = parsed[1]
                if operator in self.symbol_list:
                    left = self.reformat_math_expression(parsed[0])
                    right = self.reformat_math_expression(parsed[2])
                    return f"{left}{operator}{right}"
                else:
                    left = self.reformat_math_expression(parsed[0])
                    right = self.reformat_math_expression(parsed[2])
                    if operator=="AND":
                        return f"({left} and {right})"
                    elif operator=="OR":
                        return f"({left} or {right})"
            elif len(parsed) % 2 == 1:
                txt = "(" + self.reformat_math_expression(parsed[0])
                k = 1
                while k < len(parsed) - 1:
                    txt += " " + self.reformat_math_expression(parsed[k]) + " " + self.reformat_math_expression(parsed[k + 1])
                    k += 2
                txt += ")"
                return (txt)
            else:
                raise ValueError(f"Unexpected structure in parsed result: {parsed}")
        else:
            print("error_type_list")
        return str(parsed)

    def check_place_name_used(self,parsed):
        name_used=[]
        # If the parsed result is a single number, return it as a string
        if isinstance(parsed, str):
            if parsed not in self.name_list:
                return False

        elif isinstance(parsed, list):
            # Handle cases where it's a list of components
            if len(parsed) == 1:
                return self.reformat_math_expression(parsed[0])  # Simple case: just return the inner value
            elif len(parsed) == 2:
                left = parsed[0]
                right = self.reformat_math_expression(parsed[1])
                return True
            elif len(parsed) == 3:
                operator = parsed[1]
                if operator in self.symbol_list:
                    left = self.reformat_math_expression(parsed[0])
                else:
                    left = self.reformat_math_expression(parsed[0])
                    right = self.reformat_math_expression(parsed[2])

            elif len(parsed) % 2 == 1:
                txt = "(" + self.reformat_math_expression(parsed[0])
                k = 1
                while k < len(parsed) - 1:
                    txt += " " + self.reformat_math_expression(parsed[k]) + " " + self.reformat_math_expression(
                        parsed[k + 1])
                    k += 2
            else:
                raise ValueError(f"Unexpected structure in parsed result: {parsed}")
        else:
            print("error_type_list")
        return True

    def check_validity(self,text_to_parse):
        result = self.tryParsing(text_to_parse)
        if result[0] == True:
            print("chek1")
            text_to_parse_compare=text_to_parse.replace(" ","")
            text_to_parse_compare = text_to_parse_compare.replace("(", "")
            text_to_parse_compare = text_to_parse_compare.replace(")", "")

            result_compare=self.reformat_txt(result[1].asList())

            result_compare= result_compare.replace(" ","")
            result_compare = result_compare.replace("(", "")
            result_compare = result_compare.replace(")", "")

            if result_compare == text_to_parse_compare:
                if self.check_place_name_used(result[1].asList()):
                    return True
                else:
                    return False
            else:
                return False

        else:
            return False

    def convert_to_id(self,text_to_parse):
        result=self.tryParsing(text_to_parse)
        return self.reformat_id_txt(result[1].asList())