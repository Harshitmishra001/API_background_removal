import os
import requests
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from PIL import Image
from rembg import remove

# Initialize Flask app
app = Flask(__name__)

# Create directory for storing processed images
os.makedirs('processed_images', exist_ok=True)

@app.route('/remove-background', methods=['POST'])
def remove_background():
    try:
        # Get input data
        data = request.json
        image_url = data.get('image_url')
        bounding_box = data.get('bounding_box')

        # Validate inputs
        if not image_url or not bounding_box:
            return jsonify({"error": "Invalid input. Provide image_url and bounding_box."}), 400

        x_min = bounding_box.get('x_min')
        y_min = bounding_box.get('y_min')
        x_max = bounding_box.get('x_max')
        y_max = bounding_box.get('y_max')

        if not all(isinstance(i, int) for i in [x_min, y_min, x_max, y_max]):
            return jsonify({"error": "Bounding box coordinates must be integers."}), 400

        # Fetch the image from URL
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch image from URL."}), 400

        # Load the image
        image = Image.open(BytesIO(response.content))

        # Crop the bounding box
        cropped_image = image.crop((x_min, y_min, x_max, y_max))

        # Convert the cropped image to bytes
        cropped_image_bytes = BytesIO()
        cropped_image.save(cropped_image_bytes, format='PNG')
        cropped_image_bytes = cropped_image_bytes.getvalue()

        # Remove the background
        output_bytes = remove(cropped_image_bytes)

        # Convert the output bytes back to an image
        transparent_image = Image.open(BytesIO(output_bytes))

        # Save the processed image locally
        output_path = os.path.join('processed_images', 'result.png')
        transparent_image.save(output_path)

        # Serve the processed image
        return send_file(output_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
