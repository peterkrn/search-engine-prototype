import re
from flask import Flask, render_template, request, send_file, send_from_directory
import logging
import sys
import os
import search_engine_module

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form.get("search")
        search_results = search_engine_module.search(search_term)
        return render_template(
            "index.html", results=search_results, search_term=search_term
        )
    else:
        return render_template("index.html")


@app.route("/download/<path:filename>")
def download_file(filename):
    print(filename)
    subfolder = filename.split("_")[0]
    file_path = os.path.join("datasets", subfolder, filename)
    file_path = os.path.normpath(file_path)  # Normalize the path
    print("File Path:", file_path)

    if os.path.isfile(file_path):
        with open(file_path, "r") as file:
            content = file.read()

        return render_template("file_content.html", content=content)
    else:
        return render_template("file_not_found.html", filename=filename)


if __name__ == "__main__":
    app.run(debug=True)
