# ============================================================
# 1. IMPORTS
# ============================================================
from IPython.display import Image, display           # Notebook-only picture tools; NOT used in this .py file
import operator                                      # operator.add is the reducer for nlist
from typing import Annotated, List, Literal, TypedDict  # Literal is used in node_a's return type
from langgraph.graph import END, START, StateGraph   # Entry/exit points and the graph builder
from langgraph.types import Command, interrupt       # Command is used NOW; interrupt is for Lesson 5

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State(TypedDict):                              # The shared whiteboard
    nlist: Annotated[List[str], operator.add]        # List with a reducer: updates are ADDED

# ============================================================
# 3. DEFINE THE NODES
# ============================================================
def node_a(state: State) -> Command[Literal["b", "c", "__end__"]]:  # The hint lists every node this node may jump to (used for the diagram)
    select = state["nlist"][-1]                      # Take the LAST item of nlist (the newest message)
    if select == "b":                                # If the user typed "b"...
        next_node = "b"                              # ...the next node is "b"
    elif select == "c":                              # If the user typed "c"...
        next_node = "c"                              # ...the next node is "c"
    elif select == "q":                              # If the user typed "q"...
        next_node = END                              # ...stop the graph
    else:                                            # For any other input...
        next_node = END                              # ...also stop the graph

    return Command(                                  # Return a Command: a State update AND the next node together
        update=State(nlist=[select]),                # update = what to write to the State (this ADDS select again, see the output)
        goto=next_node                               # goto = which node runs next
    )                                                # End of the Command

def node_b(state: State) -> State:                   # Road 1
    return State(nlist=["B"])                        # Add "B"

def node_c(state: State) -> State:                   # Road 2
    return State(nlist=["C"])                        # Add "C"

# ============================================================
# 4. BUILD THE GRAPH
# ============================================================
builder = StateGraph(State)                          # Create the builder
builder.add_node("a", node_a)                        # Register node "a"
builder.add_node("b", node_b)                        # Register node "b"
builder.add_node("c", node_c)                        # Register node "c"
builder.add_edge(START, "a")                         # FIXED edge: begin at "a"
builder.add_edge("b", END)                           # FIXED edge: after "b", finish
builder.add_edge("c", END)                           # FIXED edge: after "c", finish
# builder.add_conditional_edges("a", conditional_edge)  # NOT needed: node a routes itself with Command
graph = builder.compile()                            # Compile the graph

# ============================================================
# 5. DRAW THE GRAPH
# ============================================================
print(graph.get_graph().draw_mermaid())              # Still shows dotted lines from "a", because of the Literal hint on node_a

# ============================================================
# 6. RUN AUTOMATIC TESTS
# ============================================================
for user in ["b", "c", "q", "x"]:                    # Try four different inputs
    print(f"--- input: {user} ---")                 # Label each test
    print(graph.invoke(State(nlist=[user])))         # Run and print the final State

# ============================================================
# 7. OUTPUT (checked by running it; the diagram text comes first)
# ============================================================
# --- input: b ---
# {'nlist': ['b', 'b', 'B']}           <- 'b' twice: the starting 'b' plus the update that node a added
# --- input: c ---
# {'nlist': ['c', 'c', 'C']}
# --- input: q ---
# {'nlist': ['q', 'q']}                <- goto=END, so the graph stopped after node a
# --- input: x ---
# {'nlist': ['x', 'x']}
#
# Notice: compare with file a. The double 'b' appears because this node's update ADDS select again.