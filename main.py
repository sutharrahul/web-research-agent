from ddgs import DDGS
import redis
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Optional


class AgentState(TypedDict):
    user_search: str
    search_results: Optional[list[dict]]
    summary: str
    cached: bool


r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

user_search = input("🔎 Search with Ai > ")


def check_cache(state: AgentState) -> AgentState:
    pre_search_result = r.get(state["user_search"])
    if pre_search_result:
        state["summary"] = pre_search_result
        state["cached"] = True
    else:
        state["cached"] = False

    return state


def search(state: AgentState):
    with DDGS() as ddgs:
        result = ddgs.text(state["user_search"], max_results=5)
        state["search_results"] = [item["body"] for item in result]

    return state


def summarize(state: AgentState):

    llm = ChatOllama(model="gemma3:4b")

    SYSTEM_PROMPT = f"""
    You are a research assistant. Summarize the following search result in clearly 

    Search result :
    {state['search_results']}
    """
    message = [("system", SYSTEM_PROMPT), ("user", state["user_search"])]

    res = llm.invoke(message)
    state["summary"] = res.content

    return state


def save_cache(state: AgentState):
    r.set(state["user_search"], state["summary"], ex=300)
    return state


def evaluate_response(state: AgentState) -> str:
    if state["cached"]:
        return END
    else:
        return "search"


graph_builder = StateGraph(AgentState)

graph_builder.add_node("check_cache", check_cache)
graph_builder.add_node("search", search)
graph_builder.add_node("summarize", summarize)
graph_builder.add_node("save_cache", save_cache)
# graph_builder.add_node("evaluate_response",evaluate_response)

graph_builder.add_edge(START, "check_cache")
graph_builder.add_conditional_edges("check_cache", evaluate_response)
graph_builder.add_edge("search", "summarize")
graph_builder.add_edge("summarize", "save_cache")
graph_builder.add_edge("save_cache", END)

app = graph_builder.compile()

aap_result = app.invoke(
    {
        "user_search": user_search,
        "search_results": None,
        "summary": None,
        "cached": False,
    }
)

print(f"🚀 Summary ---> {aap_result['summary']}")
