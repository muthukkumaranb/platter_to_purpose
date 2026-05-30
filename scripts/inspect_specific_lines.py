def check_line(path, line_no):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
            if 0 <= line_no - 1 < len(lines):
                line = lines[line_no - 1]
                print(f"File: {path}, Line: {line_no}")
                print(f"Content: {repr(line)}")
                print("-" * 20)
            else:
                print(f"Line {line_no} out of bounds for {path}")
    except Exception as e:
        print(f"Error reading {path}: {e}")


# Check food_detail.html around line 42 (title) and 49 (rating)
detail_path = r"c:\Users\JARSHIN J S\OneDrive\Desktop\platter_to_purpose\platter_to_purpose\platter_to_purpose\templates\food\food_detail.html"
check_line(detail_path, 42)
check_line(detail_path, 49)
check_line(detail_path, 50)

# Check food_list.html around line 10 (priority tab)
list_path = r"c:\Users\JARSHIN J S\OneDrive\Desktop\platter_to_purpose\platter_to_purpose\platter_to_purpose\templates\food\food_list.html"
check_line(list_path, 10)
