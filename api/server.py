from flask import Flask, request, jsonify  # type: ignore
import subprocess

app = Flask(__name__)


@app.route('/run', methods=['POST'])
def run_tool():
    data = request.get_json()
    tool = data.get('tool')
    args = data.get('args', [])

    if not tool:
        return jsonify({'error': 'No se especificó ninguna herramienta'}), 400

    try:
        command = [tool] + args
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
