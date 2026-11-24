# ============================================================
# 1. IMPORTS
# ============================================================
from IPython.display import Image, display           # Show pictures inside a Jupyter notebook; NOT used in this .py file
import operator                                      # operator.add joins two lists together; used here as the reducer
from typing import Annotated, List, Literal, TypedDict  # Annotated, List and TypedDict are used here; Literal is for later lessons
from langgraph.graph import END, START, StateGraph   # END and START = exit and entry points, StateGraph = the graph builder
from langgraph.types import Command, interrupt       # For later lessons (routing and human-in-the-loop); not used yet

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State2(TypedDict):                             # A State with two keys
    nlist: Annotated[List[str], operator.add]        # Annotated attaches a reducer: new lists are ADDED to the old list instead of replacing it
    count: int                                       # No reducer here, so each update to "count" REPLACES the old value

# ============================================================
# 3. DEFINE THE NODES
# ============================================================
def step_a(state: State2):                           # First node; it receives the current State
    print(f"step_a receives {state['nlist']}")       # Show what this node sees when it starts
    return {                                         # Return a plain dict; only the keys we want to update are needed
        "nlist": ["Hello from step_a"],              # The reducer adds this list to the end of the existing nlist
        "count": state["count"] + 1,                 # Read the old count, add 1, and replace the old count with it
    }                                                # End of the update

def step_b(state: State2):                           # Second node; it also receives the current State
    print(f"step_b receives {state['nlist']}")       # Show what this node sees (it should include step_a's message)
    return {                                         # Return only the keys to update
        "nlist": ["Hello from step_b"],              # The reducer appends this message after the others
        "count": state["count"] + 1,                 # Add 1 to count again (replace with the new value)
    }                                                # End of the update

# ============================================================
# 4. BUILD THE GRAPH
# ============================================================
builder2 = StateGraph(State2)                        # Create a builder using this State
builder2.add_node("a", step_a)                       # Register the first node with the name "a"
builder2.add_node("b", step_b)                       # Register the second node with the name "b"
builder2.add_edge(START, "a")                        # Start the graph at node "a"
builder2.add_edge("a", "b")                          # After "a", always go to "b"
builder2.add_edge("b", END)                          # After "b", finish the graph
graph2 = builder2.compile()                          # Compile the graph so it can run

# ============================================================
# 5. DRAW THE GRAPH
# ============================================================
print(graph2.get_graph().draw_mermaid())             # Print the graph diagram as text (works in a script, no internet needed)
# display(Image(graph2.get_graph().draw_mermaid_png())) # Notebook only: draw the graph as a picture (needs internet); keep it commented in a .py file

# ============================================================
# 6. RUN THE GRAPH
# ============================================================
result = graph2.invoke({"nlist": ["Start"], "count": 0})  # Run with a starting State; a plain dict works as input
print(result)                                        # Print the final State

# ============================================================
# 7. OUTPUT (what you should see after the diagram text; check that yours matches)
# ============================================================
# step_a receives ['Start']
# step_b receives ['Start', 'Hello from step_a']
# {'nlist': ['Start', 'Hello from step_a', 'Hello from step_b'], 'count': 2}
#
# Notice: nlist GREW (reducer), count was REPLACED (0, then 1, then 2).

