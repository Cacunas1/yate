fn main() raises:
    var filename = "dummy.txt"
    var text: String

    text = "test dummy text"

    with open(filename, "w") as file:
        file.write(text)

    with open(filename, "r") as file:
        text = file.read()

    print(text)
