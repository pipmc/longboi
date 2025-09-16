# Game Server

A Python HTTP server game with 100 rounds, oracle, and move validation.

## Features

- **100 Rounds**: Numbered 1 to 100
- **Unique Codes**: Each round has four unique code numbers (A, B, C, D) between 1-10000
- **Oracle**: Returns the four code numbers hidden among 10,000 random words
- **Move Validation**: Submit moves to advance through rounds
- **Status Tracking**: Check current round and win status

## API Endpoints

### GET /oracle
Returns text/plain with:
1. First code number is XXX
2. Second code number is XXX  
3. 10,000 random words
4. Third code number is XXX
5. Fourth code number is XXX

### POST /move
Submit a move with JSON body:
```json
{"A": 1234, "B": 5678, "C": 9012, "D": 3456}
```

Returns JSON response:
```json
{"status": "correct", "message": "Round 1 completed! Moving to round 2"}
```

### GET /status
Returns JSON with current game state:
```json
{"round": 1, "won": false}
```

## Usage

### Start the Server
```bash
python3 server.py
```

The server will start on port 7978.

### Manual Testing
```bash
# Check status
curl http://localhost:7978/status

# Get oracle (first few lines)
curl http://localhost:7978/oracle | head -5

# Submit a move
curl -X POST -H "Content-Type: application/json" \
  -d '{"A": 1234, "B": 5678, "C": 9012, "D": 3456}' \
  http://localhost:7978/move
```

### Automated Testing
```bash
# Run the test client (requires requests library)
python3 test_client.py
```

## Game Rules

1. Each round has four unique code numbers (A, B, C, D)
2. Use the oracle to find the code numbers hidden among random words
3. Submit the correct four numbers to advance to the next round
4. Complete all 100 rounds to win the game
5. Codes are unique across all rounds and regenerated for each new game

## Requirements

- Python 3.6+
- No external dependencies (uses only built-in libraries)
- For test client: `requests` library (`pip install requests`)
