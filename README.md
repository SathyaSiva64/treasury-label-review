cat > README.md <<'EOF'
# Alcohol Label Review

Hi! My name’s Sathya and my project is a small Python app that helps review alcohol labels by extracting text from label images and comparing it with information entered on an application. It is built with Streamlit and uses Tesseract OCR to read text from images.

## Here’s what it does

- Upload an image of an alcohol label and extract its text.
- Compare label information with application data, including brand, class or type, producer, alcohol content, and net contents.
- Check for the presence of the government warning heading.
- Upload multiple label images for batch review.
- View extracted text and detected values for each image.
- Download batch review results as a CSV file.

## Here are the requirements

- Python 3.10 or later
- Tesseract OCR
- The Python packages listed in `requirements.txt`

## Setup

Clone or download this repository, then open a terminal in the project folder.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
