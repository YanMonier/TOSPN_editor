
def initialize_distance_graph(variables, constraints, lower_bounds=None, upper_bounds=None):
    INF = float('inf')
    dist = {}

    # All nodes + the special source node 'src'
    nodes = variables + ['src']
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




def test_floyd_warshall_with_inequalities():
	variables = ['x1', 'x2', 'src']
	constraints = [
        ('src', 'x2', -3),   # 3 ≤ x2
        ('x2', 'src', 5),   # x2  ≤ 5
        ('src', 'x1', -2),  # 2 ≤ x1
		('x1', 'src', 7),  # x1 ≤ 7
		('x2', 'x1', 5),  # x2- x1 <5
		('x1', 'x2', -1),  # 1 < x2 - x1
    ]
	result = floyd_warshall_inequalities(variables, constraints)

	if result:
		print("System is consistent. Tightest bounds:")
		for i in variables:
			for j in variables:
				print(f"{i} - {j} ≤ {result[i][j]}")
	return (result)


def extract_bounds(dist, variables):
    alpha_star = {}
    beta_star = {}
    for var in variables:
        alpha_star[var] = -dist[var]['src']  # α* = -d[var][src]
        beta_star[var] = dist['src'][var]    # β* = d[src][var]
    return alpha_star, beta_star



variables = ['x1', 'x2', 'src']
constraints = [
	('src', 'x2', -3),   # 3 ≤ x2
	('x2', 'src', 5),   # x2  ≤ 5
	('src', 'x1', -2),  # 2 ≤ x1
	('x1', 'src', 7),  # x1 ≤ 7
	('x2', 'x1', 5),  # x2- x1 <5
	('x1', 'x2', -1),  # 1 < x2 - x1
]
dist=initialize_distance_graph(variables, constraints)
res=floyd_warshall(dist)
variables = ['x1', 'x2', 'src']
extract_bounds(res,variables)