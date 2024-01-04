import os
import re
from datetime import datetime, timedelta

# NOTE: Now I only need to update the commands.sty 


def get_date_input(prompt):
    date_pattern = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
    while True:
        user_input = input(prompt)
        if date_pattern.match(user_input):
            try:
                # If the pattern matches, try to create a date object to confirm it's a valid date
                datetime.strptime(user_input, '%m-%d')
                return user_input
            except ValueError:
                # If creating a date object fails, it's not a valid date (e.g., "02-30" is not valid)
                print("Invalid date. Please enter a valid date in MM-DD format.")
        else:
            print("Invalid format. Please enter a date in MM-DD format (e.g., 01-23).")

def get_valid_filename(prompt):
    invalid_chars_pattern = r'[<>:"/\\|?*\0]'
    
    while True:
        filename = input(prompt)
        
        # Check for invalid characters
        if re.search(invalid_chars_pattern, filename):
            print("Invalid filename. Filenames cannot contain <>:\"/\\|?* or null characters.")
            continue
        
        # Check for length (255 characters is a common maximum, but it can vary)
        if len(filename) > 255:
            print("Filename is too long. It must be fewer than 256 characters.")
            continue
        
        return filename


# make sure it is an integer
def get_integer_input(prompt, max_int = 1000000, allow_space = False):
    
    while True:
        try:
            user_input = input(prompt)
            
            if allow_space and user_input == '':
                if user_input == "final":
                    print("Get rekt!")
                return user_input
            
            user_input_int = int(user_input)  # Try to convert the input to an integer
            if user_input_int <= 0 or user_input_int > max_int:
                print("Please enter a positive integer or in range.")
                continue
            
            return user_input_int
        except ValueError:
            print("Invalid input. Please enter an integer.")

# Handle user input for due date
def get_due_date(suggested_due_dates,hw_num):
    choice = -1
    print("Please select a date:")
    if hw_num != 1 and suggested_due_dates != None:
        print(f"1 {suggested_due_dates[0]} (1 week)")
        print(f"2 {suggested_due_dates[1]} (2 week)")
        print("3 Enter other date")
    
        choice = int(input()) - 1  
    
    if choice == 2 or hw_num == 1 or suggested_due_dates == None:
        due_date = get_date_input("Enter the due date (MM-DD): ")
    else:
        due_date = suggested_due_dates[choice]
    
    return due_date

# Suggest a due date - TODO: check if there is a previous hw to use
def suggest_due_date(class_name,hw_num):
    if hw_num == 1:
        return
    
    latest_tex_file = get_latest_homework_tex(class_name,hw_num)
    try:
        with open(latest_tex_file,'r') as file:
            pass
    except FileNotFoundError as e:
        return None
    
    
    if latest_tex_file:
        due_date = extract_due_date(latest_tex_file)
        if due_date:
            suggest_due_dates = []
            # Add a week to the extracted due date
            new_due_date = due_date + timedelta(days=7)
            # Handle the year transition if necessary
            # If the month is January and the due date is in December, increment the year
            if due_date.month == 12 and new_due_date.month == 1:
                new_due_date = new_due_date.replace(year=due_date.year + 1)
            suggest_due_dates.append(new_due_date.strftime("%m-%d"))
            
            # Add two weeks
            new_due_date = due_date + timedelta(days=14)
            if due_date.month == 12 and new_due_date.month == 1:
                new_due_date = new_due_date.replace(year=due_date.year + 1)
            suggest_due_dates.append(new_due_date.strftime("%m-%d"))
            
            return suggest_due_dates
    return None

# Get the previous due date
def extract_due_date(tex_file_path):
    # Regular expression pattern to find the due date in the format "Due MM/DD"
    due_date_pattern = re.compile(r"Due (\d{2}-\d{2})")
    
    with open(tex_file_path, 'r') as file:
        tex_content = file.read()
    
    # Search for the due date in the file content
    match = due_date_pattern.search(tex_content)
    if match:
        # Extract and return the due date
        due_date_str = match.group(1)
        # Assuming the year of the due date is the current year
        current_year = datetime.now().year
        try:
            due_date = datetime.strptime(f"{current_year}-{due_date_str.replace('/', '-')}", "%Y-%m-%d")
            return due_date
        except ValueError as e:
            print(f"Error parsing date from file {tex_file_path}: {e}")
            return None
    else:
        print(f"No due date found in file {tex_file_path}.")
        return None




# Get the previous homework tex file
def get_latest_homework_tex(class_name,hw_num):    
    class_folder = f"./{class_name}"
    previous_class_number = str(hw_num-1)
    
    # Go to the previous folder 
    previous_folder = os.path.join(class_folder,"HW"+previous_class_number)
    # Get the tex file
    previous_tex_file = os.path.join(previous_folder,f"{class_name}-HW{previous_class_number}-mbailly.tex")
    return previous_tex_file

# Find homework folders to suggest next homework number
def get_next_homework_number(class_name):
    class_folder = f"./{class_name}"
    # List all items in the class folder
    items = os.listdir(class_folder)
    
    # Filter items that match the "HW#" pattern and are directories
    hw_folders = [item for item in items if re.match(r'HW\d+', item) and os.path.isdir(os.path.join(class_folder, item))]
    
    # Extract numbers from the homework folder names and find the maximum
    hw_numbers = [int(re.search(r'\d+', folder).group()) for folder in hw_folders]
    max_number = max(hw_numbers, default=0)  # Default to 0 if no folders are found
    
    return max_number + 1  # Suggest the next homework number


# Find the class folders
def list_class_folders(directory_path):
    all_items = os.listdir(directory_path)
    # Filter out items that don't start with '!' and are directories
    class_folders = [item for item in all_items if not item.startswith('!') and os.path.isdir(os.path.join(directory_path, item))]
    return class_folders


# Function to prompt user to select a class folder
def user_select_class():
    class_folders = list_class_folders("./")
    amount_class_folders = len(class_folders)
    
    print("Please select a class folder:")
    for i, folder in enumerate(class_folders):
        print(f"{i + 1}. {folder}")
    print(str(amount_class_folders+1)+" Add new class")
    
    choice = int(get_integer_input("",amount_class_folders+1)) - 1  # assuming user inputs 1 for first class, so subtract 1 to match index
    
    if choice == amount_class_folders:
        new_class = get_valid_filename("Enter class name: ")
        if not os.path.exists(new_class):
            os.makedirs(new_class)
        return new_class
    else:
        return class_folders[choice]


# Generate the latex template
def generate_latex(template, hw_num, class_name, due_date, num_questions):
    homework_content = template.replace("Template Class", class_name)
    homework_content = homework_content.replace("Homework Template Number", f"Homework {hw_num}")
    homework_content = homework_content.replace("Due Template Date", f"Due {due_date}")
    homework_content = homework_content.replace("commands","../../!TexStuff/commands")
    
    # Adding questions placeholders
    questions = ""
    for i in range(2, num_questions+1):
        questions += f"%---------------%\n%---Problem {i}---%\n%---------------%\n\n\n\\begin{{problem}}%[vskip]\n\\subsection*{{Problem {i}}}\n\nThis is a problem statement\n\n\\begin{{proof}}\n\nThis is a solution placeholder\n\n\\end{{proof}}\n\\end{{problem}}\n\n\n\n\n"
    homework_content = homework_content.replace("%replace me", questions)  # Assuming that's a good place to insert questions

    # Creating directory for the homework file
    homework_directory_name = f"HW{hw_num}"
    full_directory_path = os.path.join(class_name, homework_directory_name)
    
    if not os.path.exists(full_directory_path):
        os.makedirs(full_directory_path)

    # Save the new LaTeX file in the directory
    file_path = os.path.join(full_directory_path, f"{class_name}-HW{hw_num}-mbailly.tex")
    with open(file_path, 'w') as file:
        file.write(homework_content)

    return file_path

# Main Loop
def main():
    # load in the template
    template_path = "./!TexStuff/HW.tex"
    with open(template_path, 'r') as file:
        template_content = file.read()
    template_content[:500]
    
    
    # User inputs
        
    # Get class name 
    class_name = user_select_class()
    
    # Get homework number 
    # use class name to make guess on next hw number
    next_hw_num = get_next_homework_number(class_name)
    
    # Show the suggested next homework number and allow override
    hw_num = str(get_integer_input(f"Enter homework number (Enter to use {next_hw_num}): ",10000000000,True))
    if hw_num.strip() == "":
        hw_num = next_hw_num
    else:
        hw_num = int(hw_num)
    
    
    # Get due date
    # suggested due date
    suggested_due_dates = suggest_due_date(class_name,hw_num)
    due_date = get_due_date(suggested_due_dates,hw_num) 
    
    num_questions = int(get_integer_input("Enter the number of questions: "))
    
    if num_questions >= 9: 
        print("Sucks to suck bro lol")
    
    # Generate the LaTeX file
    generated_file_path = generate_latex(template_content, hw_num, class_name, due_date, num_questions)
    print(f"LaTeX file generated at {generated_file_path}")
    print("Have fun :)")

main()