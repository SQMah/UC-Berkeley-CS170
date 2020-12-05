import os

if __name__ == "__main__":
    for file in os.listdir("outputs"):
        f_path = os.path.join("outputs", file)
        if os.path.splitext(file)[1] == ".inprogress" and "medium" in file and os.path.splitext(file)[0] not in {"medium-82", "medium-69", "medium-163", "medium-32", "medium-239", "medium-50", "medium-27", "medium-30"}:
            print(f"Removed {file}")
            os.remove(f_path)
