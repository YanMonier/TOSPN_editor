from z3 import *
import itertools
import math

class LSPNTA():
	def __init__(self):
		self.transitionDic={}
		self.placeDic={}
		self.placeNameDic={}
		self.arcDic={}
		self.inputLabelDic={}
		self.outputLabelDic={}

		self.input_label_name_dic={}
		self.output_label_name_dic={}


		self.place_id=0
		self.transition_id = 0
		self.arc_id = 0
		self.event_id = 0
		self.output_id = 0


		self.add_Label("λ")




		self.label_to_logic_transition={}
		self.label_to_must_transition={}

		self.markingDic={}
		self.lastMarkingDic={}

	def add_Place(self,init_dic=None):
		newPlace=Place(self,init_dic)
		id=newPlace.id

		if id in self.placeDic.keys():
			raise Exception ("trying to create a place with id {} already used".format(id))
		else:
			self.placeDic[id]=newPlace
			self.placeNameDic[newPlace.name]=newPlace
			self.markingDic[newPlace.id]=newPlace.token_number
			self.lastMarkingDic[newPlace.id]=newPlace.token_number
		return(newPlace)

	def add_Transition(self,init_dic=None):
		newTransition = Transition(self,init_dic)
		id = newTransition.id

		if id in self.transitionDic.keys():
			raise Exception("trying to create a transition with id {} already used".format(id))
		else:
			self.transitionDic[id] = newTransition
		return (newTransition)

	def add_Arc(self,element1,element2,weight,timing_interval=[0,"inf"]):
		newArc = Arc(element1,element2,weight,timing_interval,self)
		id = newArc.id

		if id in self.arcDic.keys():
			raise Exception("trying to create a arc with id {} already used".format(id))
		else:
			self.arcDic[id] = newArc
		return (newArc)


	def add_Label(self,name,init_dic={"type":None}):
		newLabel = Label(name,self,init_dic)
		id = newLabel.id

		if newLabel.type == "output":
			if id in self.outputLabelDic.keys():
				raise Exception("trying to create an output label {} with id {} already used".format(newLabel.name, id))
			else:
				self.outputLabelDic[id] = newLabel
		elif newLabel.type == "input":
			if id in self.inputLabelDic.keys():
				raise Exception("trying to create an input label {} with id {} already used".format(newLabel.name, id))
			else:
				self.inputLabelDic[id] = newLabel

		if id in self.labelDic.keys():
			raise Exception("trying to create a label {} with id {} already used".format(newLabel.name,id))
		else:
			self.LabelDic[id] = newLabel

		return (newLabel)



class Label():
	label_id=0
	def __init__(self, 	name, LSPNTA, init_dic):
		if name not in self.LSPNTA.output_label_name_dic.keys() and name not in self.LSPNTA.output_label_name_dic.keys():
			self.LSPNTA = LSPNTA
			self.name = name
			self.type = init_dic["type"] #"input" or "output"
			self.id=Label.label_id
			Label.label_id+=1
			if self.type =="output":
				self.LSPNTA.output_label_name_dic[name]=self
				self.LSPNTA.outputLabelDic[self.id]=self
			elif self.type =="input":
				self.LSPNTA.input_label_name_dic[name]=self
				self.LSPNTA.inputLabelDic[self.id] = self
			else:
				raise Exception("type other than input or output")


		else:
			raise Exception("trying to create a label qith existing name {} already used".format(name))


	def update_label(self, new_name):
		if new_name not in self.LSPNTA.output_label_name_dic.keys() and new_name not in self.LSPNTA.output_label_name_dic.keys():
			if self.type == "output":
				del self.LSPNTA.output_label_name_dic[self.name]
				self.LSPNTA.output_label_name_dic[new_name]=self
			elif self.type == "input":
				del self.LSPNTA.input_label_name_dic[self.name]
				self.LSPNTA.input_label_name_dic[new_name] = self
			self.name = new_name

	def remove(self):
		if self.type == "output":
			del self.LSPNTA.output_label_name_dic[self.name]
			del self.LSPNTA.outputLabelDic[self.id]
		elif self.type == "input":
			del self.LSPNTA.input_label_name_dic[self.name]
			del self.LSPNTA.inputLabelDic[self.id]
		del self.LSPNTA.LabelDic[self.id]


class Place():
	place_id=0
	def __init__(self,LSPNTA,init_dic):
		self.LSPNTA = LSPNTA
		self.type="place"
		if init_dic==None:
			self.id=Place.place_id
			Place.place_id += 1

			test_name="P.{}".format(self.id)
			if test_name in self.LSPNTA.placeNameDic.keys():
				k=2
				new_test_name=test_name +".{}".format(k)
				while new_test_name in self.LSPNTA.placeNameDic.keys():
					k+=1
					new_test_name = test_name + ".{}".format(k)
				test_name=new_test_name
			self.name=test_name
			self.init_token_number = 0
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.init_token_number = init_dic["token"]

		self.previous_arc_list=[]
		self.next_arc_list=[]
		self.token_dic={}

		self.graphic_place=None


	def change_name(self,new_name):
		del self.LSPNTA.placeNameDic[self.name]
		self.name=new_name
		self.LSPNTA.placeNameDic[self.name]=self

	def remove(self):
		del self.LSPNTA.placeNameDic[self.name]
		del self.LSPNTA.placeDic[self.id]
		del self.LSPNTA.markingDic[self.id]
		del self.LSPNTA.lastMarkingDic[self.id]

	def change_token_number(self,new_number):
		self.token_number=new_number
		self.LSPNTA.markingDic[self.id]=self.token_number

	def add_token(self,token):
		self.token_dic[token.id]=token

	def remove_token(self,token_id):
		del self.token_dic[token_id]


class Transition():
	transition_id=0
	def __init__(self,LSPNTA,init_dic):
		self.type="transition"
		self.LSPNTA = LSPNTA

		if init_dic==None:
			self.id=Transition.transition_id
			Transition.transition_id += 1
			self.name = "T.{}".format(self.id)
			self.label = LSPNTA.labelDic[0]
			self.label.transition_dic[self.id] = self
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.label = LSPNTA.labelDic[init_dic["label_id"]]
			self.logic_type=init_dic["logic_type"] #"must" or "logic", only one must transition can fire per label observed, and has to fire, it's the update of the value, the logic transition are just here to update internal state of the system
			self.label.transition_dic[self.id] = self




		self.previous_arc_list=[]
		self.next_arc_list=[]



		self.graphic_transition = None

	def remove(self):
		del self.LSPNTA.transitionDic[self.id]

	def change_event(self,new_event):
		del self.event.transition_dic[self.id]
		self.event=new_event
		self.event.transition_dic[self.id]=self

class Arc():
	arc_id = 0
	def __init__(self,element1,element2,weight,timing_interval,LSPNTA):
		self.type="Arc"
		self.LSPNTA=LSPNTA
		self.id = Arc.arc_id
		Arc.arc_id += 1
		self.previous_element = element1
		self.next_element = element2
		self.previous_element.next_arc_list.append(self)
		self.next_element.previous_arc_list.append(self)
		self.weight=weight
		self.timing_interval=timing_interval
		self.graphic_arc = None

	def remove(self):
		self.previous_element.next_arc_list.remove(self)
		self.next_element.previous_arc_list.remove(self)
		del self.LSPNTA.arcDic[self.id]

class Token():
	token_id = 0
	def __init__(self,source_fired_transition,creation_time,time_interval,place_id):
		self.id=Token.token_id
		Token.token_id+=1
		self.creation_time=creation_time
		self.time_interval=time_interval
		self.place=place_id

		self.source_fired_transition = source_fired_transition
		self.existance=Bools('tk{}'.format(self.id))
		self.has_to_exist=False

		self.in_place=Bools('tk{}_p'.format(self.id))
		self.possible_fired_transition=[]
		self.surely_fired_transition=None

	def give_all_possible_fired_transition_before_time(self,time):
		result=[]
		for possible_fired_transition in self.possible_fired_transition:
			if possible_fired_transition.firing_time<=time:
				result.append(possible_fired_transition)
		return(result)


class Fired_transition():
	fired_transition_id=0
	def __init__(self,transition,firing_time,marking):
		self.id=Fired_transition.fired_transition_id
		Fired_transition.fired_transition_id+=1

		self.LSPNTA=transition.LSPNTA
		self.transition=transition
		self.firing_time=firing_time
		self.marking=marking

		self.existance=Bools('tr{}'.format(self.id))
		self.has_to_exist=1 #0 can't exist, 1 we don't know, 2 must exist


		#select possible token for firing the transition
		self.bool_token_used_per_places={}
		self.token_possible_per_places_set={}
		self.token_number_per_places={}


		for arc in self.transition.previous_arc_list:
			place_id=arc.previous_element.id

			self.bool_token_used_per_places[place_id]={}
			self.token_possible_per_places_set[place_id] = set()
			self.token_number_per_places[place_id]=arc.weight


			for token in self.marking.token_per_place[place_id]:
				token_max_time=token.creation_time+token.time_interval[1]
				token_min_time=token.creation_time+token.time_interval[0]
				if firing_time <= token_max_time and firing_time >= token_min_time:
					self.bool_token_used_per_places[place_id][token.id]=Bools(f'tr{self.id}_tk{token.id}')
					self.token_possible_per_places_set[place_id].add(token)
					token.possible_fired_transition.append(self)

		#Create output token from the firing of the transition
		self.output_token={}
		for arc in self.transition.next_arc_list:
			place=arc.next_element
			for k in range(arc.weight):
				new_token=Token(self,self.firing_time,arc.timing_interval)
				self.output_token[new_token.id]=new_token
				self.marking.add_token(new_token,place)


		#generate all possible combinations of tokens that can be used to explain the firing of the transition.
		self.token_used_possibilities=self.generate_combinations(self.token_possible_per_places_set, self.token_number_per_places)
		self.token_used_possibilities_per_token={}
		for place_id in self.token_possible_per_places_set.keys():
			for token_id in self.token_possible_per_places_set[place_id].keys():
				self.token_used_possibilities_per_token[token_id]=[]
		for combination in self.token_used_possibilities:
			for place_id in combination.keys():
				for token_id in combination[place_id]:
					self.token_used_possibilities_per_token[token_id].append(combination)



	def generate_combinations(self,data, selection_counts):
		# For each key, get all possible combinations of the specified size
		per_key_combinations = {
			key:list(itertools.combinations(data[key], selection_counts[key]))
			for key in data
		}
		# Use product to get the Cartesian product of all these choices
		all_combinations = list(itertools.product(*per_key_combinations.values()))

		# Format the result into a list of dicts if needed
		formatted_results = set()
		keys = list(per_key_combinations.keys())
		for combo in all_combinations:
			formatted_results.add({k:v for k, v in zip(keys, combo)})

		return formatted_results


	def propagate_remove_token(self,token):
		place_id=token.place.id
		del self.token_possible_per_places[place_id][token.id]
		self.token_possible_per_places_set[place_id].remove(token.id)

		for combination in self.token_used_possibilities_per_token[token.id].copy():
			self.token_used_possibilities.remove(combination)
			for place_id in combination.keys():
				for token_id in combination[place_id]:
					self.token_used_possibilities_per_token[token_id].remove(combination)


	def check_enought_existing_token(self):
		for place_id in self.token_possible_per_places_set.keys():
			if len(list(self.token_possible_per_places_set[place_id].keys())) < self.token_number_per_places[place_id]:
				return(False)
		return(True)




class Marking():
	def __init__(self,LSPNTA):
		self.LSPNTA = LSPNTA
		self.token_per_place={}

	def get_place(self,place_id):
		return(LSPNTA.placeDic[place_id])
	def get_transition(self,transition_id):
		return(LSPNTA.transitionDic[transition_id])

	def set_init_marking(self,time):
		token_created=set()
		for place_id in self.LSPNTA.placeDic.keys():
			self.token_per_place[place_id]=set()
			for k in range(self.LSPNTA.placeDic[place_id].init_token_number):
				new_token=Token("init",time,[0,math.inf],place_id)
				self.token_per_place[place_id].add(new_token)
				token_created.add(new_token)
		return(token_created)

	def check_enought_existing_token_on_transition(self,transition_id):
		transition=self.LSPNTA.transitionDic[transition_id]
		for arc in transition.previous_arc_list:
			place_id = arc.previous_element.id
			if len(token_per_place[place_id]) < arc.weight:
				return(False)
		return(True)





class Observer():
	def __init__(self,LSPNTA):
		self.LSPNTA=LSPNTA

		self.marking=Marking(self.LSPNTA)
		self.marking.set_init_marking()

		self.possible_fired_transition=set()

	def label_to_firable_transition(self, label_list):
		firable_transition=set()
		for label in label_list:
			for transition in self.LSPNTA.label_to_transition[label]:
				if self.marking.check_enought_existing_token_on_transition(transition.id):
					firable_transition.add(transition.id)
		return(firable_transition)

	def create_fired_transition(self,transition_id_set,time):
		possible_fired_transition_to_test={}
		for transition_id in transition_id_set:
			new_fired_transition=Fired_transition(self.LSPNTA.transitionDic[transition_id],time,self.marking)
			self.possible_fired_transition.add(Fired_transition(self.LSPNTA.transitionDic[transition_id],time,self.marking))
			possible_fired_transition_to_test[transition_id]=








