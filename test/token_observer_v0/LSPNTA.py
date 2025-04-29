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


		self.add_Event("λ")



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



class Label()
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

	"""def change_id(self,newId):
		if newId in self.TOSPN.placeDic.keys():
			raise Exception("trying to change a place id {} with id {} already used".format(self.id,self.newId))
		else:
			del self.TOSPN.placeDic[self.id]
			self.TOSPN.placeDic[newId]=self
			self.id=newId"""

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

	"""def change_id(self,newId):
		if newId in self.TOSPN.transitionDic.keys():
			raise Exception("trying to change a transition id {} with id {} already used".format(self.id,self.newId))
		else:
			del self.TOSPN.transitionDic[self.id]
			self.TOSPN.transitionDic[newId]=self
			self.id=newId"""
	def remove(self):
		del self.TOSPN.transitionDic[self.id]

	def change_event(self,new_event):
		del self.event.transition_dic[self.id]
		self.event=new_event
		self.event.transition_dic[self.id]=self

class Arc():
	arc_id = 0
	def __init__(self,element1,element2,weight,timing_interval,TOSPN):
		self.type="Arc"
		self.TOSPN=TOSPN
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
		del self.TOSPN.arcDic[self.id]

