import networkx as nx


def compute_cpm(G: nx.DiGraph) -> dict:
    """
    Forward/backward pass over the schedule graph.

    Returns a dict with:
      - float_days: {activity_id: slack in days}
      - blast_radius: {activity_id: count of downstream activities}
      - project_duration: total project length in days
      - critical_path: list of activity_ids where float == 0
    """
    topo = list(nx.topological_sort(G))

    # Forward pass — earliest start/finish
    ES, EF = {}, {}
    for n in topo:
        dur = G.nodes[n]["duration"]
        preds = list(G.predecessors(n))
        ES[n] = max([EF[p] for p in preds], default=0)
        EF[n] = ES[n] + dur

    project_duration = max(EF.values()) if EF else 0

    # Backward pass — latest start/finish
    LF, LS = {}, {}
    for n in reversed(topo):
        dur = G.nodes[n]["duration"]
        succs = list(G.successors(n))
        LF[n] = min([LS[s] for s in succs], default=project_duration)
        LS[n] = LF[n] - dur

    float_days = {n: LS[n] - ES[n] for n in topo}
    blast_radius = {n: len(nx.descendants(G, n)) for n in topo}
    critical_path = [n for n in topo if float_days[n] == 0]

    return {
        "ES": ES, "EF": EF, "LS": LS, "LF": LF,
        "float_days": float_days,
        "blast_radius": blast_radius,
        "project_duration": project_duration,
        "critical_path": critical_path,
    }