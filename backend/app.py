from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from PIL import Image
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
PDF_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_images():
    if "images" not in request.files:
        return jsonify({"error": "No images uploaded"}),400
    
    images = request.files.getlist("images")
    if not images:
        return jsonify({"error": "No images uploaded"}),400
    
    image_paths = []
    for image in images:
         image_path = os.path.join(UPLOAD_FOLDER, image.filename)
         image.save(image_path)
         image_paths.append(image_path)

    pdf_path = os.path.join(PDF_FOLDER, "output.pdf")
    create_pdf(image_paths, pdf_path)

    return jsonify({"pdf_url":f"https://imagetopdf-3nph.onrender.com/downloads/output.pdf"}), 200

def create_pdf(images_paths, pdf_path):
    if not images_paths:
        return
    first_image = Image.open(images_paths[0])
    pdf = canvas.Canvas(pdf_path, pagesize=first_image.size)

    for image_path in images_paths:
        img = Image.open(image_path)
        pdf.drawImage(image_path, 0, 0, width=img.width, height=img.height)
        pdf.showPage()
    
    pdf.save()

@app.route("/downloads/<filename>")
def download_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)