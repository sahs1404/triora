import networkx as nx
from schemas.activity_schema import Activity


def build_schedule_graph(activities: list[Activity]) -> nx.DiGraph:
    """
    Builds the DAG from activity list + predecessor links.
    Raises ValueError if the schedule references unknown activities
    or contains a cycle — both mean the uploaded data is invalid.
    """
    G = nx.DiGraph()

    for a in activities:
        G.add_node(a.id, name=a.name, duration=a.duration_days)

    for a in activities:
        for pred in a.predecessors:
            if pred not in G:
                raise ValueError(
                    f"Activity '{a.id}' lists unknown predecessor '{pred}'. "
                    f"Check sample_activities.csv for a typo or missing row."
                )
            G.add_edge(pred, a.id)

    if not nx.is_directed_acyclic_graph(G):
        cycle = nx.find_cycle(G)
        raise ValueError(f"Schedule has a cycle, not a valid project network: {cycle}")

    return G