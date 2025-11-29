import os

# 1️⃣ Set the folder where your email files are
folder = r"C:\ProjectFYP2\enron_mail_20150507\maildir\blair-l\meetings"

# 2️⃣ List all files in the folder
files = os.listdir(folder)

# 3️⃣ Keep only numeric files and convert to integers
numbers = []
for f in files:
    try:
        numbers.append(int(f.strip('.')))
    except ValueError:
        continue

# 4️⃣ Sort the numbers
numbers.sort()
print(f"Found files from {numbers[0]} to {numbers[-1]}")

# 5️⃣ Create missing files
for n in range(numbers[0], numbers[-1] + 1):
    filename = os.path.join(folder, f"{n}.")
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write("")  # empty file
        print(f"Created missing file: {n}.")
