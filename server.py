#!/usr/bin/env python3
"""Game server with 100 rounds, oracle, and move validation."""

import json
import random
import secrets
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, TypedDict, override
from urllib.parse import urlparse

# Fixed list of 12 words for the oracle
WORDS = (
    "apple",
    "banana",
    "cherry",
    "dragon",
    "elephant",
    "forest",
    "guitar",
    "happiness",
    "island",
    "journey",
    "kingdom",
    "lightning",
)


# Global game state shared across all requests
class GameState(TypedDict):
    round: int
    won: bool
    codes: dict[int, dict[str, int]]


game_state: GameState = {
    "round": 1,
    "won": False,
    "codes": {},
}


def generate_codes():
    """Generate unique codes for all 100 rounds."""
    global game_state
    used_codes: set[int] = set()
    for round_num in range(1, 101):
        codes: list[int] = []
        for _ in range(4):  # A, B, C, D
            while True:
                code = secrets.randbelow(10000) + 1  # 1 to 10000 inclusive
                if code not in used_codes:
                    used_codes.add(code)
                    codes.append(code)
                    break
        game_state["codes"][round_num] = {
            "A": codes[0],
            "B": codes[1],
            "C": codes[2],
            "D": codes[3],
        }


class GameServer(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/oracle":
            self.handle_oracle()
        elif parsed_path.path == "/status":
            self.handle_status()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/move":
            self.handle_move()
        else:
            self.send_error(404, "Not Found")

    def handle_oracle(self):
        """Return oracle information for current round."""
        global game_state

        if game_state["won"]:
            self.send_error(400, "Game already completed")
            return

        current_round = game_state["round"]
        codes = game_state["codes"][current_round]

        # Generate 10000 random words
        random_words = [random.choice(WORDS) for _ in range(10000)]

        # Build response
        response_lines = [
            f"First code number is {codes['A']}",
            f"Second code number is {codes['B']}",
            *random_words,
            f"Third code number is {codes['C']}",
            f"Fourth code number is {codes['D']}",
        ]

        response_text = "\n".join(response_lines)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(response_text.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(response_text.encode("utf-8"))

    def handle_move(self):
        """Handle move submission."""
        global game_state

        if game_state["won"]:
            self.send_error(400, "Game already completed")
            return

        # Read POST data
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            # Parse JSON data
            move_data = json.loads(post_data.decode("utf-8"))

            # Extract the four numbers (assuming they're provided as A, B, C, D)
            if not all(key in move_data for key in ["A", "B", "C", "D"]):
                self.send_error(400, "Missing required fields: A, B, C, D")
                return

            submitted_codes = {
                "A": int(move_data["A"]),
                "B": int(move_data["B"]),
                "C": int(move_data["C"]),
                "D": int(move_data["D"]),
            }

            current_round = game_state["round"]
            correct_codes = game_state["codes"][current_round]

            # Check if all codes match
            if submitted_codes == correct_codes:
                # Advance to next round
                if current_round < 100:
                    game_state["round"] += 1
                    response = {
                        "status": "correct",
                        "message": f"Round {current_round} completed! Moving to round {game_state['round']}",
                    }
                else:
                    # Game won!
                    game_state["won"] = True
                    response = {
                        "status": "won",
                        "message": "Congratulations! You've completed all 100 rounds!",
                    }
            else:
                response = {
                    "status": "incorrect",
                    "message": "Incorrect codes. Try again.",
                }

            # Send response
            response_json = json.dumps(response)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_json.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(response_json.encode("utf-8"))

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.send_error(400, f"Invalid request data: {str(e)}")

    def handle_status(self):
        """Return current game status."""
        global game_state

        status_json = json.dumps(
            {"round": game_state["round"], "won": game_state["won"]}
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(status_json.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(status_json.encode("utf-8"))

    @override
    def log_message(self, format: str, *args: Any):
        """Override to customize logging."""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server(port: int = 7978):
    """Start the game server."""
    # Generate codes before starting server
    generate_codes()

    server_address = ("", port)
    httpd = HTTPServer(server_address, GameServer)

    print(f"Game server starting on port {port}")
    print("Endpoints:")
    print("  GET  /oracle  - Get oracle information for current round")
    print("  POST /move    - Submit move (JSON with A, B, C, D fields)")
    print("  GET  /status  - Get current game status")
    print("\nExample move JSON:")
    print('  {"A": 1234, "B": 5678, "C": 9012, "D": 3456}')
    print("\nPress Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server(7978)
