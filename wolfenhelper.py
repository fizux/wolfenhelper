import tkinter as tk
from tkinter import ttk
import time

save_game_path = '/home/chris/dosbox/cw/CASTLE'
# todo: add file chooser dialog


class Castle:
    def __init__(self, filename):
        self.filename = filename
        self.data = bytearray()
        self.last_load_time = 0
        self.load()

    def set_filename(self, filename):
        self.filename = filename

    def get_filename(self):
        return self.filename

    def load(self):
        with open(self.filename, 'rb') as file1:
            self.data = bytearray(file1.read())

    def save(self):
        with open(self.filename, 'wb') as file1:
            file1.write(self.data)

    def draw_canvas(self, canvas, room_num, col, row):
        '''
        todo: fix graphics - chests and bad guys
        todo: fix display of rooms that connect
        room entry/exit points do not usually line up, so it isn't clear from the map which rooms connect
        castle layout never changes, so a hard-coded solution is possible.
        todo: figure out room data from 0x49 to 0x7F
        '''

        # handle walls and stairs
        element = self.data[0x0100 * room_num + 0x08 * row + col]

        if element & 0x01:  # draw left wall
            canvas.create_line(1, 1, 1, 10, fill="red", width=2)

        if element & 0x02:  # draw right wall
            canvas.create_line(20, 1, 20, 10, fill="red", width=2)

        if element & 0x04:  # draw top wall
            canvas.create_line(1, 1, 20, 1, fill="red", width=2)

        if element & 0x08:  # draw bottom wall
            canvas.create_line(1, 10, 20, 10, fill="red", width=2)

        if element & 0x10 and room_num in [1, 2, 9, 34, 13, 36, 49, 58]:
            ''' draw stairs if appropriate
            all rooms are generated with stairs until you get there
            once you enter a room that shouldn't have stairs, the game cleans up
            odd rooms = stairs going up; even rooms = stairs going down '''
            canvas.create_line(3, 3, 18, 3, fill="yellow", width=1)
            canvas.create_line(3, 5, 18, 5, fill="yellow", width=1)
            canvas.create_line(3, 7, 18, 7, fill="yellow", width=1)
            if not element & 0x04:  # draw stairs on top if no top wall (looks better)
                canvas.create_line(3, 1, 18, 1, fill="yellow", width=1)
            if not element & 0x08:  # draw stairs on bottom if no bottom wall (looks better)
                canvas.create_line(3, 9, 18, 9, fill="yellow", width=1)

        # handle items, doors, and bad guys
        item_list = [self.data[0x100 * room_num + 0x10 * x: 0x100 * room_num + 0x10 * (x+1)] for x in range(0x08, 0x10)]
        for item in item_list:
            item_XYlocation = item[1]
            item_Ylocation = (item_XYlocation // 0x10) % 0x05  # first digit, can be 0-4
            item_Xlocation = (item_XYlocation % 0x10) % 0x08  # second digit, can be 0-7 -- sometimes 0x0B, 0x0C

            if item_Xlocation == col and 2 * item_Ylocation == row:
                item_type = item[0]
                fill = None
                chest_contents = None
                if item_type == 0x00:  # nothing
                    pass
                elif item_type == 0x10:  # regular bad guy
                    fill = "blue"
                elif item_type == 0x20:  # SS bad guy
                    fill = "white"
                elif item_type == 0x30:  # chest
                    fill = "green"
                    chest_contents = item[0x02]
                elif item_type == 0x40:  # body
                    fill = "brown"
                elif item_type == 0x50:  # door # todo: display doors
                    pass
                elif item_type == 0x70:     # no idea what this is; might have to do with generating
                    pass                    # SS bad guys that chase you between rooms # todo: figure out 0x70

                if fill:
                    canvas.create_rectangle(3, 3, 18, 9, fill=fill)
                if chest_contents:
                    chest_text = None
                    if chest_contents in [0x01, 0x09]:
                        chest_text = "B"
                    elif chest_contents in [0x02, 0x0a]:
                        chest_text = "G"
                    elif chest_contents in [0x03, 0x0b]:
                        chest_text = "U"
                    elif chest_contents in [0x04, 0x0c]:
                        chest_text = "V"
                    elif chest_contents == 0x0F:
                        chest_text = "WP"

                    if chest_text:
                        canvas.create_text(10, 5, text=chest_text, fill="white", font=("Times", -14))


    def get_player_data(self):
        '''
        todo: handle keys
        '''
        msg = ''
        room_number = self.data[0x40]

        bullets = self.data[0x47]
        grenades = self.data[0x48]
        have_uniform = bool(self.data[0x49])
        have_vest = bool(self.data[0x4a])

        rank_score = self.data[0x6d]
        have_war_plans = bool(self.data[0x6c])

        msg += time.strftime('%H:%M:%S') + '\n'
        msg += 'Rank: {0} ({1})\n'.format(Castle.get_rank_from_score(rank_score), rank_score)
        msg += 'Room Number: {}\n'.format(room_number)
        msg += 'Floor: {}\n'.format(Castle.get_floor(room_number))
        msg += 'Bullets: {}\n'.format(bullets)
        msg += 'Grenades: {}\n'.format(grenades)
        if have_uniform:
            msg += "You are wearing a uniform\n"
        if have_vest:
            msg += "You are wearing a vest\n"
        if have_war_plans:
            msg += "You've got the War Plans!\n"
        return msg

    def get_chest_contents(self):
        msg = ''
        bullet_rooms = []
        grenade_rooms = []
        uniform_rooms = []
        vest_rooms = []
        warplans_rooms = []

        for i in range(1, 61):  # each room
            for j in range(0, 0x10):  # each item
                if self.data[i * 0x100 + j * 0x10] == 0x30:  # if chest
                    chestitem = self.data[i * 0x100 + j * 0x10 + 0x02]
                    if chestitem in [0x01, 0x09]:
                        bullet_rooms.append(i)
                    elif chestitem in [0x02, 0x0a]:
                        grenade_rooms.append(i)
                    elif chestitem in [0x03, 0x0b]:
                        uniform_rooms.append(i)
                    elif chestitem in [0x04, 0x0c]:
                        vest_rooms.append(i)
                    elif chestitem == 0x0F:
                        warplans_rooms.append(i)
                    elif chestitem >= 0x0F:
                        print("Room {0} has unknown item: {1}.".format(i, chestitem))

        msg += "Rooms with bullets: {}\n".format(bullet_rooms)
        msg += "Rooms with grenades: {}\n".format(grenade_rooms)
        msg += "Rooms with uniforms: {}\n".format(uniform_rooms)
        msg += "Rooms with vests: {}\n".format(vest_rooms)
        msg += "Rooms with War Plans: {}\n".format(warplans_rooms)
        return msg

    def fix_chests(self):
        self.load()
        for i in range(1, 61):  # each room
            for j in range(0x08, 0x10):  # each item
                if self.data[i * 0x100 + j * 0x10] == 0x30:  # if chest
                    if self.data[i * 0x100 + j * 0x10 + 4] != 0:  # and chest not already open
                        self.data[i * 0x100 + j * 0x10 + 4] = 0x01  # set to 1 sec
        self.save()

    def set_location(self, room_number):
        self.load()
        self.data[0x40] = room_number
        self.data[0x58] = room_number  # this is different only when caught/killed/escape
        self.save()

    def max_player_inventory(self):
        self.load()
        self.data[0x47] = 0xFF  # bullets
        self.data[0x48] = 0xFF  # grenades
        self.data[0x49] = 0x01  # uniform
        self.data[0x4a] = 0x01  # vest
        self.save()

    def steal_warplans(self):
        self.load()
        self.data[0x6c] = 0x01  # war plans
        self.save()

    def set_rank(self, rank):
        """
        takes either a string or integer
        """
        self.load()
        rank_dict = {'private': 0x10,
                     'corporal': 0x30,
                     'sergeant': 0x50,
                     'lieutenant': 0x70,
                     'captain': 0x90,
                     'colonel': 0xb0,
                     'general': 0xd0,
                     'field marshal': 0xf0
                     }

        if isinstance(rank, str):
            rank = rank_dict[rank.lower()]

        self.data[0x6d] = rank
        self.save()

    @staticmethod
    def get_rank_from_score(rank_score):
        """
        add 0x10 for escape w/o plans, 0x20 escape w/ plans
        subtract 1 for each time caught/killed (I think only if Room>1)
        """
        if 0x00 <= rank_score < 0x20:
            return "Private"
        elif 0x20 <= rank_score < 0x40:
            return "Corporal"
        elif 0x40 <= rank_score < 0x60:
            return "Sergeant"
        elif 0x60 <= rank_score < 0x80:
            return "Lieutenant"
        elif 0x80 <= rank_score < 0xa0:
            return "Captain"
        elif 0xa0 <= rank_score < 0xc0:
            return "Colonel"
        elif 0xc0 <= rank_score < 0xe0:
            return "General"
        elif 0xe0 <= rank_score <= 0xff:
            return "Field Marshal"
        else:
            return None

    @staticmethod
    def get_floor(room_number):
        if room_number == 1:
            return 1
        elif 2 <= room_number <= 10:
            return 2
        elif 11 <= room_number <= 35:
            return 3
        elif 36 <= room_number <= 51:
            return 4
        elif 52 <= room_number <= 60:
            return 5
        else:
            return None  # hopefully this never happens

    @staticmethod
    def get_room_number(floor, i, j):
        floor0_dict = {
            0: [None, None, None, None, None],
            1: [None, None, None, None, None],
            2: [None, None,    1, None, None],
            3: [None, None, None, None, None],
            4: [None, None, None, None, None]
        }
        floor1_dict = {
            0: [None, None, None, None, None],
            1: [None,    8,    9,   10, None],
            2: [None,    5,    6,    7, None],
            3: [None,    2,    3,    4, None],
            4: [None, None, None, None, None]
        }
        floor2_dict = {
            0: [31, 32, 33, 34, 35],
            1: [26, 27, 28, 29, 30],
            2: [21, 22, 23, 24, 25],
            3: [16, 17, 18, 19, 20],
            4: [11, 12, 13, 14, 15]
        }
        floor3_dict = {
            0: [  48,   49,   50,   51, None],
            1: [  44,   45,   46,   47, None],
            2: [  40,   41,   42,   43, None],
            3: [  36,   37,   38,   39, None],
            4: [None, None, None, None, None]
        }
        floor4_dict = {
            0: [None, None, None, None, None],
            1: [None,   58,   59,   60, None],
            2: [None,   55,   56,   57, None],
            3: [None,   52,   53,   54, None],
            4: [None, None, None, None, None]
        }

        room_dict = {
            0: floor0_dict,
            1: floor1_dict,
            2: floor2_dict,
            3: floor3_dict,
            4: floor4_dict
        }

        return room_dict[floor][i][j]


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.info_msg_text = tk.StringVar()
        self.status_msg_text = tk.StringVar()
        self.status_msg_text.set('this is the status bar!')
        self.castle = Castle(save_game_path)
        self.refresh_data()

        self.title("Castle Wolfenhelper")
        self.init_menu()
        self.init_frames()

    def do_nothing(self):
        print("doing nothing")

    def fix_chests(self):
        self.castle.fix_chests()
        self.refresh_data()

    def max_player_inventory(self):
        self.castle.max_player_inventory()
        self.refresh_data()

    def steal_warplans(self):
        self.castle.steal_warplans()
        self.refresh_data()

    def init_menu(self):
        ### top menu bar ###
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        FileMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=FileMenu)
        FileMenu.add_command(label="Set Save Game Location", command=self.do_nothing)  # todo: implement file chooser
        FileMenu.add_command(label="Refresh", command=self.refresh_data)
        FileMenu.add_command(label="Set Auto-Refresh", command=self.do_nothing)  # todo: dialog box to refresh every X seconds
        FileMenu.add_separator()
        FileMenu.add_command(label="Exit", command=self.quit)

        CheatMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cheat", menu=CheatMenu)
        CheatMenu.add_command(label="Fix Chests", command=self.fix_chests)
        CheatMenu.add_command(label="Max Inventory", command=self.max_player_inventory)
        CheatMenu.add_command(label="Set Location", command=self.do_nothing)  # todo: implement location dialog box
        CheatMenu.add_command(label="Set Rank", command=self.do_nothing)  # todo: implement rank dialog box
        CheatMenu.add_command(label="Steal War Plans", command=self.steal_warplans)

        HelpMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=CheatMenu)
        HelpMenu.add_command(label="Controls", command=self.do_nothing) # todo: implement msgbox with controls
        HelpMenu.add_command(label="Project Info", command=self.do_nothing)  # todo: implement msgbox with info
        HelpMenu.add_command(label="Legend", command=self.do_nothing)  # todo: msgbox w/ room object colors

    def init_frames(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ### left side info ###
        info_msg = tk.Message(self, width=400, textvariable=self.info_msg_text, anchor=tk.NW)
        info_msg.grid(row=0, column=0, sticky=tk.N+tk.E+tk.S+tk.W)


        ### right side map ###
        map_notebook = ttk.Notebook(self)
        for i in range(5):
            map_notebook.grid_columnconfigure(i, weight=1)
            map_notebook.grid_rowconfigure(i, weight=1)
        map_floors = []
        grey_style = ttk.Style()
        grey_style.configure("grey.TFrame", background="grey", bd=3, relief=tk.GROOVE)

        for floor_num in range(5):
            floor_frame = ttk.Frame(map_notebook)
            map_floors.append(floor_frame)
            map_notebook.add(floor_frame, text="{}F".format(str(floor_num+1)))
            for i in range(5):
                for j in range(5):
                    fm = ttk.Frame(floor_frame, width=160, height=90, style="grey.TFrame")
                    fm.grid(row=i, column=j, sticky=tk.N + tk.E + tk.S + tk.W)
                    room_num = Castle.get_room_number(floor_num, i, j)
                    if room_num is not None:
                        for k in range(8):
                            for l in range(9):
                                canvas = tk.Canvas(fm, width=20, height=10, bd=0, highlightthickness=0,
                                                   relief=tk.RIDGE, background="black")
                                self.castle.draw_canvas(canvas, room_num, k, l)
                                canvas.grid(column=k, row=l)
                    if floor_num == j == 4 and i ==3:
                        lbl = tk.Label(fm, text="==> ESCAPE!")
                        lbl.grid()

        map_notebook.grid(row=0, column=1, sticky=tk.N+tk.E+tk.W+tk.S)

        ### bottom status bar ###
        status_label = tk.Label(self, textvariable=self.status_msg_text,
                                relief=tk.GROOVE, padx=3, pady=3, anchor=tk.W
                                )
        status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E)

    def refresh_data(self):
        self.castle.load()
        self.info_msg_text.set(self.castle.get_player_data() + self.castle.get_chest_contents())
        # todo: refresh map


def main():
    mw = MainWindow()
    mw.mainloop()

if __name__ == '__main__':
    main()

