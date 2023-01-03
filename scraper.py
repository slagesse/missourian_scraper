# Import Libraries #
import gspread
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Async
import threading

event = threading.Event()

import os

path = os.path.realpath(__file__)[:-11]


# Wait function because I'm lazy
def wait(seconds):
    print("Waiting " + str(seconds) + " seconds...")
    time.sleep(seconds)


# -=- Scraper Class -=- #
class CandidateScraper:
    def __init__(self, name, sheet, page, cells, indices):
        self.name = name;
        self.indices = indices
        self.sheet = sheet
        self.page = page
        self.cells = cells.split(", ")
        self.scraped_data = []

    def scrape(self):
        wait(0.5)
        print("Scraping: " + self.name)
        # Initialize Selenium driver
        print("Requesting website HTML...")
        Options().add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options())
        try:
            driver.get("https://enr.sos.mo.gov")
            print("HTML received.")
        except:
            print("Error requesting HTML.")
            pass
        # Submit form to generate table
        print("Submitting form...")
        driver.find_element(By.ID, "MainContent_btnElectionType").click()
        wait(3)
        print("Form submitted.")

        if self.sheet[0:3].lower() == "ame":
            number = (6 - int(self.sheet[-1])) * 5 + 4
            print(number)
            print("Scraping: Amendment " + str(number) + "...")
            # Find element via subject name
            table_length = len(driver.find_elements(By.XPATH, "//table[@class='electtable']//tbody//tr"))
            actual_number = table_length - number

            xpaths = ["//table[@class='electtable']//tbody//tr[" + str(actual_number) + "]", "//table[@class='electtable']//tbody//tr[" + str(actual_number + 1) + "]", "//table[@class='electtable']//tbody//tr[" + str(actual_number + 2) + "]", "//table[@class='electtable']//tbody//tr[" + str(actual_number + 3) + "]", ]

            for i in range(len(xpaths)):
                try:
                    subject_row = driver.find_element(By.XPATH, xpaths[i])

                    row_contents = subject_row.find_elements(By.XPATH, "*")

                    index_data = []

                    for cell in row_contents:
                        try:
                            index_data.append(cell.find_element(By.XPATH, "*").find_element(By.XPATH, "*").find_element(By.XPATH, "*").find_element(By.XPATH, "*").get_attribute("innerHTML").replace(u"\u00A0", " "))
                        except:
                            try:
                                index_data.append(cell.find_element(By.XPATH, "*").find_element(By.XPATH, "*").find_element(By.XPATH, "*").get_attribute("innerHTML").replace(u"\u00A0", " "))
                            except:
                                try:
                                    index_data.append(cell.find_element(By.XPATH, "*").get_attribute("innerHTML").replace(u"\u00A0", " "))  # This picks up some nasty little none
                                except:
                                    index_data.append(cell.get_attribute("innerHTML"))


                except:
                    print("Error scraping \"" + "amendment " + "\"")
                    driver.quit()
                    pass

                self.scraped_data.append(index_data)


        else:
            for index in self.indices:
                print("Scraping: " + index + "...")
                # Find element via subject name
                xpath = "//*[contains(text(), '" + index + "')]"

                try:
                    subject_name_element = driver.find_element(By.XPATH, xpath)
                    if subject_name_element.tag_name == "strong":
                        subject_row = subject_name_element.find_element(By.XPATH, "./..").find_element(By.XPATH, "./..")
                    else:
                        subject_row = subject_name_element.find_element(By.XPATH, "./..")

                    row_contents = subject_row.find_elements(By.XPATH, "*")

                    index_data = []

                    for cell in row_contents:
                        try:
                            print("Strong")
                            index_data.append(cell.find_element(By.XPATH, "*").get_attribute("innerHTML"))
                        except:
                            print("Normal")
                            index_data.append(cell.get_attribute("innerHTML"));  # This picks up some nasty little non
                except:
                    print("Error scraping \"" + index + "\"")
                    driver.quit()
                    pass

                self.scraped_data.append(index_data)
                print(index + " successfully scraped.")

        wait(1)
        driver.quit()
        print(self.name + " successfully scraped.\n[=========================================================]")

    def update_spreadsheet(self):
        print("Requesting spreadsheet...")
        gc = gspread.service_account(filename=os.path.dirname(os.path.realpath(__file__)) + '/creds.json')
        spreadsheet = gc.open(self.sheet)
        ws = spreadsheet.get_worksheet(self.page)
        print("Spreadsheet received.")
        i = 0
        print(self.scraped_data)
        for index in self.scraped_data:
            print("Writing " + index[0] + "...")
            letter = self.cells[i][0]
            for data in index:

                cell = letter + self.cells[i][1]
                print(cell, data)
                ws.update(cell, data)
                letter = chr(ord(letter) + 1)
            print("Success.")
            i += 1
        print("[=========================================================]")
        self.clear_data()

    def clear_data(self):
        self.scraped_data = []


# -=- Graphical Interface -=- #
from tkinter import *
from tkinter import ttk
from tkmacosx import Button
import tkinter.font as tkFont


class MainWindow(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self)
        self.title("Columbia Missourian - Midterm Scraper")
        self.geometry("800x500")
        self.resizable(True, True)

        # Declare Fonts #
        self.missourian_logo = tkFont.Font(family="Big Caslon", size=60, weight="bold")
        self.nav_text_1 = tkFont.Font(family="Helvetica", size=80, weight="bold")
        self.nav_text_2 = tkFont.Font(family="Helvetica", size=50, weight="bold")
        self.small_window_text = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.smaller_window_text = tkFont.Font(family="Helvetica", size=14)
        self.edit_font = tkFont.Font(family="Helvetica", size=20)

        # Declare Colors #
        self.dark_blue = "#10387d"
        self.off_white = "#ececec"
        self.dark_gray = "#383838"
        self.gray = "#4f4f4f"
        self.orange = "#FF7F11"
        self.coral = "#EF767A"
        self.green = "#6CAE75"
        self.light_gray = "#A3A3A3"
        self.lighter_gray = "#6F6F6F"
        self.light_blue = "#06AED5"
        self.dark_orange = "#AD6A2F"

        # Threading stuff
        self.loop = IntVar()
        self.frequency = StringVar()

        self.var = []
        self.scraper_data = []
        self.scrapers = []

        self.nav = Nav(self)
        self.scraper_list = ScraperList(self)

        self.nav.grid(row=0, column=0, sticky=NS)

        self.scraper_list.grid(row=0, column=1, sticky=NSEW)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.time_dict = {"": 10, "10s": 10, "5m": 300, "10m": 600, "15m": 900, "30m": 1800, "1hr": 3600, "2hr": 7200}

        self.running = False

    def generate_scraper(self, parentWindow, name, sheet, page, cells, indices):
        print("generating...")
        parentWindow.destroy()  # Close "Add Scraper" window
        if isinstance(page, int):
            splitIndices = indices.split(", ")
            self.scraper_data.append([name, sheet, page, cells, splitIndices])
            self.scrapers.append(CandidateScraper(name, sheet, page, cells, splitIndices))
            self.scraper_list.update_scraper_list()

    def edit_scraper(self, parent, index, newName, newSheet, newPage, newCells, newIndices):
        parent.destroy()  # Close "Edit Scraper" window
        if isinstance(self.scraper_data[index][2], int):
            print(newIndices.split(", "))
            self.scraper_data[index] = [newName, newSheet, newPage, newCells, newIndices.split(", ")]
            self.scrapers[index] = CandidateScraper(newName, newSheet, newPage, newCells, newIndices.split(", "))
            self.scraper_list.update_scraper_list()

    def delete_scraper(self, index):
        del self.scraper_data[index]
        del self.scrapers[index]
        self.scraper_list.update_scraper_list()

    def open_saved_scrapers(self):
        self.scraper_bank = SavedScrapersBank(self)

    def save_scraper(self, index):
        openFile = open(path + "/saves/saved_scrapers.txt", "a")
        for attribute in self.scraper_data[index]:
            if type(attribute) == list:
                for sub_attribute in attribute:
                    openFile.write(str(sub_attribute))
                    if sub_attribute != attribute[-1]:
                        openFile.write(", ")
            else:
                openFile.write(str(attribute) + "%")
        openFile.close()
        if type(self.scraper_bank) != None:
            self.scraper_bank.load_scrapers()
            self.scraper_bank.update_saved_scraper_list()

    def cycle_scrapers(self):
        if self.running:
            self.nav.run_scrapers_button.configure(text="\u25b8")
            self.nav.run_scrapers_button.update()
            self.nav.run_scrapers_button["background"] = self.orange
            event.set()
            print("Ending processes...")
            event.clear()
            self.running = False
        else:
            self.nav.run_scrapers_button.configure(text="\u25a0")
            self.nav.run_scrapers_button.update()
            self.nav.run_scrapers_button["background"] = self.dark_orange
            scraper_thread_loop = threading.Thread(target=self.loop_scrapers, args=(), daemon=True)
            scraper_thread = threading.Thread(target=self.loop_scrapers, args=(), daemon=True)
            if self.loop.get() == 1:
                scraper_thread_loop.start()
            else:
                scraper_thread.start()
            self.running = True

    def loop_scrapers(self):
        print('Running')
        if len(self.scrapers) > 0:
            i = 0
            for scraper in self.scrapers:
                if self.var[i].get() == 1:
                    scraper.scrape()
                    scraper.update_spreadsheet()
                    print(scraper.name + " successfully scraped.")
                i += 1
        wait(self.time_dict[self.frequency.get()])
        while self.frequency.get() != "" and not event.is_set():
            if len(self.scrapers) > 0:
                i = 0
                for scraper in self.scrapers:
                    if self.var[i].get() == 1:
                        scraper.scrape()
                        scraper.update_spreadsheet()
                        print(scraper.name + " successfully scraped.")
                    i += 1
            wait(self.time_dict[self.frequency.get()])

    def run_scrapers(self):
        print('Running')
        if len(self.scrapers) > 0:
            i = 0
            for scraper in self.scrapers:
                if self.var[i].get() == 1:
                    scraper.scrape()
                    scraper.update_spreadsheet()
                    print(scraper.name + " successfully scraped.")
                i += 1


class Nav(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        options = {'bg': self.parent.dark_gray, 'width': 100, 'padx': 5, 'pady': 5}

        self.nav_heading = Label(self, text="M", font=parent.missourian_logo, background=parent.dark_gray, fg="white",
                                 borderwidth=0)
        self.nav_heading.pack(fill=X)

        self.new_scraper_button = Button(self, text="\u002B", font=parent.nav_text_1, borderless=1, bg=parent.green,
                                         fg="white", anchor=CENTER,
                                         command=lambda: AddScraperWindow(self), relief=SOLID, width=80)
        self.new_scraper_button.pack(fill=Y, expand=True)

        self.run_scrapers_button = Button(self, text="\u25b8", font=parent.nav_text_1, bd=0, fg="white",
                                          bg=parent.orange, anchor=CENTER,
                                          command=parent.cycle_scrapers,
                                          highlightcolor=parent.orange, relief=SOLID, width=80)
        self.run_scrapers_button.pack()

        self.saved_scrapers_button = Button(self, text="\u2b51", font=parent.nav_text_1, bd=0, fg="white",
                                            bg=parent.light_blue, anchor=CENTER,
                                            command=self.parent.open_saved_scrapers,
                                            highlightcolor=parent.light_blue, relief=SOLID, width=80)
        self.saved_scrapers_button.pack()

        self.configure_scrapers = Frame(self, bg=parent.dark_gray, padx=5, pady=5)
        self.configure_scrapers.pack(fill=BOTH)

        self.frame1 = Frame(self.configure_scrapers, bg=parent.dark_gray)
        self.loop_heading = Label(self.frame1, text="\U0001F501", font=parent.smaller_window_text,
                                  background=parent.dark_gray, fg="white",
                                  borderwidth=0)
        self.loop_heading.pack(side=LEFT)
        self.loop_checkbox = Checkbutton(self.frame1, variable=parent.loop, bg=parent.dark_gray, onvalue=1, offvalue=0)
        self.loop_checkbox.pack(side=LEFT, expand=TRUE)
        self.frame1.pack(fill=X)

        self.frame2 = Frame(self.configure_scrapers, bg=parent.dark_gray)
        self.frq_heading = Label(self.frame2, text="\u23F0", font=parent.smaller_window_text,
                                 background=parent.dark_gray, foreground="white",
                                 borderwidth=0)
        self.frq_heading.pack(side=LEFT)
        self.frq_combobox = ttk.Combobox(self.frame2, values=["10s", "5m", "10m", "15m", "30m", "1hr", "2hr"],
                                         width=3, background=parent.dark_gray, foreground=parent.dark_gray,
                                         textvariable=parent.frequency)
        self.frq_combobox.pack(side=LEFT, expand=True)
        self.frame2.pack(fill=X)


class ScraperList(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        options = {'bd': 0}

        self.scraper_list_canvas = Canvas(self, bg="#595959", bd=0, highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical",
                                   command=self.scraper_list_canvas.yview)
        self.scraper_list = Frame(self.scraper_list_canvas, bd=0)

        self.scraper_list.bind(
            "<Configure>",
            lambda e: self.scraper_list_canvas.configure(
                scrollregion=self.scraper_list_canvas.bbox("all")
            )
        )

        self.scraper_list_canvas.create_window((0, 0), window=self.scraper_list, anchor="nw")
        self.scraper_list_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scraper_list_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

    def update_scraper_list(self):
        i = 0

        for element in self.scraper_list.winfo_children():
            element.destroy()

        self.parent.var.append(IntVar())

        for index in root.scraper_data:
            scraper_frame = Frame(self.scraper_list, height=50, padx=10, pady=10, bg=root.gray,
                                  borderwidth=2)
            scraper_border = Frame(self.scraper_list, height=2, bg=root.lighter_gray,
                                   borderwidth=2)

            c1 = Checkbutton(scraper_frame, variable=root.var[i], onvalue=1, offvalue=0, bg=root.gray)
            c1.grid(row=0, column=0, sticky=W)
            scraper_header = Label(scraper_frame, text=index[0], font=root.small_window_text, bg=root.gray,
                                   fg="#7da7f0")
            scraper_target = Label(scraper_frame, text="\uFF5C Sheet: " + index[1], font=root.smaller_window_text,
                                   bg=root.gray)
            page_target = Label(scraper_frame, text="\uFF5C Page: " + str(index[2]), font=root.smaller_window_text,
                                bg=root.gray,
                                fg=root.light_gray)
            cells_target = Label(scraper_frame, text="\uFF5C Cells: " + index[3], font=root.smaller_window_text,
                                 bg=root.gray,
                                 fg=root.light_gray)
            # Shortens preview of targets if over 20 characters
            preview = ""
            if len(index[4][0]) > 20:
                preview = index[4][0][:20] + "..."
            else:
                preview = index[4][0]
            target_target = Label(scraper_frame, text="\uFF5C Targets: " + preview, font=root.smaller_window_text,
                                  bg=root.gray,
                                  fg=root.light_gray)

            edit_button = Button(scraper_frame, text="\u270E", bg=root.gray, highlightbackground=root.gray,
                                 borderless=1,
                                 fg=root.light_gray, width=32, font=root.edit_font,
                                 command=lambda i=i: EditScraperWindow(self, i))

            edit_button.update()

            delete_button = Button(scraper_frame, text="\u00d7", bg=root.gray, highlightbackground=root.gray,
                                   borderless=1,
                                   fg=root.light_gray, width=30, font=root.edit_font,
                                   command=lambda i=i: root.delete_scraper(i))

            save_button = Button(scraper_frame, text="\u2605", bg=root.gray, highlightbackground=root.gray,
                                 borderless=1,
                                 fg=root.light_gray, width=30, font=root.edit_font,
                                 command=lambda i=i: root.save_scraper(i))

            filler = Label(scraper_frame,
                           text="                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ",
                           font=root.smaller_window_text, bg=root.gray, fg=root.light_gray)

            scraper_frame.pack(fill=X)
            scraper_border.pack(fill=X)
            edit_button.grid(row=0, column=1)
            save_button.grid(row=0, column=2)
            delete_button.grid(row=0, column=3)
            scraper_header.grid(row=0, column=4, sticky=W)
            scraper_target.grid(row=0, column=5, sticky=W)
            page_target.grid(row=0, column=6, sticky=W)
            cells_target.grid(row=0, column=7, sticky=W)
            target_target.grid(row=0, column=8, sticky=W)
            filler.grid(row=0, column=9, sticky=W)
            i += 1


class AddScraperWindow(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title("Add Scraper")
        self.resizable(False, False)

        self.main = Frame(self, bg=root.dark_gray, padx=10, pady=10)
        self.main.pack(side=LEFT, fill=BOTH, expand=True)

        self.scraper_name_header = Label(self.main, text="Scraper name:", bg=root.dark_gray,
                                         font=root.small_window_text)
        self.scraper_name_header.grid(row=0, column=0, sticky=W)

        self.scraper_name_entry = Entry(self.main)
        self.scraper_name_entry.grid(row=1, column=0, sticky=W)

        self.spreadsheet_header = Label(self.main, text="Spreadsheet name:", bg=root.dark_gray,
                                        font=root.small_window_text)
        self.spreadsheet_header.grid(row=2, column=0, sticky=W)

        self.spreadsheet_entry = Entry(self.main)
        self.spreadsheet_entry.grid(row=3, column=0, sticky=W)

        self.page_header = Label(self.main, text="Page number:", bg=root.dark_gray, font=root.small_window_text)
        self.page_header.grid(row=4, column=0, sticky=W)

        self.page_entry = Entry(self.main)
        self.page_entry.grid(row=5, column=0, sticky=W)

        self.cells_header = Label(self.main, text="Cells:", bg=root.dark_gray, font=root.small_window_text)
        self.cells_header.grid(row=6, column=0, sticky=W)

        self.cells_entry = Entry(self.main)
        self.cells_entry.grid(row=7, column=0, sticky=W)

        self.subject_header = Label(self.main, text="Targets:", bg=root.dark_gray, font=root.small_window_text)
        self.subject_header.grid(row=8, column=0, sticky=W)

        self.subject_entry = Entry(self.main)
        self.subject_entry.grid(row=9, column=0, sticky=W)

        self.create_button = Button(self.main, text="Add Scraper",
                                    command=lambda: root.generate_scraper(self, self.scraper_name_entry.get(),
                                                                          self.spreadsheet_entry.get(),
                                                                          int(self.page_entry.get()),
                                                                          self.page_entry.get(),
                                                                          self.subject_entry.get()))
        self.create_button.grid(row=10, column=0, sticky=NSEW)


class EditScraperWindow(Toplevel):
    def __init__(self, parent, index):
        Toplevel.__init__(self, parent)
        self.title("Edit Scraper")
        self.resizable(False, False)

        self.main = Frame(self, bg=root.dark_gray, padx=10, pady=10)
        self.main.pack(side=LEFT, fill=BOTH, expand=True)

        self.scraper_name_header = Label(self.main, text="Scraper name:", bg=root.dark_gray,
                                         font=root.small_window_text)
        self.scraper_name_header.grid(row=0, column=0, sticky=W)

        self.scraper_name_entry = Entry(self.main)
        self.scraper_name_entry.grid(row=1, column=0, sticky=W)
        self.scraper_name_entry.insert(0, root.scraper_data[index][0])

        self.spreadsheet_header = Label(self.main, text="Spreadsheet name:", bg=root.dark_gray,
                                        font=root.small_window_text)
        self.spreadsheet_header.grid(row=2, column=0, sticky=W)

        self.spreadsheet_entry = Entry(self.main)
        self.spreadsheet_entry.grid(row=3, column=0, sticky=W)
        self.spreadsheet_entry.insert(0, root.scraper_data[index][1])

        self.page_header = Label(self.main, text="Page number:", bg=root.dark_gray, font=root.small_window_text)
        self.page_header.grid(row=4, column=0, sticky=W)

        self.page_entry = Entry(self.main)
        self.page_entry.grid(row=5, column=0, sticky=W)
        self.page_entry.insert(0, root.scraper_data[index][2])

        self.cells_header = Label(self.main, text="Cells:", bg=root.dark_gray, font=root.small_window_text)
        self.cells_header.grid(row=6, column=0, sticky=W)

        self.cells_entry = Entry(self.main)
        self.cells_entry.grid(row=7, column=0, sticky=W)
        self.cells_entry.insert(0, root.scraper_data[index][3])

        self.subject_header = Label(self.main, text="Targets:", bg=root.dark_gray, font=root.small_window_text)
        self.subject_header.grid(row=8, column=0, sticky=W)

        self.subject_entry = Entry(self.main)
        self.subject_entry.grid(row=9, column=0, sticky=W)
        self.subject_entry.insert(0, ", ".join(root.scraper_data[index][4]))

        self.create_button = Button(self.main, text="Save Changes",
                                    command=lambda: root.edit_scraper(self, index, self.scraper_name_entry.get(),
                                                                      self.spreadsheet_entry.get(),
                                                                      int(self.page_entry.get()),
                                                                      self.cells_entry.get(),
                                                                      self.subject_entry.get()))
        self.create_button.grid(row=10, column=0, sticky=NSEW)


class SavedScrapersBank(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.parent = parent

        self.title("Saved Scraper Bank")
        self.geometry("500x300")
        self.resizable(True, True)

        self.saved_scraper_data = []

        self.scraper_list = ScraperList(self)
        self.scraper_list.pack(fill=BOTH, expand=True)

        self.load_scrapers()
        self.update_saved_scraper_list()

    def upload_scraper(self, index):
        self.parent.generate_scraper(self,
                                     self.saved_scraper_data[index][0], self.saved_scraper_data[index][1],
                                     int(self.saved_scraper_data[index][2]), self.saved_scraper_data[index][3],
                                     self.saved_scraper_data[index][4])

    def load_scrapers(self):
        openFile = open(path + "/saves/saved_scrapers.txt", "r")
        self.saved_scraper_data = []

        for line in openFile.read().splitlines():
            tempList = line.split("%")
            self.saved_scraper_data.append(tempList)

    def delete_scraper(self, index):
        del self.saved_scraper_data[index]
        print(self.saved_scraper_data)
        with open(path + "/saves/saved_scrapers.txt", "r") as f:
            lines = f.readlines()
        with open(path + "/saves/saved_scrapers.txt", "w") as f:
            self.j = 0
            print(index)
            for line in lines:
                if self.j != index:
                    f.write(line)
                self.j += 1

        self.update_saved_scraper_list()

    def update_saved_scraper_list(self):
        i = 0
        for element in self.scraper_list.scraper_list.winfo_children():
            element.destroy()

        self.parent.var.append(IntVar())

        for index in self.saved_scraper_data:
            self.scraper_frame = Frame(self.scraper_list.scraper_list, height=50, padx=10, pady=10, bg=self.parent.gray,
                                       borderwidth=2)
            self.scraper_border = Frame(self.scraper_list.scraper_list, height=2, bg=self.parent.lighter_gray,
                                        borderwidth=2)
            self.scraper_header = Label(self.scraper_frame, text=index[0], font=self.parent.small_window_text,
                                        bg=self.parent.gray,
                                        fg="#7da7f0")
            self.scraper_target = Label(self.scraper_frame, text="\uFF5C Sheet: " + index[1],
                                        font=self.parent.smaller_window_text,
                                        bg=self.parent.gray)
            self.page_target = Label(self.scraper_frame, text="\uFF5C Page: " + str(index[2]),
                                     font=self.parent.smaller_window_text,
                                     bg=self.parent.gray,
                                     fg=self.parent.light_gray)
            self.cells_target = Label(self.scraper_frame, text="\uFF5C Cells: " + index[3],
                                      font=self.parent.smaller_window_text,
                                      bg=self.parent.gray,
                                      fg=self.parent.light_gray)
            # Shortens preview of targets if over 20 characters
            preview = ""
            if len(index[3][0]) > 20:
                preview = index[3][0][:20] + "..."
            else:
                preview = index[4]

            self.target_target = Label(self.scraper_frame, text="\uFF5C Targets: " + preview,
                                       font=self.parent.smaller_window_text,
                                       bg=self.parent.gray,
                                       fg=self.parent.light_gray)

            self.upload_button = Button(self.scraper_frame, text="\u21ea", bg=self.parent.gray,
                                        highlightbackground=self.parent.gray,
                                        borderless=1,
                                        fg=self.parent.light_gray, width=30, font=self.parent.edit_font,
                                        command=lambda i=i: self.upload_scraper(i))

            self.delete_button = Button(self.scraper_frame, text="\u00d7", bg=self.parent.gray,
                                        highlightbackground=self.parent.gray,
                                        borderless=1,
                                        fg=self.parent.light_gray, width=30, font=self.parent.edit_font,
                                        command=lambda i=i: self.delete_scraper(i))

            self.filler = Label(self.scraper_frame,
                                text="                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ",
                                font=self.parent.smaller_window_text, bg=self.parent.gray, fg=self.parent.light_gray)

            self.scraper_frame.pack(fill=X)
            self.scraper_border.pack(fill=X)
            self.upload_button.grid(row=0, column=0)
            self.delete_button.grid(row=0, column=1)
            self.scraper_header.grid(row=0, column=2, sticky=W)
            self.scraper_target.grid(row=0, column=3, sticky=W)
            self.page_target.grid(row=0, column=4, sticky=W)
            self.cells_target.grid(row=0, column=5, sticky=W)
            self.target_target.grid(row=0, column=6, sticky=W)
            self.filler.grid(row=0, column=7, sticky=W)
            i += 1


root = MainWindow()
root.mainloop()
