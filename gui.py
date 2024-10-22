import tkinter as tk
from tkinter import filedialog
import ttkbootstrap  as ttk
import os
from ttkbootstrap import Style
from MinecraftSCtoTC import MinecraftSCtoTC
import logging
from ttkbootstrap.dialogs.dialogs import Messagebox
class MCTranslatorGUI(tk.Tk):
    src_path = ""
    """
    預計要翻譯的來源
    """
    dist_path = ""
    trans_dict_path=""

    def __init__(self):
        super().__init__()
        self.title('Minecraft 簡中轉繁體翻譯 ver.2024.10.22')
        self.geometry('900x600')
        self.style = Style(theme="lumen")
        self.configure(bg='lightgray')

        # tbutton_style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 13),bordercolor='#00FF00')
        choose_btn = ttk.Button(self,text="資料夾",style="TButton",command=self._select_directory)
        # choose_btn.config(spacing2=50,spacing1=50,spacing3=50)
        choose_btn.place(x=10,y=10,height=70,width=80)

        self.style.configure('TButton', font=('Arial', 13),bordercolor='#00FF00')
        choose_btn = ttk.Button(self,text="jar\r或檔案",style="TButton",command=self._select_directory2)
        # choose_btn.config(spacing2=50,spacing1=50,spacing3=50)
        choose_btn.place(x=100,y=10,height=70,width=90)

        # ttext_style = ttk.Style()
        self.style.configure('Custom.TLabel', font=('Arial', 12),padding=(5,0))
        self.directory_label1 = ttk.Label(self, text='當前要翻譯路徑:',justify="left",style="Custom.TLabel",borderwidth=2, relief='solid')
        self.directory_label1.place(x=200,y=10,anchor="nw",height=70,width=600)

        choose_btn = ttk.Button(self,text="選擇目的地資料夾",style="TButton",command=self._select_dist_directory)
        choose_btn.place(x=10,y=90,height=70,width=180)

        self.style.configure('Custom.TLabel', font=('Arial', 12),padding=(5,0))
        self.directory_label2 = ttk.Label(self, text='目的地資料夾:',justify="left",style="Custom.TLabel",borderwidth=2, relief='solid')
        self.directory_label2.place(x=200,y=90,anchor="nw",height=70,width=600)


        choose_btn = ttk.Button(self,text="替代文字文本",style="TButton",command=self._select_replace_directory)
        choose_btn.place(x=10,y=170,height=70,width=180)

        self.style.configure('Custom.TLabel', font=('Arial', 12),padding=(5,0))
        self.directory_label3 = ttk.Label(self, text='文本位置:',justify="left",style="Custom.TLabel",borderwidth=2, relief='solid')
        self.directory_label3.place(x=200,y=170,anchor="nw",height=70,width=600)

        choose_btn = ttk.Button(self,text="執行",style="TButton",command=self._execute_translate)
        choose_btn.place(x=10,y=250,height=70,width=180)

    def _select_directory(self):
        """
        選擇來源
        """
        current_directory = os.getcwd()
        _path = filedialog.askdirectory(initialdir=current_directory)
        # 絕對路徑
        if(_path == ''):
            self.directory_label1.config(text="未選擇翻譯來源")
        else:
            self.src_path = _path
            self.directory_label1.config(text=self.src_path)
    def _select_directory2(self):
        """
        選擇來源
        """
        current_directory = os.getcwd()
        _path = filedialog.askopenfilename(initialdir=current_directory)
        # 絕對路徑
        if(_path == ''):
            self.directory_label1.config(text="未選擇翻譯來源")
        else:
            self.src_path = _path
            self.directory_label1.config(text=self.src_path)
    def _select_dist_directory(self):
        """
        選擇目的地
        """
        current_directory = os.getcwd()
        _path = filedialog.askdirectory(initialdir=current_directory)
        # 絕對路徑
        if(_path == ''):
            self.directory_label2.config(text="未選擇目的地資料夾")
        else:
            self.dist_path = _path
            self.directory_label2.config(text=self.dist_path)
    def _select_replace_directory(self):
        """
        選擇替換文本
        """
        current_directory = os.getcwd()
        _path = filedialog.askopenfilename(initialdir=current_directory)
        # 絕對路徑
        if(_path == ''):
            self.directory_label3.config(text="無文本 (未選擇)")
        elif(os.path.isdir(_path)):
            self.directory_label3.config(text="無文本 (不可選擇資料夾)")
        else:
            self.trans_dict_path = _path
            self.directory_label3.config(text=self.trans_dict_path)
    
    def _execute_translate(self):
        msctc = MinecraftSCtoTC(
            dist_path = self.dist_path,
            trans_dict_file = self.trans_dict_path
        )
        logging.info(f'MCTranslatorGUI dist_path:{self.dist_path} src_path:{self.src_path} ')
        _result = msctc.common_parse_interface(src_path=self.src_path)
        self._Messagebox(_result)

    def _Messagebox(self,_result):
        if _result:
            Messagebox.ok(message="處理完成!",title="結果")
        else:
            Messagebox.show_warning(message="路徑錯誤或未選擇路徑",title="警告")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                            logging.FileHandler('app.log', mode='w',encoding='utf-8'),  # 日誌檔案
                            logging.StreamHandler()  # 控制台輸出
                        ]
                    )
    app = MCTranslatorGUI()
    app.mainloop()