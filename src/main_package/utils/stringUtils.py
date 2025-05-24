def prependGBP(data):
    paid = str(data)
    idx = paid.find(".")  # Finding the index of the substring
    res = paid[:idx]
    formatter = "£" + res.replace("£", "")
    return formatter
