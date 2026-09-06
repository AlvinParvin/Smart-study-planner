import os

# Configuration

LOG_FILE = "study_log.txt"
# Delimiter used when loading sessions to or from the text file.
DELIMITER = "|"


def classify_session(duration):
    """
    Classify a study session by its duration (in minutes).

    - "Short"  : under 30 minutes
    - "Medium" : 30 to 90 minutes (inclusive)
    - "Long"   : over 90 minutes
    """
    if duration < 30:
        return "Short"
    elif duration <= 90:
        return "Medium"
    else:
        return "Long"


def save_sessions(sessions):
    """
    Save every logged session to LOG_FILE, one session per line.
    Fields are separated by DELIMITER so they can be split back out
    on load. This overwrites the file with the current in-memory list.
    """
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for session in sessions:
            line = DELIMITER.join([
                session["subject"],
                session["topic"],
                session["date"],
                str(session["duration"]),
            ])
            f.write(line + "\n")
    print(f"\nSaved {len(sessions)} session(s) to '{LOG_FILE}'.")


def load_sessions():
    """
    Load sessions from LOG_FILE if it exists. If the file is missing
    (e.g. the very first run) or unreadable, return an empty list
    instead of crashing.
    """
    sessions = []

    if not os.path.exists(LOG_FILE):
        #No log file yet
        return sessions

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line_number, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue  # skip blank lines

                parts = line.split(DELIMITER)
                if len(parts) != 4:
                    print(f"Warning: skipping malformed line {line_number} in {LOG_FILE}.")
                    continue

                subject, topic, date, duration_str = parts
                try:
                    duration = float(duration_str)
                except ValueError:
                    print(f"Warning: skipping line {line_number} - invalid duration.")
                    continue

                sessions.append({
                    "subject": subject,
                    "topic": topic,
                    "date": date,
                    "duration": duration,
                })
    except OSError as e:
        # Handle file reading errors
        print(f"Warning: could not read '{LOG_FILE}' ({e}). Starting with an empty log.")
        return []

    return sessions


def add_session(sessions):
    """
    Prompt the user for subject, topic, date/day label and duration
    (minutes), validate the duration, and append the new session
    as a dictionary to the sessions list.
    """
    print("\n--- Add a Study Session ---")
    subject = input("Subject: ").strip()
    topic = input("Topic covered: ").strip()
    date = input("Date or day label (e.g. 2026-08-31 or 'Monday'): ").strip()

    # Keep re-prompting until a valid positive number is entered.
    duration = None
    while duration is None:
        raw = input("Duration (minutes): ").strip()
        try:
            value = float(raw)
            if value <= 0:
                print("Duration must be a positive number. Please try again.")
                continue
            duration = value
        except ValueError:
            print("That's not a valid number. Please try again.")

    session = {
        "subject": subject,
        "topic": topic,
        "date": date,
        "duration": duration,
    }
    sessions.append(session)

    print(f"Session added: {subject} ({classify_session(duration)}, {duration:.0f} min).")



def view_sessions(sessions):
    """Display every logged session in a neatly formatted table."""
    print("\n--- All Study Sessions ---")

    if not sessions:
        print("No sessions logged yet.")
        return

    header = f"{'Subject':<15}{'Topic':<20}{'Date':<15}{'Duration':<12}{'Type':<8}"
    print(header)
    print("-" * len(header))

    for s in sessions:
        duration_str = f"{s['duration']:.0f} min"
        session_type = classify_session(s["duration"])
        print(f"{s['subject']:<15}{s['topic']:<20}{s['date']:<15}{duration_str:<12}{session_type:<8}")


def search_by_subject(sessions, subject):
    """
    Display all sessions recorded for a given subject (case-insensitive
    match) along with the total time spent on it. Show a clear message
    if nothing matches.
    """
    print(f"\n--- Sessions for '{subject}' ---")

    matches = [s for s in sessions if s["subject"].strip().lower() == subject.strip().lower()]

    if not matches:
        print(f"No sessions found for subject '{subject}'.")
        return

    header = f"{'Topic':<20}{'Date':<15}{'Duration':<12}{'Type':<8}"
    print(header)
    print("-" * len(header))

    total_minutes = 0.0
    for s in matches:
        duration_str = f"{s['duration']:.0f} min"
        session_type = classify_session(s["duration"])
        print(f"{s['topic']:<20}{s['date']:<15}{duration_str:<12}{session_type:<8}")
        total_minutes += s["duration"]

    print("-" * len(header))
    print(f"Total time spent on '{subject}': {total_minutes:.0f} minutes "
          f"({total_minutes / 60:.2f} hours).")



def study_statistics(sessions):
    """
    Compute and display:
      - total hours studied overall
      - total hours studied per subject
      - the subject with the least total study time (weakest area)
      - the single longest session recorded
    """
    print("\n--- Study Statistics ---")

    if not sessions:
        print("No sessions logged yet - nothing to analyse.")
        return

    # Total hours overall
    total_minutes = sum(s["duration"] for s in sessions)
    print(f"Total time studied overall: {total_minutes:.0f} minutes "
          f"({total_minutes / 60:.2f} hours).")

    # Total minutes per subject
    per_subject = {}
    for s in sessions:
        key = s["subject"]
        per_subject[key] = per_subject.get(key, 0) + s["duration"]

    print("\nTime studied per subject:")
    for subject, minutes in per_subject.items():
        print(f"  {subject:<15}: {minutes:.0f} min ({minutes / 60:.2f} hrs)")

    # Weakest subject = least total study time.
    weakest_subject = min(per_subject, key=per_subject.get)
    print(f"\nWeakest area (least total study time): {weakest_subject} "
          f"({per_subject[weakest_subject]:.0f} min).")

    # Longest single session
    longest = max(sessions, key=lambda s: s["duration"])
    print(f"\nLongest single session: {longest['subject']} - {longest['topic']} "
          f"({longest['duration']:.0f} min, {classify_session(longest['duration'])}) "
          f"on {longest['date']}.")


# Menu-driven interface
def display_menu():
    print("\n===== Smart Study Planner =====")
    print("1. Add a study session")
    print("2. View all sessions")
    print("3. Search sessions by subject")
    print("4. View statistics")
    print("5. Save and exit")


def main():
    sessions = load_sessions()
    if sessions:
        print(f"Loaded {len(sessions)} session(s) from '{LOG_FILE}'.")

    while True:
        display_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_session(sessions)
        elif choice == "2":
            view_sessions(sessions)
        elif choice == "3":
            subject = input("Enter subject to search for: ").strip()
            search_by_subject(sessions, subject)
        elif choice == "4":
            study_statistics(sessions)
        elif choice == "5":
            save_sessions(sessions)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
