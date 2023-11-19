from flask import Flask, render_template, request
import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG)
# Get the current file's directory (Frontend directory)
current_dir = os.path.dirname(__file__)

# Construct the path to the root folder
root_folder_path = os.path.abspath(os.path.join(current_dir, ".."))

# Add the root folder to the sys.path temporarily
sys.path.append(root_folder_path)

import search_engine_module

# Remove the root folder from sys.path to avoid potential issues
sys.path.remove(root_folder_path)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form.get("search")
        # Dummy search logic: Find documents containing the search term
        search_results = search_engine_module.search(search_term)
        print("Search Results", search_results)
        return render_template("index.html", results=search_results)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
