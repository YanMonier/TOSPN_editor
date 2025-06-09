import networkx as nx
import copy
from graphviz import Digraph
from graphviz import Source
import html

INF = float('inf')

def initialize_distance_graph(variables, constraints, lower_bounds=None, upper_bounds=None):
    INF = float('inf')
    dist = {}

    # All nodes + the special source node 'src'
    nodes = copy.deepcopy(variables)
    for u in nodes:
        dist[u] = {v: INF for v in nodes}
        dist[u][u] = 0  # zero distance to self

    # Add difference constraints: xᵢ - xⱼ ≤ c ⇨ edge xⱼ → xᵢ with weight c
    for xi, xj, c in constraints:
        dist[xj][xi] = min(dist[xj][xi], c)

    # Add lower bounds: xⱼ ≥ α ⇨ src → xⱼ with weight -α
    if lower_bounds:
        for var, alpha in lower_bounds.items():
            dist['src'][var] = min(dist['src'][var], -alpha)

    # Add upper bounds: xⱼ ≤ β ⇨ xⱼ → src with weight β
    if upper_bounds:
        for var, beta in upper_bounds.items():
            dist[var]['src'] = min(dist[var]['src'], beta)

    return dist


def floyd_warshall(dist):
	nodes = list(dist.keys())
	for k in nodes:
		for i in nodes:
			for j in nodes:
				if dist[i][j] > dist[i][k] + dist[k][j]:
					dist[i][j] = dist[i][k] + dist[k][j]

		# Detect inconsistency (negative cycle)
		work = True
	for node in nodes:
		if dist[node][node] < 0:
			work = False
		return dist, work


class SCG:
	def __init__(self,TLSPN):
		self.state_id=0
		self.TLSPN=TLSPN
		self.new_state_list=[]
		self.state_hash_dic={}
		self.edge_list=[]
		self.states={}

		self.add_new_state(None,None)
		cont=True
		while cont:
			self.explore_new_state(self.new_state_list[0])
			if self.new_state_list==[]:
				cont=False

	def add_new_state(self,old_state,arc):
		new_state=StateSCG(self,old_state,arc)
		hashkey=(frozenset(new_state.enabled_token_dic.items()),frozenset(new_state.reserved_token_dic.items()),self.convert_dist_dic_hash(new_state.dist_dic))
		if hashkey in self.state_hash_dic.keys():
			if old_state!= None:
				self.add_edge(old_state,self.state_hash_dic[hashkey],arc)
				print("DEBUG EXISTING NODE EDGE")
				print(old_state.id,self.state_hash_dic[hashkey].id)

		else:
			new_state.id = self.state_id
			self.states[self.state_id] = new_state
			self.state_id += 1
			self.state_hash_dic[hashkey]=new_state
			self.new_state_list.append(new_state)
			if old_state != None:
				self.add_edge(old_state, self.state_hash_dic[hashkey], arc)




	def add_edge(self,source, target, arc):
		self.edge_list.append(Edge(source,target,arc))

	def explore_new_state(self,state):
		arc_list=state.ArcGeneration()
		for arc in arc_list:
			self.add_new_state(state,arc)
		self.new_state_list.remove(state)


	def convert_dist_dic_hash(self,dist_dic):
		output=set()
		for key1 in dist_dic.keys():
			for key2 in dist_dic[key1].keys():
				output.add((key1,key2,dist_dic[key1][key2]))
		return(frozenset(output))


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
			state=self.states[state_id]

			txt = '<<TABLE BORDER="0" CELLBORDER="0">'
			txt += '<TR><TD>L{}</TD></TR>'.format(state_id)

			txt += '<TR><TD>{}</TD></TR> '.format(state.enabled_token_dic)
			txt += '<TR><TD>{}</TD></TR>'.format(state.reserved_token_dic)
			txt += '<TR><TD>{}</TD></TR>'.format(state.time_constraints)
			txt += '<TR><TD>{}</TD></TR>'.format(state.relative_time_constraint)
			#txt += '<TR><TD>{}</TD></TR>'.format(state.dist_dic)
			#txt += '<TR><TD>{}</TD></TR>'.format(state.debug_time_constraints)
			txt += '</TABLE>>'

			# dot.node("{}".format(location_id),label=txt, shape='box', style='rounded')
			# dot.node("{}".format(location_id), label=txt, shape='box', style='rounded', width='3', height='2')
			dot.node("{}".format(state_id), label=txt, shape="box", fontsize="12",
					 fontcolor="black", width="0.75", height="0.5", fixedsize="false")

		for edge in self.edge_list:
			source_id = edge.source.id
			target_id = edge.target.id

			arc=edge.arc
			txt = '<<TABLE BORDER="0" CELLBORDER="0">'
			txt += '<TR><TD>{}  {}  {}</TD></TR>'.format(arc.type, arc.data, arc.timing_interval)
			txt += '</TABLE>>'

			dot.edge("{}".format(source_id), "{}".format(target_id), label="{}".format(txt), color="black",
					 style="solid", labelloc="c", labeldistance="2", fontsize="10", fontcolor="black",
					 arrowsize="1.0", arrowhead="normal", arrowtail="none", constraint="true", weight="1")

		dot.format = 'pdf'
		dot.render("classgraph_plot", view="True")


class Edge():
	def __init__(self,source, target, arc):
		self.source=source
		self.target=target
		self.arc=arc

class Arc:
	def __init__(self,type,data,timing_interval):
		self.type=type #"activation" or "firing" or "sigma"
		self.data=data
		self.timing_interval=copy.deepcopy(timing_interval)


class StateSCG:
	def __init__(self,SCG,last_state,arc):
		self.SCG=SCG
		self.id=0
		self.debug_time_constraints = {}

		if last_state != None:
			self.enabled_token_dic=copy.deepcopy(last_state.enabled_token_dic)
			self.reserved_token_dic=copy.deepcopy(last_state.reserved_token_dic)
			self.activated_transition=copy.deepcopy(last_state.activated_transition) #mathcal A(C)

			self.dist_dic={}

			self.relative_time_constraint=copy.deepcopy(last_state.relative_time_constraint)
			self.time_constraints = copy.deepcopy(last_state.time_constraints)



			if arc.type=="activation":

				#update existing constraints according to arc interval of time
				up_int=arc.timing_interval[1]
				down_int=arc.timing_interval[0]
				for activated_transition_id in self.time_constraints.keys():
					self.time_constraints[activated_transition_id][0] = max(0,self.time_constraints[activated_transition_id][0] - up_int)
					self.time_constraints[activated_transition_id][1] = max(0, self.time_constraints[activated_transition_id][1] - down_int)

					#self.debug_time_constraints[activated_transition_id]=[self.time_constraints[activated_transition_id][0],self.time_constraints[activated_transition_id][1]]

				#retrieve transition activated by the event
				transition_activated_list = last_state.event_to_enabled_transition_list[arc.data]

				while transition_activated_list  != []:
					prioritary_transition_id=self.get_priority_transition(transition_activated_list)
					transition_activated_list.remove(prioritary_transition_id)
					if self.can_transition_activate(prioritary_transition_id):
						self.activate_transition(prioritary_transition_id)
				for activated_transition_id in self.time_constraints.keys():
					self.debug_time_constraints[activated_transition_id] = [
						self.time_constraints[activated_transition_id][0],
						self.time_constraints[activated_transition_id][1]]

			elif arc.type == "firing" or  arc.type == "sigma":
				sigma=[]
				if arc.type== "firing":
					sigma=[arc.data]
				else:
					sigma=arc.data

				up_int = arc.timing_interval[1]
				down_int = arc.timing_interval[0]
				for activated_transition_id in self.time_constraints.keys():
					self.time_constraints[activated_transition_id][0] = max(0, self.time_constraints[
						activated_transition_id][0] - up_int)
					self.time_constraints[activated_transition_id][1] = max(0, self.time_constraints[
						activated_transition_id][1] - down_int)
				for transition_id in sigma:
					self.fire_transition(transition_id,copy.deepcopy(arc.timing_interval))

		else:
			self.enabled_token_dic = {}
			self.reserved_token_dic = {}
			self.activated_transition = []  # mathcal A(C)
			self.relative_time_constraint = {}
			self.dist_dic = {}
			self.time_constraints={}

			for place_id in self.SCG.TLSPN.places.keys():
				self.enabled_token_dic[place_id]=self.SCG.TLSPN.places[place_id].token_number
				self.reserved_token_dic[place_id]=0



		self.event_to_enabled_transition_list={}


		didnorm=self.normalize()
		if didnorm==False:
			print("DEBUG, PN NORMALISE",last_state.id,arc.type,arc.data)

	def activate_transition(self,transition_id):
		for input_arc in self.SCG.TLSPN.transitions[transition_id].input_arcs:
			place_id=input_arc.source.id
			self.enabled_token_dic[place_id]-=input_arc.weight
			self.reserved_token_dic[place_id]+=input_arc.weight
		self.time_constraints[transition_id]=copy.deepcopy(self.SCG.TLSPN.transitions[transition_id].timing_interval)
		if transition_id not in self.relative_time_constraint.keys():
			self.relative_time_constraint[transition_id]={}
		for other_id1 in self.activated_transition:
			for other_id2 in self.activated_transition:
				if other_id1 != other_id2:
					self.relative_time_constraint[other_id1][other_id2]= self.time_constraints[other_id1][1]-self.time_constraints[other_id2][0]
				else:
					self.relative_time_constraint[other_id1][other_id2]=0

		for other_id in self.activated_transition:
			self.relative_time_constraint[transition_id][other_id] = float('inf')
			self.relative_time_constraint[other_id][transition_id] = float('inf')

		self.relative_time_constraint[transition_id][transition_id] = 0
		self.activated_transition.append(transition_id)


	def fire_transition(self,transition_id,timing_interval):
		for input_arc in self.SCG.TLSPN.transitions[transition_id].input_arcs:
			place_id=input_arc.source.id
			self.reserved_token_dic[place_id]-=input_arc.weight
		for output_arc in self.SCG.TLSPN.transitions[transition_id].output_arcs:
			place_id=output_arc.target.id
			self.enabled_token_dic[place_id]+=output_arc.weight

		del self.time_constraints[transition_id]
		self.activated_transition.remove(transition_id)

		for other_id in self.activated_transition:
			self.time_constraints[other_id][0]=max(self.time_constraints[other_id][0],-self.relative_time_constraint[transition_id][other_id])
			self.time_constraints[other_id][1]=min(self.time_constraints[other_id][1],self.relative_time_constraint[other_id][transition_id])
			print(f"DEBUG firing transid {transition_id}, other id {other_id}: [{self.time_constraints[other_id][0]};{self.time_constraints[other_id][1]}]")
			print(f"timing interval of transition firing {timing_interval}, {self.relative_time_constraint[transition_id][other_id]}, {self.relative_time_constraint[other_id][transition_id]}")
		for other_id in self.activated_transition:
			del self.relative_time_constraint[other_id][transition_id]
			if self.relative_time_constraint[other_id]=={}:
				del self.relative_time_constraint[other_id]
		del self.relative_time_constraint[transition_id]

	def ArcGeneration(self):
		arcList=[]
		if self.activated_transition!=[]:
			sigma = []
			is_lambda = 0
			for transition_id in self.activated_transition:
				if self.SCG.TLSPN.transitions[transition_id].event.name=="λ":
					is_lambda = 1
			"""if is_lambda==1:
				usigma = 0
			else:"""
			activated_transition_list=self.activated_transition
			usigma = self.get_upper_bound_beta(activated_transition_list[0])
			for k in range(1,len(activated_transition_list)):
				if usigma>self.get_upper_bound_beta(activated_transition_list[k]):
					usigma=self.get_upper_bound_beta(activated_transition_list[k])

			for tj in activated_transition_list:
				if self.get_lower_bound_alpha(tj)<=usigma:
					print(f"DEBUG state: {self.id} trans:{tj}, lower bound: {self.get_lower_bound_alpha(tj)}, upper:{self.get_upper_bound_beta(tj)}")
					if self.get_upper_bound_beta(tj) == self.get_lower_bound_alpha(tj) and self.get_upper_bound_beta(tj)==usigma:
						sigma.append(tj)
					else:
						arcList.append(Arc("firing",tj,[self.get_lower_bound_alpha(tj),usigma]))
			if sigma != []:
				arcList.append(Arc("sigma",sigma,[usigma,usigma]))
		self.get_all_event_enabled()
		if self.event_enabled!=[]:
			if "λ" in self.event_enabled:
				arcList.append(Arc("activation", "λ" , [0, 0]))
			else:
				if self.activated_transition!=[]:
					if usigma != 0:
						for event in self.event_enabled:
							arcList.append(Arc("activation", event, [0, usigma]))
				else:
					for event in self.event_enabled:
						arcList.append(Arc("activation", event, [0, INF]))
		return(arcList)


	def get_all_transition_enabled(self):
		self.transition_enabled=[]
		transition_to_test=[]
		for place_id in self.enabled_token_dic.keys():
			for arc in self.SCG.TLSPN.places[place_id].output_arcs:
				if arc.target.id not in transition_to_test:
					transition_to_test.append(arc.target.id)
		for transition_id in transition_to_test:
			if self.can_transition_activate(transition_id):
				self.transition_enabled.append(transition_id)

	def get_all_event_enabled(self):
		self.event_enabled=[]
		self.get_all_transition_enabled()
		for transition_id in self.transition_enabled:
			event = self.SCG.TLSPN.transitions[transition_id].event.name
			if event not in self.event_enabled:
				self.event_enabled.append(event)
			if event not in self.event_to_enabled_transition_list.keys():
				self.event_to_enabled_transition_list[event]=[]
			self.event_to_enabled_transition_list[event].append(transition_id)



	def can_transition_activate(self,transition_id):
		can_activate=True
		arc_list=self.SCG.TLSPN.transitions[transition_id].input_arcs
		for arc in arc_list:
			if self.enabled_token_dic[arc.source.id] < arc.weight:
				can_activate = False
		if transition_id in self.activated_transition:
			can_activate = False
		return(can_activate)



	def get_lower_bound_alpha(self,transition_id): #beta
		return(-self.dist_dic[transition_id]["src"])
	def get_upper_bound_beta(self,transition_id): #alpha
		return (self.dist_dic["src"][transition_id])
	def get_constraint_gamma(self,id1,id2):#id1-id2
		return( self.dist_dic[id2][id1])

	def get_priority_transition(self,transition_id_list):
		selected_id=transition_id_list[0]
		for k in range(len(transition_id_list)):
			if self.SCG.TLSPN.transitions[transition_id_list[k]].priority_level > self.SCG.TLSPN.transitions[selected_id].priority_level:
				selected_id=transition_id_list[k]
		return(selected_id)

	def normalize(self):
		variables = copy.deepcopy(self.activated_transition)
		variables.append("src")
		constraints = []

		for key1 in self.activated_transition:
			for key2 in self.activated_transition:
				if key1 == key2:
					constraints.append((key1, key2, 0))
				else:
					constraints.append((key1, key2, self.relative_time_constraint[key1][key2]))

		for key in self.activated_transition:
			constraints.append(("src", key, - self.time_constraints[key][0]))
			constraints.append((key, "src", self.time_constraints[key][1]))

		dist=initialize_distance_graph(variables,constraints)
		res,work=floyd_warshall(dist)
		if work == True:
			# Compute shortest path lengths between all pairs
			self.dist_dic=res
			for key1 in self.activated_transition:
				for key2 in self.activated_transition:
					if key1 != key2:
						self.relative_time_constraint[key1][key2]=self.dist_dic[key2][key1]

			for key in self.activated_transition:
				self.time_constraints[key][1]=  self.dist_dic["src"][key]
				self.time_constraints[key][0] = - self.dist_dic[key]["src"]
			return True
		else:
			self.dist_dic = res
			for key1 in self.activated_transition:
				for key2 in self.activated_transition:
					if key1 != key2:
						self.relative_time_constraint[key1][key2] = self.dist_dic[key2][key1]

			for key in self.activated_transition:
				self.time_constraints[key][1] = self.dist_dic["src"][key]
				self.time_constraints[key][0] = - self.dist_dic[key]["src"]

			return False






