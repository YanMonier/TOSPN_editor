class TLSPN():
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
		self.add_Output(".")


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

	def add_Output(self,name,init_dic=None):
		newOutput = Output(name,self,init_dic)
		id = newOutput.id

		if id in self.outputDic.keys():
			raise Exception("trying to create output {} with id {} already used".format(newOutput.name,id))
		else:
			self.outputDic[id] = newOutput
		return (newOutput)


class Output():
	output_id=0
	def __init__(self, name, TLSPN, init_dic):
		self.TLSPN = TLSPN

		if init_dic==None:
			self.id = Output.output_id
			self.name = name
			self.TLSPN.output_name_list.append(self.name)
			Output.output_id += 1
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.TLSPN.output_name_list.append(self.name)

		self.transition_dic={}

	def update_name(self,new_name):
		self.TLSPN.output_name_list.remove(self.name)
		self.TLSPN.output_name_list.append(new_name)
		self.name=new_name

	def remove(self):
		self.TLSPN.output_name_list.remove(self.name)
		del self.TLSPN.outputDic[self.id]

class Event():
	event_id = 0
	def __init__(self, name, TLSPN, init_dic):
		self.TLSPN = TLSPN

		if init_dic==None:
			self.id = Event.event_id
			self.name = name
			self.TLSPN.event_name_list.append(self.name)
			Event.event_id += 1
		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.TLSPN.event_name_list.append(self.name)

		self.transition_dic={}

	def update_name(self,new_name):
		self.TLSPN.event_name_list.remove(self.name)
		self.TLSPN.event_name_list.append(new_name)
		self.name=new_name

	def remove(self):
		self.TLSPN.event_name_list.remove(self.name)
		del self.TLSPN.eventDic[self.id]


class Place():
	place_id=0
	def __init__(self,TLSPN,init_dic):
		self.TLSPN = TLSPN
		self.type="place"
		if init_dic==None:
			self.id=Place.place_id
			Place.place_id += 1

			test_name="P.{}".format(self.id)
			if test_name in self.TLSPN.placeNameDic.keys():
				k=2
				new_test_name=test_name +".{}".format(k)
				while new_test_name in self.TLSPN.placeNameDic.keys():
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
		if newId in self.TLSPN.placeDic.keys():
			raise Exception("trying to change a place id {} with id {} already used".format(self.id,self.newId))
		else:
			del self.TLSPN.placeDic[self.id]
			self.TLSPN.placeDic[newId]=self
			self.id=newId

	def change_name(self,new_name):
		del self.TLSPN.placeNameDic[self.name]
		self.name=new_name
		self.TLSPN.placeNameDic[self.name]=self

	def remove(self):
		del self.TLSPN.placeNameDic[self.name]
		del self.TLSPN.placeDic[self.id]
		del self.TLSPN.markingDic[self.id]
		del self.TLSPN.lastMarkingDic[self.id]

	def change_token_number(self,new_number):
		self.token_number=new_number
		self.TLSPN.markingDic[self.id]=self.token_number


class Transition():
	transition_id=0
	def __init__(self,TLSPN,init_dic):
		self.type="transition"
		self.TLSPN = TLSPN

		if init_dic==None:
			self.id=Transition.transition_id
			Transition.transition_id += 1
			self.name = "T.{}".format(self.id)
			self.timing_interval = [0, 0]

			self.event = TLSPN.eventDic[0]
			self.event.transition_dic[self.id] = self

			self.output = TLSPN.outputDic[0]
			self.output.transition_dic[self.id] = self

		else:
			self.id = init_dic["id"]
			self.name = init_dic["name"]
			self.timing_interval = [init_dic["time1"], init_dic["time2"]]
			self.event = TLSPN.eventDic[init_dic["event_id"]]
			self.event.transition_dic[self.id] = self

			self.output = TLSPN.outputDic[init_dic["output_id"]]
			self.output.transition_dic[self.id] = self




		self.previous_arc_list=[]
		self.next_arc_list=[]



		self.graphic_transition = None

	def change_id(self,newId):
		if newId in self.TLSPN.transitionDic.keys():
			raise Exception("trying to change a transition id {} with id {} already used".format(self.id,self.newId))
		else:
			del self.TLSPN.transitionDic[self.id]
			self.TLSPN.transitionDic[newId]=self
			self.id=newId
	def remove(self):
		del self.TLSPN.transitionDic[self.id]

	def change_event(self,new_event):
		del self.event.transition_dic[self.id]
		self.event=new_event
		self.event.transition_dic[self.id]=self

	def change_output(self,new_output):
		del self.output.transition_dic[self.id]
		self.output = new_output
		self.output.transition_dic[self.id] = self

class Arc():
	arc_id = 0
	def __init__(self,element1,element2,TLSPN):
		self.type="Arc"
		self.TLSPN=TLSPN
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
		del self.TLSPN.arcDic[self.id]