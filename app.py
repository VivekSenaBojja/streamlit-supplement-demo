import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Daily Sachet Generator", layout="wide")
st.title("Daily Sachet Generator")

st.write("""
Paste or type your prescription below (one supplement per line).<br>
**Format:**  
`Name Days Morning Noon Evening Night Dosage`  
Example:  
`Amura_C 2-4 1 0 0 1 200mg`  
`Amura_V 1-3 0 1 0 0 100mg`
""", unsafe_allow_html=True)

# Time slot order for consistent output
time_slots = ["Morning", "Noon", "Evening", "Night"]

# For display: time slot ordering and pretty printing
time_order = {slot: i for i, slot in enumerate(time_slots)}
display_names = {
    "Morning": "Morning",
    "Noon": "Noon",
    "Evening": "Evening",
    "Night": "Night"
}

prescription_text = st.text_area("Paste your prescription here:", height=200)

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
    # Map day number -> {time slot -> [ (name, dose) ]}
    day_sachets = {}
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
                    for _ in range(supp["Timing"][slot]):  # If dose >1, add multiple times
                        day_sachets.setdefault(day, {}).setdefault(slot, []).append((supp["Name"], supp["Dose"]))
    # Now, create a flat list of (date, dayofweek, slot, [(name, dose)])
    sachet_list = []
    sachet_number = 1
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    for day in range(min_day, max_day + 1):
        date_obj = start_date + timedelta(days=day - 1)
        date_str = date_obj.strftime("%b %dth %Y")  # e.g., Jun 10th 2025
        weekday = date_obj.strftime("%A")
        slots_today = day_sachets.get(day, {})
        for slot in time_slots:
            items = slots_today.get(slot, [])
            if items:
                sachet_list.append({
                    "Number": sachet_number,
                    "Slot": slot,
                    "Date": date_str,
                    "Weekday": weekday,
                    "Supplements": items
                })
                sachet_number += 1
    return sachet_list

if prescription_text:
    supplements = parse_input_lines(prescription_text)
    sachets = build_sachets(supplements, start_date_str="2025-06-10")
    if sachets:
        st.subheader("Your Sachet Schedule")
        for sachet in sachets:
            st.markdown(f"**Sachet {sachet['Number']}: {sachet['Slot']} &nbsp;&nbsp; {sachet['Date']}**")
            st.markdown(f"*{sachet['Weekday']}*")
            for name, dose in sachet["Supplements"]:
                st.write(f"{name}&nbsp;&nbsp;&nbsp;&nbsp;{dose}")
            st.markdown("---")
    else:
        st.warning("No sachets generated. Check your formatting.")
else:
    st.info("Enter your prescription above to see your sachet schedule.")

st.markdown(
    """
    <hr>
    <sub>
    Sachets are grouped by day/time. If multiple supplements are to be taken at the same time, they are in the same sachet. <br>
    The schedule starts from Day 1 = June 10, 2025. Edit code for a different start date.<br>
    </sub>
    """,
    unsafe_allow_html=True
)
