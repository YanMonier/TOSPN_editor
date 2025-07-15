import networkx as nx
import copy
from graphviz import Digraph
from graphviz import Source
import html

INF = float('inf')

class SCIA():
	def __init__(self,SCG,dt):

		self.dt=dt
		self.SCG=SCG
		self.state_id=0
		self.transition_id = 0
		self.states={}
		self.event={}
		self.transition={}
		self.init_state_id=None
		self.init_state=None
		self.new_X=set()

		self.state_init_by_class={}
		for SCG_state_id in self.SCG.states.keys():
			new_id=self.add_state(SCG_state_id,[0,0],"close")
			if self.SCG.init_state.id==SCG_state_id:
				self.init_state_id=new_id
				self.init_state=self.states[new_id]
			self.new_X.add(new_id)
			self.state_init_by_class[SCG_state_id]=new_id

		while self.new_X != set():
			selected_scia_state_id=next(iter(self.new_X))
			selected_scia_state=self.states[selected_scia_state_id]
			SCG_state_id=selected_scia_state.SCG_state
			max_scg_state_time=self.SCG.states[SCG_state_id].usigma


			if selected_scia_state.time_interval_type=="close":
				if selected_scia_state_id==2:
					print(f"DEBUG USIGMA test {max_scg_state_time}")
				if selected_scia_state.time_interval[1]<max_scg_state_time:
					new_id = self.add_state(SCG_state_id, [selected_scia_state.time_interval[1], selected_scia_state.time_interval[1]+self.dt], "open")
					self.new_X.add(new_id)
					self.add_transition(selected_scia_state_id,"e",new_id)


			elif selected_scia_state.time_interval_type=="open":
				if max_scg_state_time!=INF:
					new_id = self.add_state(SCG_state_id, [ selected_scia_state.time_interval[0] + self.dt,
														   selected_scia_state.time_interval[0] + self.dt], "close")
					self.new_X.add(new_id)
					self.add_transition(selected_scia_state_id, "r-e", new_id)
				else:
					self.add_transition(selected_scia_state_id, "r-e", self.state_init_by_class[SCG_state_id])

			for edge in self.SCG.states[SCG_state_id].output_edge:
				timing_interval=edge.arc.timing_interval
				data=edge.arc.data
				arc_type=edge.arc.type
				SCG_state_id_out=edge.target.id
				if arc_type =="activation":
					if selected_scia_state.time_interval_type=="close":
						if (selected_scia_state.time_interval[0]>=timing_interval[0] and selected_scia_state.time_interval[0]<=timing_interval[1]) or (selected_scia_state.time_interval[1]>=timing_interval[0] and selected_scia_state.time_interval[1]<=timing_interval[1]):
							self.add_transition(selected_scia_state_id, data, self.state_init_by_class[SCG_state_id_out])
					elif selected_scia_state.time_interval_type=="open":
						if (selected_scia_state.time_interval[0] > timing_interval[0] and selected_scia_state.time_interval[0] < timing_interval[1]) or (selected_scia_state.time_interval[1] > timing_interval[0] and selected_scia_state.time_interval[1] < timing_interval[1]):
							self.add_transition(selected_scia_state_id, data,self.state_init_by_class[SCG_state_id_out])
				elif arc_type =="firing":
					trans_id=data
					output_event=self.SCG.TLSPN.transitions[trans_id].output.name
					if selected_scia_state.time_interval_type == "close":
						if (selected_scia_state.time_interval[0] >= timing_interval[0] and
							selected_scia_state.time_interval[0] <= timing_interval[1]) or (
								selected_scia_state.time_interval[1] >= timing_interval[0] and
								selected_scia_state.time_interval[1] <= timing_interval[1]):
							self.add_transition(selected_scia_state_id, output_event,
												self.state_init_by_class[SCG_state_id_out])
					elif selected_scia_state.time_interval_type == "open":
						if (selected_scia_state.time_interval[0] > timing_interval[0] and
							selected_scia_state.time_interval[0] < timing_interval[1]) or (
								selected_scia_state.time_interval[1] > timing_interval[0] and
								selected_scia_state.time_interval[1] < timing_interval[1]):
							self.add_transition(selected_scia_state_id, output_event,
												self.state_init_by_class[SCG_state_id_out])
				elif arc_type =="sigma":
					output_event_list=[]
					for trans_id in data:
						output_event_list.append(self.SCG.TLSPN.transitions[trans_id].output.name)
					if output_event_list==[]:
						print("DEBUG OUTPUT EVENT LIST EMPTY")

					if len(output_event_list)==1:
						output_event_list=output_event_list[0]
					else:
						if "." in output_event_list:
							while "." in output_event_list:
								output_event_list.remove(".")
							if len(output_event_list)==0:
								output_event_list="."
							elif  len(output_event_list)==1:
								output_event_list = output_event_list[0]
							else:
								output_event_list=tuple(sorted(output_event_list))
						else:
							output_event_list = tuple(sorted(output_event_list))


					if selected_scia_state.time_interval_type == "close":
						if (selected_scia_state.time_interval[0] >= timing_interval[0] and
							selected_scia_state.time_interval[0] <= timing_interval[1]) or (
								selected_scia_state.time_interval[1] >= timing_interval[0] and
								selected_scia_state.time_interval[1] <= timing_interval[1]):
							self.add_transition(selected_scia_state_id, output_event_list,
												self.state_init_by_class[SCG_state_id_out])
					elif selected_scia_state.time_interval_type == "open":
						if (selected_scia_state.time_interval[0] > timing_interval[0] and
							selected_scia_state.time_interval[0] < timing_interval[1]) or (
								selected_scia_state.time_interval[1] > timing_interval[0] and
								selected_scia_state.time_interval[1] < timing_interval[1]):
							self.add_transition(selected_scia_state_id, output_event_list,
												self.state_init_by_class[SCG_state_id_out])
			self.new_X.remove(selected_scia_state_id)

	def plot_graph(self):

		dot = Digraph(name='{}'.format("HA"), filename='{}.gv'.format("HA"), comment='HA graph', engine="dot")

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

			txt += '<TR><TD>C{}</TD></TR> '.format(state.SCG_state)


			if state.time_interval_type=="open":
				txt += '<TR><TD>({},{})</TD></TR>'.format(state.time_interval[0],state.time_interval[1])
			else:
				txt += '<TR><TD>[{},{}]</TD></TR>'.format(state.time_interval[0],state.time_interval[1])
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






	def add_state(self,SCG_sate_id,time_interval,interval_type):
		self.states[self.state_id]=SCIA_state(self.state_id,SCG_sate_id,time_interval,interval_type)
		self.state_id+=1
		return(self.state_id-1)

	def add_transition(self,id1,label,id2):
		self.transition[self.transition_id]=SCIA_transition(self.transition_id,id1,label,id2)
		self.transition_id+=1

		if label not in self.states[id1].output_transition.keys():
			self.states[id1].output_transition[label]=[]
		self.states[id1].output_transition[label].append(id2)

class SCIA_state():
	def __init__(self,id,SCG_state,time_interval,interval_type):
		self.id=id
		self.SCG_state=SCG_state
		self.time_interval=time_interval
		self.time_interval_type=interval_type #"closed or open

		self.output_transition={}

class SCIA_transition():
	def __init__(self,id,state1_id,label,state2_id):
		self.id=id
		self.state1_id=state1_id
		self.state2_id=state2_id
		self.label=label


