from cls import HomemadeApplication
from utils.quitAction import quit_action

if __name__ == "__main__":
    app = HomemadeApplication()
    app.mainloop()
    quit_action(app.get_var())