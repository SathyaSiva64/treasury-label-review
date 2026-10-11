
import os
import re
import streamlit as st
import pytesseract
from PIL import Image, ImageOps, ImageEnhance


TESSERACT_PATH = "/opt/homebrew/bin/tesseract"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

GOVERNMENT_WARNING = (
    "GOVERNMENT WARNING: (1) According to the Surgeon General, "
    "women should not drink alcoholic beverages during pregnancy "
    "because of the risk of birth defects. (2) Consumption of "
    "alcoholic beverages impairs your ability to drive a car or "
    "operate machinery, and may cause health problems."
)


def normalize(value):
    """Normalize text for case- and whitespace-insensitive comparison."""
    return " ".join((value or "").casefold().split()).strip()




def extract_abv(text):
    """Detect common ABV formats, including OCR punctuation variations."""
    cleaned = (text or "").replace(",", ".")

    patterns = [
        r"\b(\d{1,2}(?:\.\d{1,2})?)\s*%\s*(?:alc(?:ohol)?\.?\s*(?:by\s*)?vol(?:ume)?\.?)",
        r"\balc(?:ohol)?\.?\s*(\d{1,2}(?:\.\d{1,2})?)\s*%\s*(?:by\s*)?vol(?:ume)?\.?",
        r"\balc(?:ohol)?\.?\s*(?:by\s*)?vol(?:ume)?\.?\s*[:.]?\s*(\d{1,2}(?:\.\d{1,2})?)\s*%",
        r"\b(\d{1,2}(?:\.\d{1,2})?)\s*%\s*alc(?:ohol)?\b",
        r"\b(\d{1,2}(?:\.\d{1,2})?)\s*%\s*alc\s*/\s*vol\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            return f"{match.group(1)}%"
    return ""


def extract_net_contents(text):
    """Find common metric or US fluid-volume expressions."""
    pattern = (
        r"\b(\d+(?:\.\d+)?)\s*"
        r"(mL|ml|cL|cl|L|l|fl\.?\s?oz|fluid ounces?)\b"
    )
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return ""


def normalize_warning(text):
    """Normalize OCR text for warning-statement comparison."""
    return re.sub(r"[^a-z0-9]", "", (text or "").casefold())

def compare_values(field, expected, observed):
    if not expected.strip():
        return {
            "Field": field,
            "Application value": expected,
            "Label value": observed,
            "Result": "Not provided",
        }

    if not observed.strip():
        return {
            "Field": field,
            "Application value": expected,
            "Label value": observed,
            "Result": "Needs review: no label value",
        }

    if normalize(expected) == normalize(observed):
        result = "Match"
    else:
        result = "Discrepancy"

    return {
        "Field": field,
        "Application value": expected,
        "Label value": observed,
        "Result": result,
    }


st.set_page_config(
    page_title="Treasury Label Review",
    page_icon="🔎",
    layout="wide",
)

st.title("Treasury Label Review")
st.caption("Prototype | Alcohol label extraction and comparison")

st.warning(
    "This is an experimental review aid, not an official compliance "
    "determination. OCR and automated checks can be wrong."
)

uploaded_file = st.file_uploader(
    "Upload an alcohol label image",
    type=["png", "jpg", "jpeg", "tif", "tiff", "bmp"],
)

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image).convert("RGB")

        with st.spinner("Extracting text from label..."):
            processed = ImageOps.grayscale(image)
            processed = ImageEnhance.Contrast(processed).enhance(1.5)
            ocr_text = pytesseract.image_to_string(
                processed, config="--psm 6"
            ).strip()

        left, right = st.columns(2)
        with left:
            st.subheader("Uploaded label")
            st.image(image, use_container_width=True)

        with right:
            st.subheader("OCR output")
            st.text_area(
                "Extracted label text",
                value=ocr_text,
                height=220,
                key="ocr_output",
            )

        st.divider()
        st.header("Application information")
        st.caption("Enter the values submitted by the applicant.")

        with st.form("review_form"):
            c1, c2 = st.columns(2)

            with c1:
                expected_brand = st.text_input("Application brand name")
                expected_type = st.text_input("Application class/type")
                expected_producer = st.text_input("Application producer")

            with c2:
                expected_abv = st.text_input(
                    "Application alcohol content (e.g. 12.5%)"
                )
                expected_net = st.text_input(
                    "Application net contents (e.g. 750 mL)"
                )

            st.subheader("Label values")
            st.caption(
                "Alcohol content and net contents are prefilled from OCR "
                "when detected. Review and correct every value before "
                "comparing. Enter the other label values manually."
            )

            c3, c4 = st.columns(2)
            with c3:
                observed_brand = st.text_input("Label brand name")
                observed_type = st.text_input("Label class/type")
                observed_producer = st.text_input("Label producer")

            with c4:
                observed_abv = st.text_input(
                    "Label alcohol content",
                    value=extract_abv(ocr_text),
                )
                observed_net = st.text_input(
                    "Label net contents",
                    value=extract_net_contents(ocr_text),
                )

            submitted = st.form_submit_button("Compare application and label")

        if submitted:
            results = [
                compare_values("Brand name", expected_brand, observed_brand),
                compare_values("Class/type", expected_type, observed_type),
                compare_values("Producer", expected_producer, observed_producer),
                compare_values("Alcohol content", expected_abv, observed_abv),
                compare_values("Net contents", expected_net, observed_net),
            ]

            st.header("Comparison results")
            st.dataframe(results, use_container_width=True, hide_index=True)

            discrepancies = sum(
                row["Result"] == "Discrepancy" for row in results
            )
            needs_review = sum(
                row["Result"].startswith("Needs review")
                for row in results
            )
            matches = sum(row["Result"] == "Match" for row in results)

            m1, m2, m3 = st.columns(3)
            m1.metric("Matches", matches)
            m2.metric("Discrepancies", discrepancies)
            m3.metric("Needs review", needs_review)

            
            st.subheader("Government warning review")

            heading_match = re.search(
                r"GOVERNMENT\s+WARNING\s*:",
                ocr_text,
                re.IGNORECASE,
            )

            if not heading_match:
                st.error(
                    "Government-warning heading not detected. "
                    "Inspect the image before deciding whether the "
                    "warning is missing."
                )
            else:
                heading = heading_match.group(0)
                heading_is_uppercase = (
                    re.sub(r"\s+", "", heading) == "GOVERNMENTWARNING:"
                )

                if heading_is_uppercase:
                    st.success("Warning heading appears in uppercase.")
                else:
                    st.warning(
                        "Warning heading capitalization may be incorrect."
                    )

                expected_normalized = normalize_warning(
                    GOVERNMENT_WARNING
                )
                observed_normalized = normalize_warning(
                    ocr_text[heading_match.start():]
                )

                if expected_normalized in observed_normalized:
                    st.success(
                        "Expected warning wording detected in OCR."
                    )
                else:
                    st.warning(
                        "The complete expected warning wording was not "
                        "found in the OCR output. This may indicate a "
                        "wording discrepancy or an OCR error."
                    )

                    with st.expander("View expected warning wording"):
                        st.write(GOVERNMENT_WARNING)

                    with st.expander("View OCR text for review"):
                        st.text(ocr_text[heading_match.start():])

            st.info(
                "Human review required: OCR cannot establish whether "
                "the heading is bold, whether the warning has the "
                "required visual formatting, or whether every character "
                "was recognized correctly."
            )

    except Exception as exc:
        st.error(f"Could not process this image: {exc}")
else:
    st.info("Upload a label image to begin a review.")



# --- Batch label review ---
st.divider()
st.header("Batch label review")
st.caption(
    "Upload multiple label images to extract text and run initial checks "
    "on each image. Results are screening aids, not compliance decisions."
)

batch_files = st.file_uploader(
    "Upload multiple label images",
    type=["png", "jpg", "jpeg", "tif", "tiff", "bmp"],
    accept_multiple_files=True,
    key="batch_label_uploader",
)

if batch_files:
    batch_results = []

    progress = st.progress(0, text="Preparing batch review...")

    for index, file in enumerate(batch_files):
        try:
            batch_image = Image.open(file)
            batch_image = ImageOps.exif_transpose(batch_image).convert("RGB")

            processed = ImageOps.grayscale(batch_image)
            processed = ImageEnhance.Contrast(processed).enhance(1.5)

            text = pytesseract.image_to_string(
                processed,
                config="--psm 6",
            ).strip()

            warning_found = bool(
                re.search(r"GOVERNMENT\s+WARNING\s*:", text, re.IGNORECASE)
            )

            batch_results.append({
                "Filename": file.name,
                "OCR status": "Text detected" if text else "No text detected",
                "ABV detected": extract_abv(text) or "Not detected",
                "Net contents detected": extract_net_contents(text) or "Not detected",
                "Warning heading": (
                    "Detected" if warning_found else "Not detected"
                ),
                "Extracted text": text,
            })

        except Exception as exc:
            batch_results.append({
                "Filename": file.name,
                "OCR status": f"Error: {exc}",
                "ABV detected": "Not available",
                "Net contents detected": "Not available",
                "Warning heading": "Not checked",
                "Extracted text": "",
            })

        progress.progress(
            (index + 1) / len(batch_files),
            text=f"Processed {index + 1} of {len(batch_files)} labels",
        )

    progress.empty()

    st.subheader("Batch summary")
    st.dataframe(
        [
            {key: value for key, value in result.items()
             if key != "Extracted text"}
            for result in batch_results
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Individual OCR results")
    for result in batch_results:
        with st.expander(result["Filename"]):
            if result["Extracted text"]:
                st.text_area(
                    "Extracted text",
                    value=result["Extracted text"],
                    height=180,
                    key=f"batch_text_{result['Filename']}",
                )
            else:
                st.warning("No text was extracted for this image.")

    csv_data = __import__("pandas").DataFrame(
        [
            {key: value for key, value in result.items()
             if key != "Extracted text"}
            for result in batch_results
        ]
    ).to_csv(index=False)

    st.download_button(
        "Download batch summary (CSV)",
        data=csv_data,
        file_name="batch_label_review.csv",
        mime="text/csv",
    )