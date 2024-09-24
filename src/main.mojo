from sys import argv

# from io import File


struct TextEditor:
    var content: String
    var filename: String
    var mode: String

    fn __init__(inout self, filename: String):
        self.filename = filename
        self.content = ""
        self.mode = "normal"
        try:
            self.load_file()
        except:
            print("Error in <self.load_file()>")

    fn load_file(inout self) raises:
        # var file = File(self.filename, "r")
        # self.content = file.read()
        # file.close()
        try:
            with open(self.filename, "r") as file:
                self.content = file.read()
        except:
            raise Error("File", self.filename, "can't be found")

    fn save_file(self):
        with open(self.filename, "w") as file:
            # var file = File(self.filename, "w")
            file.write(self.content)

    fn process_normal_mode(self, inout command: String):
        if command == "i":
            self.mode = "insert"
            print("Switched to insert mode")
        elif command == ":w":
            self.save_file()
            print("File saved")
        elif command == ":q":
            print("Exiting editor")
            return False
        return True

    fn process_insert_mode(self, inout input: String):
        if input == "ESC":
            self.mode = "normal"
            print("Switched to normal mode")
        else:
            self.content += input

    fn run(self):
        var running = True
        while running:
            print("Current mode:", self.mode)
            if self.mode == "normal":
                var command = input("Enter command: ")
                running = self.process_normal_mode(command)
            elif self.mode == "insert":
                var input_text = input("Enter text (ESC to exit insert mode): ")
                self.process_insert_mode(input_text)


fn main():
    var args = argv()
    if len(args) < 2:
        print("Usage: mojo text_editor.mojo <filename>")
        return

    var filename = args[1]
    var editor = TextEditor(filename)
    editor.run()
