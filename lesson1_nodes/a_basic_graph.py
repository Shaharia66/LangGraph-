# ============================================================
# 1. IMPORTS
# ============================================================
from IPython.display import Image, display           # Show pictures inside a Jupyter notebook; NOT used in this .py file (a script cannot show the picture)
import operator                                      # Python's operator module; operator.add is a reducer, used in b_reducer_graph.py (not used here)
from typing import Annotated, List, Literal, TypedDict  # List and TypedDict are used here; Annotated is used in file b; Literal is for later lessons (conditional edges)
from langgraph.graph import END, START, StateGraph   # END and START = exit and entry points, StateGraph = the graph builder (all three are used here)
from langgraph.types import Command, interrupt       # Command and interrupt are for later lessons (routing and human-in-the-loop); not used yet

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State(TypedDict):                              # Create the State class; TypedDict makes it behave like a dictionary with fixed keys
    nlist: List[str]                                 # One key called "nlist" that must hold a list of strings

# ============================================================
# 3. DEFINE THE NODE
# ============================================================
def node_a(state: State) -> State:                   # A node is a function; it receives the current State and returns an update
    print(f"node a is receiving {state['nlist']}")   # Print what the node received, so we can watch the data flowing in
    note = "Hello World from Node a"                 # Create the text this node wants to add
    return State(nlist=[note])                       # Return a State with nlist = [note]; this REPLACES the old nlist (no reducer yet)

# ============================================================
# 4. BUILD THE GRAPH
# ============================================================
builder = StateGraph(State)                          # Create the builder and tell it what our State looks like
builder.add_node("a", node_a)                        # Register the node: the name is "a", the function is node_a
builder.add_edge(START, "a")                         # Edge: the graph begins at node "a"
builder.add_edge("a", END)                           # Edge: after node "a" the graph finishes
graph = builder.compile()                            # Check the graph is valid and turn it into a runnable object

# ============================================================
# 5. DRAW THE GRAPH
# ============================================================
print(graph.get_graph().draw_mermaid())              # Print the graph diagram as text (works in a script, no internet needed)
# display(Image(graph.get_graph().draw_mermaid_png())) # Notebook only: draw the graph as a picture (needs internet); keep it commented in a .py file

# ============================================================
# 6. RUN THE GRAPH
# ============================================================
initial_state = State(                               # Create the starting State
    nlist=["Hello Node a, how are you?"]             # Put one message in the list as the starting data
)                                                    # End of the starting State
result = graph.invoke(initial_state)                 # Run the graph from START to END and keep the final State
print(result)                                        # Print the final State

# ============================================================
# 7. OUTPUT (what you should see after the diagram text)
# ============================================================
# node a is receiving ['Hello Node a, how are you?']   <- printed by node_a while the graph runs
# {'nlist': ['Hello World from Node a']}               <- the final State
#
# Notice: the starting message is gone. The node's update REPLACED the list.

