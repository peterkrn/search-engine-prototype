from flask import Flask, render_template, request

app = Flask(__name__)

# Dummy data representing documents
documents = [
    {"id": 1, "title": "Document 1", "content": "This is the content of Document 1."},
    {"id": 2, "title": "Document 2", "content": "This is the content of Document 2."},
    # Add more documents as needed
]


@app.route("/", methods=["GET", "POST"])
def index():
    search_results = None

    if request.method == "POST":
        search_term = request.form.get("search")
        # Dummy search logic: Find documents containing the search term
        search_results = [
            doc for doc in documents if search_term.lower() in doc["title"].lower()
        ]

    return render_template("index.html", search_results=search_results)


@app.route("/document/<int:result_id>")
def document(result_id):
    # Find the document with the given ID
    result = next((doc for doc in documents if doc["id"] == result_id), None)
    if result:
        return render_template("document.html", result=result)
    else:
        return "Document not found"


if __name__ == "__main__":
    app.run(debug=True)