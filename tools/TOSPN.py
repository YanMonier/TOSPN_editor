class TOSPN():
	def __init__(self):
		self.transitionDic={}
		self.placeDic={}
		self.placeNameDic={}
		self.arcDic={}
		self.eventDic={}
		self.outputDic={}
		self.event_name_list=[]


		self.place_id=0
		self.transition_id = 0
		self.arc_id = 0
		self.event_id = 0
		self.output_id = 0


		self.add_Event("λ")

		self.output_name_list=[]

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

	def add_Arc(self,element1,element2):
		newArc = Arc(element1,element2,self)
		id = newArc.id

		if id in self.arcDic.keys():
			raise Exception("trying to create a arc with id {} already used".format(id))
		else:
			self.arcDic[id] = newArc
		return (newArc)


	def add_Event(self,name,init_dic=None):
		newEvent = Event(name,self,init_dic)
		id = newEvent.id

		if id in self.eventDic.keys():
			raise Exception("trying to create an event {} with id {} already used".format(newEvent.name,id))
		else:
			self.eventDic[id] = newEvent
		return (newEvent)

	def add_Output(self,name,math_expression, txt_expression,init_dic=None):
		newOutput = Output(name,math_expression, txt_expression,self,init_dic)
		id = newOutput.id

		if id in self.outputDic.keys():
			raise Exception("trying to create an event with id {} already used".format(id))
		else:
			self.outputDic[id] = newOutput
		return (newOutput)


class Output():
	output_id=0
	def __init__(self, name,math_expression, txt_expression ,TOSPN, init_dic):
		print("new_output",txt_expression )
		self.TOSPN = TOSPN

		if init_dic==None:
			self.id = Output.output_id
			Output.output_id += 1
			self.name = name
			self.TOSPN.output_name_list.append(self.name)
			self.math_marking_expression=math_expression
			self.txt_marking_expression=txt_expression
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.TOSPN.output_name_list.append(self.name)
			self.math_marking_expression = init_dic["math_expression"]
			self.txt_marking_expression = init_dic["txt_expression"]

	def retrieve_marking_name_expression(self):
		converted_marking_expression = self.txt_marking_expression
		print("marking_txt_expression",self.txt_marking_expression)
		for id in self.TOSPN.placeDic.keys():
			converted_marking_expression = converted_marking_expression.replace("P.{}".format(id), str(self.TOSPN.placeDic[id].name))
		converted_marking_expression = converted_marking_expression.replace("and".format(id),str("AND"))
		converted_marking_expression = converted_marking_expression.replace("or".format(id),str("OR"))
		return(converted_marking_expression)

	def evaluate_marking_expression(self):
		last_marking=self.TOSPN.lastMarkingDic
		new_marking=self.TOSPN.markingDic
		converted_marking_expression = self.marking_expression
		for id in marking_dic.keys():
			converted_marking_expression = converted_marking_expression.replace("P.{}".format(id), str(marking_dic[id]))

		return eval(converted_marking_expression)


	def FD(self,last_marking,new_marking,marking_expression):
		if self.eval_marking_expression(last_marking,marking_expression)==True and self.eval_marking_expression(new_marking,marking_expression)==False:
			return(True)
		else:
			return(False)

	def FM(self,last_marking,new_marking,marking_expression):
		if self.eval_marking_expression(last_marking,marking_expression)==False and self.eval_marking_expression(new_marking,marking_expression)==True:
			return(True)
		else:
			return(False)


	def update_name(self, new_name):
		self.TOSPN.output_name_list.remove(self.name)
		self.TOSPN.output_name_list.append(new_name)
		self.name = new_name

	def update_expression(self,new_math_expression,new_txt_expression):
		self.math_marking_expression = new_math_expression
		self.txt_marking_expression = new_txt_expression

	def remove(self):
		self.TOSPN.output_name_list.remove(self.name)
		del self.TOSPN.outputDic[self.id]

class Event():
	event_id = 0
	def __init__(self, name, TOSPN, init_dic):
		self.TOSPN = TOSPN

		if init_dic==None:
			self.id = Event.event_id
			self.name = name
			self.TOSPN.event_name_list.append(self.name)
			Event.event_id += 1
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.TOSPN.event_name_list.append(self.name)

		self.transition_dic={}

	def update_name(self,new_name):
		self.TOSPN.event_name_list.remove(self.name)
		self.TOSPN.event_name_list.append(new_name)
		self.name=new_name

	def remove(self):
		self.TOSPN.event_name_list.remove(self.name)
		del self.TOSPN.eventDic[self.id]


class Place():
	place_id=0
	def __init__(self,TOSPN,init_dic):
		self.TOSPN = TOSPN
		self.type="place"
		if init_dic==None:
			self.id=Place.place_id
			Place.place_id += 1

			test_name="P.{}".format(self.id)
			if test_name in self.TOSPN.placeNameDic.keys():
				k=2
				new_test_name=test_name +".{}".format(k)
				while new_test_name in self.TOSPN.placeNameDic.keys():
					k+=1
					new_test_name = test_name + ".{}".format(k)
				test_name=new_test_name
			self.name=test_name
			self.token_number = 0
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.token_number = init_dic["token"]

		self.previous_arc_list=[]
		self.next_arc_list=[]

		self.graphic_place=None

	def change_id(self,newId):
		if newId in self.TOSPN.placeDic.keys():
			raise Exception("trying to change a place id {} with id {} already used".format(self.id,self.newId))
		else:
			del self.TOSPN.placeDic[self.id]
			self.TOSPN.placeDic[newId]=self
			self.id=newId

	def change_name(self,new_name):
		del self.TOSPN.placeNameDic[self.name]
		self.name=new_name
		self.TOSPN.placeNameDic[self.name]=self

	def remove(self):
		del self.TOSPN.placeNameDic[self.name]
		del self.TOSPN.placeDic[self.id]
		del self.TOSPN.markingDic[self.id]
		del self.TOSPN.lastMarkingDic[self.id]

	def change_token_number(self,new_number):
		self.token_number=new_number
		self.TOSPN.markingDic[self.id]=self.token_number


class Transition():
	transition_id=0
	def __init__(self,TOSPN,init_dic):
		self.type="transition"
		self.TOSPN = TOSPN

		if init_dic==None:
			self.id=Transition.transition_id
			Transition.transition_id += 1
			self.name = "T.{}".format(self.id)
			self.timing_interval = [0, 0]

			self.event = TOSPN.eventDic[0]
			self.event.transition_dic[self.id] = self
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.timing_interval = [init_dic["time1"], init_dic["time2"]]
			self.event = TOSPN.eventDic[init_dic["event_id"]]
			self.event.transition_dic[self.id] = self




		self.previous_arc_list=[]
		self.next_arc_list=[]



		self.graphic_transition = None

	def change_id(self,newId):
		if newId in self.TOSPN.transitionDic.keys():
			raise Exception("trying to change a transition id {} with id {} already used".format(self.id,self.newId))
		else:
			del self.TOSPN.transitionDic[self.id]
			self.TOSPN.transitionDic[newId]=self
			self.id=newId
	def remove(self):
		del self.TOSPN.transitionDic[self.id]

	def change_event(self,new_event):
		del self.event.transition_dic[self.id]
		self.event=new_event
		self.event.transition_dic[self.id]=self

class Arc():
	arc_id = 0
	def __init__(self,element1,element2,TOSPN):
		self.type="Arc"
		self.TOSPN=TOSPN
		self.id = Arc.arc_id
		Arc.arc_id += 1
		self.previous_element = element1
		self.next_element = element2
		self.previous_element.next_arc_list.append(self)
		self.next_element.previous_arc_list.append(self)
		self.weight=1
		self.graphic_arc = None

	def remove(self):
		self.previous_element.next_arc_list.remove(self)
		self.next_element.previous_arc_list.remove(self)
		del self.TOSPN.arcDic[self.id]

