from pathlib import Path
from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, abort, url_for, flash, session
from werkzeug.utils import secure_filename
from . import app
from utils.paths import get_root_folder, get_visualization_folder, get_data_folder
from visualization.ProcessData import ProcessData
from visualization.VisualizeData import VisualizeData

IMAGES_DIR = Path(Path(app.static_folder).joinpath("images"))
JSON_FILES_DIR = Path(Path(app.static_folder).joinpath("json"))
# UPLOADED_FILE_DIR = get_data_folder()
# UPLOADED_FILE_NAME = ""

def is_extension_valid(file_name):
    return "." in file_name and file_name.rsplit(".",1)[1].lower() in app.config["UPLOAD_EXTENSIONS"]

@app.route("/upload/", methods=["GET", "POST"])
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
            return redirect(request.url)
        
    return render_template("upload_file.html")

@app.route("/")
@app.route("/select-types/", methods=["GET", "POST"])
def select_types():
    print("File name in select_types: ", app.config['UPLOADED_FILE_NAME'])
    print("ROOT FOLDER:", get_root_folder())
    print("Visualization FOLDER:", get_visualization_folder())
    column_names = []
        

    if request.method == "GET" and app.config['UPLOADED_FILE_NAME']:
        file_path = get_data_folder() / app.config["UPLOADED_FILE_NAME"]
        # uploaded_file_path = get_data_folder().joinpath(app.config['UPLOADED_FILE_NAME'])
        # print("FILE will be read: ", file_path)
        df = process.read_file(file_path)
        column_names = df.columns.to_list()
        
        # print("Visualize:", df.shape)
        # df_tokenized, df_row_length = process.process_df_text(df)
        # frequencies_by_column = {}
        # for index_name in df_tokenized.index:
        #     frequencies_by_column[index_name] = process.freq_dist(df_tokenized[index_name])
        # visualizer.plot_counts_vs_word(frequencies_by_column)
        # visualizer.plot_wordcloud(frequencies_by_column)
        # visualizer.plot_row_length(df_row_length)

        # df_numeric, correlation_matrix = process.process_df_numeric(df)
        # if not df_numeric.columns.empty:
        #     visualizer.plot_correlation(correlation_matrix)
        #     visualizer.plot_hist(df_numeric)
        # app.config['UPLOADED_FILE_NAME'] = ""

    if request.method == "POST":
        column_types = request.form.to_dict(flat=True)
        user_file_and_types = {"types": column_types, "file_name": app.config['UPLOADED_FILE_NAME']}
        with open( JSON_FILES_DIR / "user_file_and_types.json", "w+") as file:
            json.dump(user_file_and_types, file, sort_keys=False, indent=4)
        return render_template("select_types.html", column_names=column_names, column_types=column_types)
    
    # print("IMAGES FOLDER: {0}".format(app.static_folder))
    # print("IMAGES LIST: {0}".format(images_list))
    
    return render_template("select_types.html", column_names=column_names)

@app.route("/visualize/", methods=["GET","POST"])
def visualize():
    with open(JSON_FILES_DIR / "user_file_and_types.json", "r") as file:
        user_file_and_types = json.load(file)
    # print("Column TYPES in visualize:", user_file_and_types)
    if request.method == "POST":
        graph_types = request.form.to_dict(flat=True).get("types")
        try:
            graph_types_list = json.loads(graph_types)
            print("Graph Types in visualize ", graph_types_list)
        except:
            return "invalid input"
    return render_template("visualize.html", user_file_and_types=user_file_and_types)

@app.route("/visualize/plot/", methods=["GET", "POST"])
def plot():
    user_request = (
        # {"graph_type":"bar", "column_name":"STATE"}, 
        # {"graph_type":"pie", "column_name":"ACCOUNT_LENGTH"},
        # {"graph_type":"bar", "column_name":"NUMBER_CUSTOMER_SERVICE_CALLS"},
        # {"graph_type":"pie", "column_name":"CHURN"},
        # {"graph_type":"correlation"},
        # {"graph_type":"scatter", "x":"AGE", "y":"PRICE"},
        # {"graph_type":"histogram", "x":"AGE", "bins":50, "density":True},
        # {"graph_type":"histogram", "x":"PRICE", "bins":40, "density":False},
        # {"graph_type":"boxplot", "x":"AGE", "y":"PRICE"},
        # {"graph_type":"boxplot", "x":"AGE"},
        {"graph_type":"timeseries", "x":"Date", "y1":"Deaths", "y2":"Recovered"},
        {"graph_type":"timeseries", "x":"Date", "y1":"Confirmed"},
        {"graph_type":"timeseries", "x":"Date", "y2":"Deaths"},
    )
    if request.method == "POST":
        print("PLOT FORM:", request.form.to_dict(flat=True))
        column_types = request.form.to_dict(flat=True)
        df = process.read_file(get_data_folder() / app.config["UPLOADED_FILE_NAME"])
        df_categoric = process.process_categorical(df, column_types)
        df_numeric = process.process_numeric(df, column_types)
        df_datetime = process.process_datetime(df, column_types)
        print("DF datetime DTYPE:", df_datetime.dtypes)
        print("DF datetime type:", type(df_datetime))
        for user_req in user_request:
            if user_req.get("graph_type") == "bar":
                if user_req.get("column_name") in df_categoric.columns:
                    visualizer.plot_bar(df, user_req.get("column_name"))
                else:
                    # TODO Bar plot only available for categoric columns
                    pass
            elif user_req.get("graph_type") == "pie":
                if user_req.get("column_name") in df_categoric.columns:
                    visualizer.plot_pie(df, user_req.get("column_name"))
                else:
                    # TODO Pie plot is only available for categoric columns
                    pass
            elif user_req.get("graph_type") == "correlation":
                visualizer.plot_correlation(df_numeric)
            
            elif user_req.get("graph_type") == "scatter":
                if (user_req.get("x") in df_numeric.columns) and (user_req.get("y") in df_numeric.columns):
                    visualizer.plot_scatter(df_numeric, user_req.get("x"), user_req.get("y"))
                else:
                    # TODO Scatter is only available for numeric columns
                    pass
            elif user_req.get("graph_type") == "histogram":
                if user_req.get("x") in df_numeric.columns:
                    visualizer.plot_histogram(df_numeric, user_req.get("x"), user_req.get("bins"), user_req.get("density"))
                else:
                    # TODO Histogram is only available for numeric columns
                    pass
            elif user_req.get("graph_type") == "boxplot":
                if user_req.get("x") == df_datetime.name or user_req.get("y") == df_datetime.name: # Add df_datetime.columns
                    # TODO boxplot is only available for non_datetime type columns
                    pass
                else:
                    visualizer.plot_boxplot(df, user_req.get("x"), user_req.get("y", -1))
            elif user_req.get("graph_type") == "timeseries":
                if user_req.get("x") == df_datetime.name:
                    visualizer.plot_time(df, user_req.get("x"), user_req.get("y1", -1), user_req.get("y2", -1))
                else:
                    #TODO the x column should be of type datetime
                    pass
    else:
        column_types = {}    
       
    images_list = [child.name for child in IMAGES_DIR.iterdir()]
    return render_template('plot.html', images=images_list, column_types=column_types)

process = ProcessData()
visualizer = VisualizeData(IMAGES_DIR)

@app.route("/high-charts/")
def high_charts():    
    return render_template("high_charts.html")

# @app.route("/api/data")
# def get_data():
#     return app.send_static_file("data.json")

if __name__ == "__main__":
    app.run(debug=True)