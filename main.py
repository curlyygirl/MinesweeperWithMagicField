from tkinter import *
from datetime import datetime
import random
import time
from tkinter import messagebox
from collections import deque

SIZE_Y = 10
SIZE_X = 10

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BUTTON_CLICKED = "<Button-1>"
BUTTON_FLAGGED = "<Button-3>"
window = None


class MagicMinesweeper:

    def __init__(self, tk):

        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "mines": Label(self.frame, text="Mines: 0"),
            "flags": Label(self.frame, text="Flags: 0")
        }

        self.labels["time"].grid(row=0, column=0, columnspan=SIZE_Y)  # top label
        self.labels["mines"].grid(row=SIZE_X + 1, column=0, columnspan=int(SIZE_Y / 2))  # bottom left label
        self.labels["flags"].grid(row=SIZE_X + 1, column=int(SIZE_Y / 2) - 1,
                                  columnspan=int(SIZE_Y / 2))  # bottom right label

        # images
        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "clicked": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "numbers": [PhotoImage(file="images/tile_" + str(i) + ".gif") for i in range(1, 9)]
        }

        self.restart()  # start game
        self.update_timer()  # start timer

    def set_up(self):
        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0
        self.startTime = None
        self.afterMagicField = False
        self.mines = 0

        # create buttons

        self.fields = [[self.new_field(x, y) for y in range(SIZE_Y)] for x in range(SIZE_X)]

        # loop again to find nearby mines and display number on tile
        for row in self.fields:
            for field in row:
                mc = 0
                for n in self.get_neighbors(field["coordinates"]["x"], field["coordinates"]["y"]):
                    mc += 1 if n["isMine"] else 0
                field["mines"] = mc

    def new_field(self, x, y):
        field = {
            "id": str(x) + "_" + str(y),
            "isMine": random.uniform(0.0, 1.0) < 0.1,
            "state": STATE_DEFAULT,
            "coordinates": {
                "x": x,
                "y": y
            },
            "button": Button(self.frame, image=self.images["plain"]),
            "mines": 0,  # set mines later
            "magic": random.uniform(0.0, 1.0) < 0.05
        }
        field["button"].bind(BUTTON_CLICKED, self.click_wrapper(x, y))
        field["button"].bind(BUTTON_FLAGGED, self.right_click_wrapper(x, y))
        field["button"].grid(row=x + 1, column=y)

        if field["isMine"]:
            self.mines += 1

        return field

    def get_neighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x - 1, "y": y - 1},  # top right
            {"x": x - 1, "y": y},  # top middle
            {"x": x - 1, "y": y + 1},  # top left
            {"x": x, "y": y - 1},  # left
            {"x": x, "y": y + 1},  # right
            {"x": x + 1, "y": y - 1},  # bottom right
            {"x": x + 1, "y": y},  # bottom middle
            {"x": x + 1, "y": y + 1},  # bottom left
        ]
        for n in coords:
            try:
                if n["x"] < 0 or n["y"] < 0:
                    raise IndexError
                neighbors.append(self.fields[n["x"]][n["y"]])
            except IndexError:
                pass
        return neighbors

    def refresh_labels(self):
        self.labels["flags"].config(text="Flags: " + str(self.flagCount))
        self.labels["mines"].config(text="Mines: " + str(self.mines))

    def click_wrapper(self, x, y):
        return lambda Button: self.on_click(self.fields[x][y])

    def right_click_wrapper(self, x, y):
        return lambda Button: self.on_right_click(self.fields[x][y])

    def on_click(self, field):
        if self.startTime is None:
            self.startTime = datetime.now()

        # show field while 3 sec
        if self.afterMagicField:
            if field["isMine"]:
                field["button"].config(image=self.images["mine"])
            elif field["mines"] == 0:
                field["button"].config(image=self.images["clicked"])
            else:
                field["button"].config(image=self.images["numbers"][field["mines"] - 1])
            self.tk.update()
            time.sleep(3)
            field["button"].config(image=self.images["plain"])
            self.afterMagicField = False
            return

        # game over
        if field["isMine"]:
            self.game_over(False)
            return

        # uncover field
        if field["mines"] == 0:
            field["button"].config(image=self.images["clicked"])
            self.clear_surrounding_fields(field["id"])
        else:
            field["button"].config(image=self.images["numbers"][field["mines"] - 1])
        if field["state"] != STATE_CLICKED:
            field["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (SIZE_X * SIZE_Y) - self.mines:
            self.game_over(True)

        # magic field
        if field["magic"]:
            self.afterMagicField = messagebox.askyesno("Magic Field",
                                                       "You can click on the field you want to see. Do you want to?")

    def on_right_click(self, field):
        if self.startTime is None:
            self.startTime = datetime.now()

        # if not clicked
        if field["state"] == STATE_DEFAULT:
            field["button"].config(image=self.images["flag"])
            field["state"] = STATE_FLAGGED
            field["button"].unbind(BUTTON_CLICKED)
            # if a mine
            if field["isMine"]:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refresh_labels()
        # if flagged -> unflag
        elif field["state"] == STATE_FLAGGED:
            field["button"].config(image=self.images["plain"])
            field["state"] = STATE_DEFAULT
            field["button"].bind(BUTTON_CLICKED,
                                 self.click_wrapper(field["coordinates"]["x"], field["coordinates"]["y"]))
            # if a mine
            if field["isMine"]:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refresh_labels()

    def game_over(self, won):
        for row in self.fields:
            for field in row:
                if field["isMine"] == False and field["state"] == STATE_FLAGGED:
                    field["button"].config(image=self.images["wrong"])
                if field["isMine"] == True and field["state"] != STATE_FLAGGED:
                    field["button"].config(image=self.images["mine"])

        self.tk.update()

        msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = messagebox.askyesno("Game Over", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()

    def clear_surrounding_fields(self, id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])
            for field in self.get_neighbors(x, y):
                self.clear_field(field, queue)

    def clear_field(self, field, queue):
        if field["state"] != STATE_DEFAULT:
            return
        if field["mines"] == 0:
            field["button"].config(image=self.images["clicked"])
            queue.append(field["id"])
        else:
            field["button"].config(image=self.images["numbers"][field["mines"] - 1])

        field["state"] = STATE_CLICKED
        self.clickedCount += 1

    def restart(self):
        self.set_up()
        self.refresh_labels()

    def update_timer(self):
        time_string = "00:00:00"
        if self.startTime is not None:
            delta = datetime.now() - self.startTime
            time_string = str(delta).split('.')[0]  # take only seconds
            if delta.total_seconds() < 3600:
                time_string = "0" + time_string
        self.labels["time"].config(text=time_string)
        self.frame.after(100, self.update_timer)  # refresh timer after 0.1 second


######End of class MagicMinesweeper######

def main():
    window = Tk()
    window.title("Magic Minesweeper")
    minesweeper = MagicMinesweeper(window)
    window.mainloop()


if __name__ == "__main__":
    main()
