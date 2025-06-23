from fastapi import FastAPI
from pydantic import BaseModel

from .llm import (
    answer_question,
    detect_intent,
    generate_patch,
    generate_shell_command,
    generate_script,
)
from .tasks import apply_patch_and_build, run_shell_command, save_and_maybe_run_script

app = FastAPI(title="Local MCP Server")


class CommandRequest(BaseModel):
    text: str


@app.post("/command")
async def command(req: CommandRequest):
    intent = detect_intent(req.text)
    if intent == "modify_code":
        patch = generate_patch(req.text)
        result = apply_patch_and_build(patch)
        return {"intent": intent, "result": result}
    elif intent == "shell_command":
        cmd = generate_shell_command(req.text)
        output = run_shell_command(cmd)
        return {"intent": intent, "command": cmd, "output": output}
    elif intent == "generate_script":
        info = generate_script(req.text)
        output = save_and_maybe_run_script(info)
        return {"intent": intent, "info": info, "output": output}
    else:
        answer = answer_question(req.text)
        return {"intent": "ask_question", "answer": answer}
