from waitress import serve
from main import app

print("=" * 50)
print("  Server running at http://127.0.0.1:5020")
print("  Press Ctrl+C to stop")
print("=" * 50)

serve(app, host='0.0.0.0', port=5020, threads=4)
