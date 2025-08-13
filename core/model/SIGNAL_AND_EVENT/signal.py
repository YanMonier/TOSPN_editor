class Signal():
	def __init__(self,ID,name,source_id,units,description):
		self.id=ID
		self.name=name
		self.source_id=source_id
		self.units=units
		self.description=description

class Signal_manager():
	def __init__(self):
		self.signal_id=0
		self.signals={}
		self.signal_name_to_id={}
		self.id_to_source_id_mapping={}
		self.source_id_to_id_mapping={}

	def add_signals(self,signal_name,source_id,units="",description=""):
		new_signal=Signal(self.signal_id,signal_name,source_id,units,description)
		self.signals[self.signal_id]=new_signal
		self.signal_name_to_id[signal_name] = new_signal.id
		self.signal_id+=1
		return(new_signal)

	def remove_signals(self,signal_id):
		if signal_id in self.id_to_source_id_mapping.keys():
			source_id=self.id_to_source_id_mapping[signal_id]
			del self.id_to_source_id_mapping[signal_id]
			del self.source_id_to_id_mapping[source_id]
		signal_name = self.signals[signal_id].name
		del self.signal_name_to_id[signal_name]
		del self.signals[signal_id]

	def check_name_validity(self,name):
		if name in self.signal_name_to_id.keys():
			return(False)
		else:
			return(True)

	def change_signal_name(self,signal_id,new_name):
		old_name=self.signals[signal_id].name
		del self.signal_name_to_id[old_name]
		self.signal_name_to_id[new_name]=signal_id
		self.signals[signal_id].name=new_name

	def load_signals(self,output_dic):

		self.signal_id = 0
		self.signals = {}
		self.signal_name_to_id = {}
		self.id_to_source_id_mapping = {}
		self.source_id_to_id_mapping = {}

		for sigid in output_dic["id"].keys():
			signal_name=output_dic["id"][sigid]["name"]
			source_id=int(output_dic["id"][sigid]["source_id"])
			units=output_dic["id"][sigid]["units"]
			description=output_dic["id"][sigid]["description"]
			new_signal = Signal(int(sigid), signal_name, source_id, units, description)
			self.signals[int(sigid)] = new_signal
			self.signal_name_to_id[signal_name] = int(sigid)
		self.signal_id=int(output_dic["param"]["signal_id"])

	def save_signals(self):
		output_dic={"id":{},"param":{}}
		for sigid in self.signals.keys():
			output_dic["id"][sigid]={}
			output_dic["id"][sigid]["name"]=self.signals[sigid].name
			output_dic["id"][sigid]["source_id"]=self.signals[sigid].source_id
			output_dic["id"][sigid]["units"]=self.signals[sigid].units
			output_dic["id"][sigid]["description"]=self.signals[sigid].description
		output_dic["param"]["signal_id"]=self.signal_id
		return(output_dic)
