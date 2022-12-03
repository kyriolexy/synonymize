import tkinter
from tkinter import filedialog
import tkinter.messagebox
import customtkinter
import textract
import os
from contextlib import redirect_stdout
import webbrowser as wb
import string
from api import get_related

REMOVE_PUNCT = str.maketrans(string.punctuation, " " * len(string.punctuation))
SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
R_SUBSCRIPT = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(
    "blue"
)  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Synonymizer")
        self.geometry(f"{1100}x{580}")
        self.resizable(width=False, height=False)

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(
            master=self, width=180, corner_radius=0
        )
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_left ============
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Synonymizer", font=("Roboto", -16)
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_2 = customtkinter.CTkButton(
            self.sidebar_frame, text="Export", command=lambda: self.export()
        )
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(
            self.sidebar_frame,
            text="Credits",
            command=lambda: wb.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        )
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="UI Scaling:", anchor="w"
        )
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling,
        )
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=1)
        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(
            row=0, column=0, columnspan=2, rowspan=10, pady=20, padx=20, sticky="nsew"
        )

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.rowconfigure(1, weight=9)
        self.frame_info.columnconfigure(0)

        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        self.text_info = customtkinter.CTkLabel(master=self.frame_info, text="Text:")
        self.text_info.grid(row=0, column=0, columnspan=2, pady=0, padx=0, sticky="")
        self.textbox = customtkinter.CTkTextbox(master=self.frame_info)
        self.textbox.grid(
            row=1, column=0, rowspan=9, columnspan=2, pady=5, padx=5, sticky="nsew"
        )

        # ============ frame_right ============

        self.frame_right_label = customtkinter.CTkLabel(
            master=self.frame_right, text="Actions:"
        )
        self.frame_right_label.grid(
            row=0, column=2, columnspan=1, pady=20, padx=10, sticky=""
        )

        self.analyze = customtkinter.CTkButton(
            master=self.frame_right,
            width=120,
            height=32,
            text="Analyze word",
            command=self.analyze,
        )
        self.analyze.grid(row=1, column=2, pady=10, padx=20, sticky="n")

        self.replace = customtkinter.CTkButton(
            master=self.frame_right,
            width=120,
            height=32,
            text="Replace word",
            command=self.replace,
        )
        self.replace.grid(row=2, column=2, pady=10, padx=20, sticky="n")

        self.combo_val = customtkinter.StringVar(value="")
        self.combobox = customtkinter.CTkComboBox(
            master=self.frame_right,
            values=[""],
            command=self.combobox_event,
            variable=self.combo_val,
        )
        self.combobox.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        # set default values
        # self.button_import(start=True)
        self._start_ran = False
        self.sidebar_button_1 = customtkinter.CTkButton(
            self.sidebar_frame, text="Import", command=self.button_import()
        )
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

    def button_import(self):
        start = self._start_ran
        filetypes = (
            (
                "Text files",
                "*.csv *.doc *.docx *.eml *.epub *.gif *jpg *.jpeg *.json *.html *.htm *.mp3 *.msg *.odt \
            *.ogg *.pdf *.png *.pptx *.ps *.rtf *.tiff *.tif *.txt *.wav *.xlsx *.xls",
            ),
            ("All files", "*.*"),
        )

        if start is None:
            with redirect_stdout(os.devnull):
                filename = filedialog.askopenfilename(
                    title="Open a supported Text File",
                    filetypes=filetypes,
                    initialdir=f"{os.path.expanduser('~')}\\Documents",
                )

            try:
                processed = textract.process(filename)
            except Exception as e:
                tkinter.messagebox.showerror("An Error has occurred", e)
                return False
        else:
            with open("defaultvalues.txt", "r") as _f:
                processed = _f.read()
        # self.textbox.delete("1.0", tkinter.END)
        processed = processed.replace("\n", " \n")
        _processed = ""
        c = 0
        for i in processed.split(" "):
            punct = i[-1] if i[-1] in string.punctuation else ""
            p_bool = punct == ""
            _processed += (
                f" {i if p_bool else i[:-1]}{str(c).translate(SUBSCRIPT)}{punct}"
            )
            # print(f"{c=}: {repr(_processed)=}")
            c += 1

        self.textbox.insert("1.0", _processed)
        self._start_ran = True
        return True

    def button_event(self):
        print("Button pressed")

    def export(self):
        text = self.textbox.get("1.0", tkinter.END)
        with redirect_stdout(os.devnull):
            filename = tkinter.filedialog.asksaveasfilename(
                title="Save to folder",
                initialfile="Untitled.txt",
                initialdir=f"{os.path.expanduser('~')}\\Documents",
                defaultextension=".txt",
                filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")],
            )
            with open(filename, "w") as f:
                f.write(self.textbox.get("1.0", tkinter.END))

    def replace(self):
        choice = self.combobox.get()
        r_ind = int(
            self.textbox.get("1.0", tkinter.END)
            .translate(R_SUBSCRIPT)
            .find(self._sel.translate(R_SUBSCRIPT) + " ")
        )
        text = self.textbox.get("1.0", tkinter.END)
        self.textbox.destroy()
        self.textbox = customtkinter.CTkTextbox(master=self.frame_info)
        self.textbox.grid(
            row=1, column=0, rowspan=9, columnspan=2, pady=5, padx=5, sticky="nsew"
        )
        _text = text[:r_ind] + choice + text[r_ind + len(self.sel) - 1 :]
        self.textbox.insert("1.0", _text)

        self.sel, self._sel = choice + self.subscr, choice + self.subscr

    def combobox_event(self, choice):
        """
        this shit is stupid
        fuck you you tkinter bastards
        """
        # r_ind = (
        #     a
        #     if (a := self.textbox.get("1.0", tkinter.END).rfind(self.sel + " ")) == -1
        #     else self.textbox.get("1.0", tkinter.END).rfind(self.sel + "\n")
        # )
        text = self.textbox.get("1.0", tkinter.END)
        r_ind = int(
            text.translate(R_SUBSCRIPT).find(self._sel.translate(R_SUBSCRIPT) + " ")
        )
        self.textbox.destroy()
        self.textbox = customtkinter.CTkTextbox(master=self.frame_info)
        self.textbox.grid(
            row=1, column=0, rowspan=9, columnspan=2, pady=5, padx=5, sticky="nsew"
        )
        a = text[r_ind + len(self.sel) - 1 :]
        _text = text[:r_ind] + choice + text[r_ind + len(self._sel) - 1 :]
        self.textbox.insert("1.0", _text)

        self._sel = choice + self.subscr

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def analyze(self):
        try:
            _sel = self.textbox.selection_get()
            sel = "".join(
                [
                    i
                    for i in self.textbox.selection_get()
                    .translate(REMOVE_PUNCT)
                    .lower()
                    if i.isalpha()
                ]
            )
        except __import__("_tkinter").TclError:
            tkinter.messagebox.showwarning("Warning", "No selected textbox")
            return

        if sel.count(" ") > 1:
            self.textbox.selection_clear()
            tkinter.messagebox.showwarning("Warning", "Selected more than one word")
            return

        self.sel, self._sel = _sel, _sel
        self.subscr = "".join([i for i in _sel if not i.isalpha()])
        self.combobox.configure(values=get_related(sel))
        self.combo_val.set(value=sel)

    def change_scaling(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
