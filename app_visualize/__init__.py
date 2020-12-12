from pathlib import Path
from utils.paths import get_visualization_folder
import flask
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '7wVqacgKTB'
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['xlsx', 'xls']
app.config['UPLOAD_PATH'] = get_visualization_folder() / "data"
app.config['UPLOADED_FILE_NAME'] = ""

