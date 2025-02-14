from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from PIL import Image
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import mammoth

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
PDF_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Hello, your Flask app is running on Render!"

@app.route("/upload", methods=["POST"])
def upload_images():
    if "images" not in request.files:
        return jsonify({"error": "No images uploaded"}), 400
    
    images = request.files.getlist("images")
    if not images:
        return jsonify({"error": "No images uploaded"}), 400
    
    image_paths = []
    for image in images:
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)
        image_paths.append(image_path)

    pdf_path = os.path.join(PDF_FOLDER, "output.pdf")
    create_pdf(image_paths, pdf_path)

    return jsonify({"pdf_url": f"https://imagetopdf-3nph.onrender.com/downloads/output.pdf"}), 200

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

@app.route("/convert-pdf-to-word", methods=["POST"])
def convert_pdf_to_word():
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400

    pdf_file = request.files["pdf"]
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    pdf_file.save(pdf_path)

    word_path = os.path.join(PDF_FOLDER, pdf_file.filename.replace(".pdf", ".docx"))

    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

    with open(word_path, "wb") as word_file:
        word_file.write(mammoth.convert_to_docx(text.encode()).value.encode())

    return jsonify({"word_url": f"https://imagetopdf-3nph.onrender.com/downloads/{os.path.basename(word_path)}"}), 200

@app.route("/merge-pdfs", methods=["POST"])
def merge_pdfs():
    if "pdfs" not in request.files:
        return jsonify({"error": "No PDFs uploaded"}), 400

    pdf_files = request.files.getlist("pdfs")
    merger = PdfMerger()

    pdf_paths = []
    for pdf in pdf_files:
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
        pdf.save(pdf_path)
        pdf_paths.append(pdf_path)
        merger.append(pdf_path)

    output_path = os.path.join(PDF_FOLDER, "merged.pdf")
    merger.write(output_path)
    merger.close()

    return jsonify({"pdf_url": f"https://imagetopdf-3nph.onrender.com/downloads/merged.pdf"}), 200

@app.route("/compress-pdf", methods=["POST"])
def compress_pdf():
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400

    pdf_file = request.files["pdf"]
    input_pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    pdf_file.save(input_pdf_path)

    output_pdf_path = os.path.join(PDF_FOLDER, "compressed_" + pdf_file.filename)
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()  # Lossless compression
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

    return jsonify({"pdf_url": f"https://imagetopdf-3nph.onrender.com/downloads/{os.path.basename(output_pdf_path)}"}), 200

@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory(PDF_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
