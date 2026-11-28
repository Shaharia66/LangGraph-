# ============================================================
# 1. IMPORTS
# ============================================================
import operator                                      # operator.add is the reducer for nlist
from typing import Annotated, List, Literal, TypedDict  # Literal is used for the Command type hint
from langgraph.graph import END, START, StateGraph   # Entry/exit points and the graph builder
from langgraph.types import Command                  # Command lets a node update the State and choose the next node
from langgraph.checkpoint.memory import InMemorySaver  # The checkpointer that saves State in memory (RAM)

# ============================================================
# 2. DEFINE THE STATE AND NODES
# ============================================================
class State(TypedDict):                              # The shared whiteboard
    nlist: Annotated[List[str], operator.add]        # List with a reducer: updates are ADDED

def node_a(state: State) -> Command[Literal["b", "c", "__end__"]]:  # Decision node
    select = state["nlist"][-1]                      # Take the LAST item of nlist
    if select == "b":                                # If it is "b"...
        next_node = "b"                              # ...go to "b"
    elif select == "c":                              # If it is "c"...
        next_node = "c"                              # ...go to "c"
    else:                                            # For "q" or anything else...
        next_node = END                              # ...stop the graph
    return Command(update=State(nlist=[select]), goto=next_node)  # Update the State and choose the next node

def node_b(state: State) -> State:                   # Road 1
    return State(nlist=["B"])                        # Add "B"

def node_c(state: State) -> State:                   # Road 2
    return State(nlist=["C"])                        # Add "C"

# ============================================================
# 3. BUILD THE BUILDER (compiled in different ways below)
# ============================================================
builder = StateGraph(State)                          # Create the builder
builder.add_node("a", node_a)                        # Register node "a"
builder.add_node("b", node_b)                        # Register node "b"
builder.add_node("c", node_c)                        # Register node "c"
builder.add_edge(START, "a")                         # Begin at "a"
builder.add_edge("b", END)                           # After "b", finish
builder.add_edge("c", END)                           # After "c", finish

# ============================================================
# 4. WITHOUT MEMORY
# ============================================================
print("--- 1. Without memory ---")                   # Section label
graph_no_memory = builder.compile()                  # Compile with NO checkpointer
print(graph_no_memory.invoke(State(nlist=["b"])))    # First run
print(graph_no_memory.invoke(State(nlist=["c"])))    # Second run: it knows NOTHING about the first one

# ============================================================
# 5. WITH MEMORY: TWO SEPARATE THREADS
# ============================================================
print("--- 2. With memory: two threads ---")         # Section label
graph = builder.compile(checkpointer=InMemorySaver())  # Compile WITH a checkpointer
thread_1 = {"configurable": {"thread_id": "1"}}      # Save slot number 1
thread_2 = {"configurable": {"thread_id": "2"}}      # Save slot number 2
print("thread 1:", graph.invoke(State(nlist=["b"]), thread_1))  # Thread 1, first message
print("thread 1:", graph.invoke(State(nlist=["c"]), thread_1))  # Thread 1, second message: it REMEMBERS the first
print("thread 2:", graph.invoke(State(nlist=["c"]), thread_2))  # Thread 2: a fresh start, no mixing with thread 1
print("thread 1:", graph.invoke(State(nlist=["q"]), thread_1))  # Back to thread 1: its memory is still there

# ============================================================
# 6. READ THE SAVED STATE
# ============================================================
print("--- 3. Read the saved state ---")             # Section label
snapshot = graph.get_state(thread_1)                 # Ask for the latest saved snapshot of thread 1
print(snapshot.values)                               # The saved State (the same as the last result)
print(snapshot.next)                                 # Which nodes would run next; () means the run is finished

# ============================================================
# 7. LOOK AT THE CHECKPOINT HISTORY
# ============================================================
print("--- 4. Checkpoint history (newest first) ---")  # Section label
history = list(graph.get_state_history(thread_1))    # Get ALL saved snapshots of thread 1 as a list
print("checkpoints:", len(history))                  # How many snapshots exist
for item in history:                                 # Go through them one by one
    print(item.metadata["step"], item.next, item.values["nlist"])  # step number, nodes still to run, saved list

# ============================================================
# 8. TIME TRAVEL
# ============================================================
print("--- 5. Time travel: continue from an earlier checkpoint ---")  # Section label
earlier = [item for item in history if item.metadata["step"] == 2][0]  # Find the snapshot at step 2 (after the first run finished)
print("going back to:", earlier.values["nlist"])     # Show what the State looked like at that point
print("new result:", graph.invoke(State(nlist=["c"]), earlier.config))  # Continue from THAT snapshot with a new input

# ============================================================
# 9. THE COMMON MISTAKE
# ============================================================
print("--- 6. Forgetting the thread_id ---")         # Section label
try:                                                 # Try to run without a config
    graph.invoke(State(nlist=["b"]))                 # No thread_id given
except Exception as e:                               # Catch the error LangGraph raises
    print(type(e).__name__)                          # Print the error's name

# ============================================================
# 10. OUTPUT (checked by running it)
# ============================================================
# --- 1. Without memory ---
# {'nlist': ['b', 'b', 'B']}
# {'nlist': ['c', 'c', 'C']}                         <- no trace of the first run
# --- 2. With memory: two threads ---
# thread 1: {'nlist': ['b', 'b', 'B']}
# thread 1: {'nlist': ['b', 'b', 'B', 'c', 'c', 'C']}   <- remembers the first message
# thread 2: {'nlist': ['c', 'c', 'C']}                  <- separate thread, fresh start
# thread 1: {'nlist': ['b', 'b', 'B', 'c', 'c', 'C', 'q', 'q']}
# --- 3. Read the saved state ---
# {'nlist': ['b', 'b', 'B', 'c', 'c', 'C', 'q', 'q']}
# ()
# --- 4. Checkpoint history (newest first) ---
# checkpoints: 11
# 9 () ['b', 'b', 'B', 'c', 'c', 'C', 'q', 'q']
# 8 ('a',) ['b', 'b', 'B', 'c', 'c', 'C', 'q']
# 7 ('__start__',) ['b', 'b', 'B', 'c', 'c', 'C']
# 6 () ['b', 'b', 'B', 'c', 'c', 'C']
# 5 ('c',) ['b', 'b', 'B', 'c', 'c']
# 4 ('a',) ['b', 'b', 'B', 'c']
# 3 ('__start__',) ['b', 'b', 'B']
# 2 () ['b', 'b', 'B']
# 1 ('b',) ['b', 'b']
# 0 ('a',) ['b']
# -1 ('__start__',) []
# --- 5. Time travel: continue from an earlier checkpoint ---
# going back to: ['b', 'b', 'B']
# new result: {'nlist': ['b', 'b', 'B', 'c', 'c', 'C']}
# --- 6. Forgetting the thread_id ---
# ValueError
