import networkx as nx
import copy
from graphviz import Digraph
from graphviz import Source
import html



class SCIA_observer():
	def __init__(self, SCIA):
		self.SCIA = SCIA
		self.non_observable_event = self.SCIA.SCG.TLSPN.get_unobservable_event()
		self.states = {}
		self.states_hash = {}
		self.state_id = 0
		self.init_state_id = self.add_state([SCIA.init_state_id])
		self.not_explored_state = [self.init_state_id]
		self.explored_state = []

		self.transition = {}
		self.transition_id=0
		self.active_state=None

		self._listeners=[]

		while self.not_explored_state != []:
			exploring_state = self.states[self.not_explored_state[0]]
			self.explored_state.append(exploring_state.id)
			next_label_list = exploring_state.get_next_possible_label()
			for next_label in next_label_list:
				next_scia_state_list = exploring_state.give_next_state_list(next_label)
				next_observer_state_id = self.add_state(next_scia_state_list)
				if next_observer_state_id not in self.explored_state and next_observer_state_id not in self.not_explored_state:
					self.not_explored_state.append(next_observer_state_id)
				self.add_transition(exploring_state.id, next_label, next_observer_state_id)

			self.not_explored_state.remove(exploring_state.id)

	def add_transition(self, id1, label, id2):
		self.transition[self.transition_id] = Transition_observer(self.transition_id, id1, label, id2)
		self.transition_id += 1
		if label not in self.states[id1].output_transition.keys():
			self.states[id1].output_transition[label] = None
		self.states[id1].output_transition[label]=id2

	def add_state(self, scia_state_list):
		new_state = State_observer(self.SCIA, scia_state_list, self.non_observable_event)
		new_state_hash = tuple(sorted(new_state.possible_scia_state))
		if new_state_hash not in self.states_hash.keys():
			self.states[self.state_id] = new_state
			self.states_hash[new_state_hash] = self.state_id
			new_state.id=self.state_id
			self.state_id += 1
			return (self.state_id - 1)
		else:
			existing_state_id = self.states_hash[new_state_hash]
			return (existing_state_id)

	def plot_graph(self):

		dot = Digraph(name='{}'.format("HA"), filename='{}.gv'.format("HA"), comment='HA graph', engine="neato")

		round_val = 3
		# dot.graph_attr['layout'] = "neato"
		# dot.graph_attr['mode'] = "isep"
		# dot.graph_attr['nodesep'] = "0.5"
		# dot.graph_attr['splines'] = "false"
		# dot.graph_attr['overlap'] = "false"
		# dot.graph_attr['sep'] = "2"
		# dot.attr(size='10,10')  # Size of the output graph
		# dot.attr(dpi='300')  # Resolution
		# dot.attr(splines='true')  # Use splines to avoid overlapping edges

		dot.attr(overlap='false')  # Avoid node overlap
		dot.attr(pack='true')  # Pack the layout
		dot.attr(sep='0.5')  # Increase the separation between nodes
		dot.attr(rankdir='BT')  # Top to Bottom layout (change to 'LR' for Left to Right)

		for state_id in self.states.keys():
			state = self.states[state_id]

			txt = '<<TABLE BORDER="0" CELLBORDER="0">'
			txt += '<TR><TD>X{}</TD></TR>'.format(state_id)

			txt += '<TR><TD>C{}</TD></TR> '.format("")#state.possible_scia_state)

			# txt += '<TR><TD>{}</TD></TR>'.format(state.dist_dic)
			# txt += '<TR><TD>{}</TD></TR>'.format(state.debug_time_constraints)
			txt += '</TABLE>>'

			# dot.node("{}".format(location_id),label=txt, shape='box', style='rounded')
			# dot.node("{}".format(location_id), label=txt, shape='box', style='rounded', width='3', height='2')
			dot.node("{}".format(state_id), label=txt, shape="box", fontsize="12",
					 fontcolor="black", width="0.75", height="0.5", fixedsize="false")

		for edge in self.transition.values():
			source_id = edge.state1_id
			target_id = edge.state2_id

			txt = '<<TABLE BORDER="0" CELLBORDER="0">'
			txt += '<TR><TD> {} </TD></TR>'.format(edge.label)
			txt += '</TABLE>>'
			dot.edge("{}".format(source_id), "{}".format(target_id), label="{}".format(txt))

		dot.format = 'pdf'
		dot.render("sciagraph_plot", view="True")

	def reset_detection(self):
		self.active_state=self.states[self.init_state_id]

	def give_next_detected_state(self,event_name):

		if event_name in self.active_state.output_transition.keys():
			next_state_id=self.active_state.output_transition[event_name]
			next_state=self.states[next_state_id]
			self.last_active_state = self.active_state
			self.last_label = event_name
			self.active_state=next_state
			self.notify_listeners("change_active_state",{"last_active_state":self.last_active_state,"new_active_state":self.active_state,"last_label":self.last_label})
			return(True)
		else:
			return(False)

	def add_listener(self, listener):
		"""Add a listener to this TLSPN."""
		if listener not in self._listeners:
			self._listeners.append(listener)

	def remove_listener(self, listener):
		"""Remove a listener from this TLSPN."""
		if listener in self._listeners:
			self._listeners.remove(listener)

	def notify_listeners(self, event_type, data=None):
		"""Notify all listeners of a change."""
		for listener in self._listeners:
			listener.on_change(self, event_type, data)



class State_observer():
	def __init__(self,SCIA,scia_state_list_to_check,non_observable_event):
		self.SCIA=SCIA
		self.possible_scia_state=[]
		self.non_observable_label=non_observable_event
		self.id=0
		self.output_transition={}

		while scia_state_list_to_check!=[]:
			scia_state_id=scia_state_list_to_check[0]
			scia_state=self.SCIA.states[scia_state_id]
			for non_obs_label in self.non_observable_label:
				if non_obs_label in scia_state.output_transition.keys():
					for next_scia_state_id in scia_state.output_transition[non_obs_label]:
						if next_scia_state_id not in self.possible_scia_state:
							scia_state_list_to_check.append(next_scia_state_id)
			self.possible_scia_state.append(scia_state_id)
			scia_state_list_to_check.remove(scia_state_id)

	def give_next_state_list(self,label):
		next_scia_state_id_list=[]
		for scia_state_id in self.possible_scia_state:
			scia_state=self.SCIA.states[scia_state_id]
			if label in scia_state.output_transition.keys():
				for next_scia_state_id in scia_state.output_transition[label]:
					if next_scia_state_id not in next_scia_state_id_list:
						next_scia_state_id_list.append(next_scia_state_id)
		return(next_scia_state_id_list)

	def get_next_possible_label(self):
		next_possible_label=[]
		for scia_state_id in self.possible_scia_state:
			scia_state=self.SCIA.states[scia_state_id]
			for label in scia_state.output_transition.keys():
				if label not in next_possible_label and label not in self.non_observable_label:
					next_possible_label.append(label)
		return(next_possible_label)

class Transition_observer():
	def __init__(self,id,state1_id,label,state2_id):
		self.id=id
		self.state1_id=state1_id
		self.state2_id=state2_id
		self.label=label
