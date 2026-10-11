# Alcohol Label Review

Hi! My name’s Sathya and my project is a small Python app that helps review alcohol labels by extracting text from label images and comparing it with information entered on an application. It is built with Streamlit and uses Tesseract OCR to read text from images.

**Approach:** I did not want to over-engineer this app, so I kept it simple and straightforward while fulfilling the necessary requirements. Built a Streamlit application that uses OCR to extract text from alcohol labels, identify key information such as ABV and net contents, and check for the government warning heading. Supports individual and batch uploads, with CSV export for batch results.

**Tools Used:** Python, Streamlit, Tesseract OCR, pytesseract, Pillow, GitHub, and Streamlit Community Cloud.

**Assumptions:** Label images are sufficiently clear for OCR. Automated checks provide preliminary screening rather than definitive regulatory compliance determinations. OCR may miss or misread text, so results require human review.

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
