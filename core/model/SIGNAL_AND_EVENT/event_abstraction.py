import copy

from pyparsing import Forward, Word, alphas, alphanums, nums, Literal, Group, Optional, Suppress, ZeroOrMore, oneOf, \
    infixNotation, opAssoc, ParseException, Regex





class EventAbstraction():
	def __init__(self,event_id,signal_manager):
		self.event_id=event_id
		self.rule=[]
		self.signal_manager=signal_manager


class EventAbstraction_manager():
	def __init__(self,signal_manager):
		self.events={}
		self.outputs={}
		self.TLSPN=None
		self.signal_manager=signal_manager
		self.update_TLSPN(self.TLSPN)
		self.event_signal_parser=EventSignalParser(self.signal_manager)

	def update_TLSPN(self,TLSPN):
		if TLSPN != None:
			self.TLSPN=TLSPN
			self.event_signal_parser.update_parsing_element()
			for event_id in self.events.keys():
				if event_id not in self.TLSPN.events.keys():
					del self.events[event_id]

			for event_id in TLSPN.events.keys():
				if event_id not in self.events.keys() and TLSPN.events[event_id].name != "λ":
					self.add_event_abstraction(event_id)


			for output_id in self.outputs.keys():
				if output_id not in self.TLSPN.outputs.keys():
					del self.outputs[output_id]

			for output_id in TLSPN.outputs.keys():
				if output_id not in self.outputs.keys() and TLSPN.outputs[output_id].name != ".":
					self.add_output_abstraction(output_id)

	def reset_TLSPN(self,TLSPN):
		self.events={}
		self.update_TLSPN(TLSPN)

	def add_event_abstraction(self,event_id):
		self.events[event_id]=EventAbstraction(event_id,self)

	def add_output_abstraction(self,output_id):
		self.outputs[output_id]=EventAbstraction(output_id,self)

	def load_event(self,dic):
		for event_id in dic["event"]["id"].keys():
			if int(event_id) in self.events.keys():
				self.events[int(event_id)].rule=dic["event"]["id"][event_id]["rule"]
		for output_id in dic["output"]["id"].keys():
			if int(output_id) in self.outputs.keys():
				self.outputs[int(output_id)].rule=dic["event"]["id"][output_id]["rule"]

	def save_event(self):
		dic={"event":{"id":{}},"output":{"id":{}}}
		for event_id in self.events.keys():
			dic["event"]["id"][event_id]={}
			dic["event"]["id"][event_id]["rule"]=self.events[event_id].rule
		for output_id in self.outputs.keys():
			dic["output"]["id"][output_id]={}
			dic["output"]["id"][output_id]["rule"]=self.outputs[output_id].rule
		return(dic)





class EventSignalParser():
	def __init__(self, signal_manager):
		self.signal_manager=signal_manager
		print(f"Debug: Initializing EventSignalParser with TLSPN events and signals: {self.signal_manager.signal_name_to_id.keys()}")
		self.update_parsing_element()

	def update_parsing_element(self):
		print("Debug: Updating parsing elements")
		self.signal_list=list(self.signal_manager.signals.values())
		self.signal_name_list = []
		for signal in self.signal_list:
			self.signal_name_list.append(signal.name)

		print(f"Debug: Available signal names: {self.signal_name_list}")

		self.lparen = Literal("(").suppress()
		self.rparen = Literal(")").suppress()

		self.operator_list = ["AND", "OR"]
		self.operator = oneOf(self.operator_list)

		self.symbol_list = ["==", "<=", ">=", "<", ">", "!="]
		self.symbol = oneOf(self.symbol_list)
		self.integer = Regex(r'[0-9][0-9]*')

		self.func_ind = oneOf(["R", "F"])
		self.signal_name = oneOf(self.signal_name_list)  # Function name or variable
		print(f"Debug: signal name parser set up with: {self.signal_name}")
		self.marking = Group(self.signal_name + self.symbol + self.integer)

		self.operand_with_function = Forward()
		self.operand_without_function = Forward()

		self.function = Forward()
		self.expr_without_function = Forward()
		self.expr_with_function = Forward()

		self.operand_with_function << self.function | self.marking | Group(
			self.lparen + self.operand_with_function + self.rparen) | self.operand_without_function
		self.operand_without_function << self.marking | Group(self.lparen + self.operand_without_function + self.rparen)

		self.arg_with_function = Group(
			self.operand_with_function | self.function | self.marking | self.operand_without_function)
		self.arg_without_function = Group(self.marking | self.operand_without_function | self.signal_name)

		self.function << (self.func_ind + self.lparen + self.expr_without_function + self.rparen)

		self.expr_without_function <<= infixNotation(self.arg_without_function, [(self.operator, 2, opAssoc.LEFT)])
		self.expr_with_function <<= infixNotation(self.function, [(self.operator, 2, opAssoc.LEFT)])


	def tryParsing(self, text_to_parse):
		self.update_parsing_element()
		try:
			print(f"Debug: Attempting to parse: {text_to_parse}")
			result = self.expr_with_function.parseString(text_to_parse)
			print(f"Debug: Initial parse successful: {result}")

			text_to_parse_without_space = text_to_parse.replace(" ", "")
			text_to_parse_without_space = text_to_parse_without_space.replace(")", "")
			text_to_parse_without_space = text_to_parse_without_space.replace("(", "")
			print(f"Debug: Cleaned input: {text_to_parse_without_space}")

			reconstructed_text = self.reformat_txt(result.asList())
			print(f"Debug: Reconstructed text: {reconstructed_text}")

			reconstructed_text_without_space = reconstructed_text.replace(" ", "")
			reconstructed_text_without_space = reconstructed_text_without_space.replace("(", "")
			reconstructed_text_without_space = reconstructed_text_without_space.replace(")", "")
			print(f"Debug: Cleaned reconstructed: {reconstructed_text_without_space}")

			if reconstructed_text_without_space == text_to_parse_without_space:
				print("Debug: Validation successful")
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

	def reformat_txt(self, parsed):
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
			elif len(parsed) % 2 == 1:
				txt = "(" + self.reformat_txt(parsed[0])
				k = 1
				while k < len(parsed) - 1:
					txt += " " + self.reformat_txt(parsed[k]) + " " + self.reformat_txt(parsed[k + 1])
					k += 2
				txt += ")"
				return (txt)
			else:
				raise ValueError(f"Unexpected structure in parsed result: {parsed}")
		else:
			print("error_type_list")
		return str(parsed)


	def reformat_id_txt(self, parsed):
		# If the parsed result is a single number, return it as a string
		if isinstance(parsed, str):
			if parsed in self.signal_name_list:
				name = parsed
				id = self.signal_manager.signal_name_to_id[name]
				return "S.{}".format(id)
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
			elif len(parsed) % 2 == 1:
				txt = "(" + self.reformat_id_txt(parsed[0])
				k = 1
				while k < len(parsed) - 1:
					txt += " " + self.reformat_id_txt(parsed[k]) + " " + self.reformat_id_txt(parsed[k + 1])
					k += 2
				txt += ")"
				return (txt)
			else:
				raise ValueError(f"Unexpected structure in parsed result: {parsed}")
		else:
			print("error_type_list")
		return str(parsed)


	def reformat_math_expression(self, parsed):
		# If the parsed result is a single number, return it as a string
		if isinstance(parsed, str):
			if parsed in self.signal_name_list:
				name = parsed
				id = self.signal_manager.signal_name_to_id[name]
				return "S.{}".format(id)
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
					if operator == "AND":
						return f"({left} and {right})"
					elif operator == "OR":
						return f"({left} or {right})"
			elif len(parsed) % 2 == 1:
				txt = "(" + self.reformat_math_expression(parsed[0])
				k = 1
				while k < len(parsed) - 1:
					txt += " " + self.reformat_math_expression(parsed[k]) + " " + self.reformat_math_expression(
						parsed[k + 1])
					k += 2
				txt += ")"
				return (txt)
			else:
				raise ValueError(f"Unexpected structure in parsed result: {parsed}")
		else:
			print("error_type_list")
		return str(parsed)


	def check_signal_name_used(self, parsed):
		name_used = []
		# If the parsed result is a single number, return it as a string
		if isinstance(parsed, str):
			if parsed not in self.signal_name_list:
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


	def check_validity(self, text_to_parse):
		"""Check if the expression is valid."""
		print(f"Debug: Checking validity of expression: {text_to_parse}")
		result = self.tryParsing(text_to_parse)

		print(f"Debug: Parsing result: {result[0]}")
		if result[0] == True:
			print("chek1")
			text_to_parse_compare = text_to_parse.replace(" ", "")
			text_to_parse_compare = text_to_parse_compare.replace("(", "")
			text_to_parse_compare = text_to_parse_compare.replace(")", "")

			result_compare = self.reformat_txt(result[1].asList())

			result_compare = result_compare.replace(" ", "")
			result_compare = result_compare.replace("(", "")
			result_compare = result_compare.replace(")", "")

			if result_compare == text_to_parse_compare:
				if self.check_signal_name_used(result[1].asList()):
					return True
				else:
					return False
			else:
				return False

		else:
			return False


	def convert_to_id(self, text_to_parse):
		result = self.tryParsing(text_to_parse)
		return self.reformat_id_txt(result[1].asList())


	def convert_list_into_ID(self,mylist):
		for k in range(len(mylist)):
			if isinstance(mylist[k],list):
				self.convert_list_into_ID(mylist[k])
			else:
				if mylist[k] in self.signal_manager.signal_name_to_id.keys():
					mylist[k]=f"S.{self.signal_manager.signal_name_to_id[mylist[k]]}"

	def convert_list_into_name(self,mylist):
		for k in range(len(mylist)):
			if isinstance(mylist[k],list):
				self.convert_list_into_name(mylist[k])
			else:
				if mylist[k][:2]=="S.":
					print("HERE")
					print(mylist[k][:2])
					print(self.signal_manager.signals)
					print(int(mylist[k][2:]))
					if int(mylist[k][2:]) in self.signal_manager.signals.keys():
						mylist[k]=self.signal_manager.signals[int(mylist[k][2:])].name

	def parse_to_id(self, text_to_parse):
		result = self.tryParsing(text_to_parse)
		result=result[1].asList()
		self.convert_list_into_ID(result)
		return(result)


	def convert_parsed_id_to_parse_name(self, parsed_id):
		self.convert_list_into_name(parsed_id)
		return(parsed_id)

	def convert_parsed_id_into_txt_name(self,parsed_id):
		parsed_id2=copy.deepcopy(parsed_id)
		self.convert_list_into_name(parsed_id2)
		print("converted: ",parsed_id2)
		return(self.reformat_txt(parsed_id2))
