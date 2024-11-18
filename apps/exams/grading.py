def generate_grade(marks: int):
    if marks >= 70 and marks <= 100:
        return "A"
    elif marks >= 60 and marks <= 69:
        return "B"
    elif marks >= 50 and marks <= 59:
        return "C"
    elif marks >= 40 and marks <= 49:
        return "D"
    elif marks >= 0 and marks <= 39:
        return "E"
    else:
        return "F"
