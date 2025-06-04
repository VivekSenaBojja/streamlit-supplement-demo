import streamlit as st
import requests
import re

st.set_page_config(page_title="Supplement Schedule Extractor", layout="wide")
st.title("Supplement Schedule Extractor (with OCR.space)")

st.write(
    "Upload your supplement prescription image (JPEG or PDF). "
    "This app uses OCR.space API to extract text, then parses your supplement schedule. "
    "**No data is stored.**"
)

uploaded_file = st.file_uploader("Upload a prescription image (JPEG or PDF)", type=['jpg', 'jpeg', 'png', 'pdf'])

def ocr_space_file(file, api_key, language='eng'):
    url = 'https://api.ocr.space/parse/image'
    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': language,
    }
    files = {'filename': file}
    response = requests.post(url, files=files, data=payload)
    result = response.json()
    try:
        text = result['ParsedResults'][0]['ParsedText']
    except Exception as e:
        st.error(f"OCR.space error: {e}\n\nRaw response: {result}")
        return ""
    return text

def parse_prescription(text):
    supplements = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty, spray, and irrelevant lines
        if not line or 'Spry.' in line or 'Spry' in line or line.lower().startswith('finding summary'):
            continue
        # Only lines with Tab. or Cap.
        if 'Tab.' in line or 'Cap.' in line or 'Tab' in line or 'Cap' in line:
            # Fuzzy match: type, name, day range, possible doses
            type_match = re.search(r'(Tab\.?|Cap\.?)', line)
            name_match = re.search(r'(Tab\.?|Cap\.?)\s*([A-Za-z0-9 >\+\-]+)', line)
            days_match = re.search(r'Day\s*(\d+)[^\d]+Day\s*(\d+)', line)
            # Find doses (e.g. 1 - 0 - 0 - 1 or 0 - 0 - 0 - 1)
            dose_match = re.search(r'(\d)\s*-\s*(\d)\s*-\s*(\d)\s*-\s*(\d)', line)
            if type_match and name_match and days_match:
                type_ = type_match.group(1).replace('.', '')
                name = name_match.group(2).strip()
                day_start = days_match.group(1)
                day_end = days_match.group(2)
                dose_morning = dose_match.group(1) if dose_match else "?"
                dose_noon = dose_match.group(2) if dose_match else "?"
                dose_evening = dose_match.group(3) if dose_match else "?"
                dose_night = dose_match.group(4) if dose_match else "?"
                timing = {}
                if dose_morning != "0" and dose_morning != "?": timing["Morning"] = int(dose_morning)
                if dose_noon != "0" and dose_noon != "?": timing["Noon"] = int(dose_noon)
                if dose_evening != "0" and dose_evening != "?": timing["Evening"] = int(dose_evening)
                if dose_night != "0" and dose_night != "?": timing["Night"] = int(dose_night)
                supplements.append({
                    "Name": name,
                    "Type": type_,
                    "Days": f"Day {day_start} - Day {day_end}",
                    "Timing": timing if timing else "Dose missing or unclear"
                })
    return supplements

API_KEY = "K86044279488957"  # <-- Replace with your OCR.space API key

if uploaded_file is not None:
    st.info("Running OCR, please wait a few seconds...")
    text = ocr_space_file(uploaded_file, API_KEY)
    if text:
        st.subheader("OCR Extracted Text")
        st.text_area("Extracted Text", text, height=200)
        supplements = parse_prescription(text)
        if supplements:
            st.subheader("Extracted Supplement Schedule")
            for supp in supplements:
                st.markdown(f"**{supp['Name']} ({supp['Type']}) — {supp['Days']}**")
                if isinstance(supp['Timing'], dict):
                    for time, dose in supp['Timing'].items():
                        st.write(f"{time}: {dose}")
                else:
                    st.write(supp['Timing'])
                st.markdown("---")
        else:
            st.warning("No valid supplements found in the extracted text. Try a clearer image or different prescription format.")

st.markdown(
    """
    <hr>
    <sub>
    ⚡️ This MVP uses [OCR.space API](https://ocr.space/) for live OCR and supports JPEG, PNG, and PDF.<br>
    If extraction fails, try scanning a clearer image or re-uploading.<br>
    Ignores sprays. Handles most standard supplement prescription formats.
    </sub>
    """,
    unsafe_allow_html=True
)
