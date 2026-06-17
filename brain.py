from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME, MAX_NAME
from memory import fetch_relevant_memories, save_memory
import actions
import json

client = Groq(api_key=GROQ_API_KEY)

conversation_history = []

# ─── MEMORY CONTEXT ───────────────────────────────────────────────────────────

def _build_memory_context(user_input: str) -> str:
    relevant = fetch_relevant_memories(user_input)
    if not relevant:
        return ""
    memory_block = "\n".join(relevant)
    return f"\n\nRelevant memories from past sessions:\n{memory_block}"

# ─── ACTION ROUTER ────────────────────────────────────────────────────────────

def _route_action(user_input: str):
    prompt = f"""You are an action classifier for a personal AI assistant called {MAX_NAME}.

Classify this user input and respond ONLY with a JSON object.

User input: "{user_input}"

If this is an action request, respond with:
{{"type": "action", "action": "<action_name>", "params": {{}}}}

Available actions and their params:
- open_app: {{"app": "app name"}}
- open_website: {{"site": "site name or search query"}}
- open_folder: {{"name": "folder name"}}
- open_file: {{"folder": "folder name", "file": "filename"}}
- register_folder: {{"name": "friendly name", "path": "full folder path"}}
- list_folders: {{}}
- rescan_apps: {{}}

IMPORTANT RULES:
- If the user says "open X" and X sounds like a game, software, or desktop app (even if unfamiliar), use open_app NOT open_website.
- Only use open_website if the user explicitly says "search for", "go to", "open the website", or names a clear website/URL.
- When in doubt between open_app and open_website, always prefer open_app.

If this is just conversation (questions, chat, memory-related, anything else), respond with:
{{"type": "conversation"}}

No explanation. No markdown. Just the JSON."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        if data.get("type") == "conversation":
            return None

        action = data.get("action")
        params = data.get("params", {})

        if action == "open_app":
            return actions.open_app(params.get("app", ""))
        elif action == "open_website":
            return actions.open_website(params.get("site", ""))
        elif action == "open_folder":
            return actions.open_registered_folder(params.get("name", ""))
        elif action == "open_file":
            return actions.open_file_in_folder(params.get("folder", ""), params.get("file", ""))
        elif action == "register_folder":
            return actions.register_folder(params.get("name", ""), params.get("path", ""))
        elif action == "list_folders":
            return actions.list_registered_folders()
        elif action == "rescan_apps":
            return actions.rescan_apps()
        else:
            return None

    except Exception:
        return None

# ─── AUTO MEMORY SAVE ─────────────────────────────────────────────────────────

def _auto_save_memories(user_input: str, reply: str):
    prompt = f"""You are a memory extraction assistant for a personal AI called {MAX_NAME}.

Given this exchange, extract anything worth remembering long-term (projects, preferences, investments, tasks, goals, or personal facts).
If nothing is worth saving, return an empty list.

User said: "{user_input}"
{MAX_NAME} replied: "{reply}"

Respond ONLY with a JSON array like:
[
  {{"category": "project", "content": "User is building MAX Phase 3 with PC automation"}},
  {{"category": "investment", "content": "User invested in UTI Nifty 50 Direct Growth via SIP"}}
]

If nothing to save: []
No explanation. No markdown. Just the JSON array."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        memories = json.loads(raw)
        for item in memories:
            if "category" in item and "content" in item:
                save_memory(item["category"], item["content"])
    except Exception:
        pass

# ─── MAIN ENTRY POINT ─────────────────────────────────────────────────────────

def ask_max(user_input: str) -> str:

    # 1. Check if it's an action first
    action_result = _route_action(user_input)
    if action_result:
        return action_result

    # 2. Fetch relevant memories
    memory_context = _build_memory_context(user_input)

    # 3. Build system prompt
    system_prompt = (
    f"You are {MAX_NAME}, a personal AI assistant with voice input and output — "
    f"the user speaks to you via speech-to-text and hears your replies via "
    f"text-to-speech. Never claim to be text-only or unable to speak. "
    f"However, write ONLY plain conversational text that should be spoken aloud — "
    f"never include stage directions, action descriptions, or tone/emotion cues "
    f"in parentheses or asterisks (e.g. do not write '(smiling)' or "
    f"'*speaks warmly*'). Be concise, helpful, and direct."
    f"{memory_context}"
)
    # 4. Add to history and call Groq
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            *conversation_history
        ]
    )

    reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    # 5. Auto-save anything worth remembering
    _auto_save_memories(user_input, reply)

    return reply