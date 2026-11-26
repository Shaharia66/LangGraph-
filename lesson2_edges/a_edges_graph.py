# ============================================================
# 1. IMPORTS
# ============================================================
from IPython.display import Image, display           # Show pictures inside a Jupyter notebook; NOT used in this .py file
import operator                                      # operator.add joins two lists; used as the reducer for nlist
from typing import Annotated, List, Literal, TypedDict  # Annotated, List, TypedDict are used here; Literal is for later lessons
from langgraph.graph import END, START, StateGraph   # END and START = exit and entry points, StateGraph = the graph builder
from langgraph.types import Command, interrupt       # For later lessons (routing and human-in-the-loop); not used yet

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State(TypedDict):                              # The shared whiteboard
    nlist: Annotated[List[str], operator.add]        # A list with a reducer: every update is ADDED; needed because two nodes write at the same time

# ============================================================
# 3. DEFINE THE NODES
# ============================================================

def node_a(state: State) -> State:                   # First node
    print(f"Adding 'A' to {state['nlist']}")         # Show what the State looked like when this node started
    return State(nlist=["A"])                        # Add "A" (the reducer appends it to the old list)

def node_b(state: State) -> State:                   # Runs in parallel with node_c
    print(f"Adding 'B' to {state['nlist']}")         # Show what this node sees
    return State(nlist=["B"])                        # Add "B"

def node_c(state: State) -> State:                   # Runs in parallel with node_b
    print(f"Adding 'C' to {state['nlist']}")         # Show what this node sees (it does NOT see "B")
    return State(nlist=["C"])                        # Add "C"

def node_bb(state: State) -> State:                  # Follows node_b; runs in parallel with node_cc
    print(f"Adding 'BB' to {state['nlist']}")        # Show what this node sees
    return State(nlist=["BB"])                       # Add "BB"

def node_cc(state: State) -> State:                  # Follows node_c; runs in parallel with node_bb
    print(f"Adding 'CC' to {state['nlist']}")        # Show what this node sees
    return State(nlist=["CC"])                       # Add "CC"

def node_d(state: State) -> State:                   # The last node; it collects the work of both branches
    print(f"Adding 'D' to {state['nlist']}")         # Show what this node sees (everything so far)
    return State(nlist=["D"])                        # Add "D"

# ============================================================
# 4. BUILD THE GRAPH
# ============================================================
builder = StateGraph(State)                          # Create the builder and tell it what our State looks like

# Add nodes
builder.add_node("a", node_a)                        # Register node "a"
builder.add_node("b", node_b)                        # Register node "b"
builder.add_node("c", node_c)                        # Register node "c"
builder.add_node("bb", node_bb)                      # Register node "bb"
builder.add_node("cc", node_cc)                      # Register node "cc"
builder.add_node("d", node_d)                        # Register node "d"

# Add edges
builder.add_edge(START, "a")                         # The graph begins at "a"
builder.add_edge("a", "b")                           # FAN-OUT: after "a", go to "b"...
builder.add_edge("a", "c")                           # ...and ALSO to "c" (b and c run in the same step)
builder.add_edge("b", "bb")                          # SEQUENCE: after "b", go to "bb"
builder.add_edge("c", "cc")                          # SEQUENCE: after "c", go to "cc"
builder.add_edge("bb", "d")                          # FAN-IN: "bb" feeds "d"
builder.add_edge("cc", "d")                          # FAN-IN: "cc" also feeds "d"
builder.add_edge("d", END)                           # After "d", the graph finishes

# Compile
graph = builder.compile()                            # Check the graph is valid and make it runnable

# ============================================================
# 5. DRAW THE GRAPH
# ============================================================
print(graph.get_graph().draw_mermaid())              # Print the diagram as text (works in a script, no internet needed)
# display(Image(graph.get_graph().draw_mermaid_png())) # Notebook only: draw the graph as a picture (needs internet)

# ============================================================
# 6. RUN THE GRAPH
# ============================================================
initial_state = State(                               # Create the starting State
    nlist=["Initial String:"]                        # Start the list with one text item
)                                                    # End of the starting State
result = graph.invoke(initial_state)                 # Run the graph from START to END and keep the final State
print(result)                                        # Print the final State

# ============================================================
# 7. OUTPUT (I have not run it, so check that yours matches)
# ============================================================
# Adding 'A' to ['Initial String:']
# Adding 'B' to ['Initial String:', 'A']
# Adding 'C' to ['Initial String:', 'A']
# Adding 'BB' to ['Initial String:', 'A', 'B', 'C']
# Adding 'CC' to ['Initial String:', 'A', 'B', 'C']
# Adding 'D' to ['Initial String:', 'A', 'B', 'C', 'BB', 'CC']
# {'nlist': ['Initial String:', 'A', 'B', 'C', 'BB', 'CC', 'D']}
#
# Notice 1: B and C both saw only ['Initial String:', 'A'] (same step, they cannot see each other).
# Notice 2: BB and CC both saw 'B' and 'C' (they ran after step 2 finished).
# Notice 3: D saw everything, because it ran last.
# Notice 4: the print lines of B and C (and of BB and CC) may appear in either order; that is normal for parallel nodes.

