# ============================================================
# 1. IMPORTS
# ============================================================
import operator                                      # operator.add is the reducer for the log list
from typing import Annotated, List, Literal, TypedDict  # Literal is used for the router's return type
from langgraph.graph import END, START, StateGraph   # Entry/exit points and the graph builder

# ============================================================
# 2. DEFINE THE STATE
# ============================================================
class State(TypedDict):                              # The shared whiteboard
    count: int                                       # A counter; no reducer, so each update REPLACES it
    log: Annotated[List[str], operator.add]          # A log list; reducer, so each update is ADDED

# ============================================================
# 3. DEFINE THE NODE AND THE ROUTER
# ============================================================
def work(state: State):                              # The node that will run repeatedly
    new_count = state["count"] + 1                   # Add 1 to the counter
    print(f"work runs, count is now {new_count}")    # Show each run so you can count them
    return {"count": new_count, "log": [f"work #{new_count}"]}  # Update the counter and add a log line

def should_continue(state: State) -> Literal["again", "done"]:  # The router: answers with a LABEL, not a node name
    if state["count"] < 3:                           # If we have run fewer than 3 times...
        return "again"                               # ...say "again"
    return "done"                                    # Otherwise say "done"

# ============================================================
# 4. BUILD THE GRAPH WITH A PATH MAP
# ============================================================
builder = StateGraph(State)                          # Create the builder
builder.add_node("work", work)                       # Register the node "work"
builder.add_edge(START, "work")                      # FIXED edge: begin at "work"
builder.add_conditional_edges(                       # CONDITIONAL edge with a path map
    "work",                                          # After "work" finishes, call the router
    should_continue,                                 # The router function
    {"again": "work", "done": END},                  # PATH MAP: label "again" -> node "work" (a LOOP), label "done" -> END
)                                                    # End of the conditional edge
graph = builder.compile()                            # Compile the graph

# ============================================================
# 5. RUN THE LOOP
# ============================================================
print(graph.invoke({"count": 0, "log": []}))         # Start with count 0 and an empty log, run, print the final State

# ============================================================
# 6. A LOOP THAT NEVER STOPS (with a safety limit)
# ============================================================
def forever(state: State) -> Literal["again"]:       # A bad router that always says "again"
    return "again"                                   # Never says "done"

b2 = StateGraph(State)                               # Create a second builder
b2.add_node("work", work)                            # Register the same node
b2.add_edge(START, "work")                           # Begin at "work"
b2.add_conditional_edges("work", forever, {"again": "work"})  # Always loop back to "work"
g2 = b2.compile()                                    # Compile the graph
try:                                                 # Try to run it, but be ready for an error
    g2.invoke({"count": 0, "log": []}, {"recursion_limit": 5})  # Allow at most 5 steps (a small limit on purpose)
except Exception as e:                               # Catch the error LangGraph raises
    print(type(e).__name__)                          # Print the error's name

# ============================================================
# 7. OUTPUT (checked by running it)
# ============================================================
# work runs, count is now 1
# work runs, count is now 2
# work runs, count is now 3
# {'count': 3, 'log': ['work #1', 'work #2', 'work #3']}     <- the loop stopped by itself after 3 runs
# work runs, count is now 1
# work runs, count is now 2
# work runs, count is now 3
# work runs, count is now 4
# work runs, count is now 5
# GraphRecursionError                                        <- LangGraph stopped the endless loop at the limit of 5