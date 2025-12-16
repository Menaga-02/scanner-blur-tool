from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import cv2, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Read the uploaded image
            image = cv2.imread(filepath)

            # Initialize QR code detector
            qr_detector = cv2.QRCodeDetector()
            data, points, _ = qr_detector.detectAndDecode(image)

            if points is not None:
                # Convert points to integer coordinates
                points = points[0].astype(int)

                # Get bounding box of QR code
                x_min, y_min = points[:, 0].min(), points[:, 1].min()
                x_max, y_max = points[:, 0].max(), points[:, 1].max()

                # Ensure coordinates are within image boundaries
                x_min, y_min = max(0, x_min), max(0, y_min)
                x_max, y_max = min(image.shape[1], x_max), min(image.shape[0], y_max)

                # Extract QR region
                qr_region = image[y_min:y_max, x_min:x_max]

                # Blur only the QR code region
                qr_blurred = cv2.GaussianBlur(qr_region, (55, 55), 0)

                # Replace original QR region with blurred one
                image[y_min:y_max, x_min:x_max] = qr_blurred

            # Save output
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], "blurred_" + filename)
            cv2.imwrite(output_path, image)

            return redirect(url_for("result", filename="blurred_" + filename))
    return render_template("index.html")

@app.route("/result/<filename>")
def result(filename):
    return render_template("result.html", filename=filename)

@app.route("/uploads/<filename>")
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
