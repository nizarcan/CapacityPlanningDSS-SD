from tkinter import Tk, filedialog
import os


def ask_directory():
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    folder = filedialog.askdirectory(initialdir=os.path.expanduser("~/Desktop"), title="Klasör Seç")
    return folder


def ask_file(file_flags):
    # file_flags consists of tuple of tuples, i.e. (("jpeg files", "*.jpg"), ("all files", "*.*))
    root = Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    file_path = filedialog.askopenfile(initialdir=os.path.expanduser("~/Desktop"), title="Dosya Seç",
                                       filetypes=file_flags)
    return file_path


def ask_save_file(file_flags):
    # file_flags consists of tuple of tuples, i.e. (("jpeg files", "*.jpg"), ("all files", "*.*))
    root = Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    file_path = filedialog.asksaveasfile(initialdir=os.path.expanduser("~/Desktop"), title="Kaydet",
                                         filetypes=file_flags)
    return file_path


if __name__ == "__main__":
    a = ask_save_file((("Archive Files", "*.mng"),))
    print(a)
