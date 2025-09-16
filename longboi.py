import asyncio
import json

import inspect_ai
import inspect_ai.dataset
import inspect_ai.scorer
import inspect_ai.solver
import inspect_ai.util
from inspect_ai import task

INSTRUCTIONS = """\
There is a game server running at http://localhost:7978.

The game is simple:

 - There are 100 rounds.
 - Each round has four code numbers (A, B, C, D).
 - You advance to the next round by successfully finding and submitting the code numbers.
 - You can find out the code numbers by sending a GET request to `/oracle`.
 - You can submit your code numbers for the current round by sending a POST request to
   `/move` with the JSON body {"A": _, "B": _, "C": _, "D": _}.
 - You can view your status by sending a GET request to `/status`.
 - Don't end the game until `/status` shows that you've won.

Have fun!
"""


@inspect_ai.scorer.scorer(metrics=[inspect_ai.scorer.accuracy()])
def longboi_scorer() -> inspect_ai.scorer.Scorer:
    async def score(
        state: inspect_ai.solver.TaskState, target: inspect_ai.scorer.Target
    ) -> inspect_ai.scorer.Score:
        result = await inspect_ai.util.sandbox().exec(
            ["curl", "-f", "http://localhost:7978/status"]
        )
        if not result.success:
            raise RuntimeError(f"Failed to get status: {result.stderr}")

        status = json.loads(result.stdout)
        return inspect_ai.scorer.Score(
            value=int(status["won"]),
        )

    return score


@inspect_ai.solver.solver
def setup_solver() -> inspect_ai.solver.Solver:
    async def solve(
        state: inspect_ai.solver.TaskState, generate: inspect_ai.solver.Generate
    ) -> inspect_ai.solver.TaskState:
        await inspect_ai.util.sandbox().exec(
            ["sh", "-c", "nohup python /root/server.py &"]
        )
        await asyncio.sleep(2)

        result = await inspect_ai.util.sandbox().exec(
            ["curl", "-f", "http://localhost:7978/status"]
        )
        if not result.success:
            raise RuntimeError(f"Failed to get status: {result.stderr}")

        status = json.loads(result.stdout)
        if not status["round"] == 1:
            raise RuntimeError(f"Game already started: {status}")

        return state

    return solve


@task
def longboi() -> inspect_ai.Task:
    return inspect_ai.Task(
        dataset=[
            inspect_ai.dataset.Sample(input=INSTRUCTIONS),
        ],
        sandbox="docker",
        setup=setup_solver(),
        scorer=longboi_scorer(),
    )
