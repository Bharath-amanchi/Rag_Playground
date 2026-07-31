from collections import defaultdict

chat_history = defaultdict(list)


def add_message(session_id, role, content):
    chat_history[session_id].append(
        {
            "role": role,
            "content": content,
        }
    )


def get_history(session_id):
    return chat_history.get(session_id, [])