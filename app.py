import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Daily Sachet Generator", layout="wide")
st.title("Daily Sachet Generator")

# Time slots and order
time_slots = ["Morning", "Noon", "Evening", "Night"]
time_order = {slot: i for i, slot in enumerate(time_slots)}

# --- Layout: Two columns
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("Paste your prescription")
    st.write("""
    Paste or type your prescription below (one supplement per line).<br>
    **Format:**  
    `Name Days Morning Noon Evening Night Dosage`  
    Example:  
    `Amura_C 2-4 1 0 0 1 200mg`  
    `Amura_V 1-3 0 1 0 0 100mg`
    """, unsafe_allow_html=True)

    prescription_text = st.text_area("Prescription input:", height=300)

def parse_input_lines(text):
    supplements = []
    for line in text.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) < 7:
            continue  # skip invalid lines
        name = parts[0]
        days = parts[1]
        morning, noon, evening, night = map(int, parts[2:6])
        dose = parts[6]
        # Handle day range
        if '-' in days:
            start, end = days.split('-')
            day_range = list(range(int(start), int(end) + 1))
        else:
            day_range = [int(days)]
        timing = {
            "Morning": morning,
            "Noon": noon,
            "Evening": evening,
            "Night": night
        }
        supplements.append({
            "Name": name,
            "Days": day_range,
            "Timing": timing,
            "Dose": dose
        })
    return supplements

def build_sachets(supplements, start_date_str="2025-06-10"):
    # Map (day number, slot) -> list of (name, dose)
    sachet_dict = {}
    min_day = None
    max_day = None
    for supp in supplements:
        for day in supp["Days"]:
            if min_day is None or day < min_day:
                min_day = day
            if max_day is None or day > max_day:
                max_day = day
            for slot in time_slots:
                if supp["Timing"][slot] > 0:
                    # For each dose (can be >1)
                    for _ in range(supp["Timing"][slot]):
                        sachet_dict.setdefault((day, slot), []).append((supp["Name"], supp["Dose"]))
    # Prepare final sachets in strict chrono order
    sachet_list = []
    sachet_number = 1
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    for day in range(min_day, max_day + 1):
        date_obj = start_date + timedelta(days=day - 1)
        date_str = date_obj.strftime("%b %dth %Y")  # e.g., Jun 10th 2025
        weekday = date_obj.strftime("%A")
        for slot in time_slots:
            items = sachet_dict.get((day, slot), [])
            if items:
                sachet_list.append({
                    "Number": sachet_number,
                    "DayNum": day,
                    "Slot": slot,
                    "Date": date_str,
                    "Weekday": weekday,
                    "Supplements": items
                })
                sachet_number += 1
    return sachet_list

with col2:
    st.header("Sachet schedule")
    if 'prescription_text' in locals() and prescription_text:
        supplements = parse_input_lines(prescription_text)
        sachets = build_sachets(supplements, start_date_str="2025-06-10")
        if sachets:
            for sachet in sachets:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#fff;
                        border-radius:16px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                        padding:22px 28px 20px 28px;
                        margin-bottom:30px;
                        width:340px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        ">
                        <div style="font-size:28px; font-weight:700; color:#232323; margin-bottom:4px;">
                            {sachet['Slot'].upper()}
                        </div>
                        <div style="font-size:18px; color:#444; margin-bottom:3px;">
                            {sachet['Weekday']}
                        </div>
                        <div style="font-size:18px; color:#444; margin-bottom:8px;">
                            {sachet['Date']}
                        </div>
                        <hr style="margin:6px 0 10px 0; border-top:1.5px solid #ececec;">
                        <div style="font-size:17px; color:#232323;">
                            {"<br>".join(f"1 {name.upper()} {dose.upper()}" for name, dose in sachet["Supplements"])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No sachets generated. Please check your formatting.")
    else:
        st.info("Paste your prescription on the left to view the schedule.")
