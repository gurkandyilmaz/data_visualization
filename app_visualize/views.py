from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, abort, url_for, flash, session
from werkzeug.utils import secure_filename
from . import app
from utils.paths import get_root_folder, get_visualization_folder
from visualization.ProcessData import ProcessData
from visualization.VisualizeData import VisualizeData

UPLOADED_FILE_DIR = Path.cwd().parent.joinpath("visualization/data/")
IMAGES_DIR = Path(Path(app.static_folder).joinpath("images"))
UPLOADED_FILE_NAME = ""

def is_extension_valid(file_name):
    return "." in file_name and file_name.rsplit(".",1)[1].lower() in app.config["UPLOAD_EXTENSIONS"]

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    session["file_name"] = ""
    if request.method == "POST":
        # print(request.files)
        if "file" not in request.files:
            flash("No File Part")
            # print("No File Part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No File Selected")
            # print("No File Selected")
            return redirect(request.url)
        if not is_extension_valid(file.filename):
            flash("Only xlsx and xls formats.")
            return redirect(request.url)
        if file and is_extension_valid(file.filename):
            file_name = secure_filename(file.filename)
            file.save(app.config['UPLOAD_PATH'].joinpath(file_name))
            # session["file_name"] = file_name
            app.config['UPLOADED_FILE_NAME'] = file_name
            # print("File name in upload file: ", UPLOADED_FILE_NAME)
            flash("File Saved Succesfully.")
            print("FILE PATH: ", app.config['UPLOAD_PATH'].joinpath(file_name))
            return redirect(url_for("visualize"))
        
    return render_template("upload_file.html")

@app.route("/")
@app.route("/visualize")
def visualize():
    print("File name in visualize: ", app.config['UPLOADED_FILE_NAME'])
    print("ROOT FOLDER:", get_root_folder())
    print("Visualization FOLDER:", get_visualization_folder())
    if app.config['UPLOADED_FILE_NAME']:
        visualizer = VisualizeData(IMAGES_DIR)
        process = ProcessData()
        uploaded_file_path = UPLOADED_FILE_DIR.joinpath(app.config['UPLOADED_FILE_NAME'])
        print("FILE will be read: ", uploaded_file_path)
        df = process.read_file(uploaded_file_path)
        df_tokenized, df_row_length = process.process_df_text(df)
        frequencies_by_column = {}
        for index_name in df_tokenized.index:
            frequencies_by_column[index_name] = process.freq_dist(df_tokenized[index_name])
        visualizer.plot_counts_vs_word(frequencies_by_column)
        visualizer.plot_wordcloud(frequencies_by_column)
        visualizer.plot_row_length(df_row_length)

        df_numeric, correlation_matrix = process.process_df_numeric(df)
        if not df_numeric.columns.empty:
            visualizer.plot_correlation(correlation_matrix)
            visualizer.plot_hist(df_numeric)
        app.config['UPLOADED_FILE_NAME'] = ""
    images_list = [child.name for child in IMAGES_DIR.iterdir()]
    # print("IMAGES FOLDER: {0}".format(app.static_folder))
    # print("IMAGES LIST: {0}".format(images_list))
    return render_template("visualize.html", images=images_list)

# @app.route("/hello/")
# @app.route("/hello/<name>")
# def base(name=None):    
#     return render_template("base.html", name=name, date=datetime.now())

# @app.route("/api/data")
# def get_data():
#     return app.send_static_file("data.json")

# if __name__ == "__main__":
#     app.run(debug=True)