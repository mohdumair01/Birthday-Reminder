import json
import os
from datetime import datetime, timedelta


class BirthdayReminder:

  def __init__(self, filename="birthdays.json"):
    """Initialize the system with a storage file."""
    self.filename = filename
    self.birthdays = self.load_data()

  def load_data(self):
    """Load birthday records from a JSON file permanently."""
    if os.path.exists(self.filename):
      try:
        with open(self.filename, "r") as file:
          return json.load(file)
      except json.JSONDecodeError:
        return {}
    return {}

  def save_data(self):
    """Save the current birthday records to the JSON file."""
    with open(self.filename, "w") as file:
      json.dump(self.birthdays, file, indent=4)

  def add_birthday(self):
    """Add a new name and birthday record with flexible date formats."""
    name = input("\nEnter name: ").strip()
    if not name:
      print("Error: Name cannot be empty.")
      return

    date_str = input(
        "Enter birthday date (e.g., 25-12-26 or 25-12-2026): "
    ).strip()

    parsed_date = None
    # Try both 2-digit (%y) and 4-digit (%Y) year formats automatically
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
      try:
        parsed_date = datetime.strptime(date_str, fmt)
        break
      except ValueError:
        continue

    if parsed_date is None:
      print(
          "Error: Invalid date format. Please use DD-MM-YY or DD-MM-YYYY (e.g.,"
          " 25-12-26)."
      )
      return

    # Store the date in a clean, consistent format (DD-MM-YY)
    self.birthdays[name] = parsed_date.strftime("%d-%m-%y")
    self.save_data()
    print(f"Success: Birthday for '{name}' has been saved successfully!")

  def view_all_birthdays(self):
    """Display all saved birthday records."""
    if not self.birthdays:
      print("\nNo birthday records found.")
      return

    print("\n--- Saved Birthdays ---")
    for name, date in self.birthdays.items():
      print(f"• {name}: {date}")

  def search_birthday(self):
    """Search for a birthday record by name."""
    search_query = input("\nEnter name to search: ").strip().lower()
    found = False

    print("\n--- Search Results ---")
    for name, date in self.birthdays.items():
      if search_query in name.lower():
        print(f"• {name}: {date}")
        found = True

    if not found:
      print("No matching records found.")

  def check_reminders(self):
    """Check for birthdays occurring today or within the next specified days."""
    if not self.birthdays:
      print("\nNo records available to check reminders.")
      return

    try:
      days_ahead = int(
          input("\nEnter the number of days to check ahead (e.g., 7): ")
      )
    except ValueError:
      print("Error: Please enter a valid number.")
      return

    today = datetime.now().date()
    end_date = today + timedelta(days=days_ahead)

    print(f"\n--- Birthday Reminders (Next {days_ahead} Days) ---")
    found_reminder = False

    for name, date_str in self.birthdays.items():
      bday = datetime.strptime(date_str, "%d-%m-%y").date()
      bday_this_year = bday.replace(year=today.year)

      if bday_this_year < today:
        bday_this_year = bday.replace(year=today.year + 1)

      if today <= bday_this_year <= end_date:
        found_reminder = True
        days_remaining = (bday_this_year - today).days

        if days_remaining == 0:
          print(f"🎉 TODAY IS SPECIAL: It's {name}'s Birthday today!")
        else:
          print(
              f"📅 Upcoming: {name}'s birthday is on"
              f" {bday_this_year.strftime('%d-%m-%y')} ({days_remaining} days"
              " left)"
          )

    if not found_reminder:
      print(f"No birthdays coming up in the next {days_ahead} days.")


def main():
  """Main application loop providing a user-friendly menu interface."""
  system = BirthdayReminder()

  while True:
    print("\n==============================")
    print("   BIRTHDAY REMINDER SYSTEM   ")
    print("==============================")
    print("1. Add Birthday")
    print("2. View All Birthdays")
    print("3. Search Birthday")
    print("4. Check Upcoming Reminders")
    print("5. Exit")

    choice = input("Choose an option (1-5): ").strip()

    if choice == "1":
      system.add_birthday()
    elif choice == "2":
      system.view_all_birthdays()
    elif choice == "3":
      system.search_birthday()
    elif choice == "4":
      system.check_reminders()
    elif choice == "5":
      print("\nExiting program. Goodbye!")
      break
    else:
      print("Invalid choice! Please select an option between 1 and 5.")


if __name__ == "__main__":
  main()