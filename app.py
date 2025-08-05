from flask import Flask, request, jsonify, render_template
from collections import deque

app = Flask(__name__)

def fifo(reference_string, frame_count):
    frames = deque()
    steps = []
    faults = 0

    for page in reference_string:
        fault = False
        if page not in frames:
            fault = True
            if len(frames) >= frame_count:
                frames.popleft()
            frames.append(page)
            faults += 1

        steps.append({
            "page": page,
            "frames": list(frames) + [None] * (frame_count - len(frames)),
            "page_fault": fault
        })

    return steps, faults

def lru(reference_string, frame_count):
    frames = []
    usage = {}
    steps = []
    faults = 0

    for i, page in enumerate(reference_string):
        fault = False
        if page not in frames:
            fault = True
            if len(frames) >= frame_count:
                lru_page = min(usage, key=usage.get)
                frames.remove(lru_page)
                usage.pop(lru_page)
            frames.append(page)
            faults += 1
        usage[page] = i

        steps.append({
            "page": page,
            "frames": frames[:] + [None] * (frame_count - len(frames)),
            "page_fault": fault
        })

    return steps, faults

def optimal(reference_string, frame_count):
    frames = []
    steps = []
    faults = 0

    for i, page in enumerate(reference_string):
        fault = False
        if page not in frames:
            fault = True
            if len(frames) < frame_count:
                frames.append(page)
            else:
                future = reference_string[i+1:]
                indices = [future.index(p) if p in future else float('inf') for p in frames]
                replace_index = indices.index(max(indices))
                frames[replace_index] = page
            faults += 1

        steps.append({
            "page": page,
            "frames": frames[:] + [None] * (frame_count - len(frames)),
            "page_fault": fault
        })

    return steps, faults

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.json
    reference_string = list(map(int, data['reference_string'].split()))
    frame_count = int(data['frames'])
    algorithm = data['algorithm']

    if algorithm == 'FIFO':
        steps, faults = fifo(reference_string, frame_count)
    elif algorithm == 'LRU':
        steps, faults = lru(reference_string, frame_count)
    elif algorithm == 'OPT':
        steps, faults = optimal(reference_string, frame_count)
    else:
        return jsonify({"error": "Invalid algorithm"}), 400

    return jsonify({"steps": steps, "faults": faults})

if __name__ == "__main__":
    app.run(debug=True)
