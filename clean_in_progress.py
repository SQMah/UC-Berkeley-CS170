import os

if __name__ == "__main__":
    for file in os.listdir("outputs"):
        f_path = os.path.join("outputs", file)
        if os.path.splitext(file)[1] == ".inprogress":
            print(f"Removed {file}")
            os.remove(f_path)
