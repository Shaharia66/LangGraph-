# ============================================================
# 1. IMPORTS
# ============================================================
from IPython.display import Image, display           # Notebook-only picture tools; NOT used in this .py file
import operator                                      # operator.add is the reducer for nlist
from typing import Annotated, List, Literal, TypedDict  # Literal is used for the Command type hint
from langgraph.graph import END, START, StateGraph   # Entry/exit points and the graph builder
from langgraph.types import Command, interrupt       # Command is used NOW; interrupt is for Lesson 5
from langgraph.checkpoint.memory import InMemorySaver  # NEW: the checkpointer that saves State in memory (RAM)

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State(TypedDict):                              # The shared whiteboard
    nlist: Annotated[List[str], operator.add]        # List with a reducer: new input is ADDED to the saved list

# ============================================================
# 3. DEFINE THE NODES (same as Lesson 3, Command version)
# ============================================================
def node_a(state: State) -> Command[Literal["b", "c", "__end__"]]:  # Decision node; the hint lists where it may jump
    select = state["nlist"][-1]                      # Take the LAST item of nlist (the newest message)
    if select == "b":                                # If the newest message is "b"...
        next_node = "b"                              # ...go to node "b"
    elif select == "c":                              # If it is "c"...
        next_node = "c"                              # ...go to node "c"
    elif select == "q":                              # If it is "q"...
        next_node = END                              # ...stop the graph
    else:                                            # For anything else...
        next_node = END                              # ...also stop the graph
    return Command(                                  # Return a State update AND the next node together
        update=State(nlist=[select]),                # Add the message to nlist again (this is why letters appear twice)
        goto=next_node                               # Which node runs next
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

# ============================================================
# 5. ADD MEMORY (the new part of this lesson)
# ============================================================
memory = InMemorySaver()                             # Create the checkpointer; it will store a checkpoint after every step
config = {"configurable": {"thread_id": "1"}}        # Choose the thread (save slot) named "1"; same id = same memory
graph = builder.compile(checkpointer=memory)         # Compile the graph WITH the checkpointer attached

# ============================================================
# 6. RUN THE LOOP
# ============================================================
while True:                                          # Repeat until we break out
    user = input("b, c, or q to quit: ")             # Ask you to type b, c, or q
    input_state = State(nlist=[user])                # Wrap what you typed in a State
    result = graph.invoke(input_state, config)       # Run the graph; the config tells it WHICH thread's memory to use
    print(result)                                    # Print the full State (it includes everything from earlier turns)
    if result["nlist"][-1] == "q":                   # If the last item is "q"...
        print("quit")                                # ...say we are quitting
        break                                        # ...and leave the loop

# ============================================================
# 7. OUTPUT (checked by running it; type  b, c, b, q  in that order)
# ============================================================
# {'nlist': ['b', 'b', 'B']}
# {'nlist': ['b', 'b', 'B', 'c', 'c', 'C']}
# {'nlist': ['b', 'b', 'B', 'c', 'c', 'C', 'b', 'b', 'B']}
# {'nlist': ['b', 'b', 'B', 'c', 'c', 'C', 'b', 'b', 'B', 'q', 'q']}
# quit
#
# Notice: the list KEEPS GROWING across invokes. That is the memory.
# Notice: the memory is gone when the program ends, because InMemorySaver lives in RAM.