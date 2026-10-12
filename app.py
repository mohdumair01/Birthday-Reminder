
import json
import os
from datetime import date, datetime, timedelta

import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Birthday Reminder System",
    page_icon="🎂",
    layout="wide"
)

DATA_FILE = "birthdays.json"


# ---------------- DATA HANDLING ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_data(birthdays):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(birthdays, file, indent=4)


if "birthdays" not in st.session_state:
    st.session_state.birthdays = load_data()


# ---------------- DATE HANDLING ----------------
def parse_birthday(date_str):
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def next_birthday(date_str):
    birthday = parse_birthday(date_str)
    if birthday is None:
        return None

    today = date.today()

    for year in (today.year, today.year + 1):
        try:
            upcoming = birthday.replace(year=year)
        except ValueError:
            # Handle February 29 in a non-leap year.
            upcoming = date(year, 2, 28)

        if upcoming >= today:
            return upcoming

    return None


# ---------------- APPLICATION HEADER ----------------
st.title("🎂 Birthday Reminder System")
st.caption("Keep track of birthdays and never miss a special day!")

st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🎉 Navigation")

page = st.sidebar.radio(
    "Choose an option",
    [
        "Dashboard",
        "Add Birthday",
        "View Birthdays",
        "Search Birthday",
        "Upcoming Reminders"
    ]
)

birthdays = st.session_state.birthdays


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.subheader("Welcome to Your Birthday Manager!")

    today = date.today()
    upcoming_today = sum(
        1 for birthday_str in birthdays.values()
        if next_birthday(birthday_str) == today
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Birthdays", len(birthdays))
    col2.metric("Birthdays Today", upcoming_today)
    col3.metric(
        "Upcoming in 7 Days",
        sum(
            1 for birthday_str in birthdays.values()
            if next_birthday(birthday_str) is not None
            and 0 <= (next_birthday(birthday_str) - today).days <= 7
        )
    )

    st.divider()

    st.subheader("✨ Quick Guide")
    st.markdown("""
    - **Add Birthday:** Save a person's name and birthday.
    - **View Birthdays:** See all saved birthday records.
    - **Search Birthday:** Find a person by name.
    - **Upcoming Reminders:** Check birthdays coming soon.
    """)

    todays_names = [
        name for name, birthday_str in birthdays.items()
        if next_birthday(birthday_str) == today
    ]

    if todays_names:
        st.success(
            "🎉 Today's birthday: " + ", ".join(todays_names)
        )
        st.balloons()
    else:
        st.info("No birthdays today. Check your upcoming reminders!")


# ---------------- ADD BIRTHDAY ----------------
elif page == "Add Birthday":
    st.subheader("➕ Add a Birthday")

    with st.form("add_birthday_form"):
        name = st.text_input("Enter person's name")
        birthday_date = st.date_input(
            "Select birthday",
            value=date.today(),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )

        submitted = st.form_submit_button(
            "Save Birthday",
            use_container_width=True
        )

    if submitted:
        name = name.strip()

        if not name:
            st.error("Please enter a name.")
        else:
            # Store in the original program's DD-MM-YY format.
            st.session_state.birthdays[name] = birthday_date.strftime(
                "%d-%m-%y"
            )

            try:
                save_data(st.session_state.birthdays)
                st.success(f"🎉 Birthday saved successfully for {name}!")
                st.rerun()
            except OSError:
                st.error("Unable to save the file. Please check permissions.")


# ---------------- VIEW BIRTHDAYS ----------------
elif page == "View Birthdays":
    st.subheader("📋 All Saved Birthdays")

    if not birthdays:
        st.info("No birthday records found. Add a birthday to get started.")
    else:
        sorted_birthdays = sorted(
            birthdays.items(),
            key=lambda item: (
                next_birthday(item[1]) or date.max,
                item[0].lower()
            )
        )

        for name, birthday_str in sorted_birthdays:
            upcoming = next_birthday(birthday_str)

            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"🎂 **{name}** — {birthday_str}")
                if upcoming:
                    st.caption(
                        f"Next birthday: {upcoming.strftime('%d-%m-%Y')}"
                    )

            with col2:
                if st.button("🗑️ Delete", key=f"delete_{name}"):
                    st.session_state.delete_name = name

            if st.session_state.get("delete_name") == name:
                st.warning(f"Delete the birthday record for {name}?")
                yes_col, no_col = st.columns(2)

                with yes_col:
                    if st.button("Confirm Delete", key=f"yes_{name}"):
                        st.session_state.birthdays.pop(name, None)
                        st.session_state.pop("delete_name", None)
                        try:
                            save_data(st.session_state.birthdays)
                            st.success("Birthday deleted.")
                            st.rerun()
                        except OSError:
                            st.error("Unable to save the updated records.")

                with no_col:
                    if st.button("Cancel", key=f"no_{name}"):
                        st.session_state.pop("delete_name", None)
                        st.rerun()

            st.divider()


# ---------------- SEARCH BIRTHDAY ----------------
elif page == "Search Birthday":
    st.subheader("🔍 Search for a Birthday")

    search_query = st.text_input("Enter a name to search").strip().lower()

    if search_query:
        results = [
            (name, birthday_str)
            for name, birthday_str in birthdays.items()
            if search_query in name.lower()
        ]

        if results:
            for name, birthday_str in results:
                st.success(f"🎂 **{name}** — {birthday_str}")
        else:
            st.warning("No matching birthday records found.")
    else:
        st.caption("Enter a name or part of a name to search.")


# ---------------- UPCOMING REMINDERS ----------------
elif page == "Upcoming Reminders":
    st.subheader("📅 Upcoming Birthday Reminders")

    days_ahead = st.number_input(
        "Check birthdays within how many days?",
        min_value=0,
        max_value=366,
        value=7,
        step=1
    )

    today = date.today()
    end_date = today + timedelta(days=int(days_ahead))

    reminders = []

    for name, birthday_str in birthdays.items():
        upcoming = next_birthday(birthday_str)

        if upcoming and today <= upcoming <= end_date:
            days_remaining = (upcoming - today).days
            reminders.append(
                (upcoming, name, birthday_str, days_remaining)
            )

    reminders.sort(key=lambda item: (item[0], item[1].lower()))

    if not birthdays:
        st.info("No records available. Add birthdays first.")
    elif reminders:
        for upcoming, name, birthday_str, days_remaining in reminders:
            if days_remaining == 0:
                st.success(
                    f"🎉 TODAY IS SPECIAL! It's **{name}'s birthday today!**"
                )
                st.balloons()
            else:
                st.info(
                    f"📅 **{name}** — "
                    f"{upcoming.strftime('%d-%m-%Y')} "
                    f"({days_remaining} days left)"
                )
    else:
        st.info(
            f"No birthdays coming up in the next {int(days_ahead)} days."
        )

st.divider()
st.caption("🎂 Birthday Reminder System | Built with Python and Streamlit")
