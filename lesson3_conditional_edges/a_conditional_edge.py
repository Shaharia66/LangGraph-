# ============================================================
# 1. IMPORTS
# ============================================================
from IPython.display import Image, display           # Notebook-only picture tools; NOT used in this .py file
import operator                                      # operator.add is the reducer for nlist
from typing import Annotated, List, Literal, TypedDict  # Literal is used NOW (router return type); the rest as before
from langgraph.graph import END, START, StateGraph   # Entry/exit points and the graph builder
from langgraph.types import Command, interrupt       # Command is used in file b; interrupt is for Lesson 5

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State(TypedDict):                              # The shared whiteboard
    nlist: Annotated[List[str], operator.add]        # A list with a reducer: every update is ADDED to the old list

# ============================================================
# 3. DEFINE THE NODES
# ============================================================
def node_a(state: State):                            # The decision-point node
    print(f"node a sees {state['nlist']}")           # Show what node a sees (added by me so you can follow the flow)
    return                                           # Return nothing: no State update; the router does the deciding

def node_b(state: State) -> State:                   # Road 1
    return State(nlist=["B"])                        # Add "B" to the list

def node_c(state: State) -> State:                   # Road 2
    return State(nlist=["C"])                        # Add "C" to the list

# ============================================================
# 4. DEFINE THE ROUTER (the traffic officer)
# ============================================================
def conditional_edge(state: State) -> Literal["b", "c", "__end__"]:  # Reads the State, returns the NAME of the next node (or END)
    select = state["nlist"][-1]                      # Take the LAST item of nlist (the newest message)
    if select == "b":                                # If the user typed "b"...
        return "b"                                   # ...go to node "b"
    elif select == "c":                              # If the user typed "c"...
        return "c"                                   # ...go to node "c"
    elif select == "q":                              # If the user typed "q" (quit)...
        return END                                   # ...stop the graph
    else:                                            # For any other input...
        return END                                   # ...also stop the graph

# ============================================================
# 5. BUILD THE GRAPH
# ============================================================
builder = StateGraph(State)                          # Create the builder and tell it what our State looks like

# Add nodes
builder.add_node("a", node_a)                        # Register node "a"
builder.add_node("b", node_b)                        # Register node "b"
builder.add_node("c", node_c)                        # Register node "c"

# Add edges
builder.add_edge(START, "a")                         # FIXED edge: the graph begins at "a"
builder.add_edge("b", END)                           # FIXED edge: after "b", finish
builder.add_edge("c", END)                           # FIXED edge: after "c", finish
builder.add_conditional_edges("a", conditional_edge) # CONDITIONAL edge: after "a", the router picks the next node

# Compile
graph = builder.compile()                            # Check the graph is valid and make it runnable

# ============================================================
# 6. DRAW THE GRAPH
# ============================================================
print(graph.get_graph().draw_mermaid())              # Print the diagram as text; "-.->" lines are the dotted conditional edges
# display(Image(graph.get_graph().draw_mermaid_png())) # Notebook only: draw the graph as a picture (needs internet)

# ============================================================
# 7. RUN AUTOMATIC TESTS
# ============================================================
for user in ["b", "c", "q", "x"]:                    # Try four different inputs, one after another
    print(f"--- input: {user} ---")                 # Label each test
    print(graph.invoke(State(nlist=[user])))         # Run the graph with that input as the first list item and print the final State

# ============================================================
# 8. INTERACTIVE LOOP (like the course)
# ============================================================
while True:                                          # Repeat forever until we break out
    user = input("b, c, or q to quit: ")             # Ask you to type b, c, or q
    result = graph.invoke(State(nlist=[user]))       # Run the graph with what you typed as the starting State
    print(result)                                    # Print the final State
    if user == "q":                                  # If you typed q...
        break                                        # ...leave the loop and end the program

# ============================================================
# 9. OUTPUT (checked by running it; the diagram text comes first)
# ============================================================
# --- input: b ---
# node a sees ['b']
# {'nlist': ['b', 'B']}                <- router chose "b", node b added "B"
# --- input: c ---
# node a sees ['c']
# {'nlist': ['c', 'C']}                <- router chose "c", node c added "C"
# --- input: q ---
# node a sees ['q']
# {'nlist': ['q']}                     <- router returned END, so neither b nor c ran
# --- input: x ---
# node a sees ['x']
# {'nlist': ['x']}                     <- any unknown input also ends the graph