# ============================================================
# 1. IMPORTS
# ============================================================
from IPython.display import Image, display           # Notebook-only picture tools; NOT used in this .py file
import operator                                      # operator.add is the reducer for nlist
from typing import Annotated, List, Literal, TypedDict  # Annotated, List, TypedDict are used; Literal is for later lessons
from langgraph.graph import END, START, StateGraph   # Entry/exit points and the graph builder
from langgraph.types import Command, interrupt       # For later lessons; not used yet

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State(TypedDict):                              # The shared whiteboard
    nlist: Annotated[List[str], operator.add]        # List with a reducer, because parallel nodes write to it

# ============================================================
# 3. DEFINE THE NODES
# ============================================================
def node_a(state: State) -> State:                   # First node
    print(f"Adding 'A' to {state['nlist']}")         # Show what this node sees
    return State(nlist=["A"])                        # Add "A"

def node_b(state: State) -> State:                   # Long branch, first node
    print(f"Adding 'B' to {state['nlist']}")         # Show what this node sees
    return State(nlist=["B"])                        # Add "B"

def node_bb(state: State) -> State:                  # Long branch, second node
    print(f"Adding 'BB' to {state['nlist']}")        # Show what this node sees
    return State(nlist=["BB"])                       # Add "BB"

def node_c(state: State) -> State:                   # Short branch (only one node)
    print(f"Adding 'C' to {state['nlist']}")         # Show what this node sees
    return State(nlist=["C"])                        # Add "C"

def node_d(state: State) -> State:                   # The node that joins both branches
    print(f"Adding 'D' to {state['nlist']}")         # Show what this node sees
    return State(nlist=["D"])                        # Add "D"

# ============================================================
# 4. BUILD GRAPH 1: SEPARATE EDGES INTO "d"
# ============================================================
builder1 = StateGraph(State)                         # Create the first builder
builder1.add_node("a", node_a)                       # Register node "a"
builder1.add_node("b", node_b)                       # Register node "b"
builder1.add_node("bb", node_bb)                     # Register node "bb"
builder1.add_node("c", node_c)                       # Register node "c"
builder1.add_node("d", node_d)                       # Register node "d"
builder1.add_edge(START, "a")                        # Begin at "a"
builder1.add_edge("a", "b")                          # FAN-OUT: "a" starts "b"...
builder1.add_edge("a", "c")                          # ...and "c" in the same step
builder1.add_edge("b", "bb")                         # Long branch continues: b -> bb
builder1.add_edge("bb", "d")                         # SEPARATE edge: when "bb" finishes, "d" can run
builder1.add_edge("c", "d")                          # SEPARATE edge: when "c" finishes, "d" can run (this happens EARLIER than bb)
builder1.add_edge("d", END)                          # After "d", finish
graph1 = builder1.compile()                          # Compile graph 1

# ============================================================
# 5. BUILD GRAPH 2: ONE EDGE FROM A LIST ["bb", "c"] INTO "d"
# ============================================================
builder2 = StateGraph(State)                         # Create the second builder
builder2.add_node("a", node_a)                       # Register node "a"
builder2.add_node("b", node_b)                       # Register node "b"
builder2.add_node("bb", node_bb)                     # Register node "bb"
builder2.add_node("c", node_c)                       # Register node "c"
builder2.add_node("d", node_d)                       # Register node "d"
builder2.add_edge(START, "a")                        # Begin at "a"
builder2.add_edge("a", "b")                          # FAN-OUT: "a" starts "b"...
builder2.add_edge("a", "c")                          # ...and "c" in the same step
builder2.add_edge("b", "bb")                         # Long branch continues: b -> bb
builder2.add_edge(["bb", "c"], "d")                  # JOIN: "d" WAITS until BOTH "bb" and "c" are finished, then runs once
builder2.add_edge("d", END)                          # After "d", finish
graph2 = builder2.compile()                          # Compile graph 2

# ============================================================
# 6. RUN BOTH GRAPHS
# ============================================================
print("--- Graph 1: separate edges ---")             # Label the first run
result1 = graph1.invoke({"nlist": ["Start"]})        # Run graph 1 with a starting State
print(result1)                                       # Print its final State

print("--- Graph 2: list edge (join) ---")           # Label the second run
result2 = graph2.invoke({"nlist": ["Start"]})        # Run graph 2 with the same starting State
print(result2)                                       # Print its final State

# ============================================================
# 7. OUTPUT (I have not run it, so check that yours matches)
# ============================================================
# --- Graph 1: separate edges ---
# Adding 'A' to ['Start']
# Adding 'B' to ['Start', 'A']
# Adding 'C' to ['Start', 'A']
# Adding 'BB' to ['Start', 'A', 'B', 'C']          <- BB and the first D run in the same step,
# Adding 'D' to ['Start', 'A', 'B', 'C']              so these two lines can appear in either order
# Adding 'D' to ['Start', 'A', 'B', 'C', 'BB', 'D']   <- D runs a SECOND time after BB finishes
# {'nlist': ['Start', 'A', 'B', 'C', 'BB', 'D', 'D']}   <- note the double 'D' (the order of BB and the first D may differ)
#
# --- Graph 2: list edge (join) ---
# Adding 'A' to ['Start']
# Adding 'B' to ['Start', 'A']
# Adding 'C' to ['Start', 'A']
# Adding 'BB' to ['Start', 'A', 'B', 'C']
# Adding 'D' to ['Start', 'A', 'B', 'C', 'BB']        <- D ran once, only after BOTH branches finished
# {'nlist': ['Start', 'A', 'B', 'C', 'BB', 'D']}
#
# Lesson: with branches of different length, use add_edge([...], "d") so "d" waits for all of them.
