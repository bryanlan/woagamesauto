import os
import pandas as pd
from difflib import get_close_matches

# Define constants
CSV_FILE_PATH = r'C:\Users\blangl\vs code projects\woagamesauto\Game Compatibility Form.csv'
SOURCE_GAME_FOLDER = r'C:\Users\blangl\vs code projects\woasubmit\works-on-woa\src\content\games'
SOURCE_USER_REPORTS_FOLDER = r'C:\Users\blangl\vs code projects\woasubmit\works-on-woa\src\content\user_reports_games'
PROCESSED_COLUMN_NAME = 'Processed'

# Column names mapping
COLUMNS = {
    "email": "Email",
    "name": "Name",
    "game_name": "Name of Game",
    "categories": "Categories",
    "publisher": "Publisher",
    "compatibility": "Compatibility",
    "device_configuration": r"Device Configuration eg Snapdragon X Elite - 32 GB",
    "date_tested": "Date tested1",
    "os_version": "OS Version",
    "driver_id": "Driver ID",
    "compatibility_details": "Compatibility Details",
    "auto_super_resolution_compatibility": "Auto Super Resolution Compatibility",
    "auto_super_res_fps_boost": "Auto Super Res FPS boost",
    "reporter": "Your name/gamertag"
}
# Utility function to format game name
def format_game_name(game_name):
    return game_name.lower().replace(' ', '_').replace(':', '')

# Utility function to handle NaN values
def handle_nan(value):
    return "" if pd.isna(value) else value

# Utility function to format date to YYYY-MM-DD
def format_date(date_value):
    try:
        return pd.to_datetime(date_value).strftime('%Y-%m-%d')
    except Exception:
        return ""
# Function to save data to a dictionary
# Function to save data to a dictionary
def save_row_data(row):
    row_data = {key: handle_nan(row[COLUMNS[key]]) for key in COLUMNS}
    # Format the date_tested field
    row_data["date_tested"] = format_date(row_data["date_tested"])
    # Format the compatibility field to lowercase and only take the part before the first space
    row_data["compatibility"] = row_data["compatibility"].split(' ')[0].lower()
    return row_data

# Function to find matching game files
def find_matching_files(game_name, folder):
    game_files = [f for f in os.listdir(folder) if f.lower().endswith('.md')]
    game_names = [os.path.splitext(f)[0].lower() for f in game_files]
    exact_match = game_name.lower() in game_names
    close_matches = get_close_matches(game_name.lower(), game_names, n=3, cutoff=0.1)
    return exact_match, close_matches

# Function to handle user input for game file selection
def handle_user_input(matches, game_name):
    if matches:
        print("Select one of the following options for the game:")
        for i, match in enumerate(matches):
            print(f"{i + 1}: {match}")
        print(f"{len(matches) + 1}: Create new game called '{game_name}'")
        print(f"{len(matches) + 2}: Create new game with custom name")

        choice = int(input("Enter your choice (number): ")) - 1
        if choice < len(matches):
            return matches[choice], True
        elif choice == len(matches):
            return game_name, False
        else:
            return input("Enter custom game name: "), False
    else:
        print(f"No close matches found for '{game_name}'.")
        return input("Enter custom game name: "), False
# Function to generate a unique filename in the specified folder
def generate_unique_filename(folder, base_name):
    counter = 1
    while True:
        file_name = f"{base_name}_{counter:04d}.md"
        file_path = os.path.join(folder, file_name)
        if not os.path.exists(file_path):
            return file_path
        counter += 1
# Function to create a new .md file with game-specific information
def create_md_file(game_name, game_data, folder, is_new_game):
    formatted_game_name = format_game_name(game_name)
    auto_super_res_fps_boost = game_data['auto_super_res_fps_boost']
    auto_super_res_fps_boost_str = f"{auto_super_res_fps_boost}% Boost" if auto_super_res_fps_boost else ""
    if is_new_game:
        md_content = (
            "---\n"
            f"name: \"{game_name}\"\n"
            f"categories: [{game_data['categories']}]\n"
            f"publisher: {game_data['publisher']}\n"
            f"compatibility: {game_data['compatibility']}\n"
            f"device_configuration: {game_data['device_configuration']}\n"
            f"date_tested: {game_data['date_tested']}\n"
            f"os_version: \"{game_data['os_version']}\"\n"
            f"compatibility_details: \"{game_data['compatibility_details']}\"\n"
            f"auto_super_resolution:\n"
            f"    compatibility: {game_data['auto_super_resolution_compatibility']}\n"
            f"    fps boost: {auto_super_res_fps_boost_str}\n"
            "---\n"
        )
        file_path = os.path.join(folder, f"{formatted_game_name}.md")
    else:
        md_content = (
            "---\n"
            f"game: \"{game_name}\"\n"
            f"compatibility: {game_data['compatibility']}\n"
            f"device_configuration: {game_data['device_configuration']}\n"
            f"date_tested: {game_data['date_tested']}\n"
            f"os_version: \"{game_data['os_version']}\"\n"
            f"compatibility_details: \"{game_data['compatibility_details']}\"\n"
            f"auto_super_resolution:\n"
            f"    compatibility: {game_data['auto_super_resolution_compatibility']}\n"
            f"    fps boost: {auto_super_res_fps_boost_str}\n"
            f"reporter: {game_data['reporter']}\n"
            "---\n"

        )
        file_path = generate_unique_filename(folder, formatted_game_name)



    with open(file_path, "w") as file:
        file.write(md_content)
    print(f"Created new game file: {file_path}")

# Main function to execute the steps
def main():
    # Load the CSV file
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print("CSV file read successfully.")
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # Get all unprocessed rows
    unprocessed_rows = df[df[PROCESSED_COLUMN_NAME].isnull()]

    index = 0
    while index < len(unprocessed_rows):
        row = unprocessed_rows.iloc[index]
        game_data = save_row_data(row)
        game_name = game_data["game_name"]

        # Check for additional compatibility data in subsequent rows
        additional_compatibility_data = []
        next_index = index + 1
        while next_index < len(unprocessed_rows) and pd.isna(unprocessed_rows.iloc[next_index, 0]) and not pd.isna(unprocessed_rows.iloc[next_index][COLUMNS["compatibility_details"]]):
            additional_compatibility_data.append(unprocessed_rows.iloc[next_index][COLUMNS["compatibility_details"]])
            next_index += 1

        if additional_compatibility_data:
            game_data["compatibility_details"] += " " + " ".join(additional_compatibility_data)
        
        # Check for matching game files
        exact_match, matches = find_matching_files(game_name, SOURCE_GAME_FOLDER)

        if exact_match:
            selected_game = game_name
            game_already_exists = True
        else:
            selected_game, game_already_exists = handle_user_input(matches, game_name)

        # Output selected game
        print(f"Selected game: {selected_game}")

        # Logic for creating files in appropriate locations
        if game_already_exists:
            print(f"Game '{selected_game}' already exists.")
            create_md_file(selected_game, game_data, SOURCE_USER_REPORTS_FOLDER, False)
        else:
            create_md_file(selected_game, game_data, SOURCE_GAME_FOLDER, True)

        # Update the CSV file
        df.at[unprocessed_rows.index[index], PROCESSED_COLUMN_NAME] = 1
        for skip_index in range(index + 1, next_index):
            df.at[unprocessed_rows.index[skip_index], PROCESSED_COLUMN_NAME] = 1
        try:
            df.to_csv(CSV_FILE_PATH, index=False)
            print(f"CSV file updated after processing row {index}.")
        except Exception as e:
            print(f"Error saving the CSV file after processing row {index}: {e}")

        # Move to the next row to process
        index = next_index

    print("All rows processed successfully.")

if __name__ == "__main__":
    main()