from flask import Flask, request, jsonify
import base64
from groq import Groq
import os
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Initialize Groq API client with your API key
client = Groq(api_key="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")

# Function to convert image file to base64 encoding
def encode_image(image_data):
    img = Image.open(BytesIO(image_data))
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_base64

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        # Ensure image and query are provided
        if 'image' not in request.files or 'query' not in request.form:
            return jsonify({'error': 'Missing image or query parameter'}), 400

        # Get the image file and query parameter
        image_file = request.files['image']
        query = request.form['query']

        # Convert the image to base64 encoding
        image_data = image_file.read()
        image_base64 = encode_image(image_data)

        # Call Groq API to process the image and query
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                        },
                    },
                ],
            }],
            model="llama-3.2-11b-vision-preview",
        )

        # Extract the response from the Groq API
        response_text = chat_completion.choices[0].message.content
        return jsonify({'response': response_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
