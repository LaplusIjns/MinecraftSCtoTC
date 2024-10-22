import win32com.client
import os
import re
import shutil
import copy
import json
import logging
import concurrent.futures
import pythoncom
import time
from win32com.client import DispatchEx
from opencc import OpenCC
import zipfile
import fnmatch
from pathlib import Path

class MinecraftSCtoTC():
    """
    簡體翻譯成繁體
    """
    dist_path: str
    """
    dist_path: 翻譯結果目的地 預設 /example
    """
    prefer_trans_type: str
    """
    翻譯模式 opencc or word
    """
    warning_alert = "PLEASE RECHECK THIS TRANSLATION!"
    """
    翻譯出錯時替代字串
    """
    trans_dict_list:list
    """
    list of dict !!
    """
    _constant_dist_path = 'defaultFolder'
    _constant_prefer_trans_type = 'opencc'
    def __init__(self,dist_path=_constant_dist_path,prefer_trans_type=_constant_prefer_trans_type,trans_dict_list=None,trans_dict_file=None) -> None:

        try:
            if self._is_valid_file_path(dist_path):
                self.dist_path = dist_path
            else :
                logging.warning(f'不是合法路徑: {dist_path}')
                self.dist_path=self._constant_dist_path
            try:
                os.makedirs(self.dist_path)
            except Exception as e:
                logging.warning(f'路徑已存在')
        except Exception as e:
            logging.warning(f'__init__ 路徑初始化失敗: 絕對路徑: {os.path.abspath(dist_path)} Exception: {e}')

        if(prefer_trans_type=='word' or prefer_trans_type=='opencc'):
            self.prefer_trans_type = prefer_trans_type
        else :
            logging.warning(f'不是合法翻譯類型: {prefer_trans_type}')
            self.prefer_trans_type = self._constant_prefer_trans_type
        self.trans_dict_list = trans_dict_list
        self.trans_dict_list = [] if trans_dict_list is None else self.trans_dict_list

        if trans_dict_file is not None and os.path.isfile(trans_dict_file):
            _tmp_trans_dict_list_content = self.parse_file(trans_dict_file)
            _tmp_trans_dict_list_content = self._parse_string_to_dict_list(_tmp_trans_dict_list_content)
            self.trans_dict_list.extend(_tmp_trans_dict_list_content)
        
        logging.debug(f'dist_path: {self.dist_path}')
        logging.debug(f'prefer_trans_type: {self.prefer_trans_type}')
        logging.debug(f'trans_dict_list: {self.trans_dict_list}')
    def _select_translate_type(self,text)->str:
        if(self.prefer_trans_type=='word'):
            return self._translate_text(text)
        elif(self.prefer_trans_type=='opencc'):
            return self._translate_text2(text)
    def _translate_text(self, text, WdTCSCConverterDirection='0')->str:
        """
        Class 類請使用 _select_translate_type
        調用Office Word翻譯功能 <br>
        有潛在bug請勿使用 <br>
        text : 要翻譯的簡中 <br>
        WdTCSCConverterDirection <br>
        wdTCSCConverterDirectionAuto	2	<br>
        Convert in the appropriate direction based on the detected language of the specified range. <br>
        <br>
        wdTCSCConverterDirectionSCTC	0	 <br>
        Convert from Simplified Chinese to Traditional Chinese. <br>
        <br>
        wdTCSCConverterDirectionTCSC	1	<br>
        Convert from Traditional Chinese to Simplified Chinese.<br>
        arg0 WdTCSCConverterDirection<br>
        <br>
        """
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            doc = word.Documents.Add()
            range_obj = doc.Content
            range_obj.Text = text
            range_obj.TCSCConverter(WdTCSCConverterDirection,"1", "1")
            text = range_obj.Text
            doc.Close(SaveChanges=False)
            return self._replace_text_by_list(text)
        except Exception as e:
            logging.error(f'translate_text發生錯誤。 {e}')
            logging.error(f'translate_text text {text}')
            time.sleep(1)
            return self.warning_alert
        finally:
            # 關閉 Word 應用
            # doc.Close(SaveChanges=False)
            if word:
                word.Quit()
            del(word)
            pythoncom.CoUninitialize()
    def _translate_text2(self,text) ->str:
        """
        Class 類請使用 _select_translate_type <br>
        使用 opencc 翻譯 
        """
        try:
            cc = OpenCC('s2twp')
            return self._replace_text_by_list(cc.convert(text))
        except Exception as e:
            logging.error(f'translate_text2發生錯誤。 {e}')
            logging.error(f'translate_text2 text {text}')
            return self.warning_alert
    def parse_file(self,file_path)->str:
        """
        開檔並回傳內容 存檔請用 parse_file_to_path
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # logging.info(f'open_file {content}')
                return content
        except Exception as e:
            logging.error(f'open_file 時發生錯誤。 {e}')
    def parse_file_to_path(self,file_path)->str:
        """
        開檔並回傳內容
        """
        try:
            if not os.path.exists(os.path.dirname(self.dist_path)):
                try:
                    os.makedirs(os.path.dirname(self.dist_path))
                except Exception as e:
                    logging.warning(f'路徑已存在')
            _content = self.parse_file(file_path=file_path)
            _content = self._select_translate_type(_content)
            with open(self.dist_path+"\\"+os.path.basename(file_path), 'w', encoding='utf-8') as file:
                    file.write(_content)
        except Exception as e:
            logging.error(f'open_file 時發生錯誤。 {e}')
    def _save_file(self,file_path,content)->None:
        """
        存檔到指定絕對路徑
        """
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except Exception as e:
                logging.warning(f'路徑已存在')
        try:
            if os.path.exists(file_path):
                """
                如果檔案已存在
                進行翻譯合併
                """
                logging.debug("檔案已存在 進行合併 "+file_path)
                json1 = self._open_file_to_json(file_path)
                json2 = json.loads(content)
                json_result = self._get_tc_from_two_json(json1,json2)
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(json_result, file, ensure_ascii=False)
            else :
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
        except Exception as e:
            logging.info(f'save_file 發生錯誤。 {e}')
    def parse_dirt(self,folder_path,src_path)->None:
        """ 
        src_path、folder_path 源頭檔案 <br>
        dist_path 翻譯目的地 <br>
        開啟特定路徑並逐一翻譯
        """
        if not os.path.exists(src_path):
            logging.warning(f"open_dirt 文件不存在: {src_path}")
            return
        queue_datas = []
        try:
            files = os.listdir(folder_path)
            pattern = re.compile(r'.*\.(json|md|gui)$', re.IGNORECASE)
            pattern2 = re.compile(r'.*\.(jar)$', re.IGNORECASE)
            logging.debug("資料夾中的檔案:")
            for file in files:
                abs_file_path_name = folder_path+"\\"+file
                if os.path.isfile(abs_file_path_name):
                    # logging.debug(f"{file} 是一個檔案。")
                    if("zh_cn.json"==file):
                        queue_datas.append({
                            "action":"1",
                            "dist_path":self.dist_path,
                            "src_path":src_path,
                            "file":file,
                            "abs_file_path_name":abs_file_path_name
                        })
                        # action1_sc_to_tc(dist_path, src_path, file, abs_file_path_name)
                    elif pattern.match(file):
                        queue_datas.append({
                            "action":"2",
                            "dist_path":self.dist_path,
                            "src_path":src_path,
                            "file":file,
                            "abs_file_path_name":abs_file_path_name
                        })
                    elif pattern2.match(file):
                        queue_datas.append({
                            "action":"4",
                            "dist_path":self.dist_path,
                            "src_path":src_path,
                            "file":file,
                            "abs_file_path_name":abs_file_path_name
                        })
                        # action2_other_json(dist_path, src_path, file, abs_file_path_name)
                    else:
                        queue_datas.append({
                            "action":"3",
                            "dist_path":self.dist_path,
                            "src_path":src_path,
                            "file":file,
                            "abs_file_path_name":abs_file_path_name
                        })
                        # action3_transfer_file(dist_path, src_path, file, abs_file_path_name)    
                elif os.path.isdir(abs_file_path_name):
                    logging.debug(f"{file} 是一個資料夾。")
                    # logging.debug(abs_file_path)
                    logging.debug("相對路徑: "+self._relate_path(abs_file_path_name,src_path))
                    # logging.debug(abs_file_path_name)
                    self._sub_open_dirt(abs_file_path_name,self.dist_path,src_path,queue_datas)
                else:
                    logging.debug(f"{file} 既不是檔案也不是資料夾。")
        except Exception as e:
            logging.error(f'parse_dirt 發生錯誤。 {e}')
        # pprint(queue_datas)。
        self._process_queue_data(queue_datas)
    def parse_jar(self,src_path)->None:
        """
        folder_path 源頭檔案 <br>
        dist_path 翻譯目的地 <br>
        開啟特定jar並把zh_cn 轉為 zh_tw
        """
        if not os.path.exists(src_path):
            logging.warning(f"parse_jar 文件不存在: {src_path}")
            return
        try:
            _find = False
            with zipfile.ZipFile(src_path, 'r') as jar:
                files = jar.namelist()
                for file_name in files:
                # print(file_name)
                    if fnmatch.fnmatch(file_name, 'assets/*/lang/zh_cn.json'):
                        _find = True
                        with jar.open(file_name) as file:
                            content = file.read()
                            content = content.decode('utf-8')
                        content = self._select_translate_type(content)
                        self._save_file(os.path.abspath(self.dist_path+"\\"+os.path.normpath(file_name).replace("zh_cn","zh_tw")),content)
            if _find is False:
                logging.info(f'jar檔 {src_path} 無 zh_cn.json')
        except Exception as e:
            logging.error(f'parse_jar {src_path} generated an exception: {e}')
    def _process_queue_data(self,queue_datas)->None:
        # threads = []
        # for queue_data in queue_datas:
            # process_single_data(queue_data)
            # thread = threading.Thread(target=process_single_data, args=(queue_data,))
            # threads.append(thread)
            # thread.start()

        # for thread in threads:
        #     thread.join()
        # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_task = {executor.submit(self._process_single_data, queue_data): queue_data for queue_data in queue_datas}
            concurrent.futures.wait(future_to_task)
            for future in concurrent.futures.as_completed(future_to_task):
                task_number = future_to_task[future]
                try:
                    result = future.result()
                    logging.info(f'Task {task_number} result: {result}')
                except Exception as e:
                    logging.error(f'Task {task_number} generated an exception: {e}')
    def _process_single_data(self,queue_data)->None:
        action = queue_data['action']
        dist_path = queue_data['dist_path']
        src_path = queue_data['src_path']
        file = queue_data['file']
        abs_file_path_name = queue_data['abs_file_path_name']
        # logging.debug(f"{queue_data}")
        if action == '1':
            self._action1_sc_to_tc(dist_path, src_path, file, abs_file_path_name)
        elif action == '2':
            self._action2_other_json(dist_path, src_path, file, abs_file_path_name)
        elif action == '3':
            self._action3_transfer_file(dist_path, src_path, file, abs_file_path_name)
        elif action == '4':
            self._action4_transfer_file(dist_path, src_path, file, abs_file_path_name)
    def _action4_transfer_file(self,dist_path, src_path, file, abs_file_path_name)->None:
        self.parse_jar(abs_file_path_name)
    def _action3_transfer_file(self,dist_path, src_path, file, abs_file_path_name)->None:
        logging.info(f"需要複製移動的檔案 {abs_file_path_name}")
        if not os.path.exists((dist_path+"\\"+ self._relate_path(abs_file_path_name,src_path))):
            try:
                os.makedirs((dist_path+"\\"+ self._relate_path(abs_file_path_name,src_path)))
            except Exception as e:
                logging.warning(f'路徑已存在')
        shutil.copy(abs_file_path_name,  dist_path+"\\"+ self._relate_path(abs_file_path_name,src_path)+"\\"+file)
    def _action2_other_json(self,dist_path, src_path, file, abs_file_path_name)->None:
        logging.info(f"要翻譯的其他json {abs_file_path_name}")
        content =self._select_translate_type( self.parse_file(abs_file_path_name) )
        # logging.debug(f"{content} 內容1")
        self._save_file( dist_path+"\\"+ self._relate_path(abs_file_path_name,src_path)+"\\"+file,content)
    def _action1_sc_to_tc(self,dist_path, src_path, file, abs_file_path_name)->None:
        logging.info(f"需要翻譯的中文檔案 {abs_file_path_name}")
        print(f"要翻譯的其他json {abs_file_path_name}")
        content =self._select_translate_type( self.parse_file(abs_file_path_name) )
        # logging.debug(f"{content} 內容2")
        self._save_file( dist_path+"\\"+ self._relate_path(abs_file_path_name,src_path)+"\\"+"zh_tw.json",content)
    def _sub_open_dirt(self,folder_path,dist_path,src_path,queue_datas)->None:
        """
        folder_path 源頭檔案 <br>
        dist_path 翻譯目的地 <br>
        開啟特定路徑並逐一翻譯
        """
        try:
            files = os.listdir(folder_path)
            pattern = re.compile(r'.*\.json$', re.IGNORECASE)
            logging.debug(f"{folder_path} 資料夾中的檔案: {files}")
            for file in files:
                abs_file_path_name = folder_path+"\\"+file
                if os.path.isfile(abs_file_path_name):
                    # logging.debug(f"{file} 是一個檔案。")
                    if("zh_cn.json"==file):
                        queue_datas.append({
                            "action":"1",
                            "dist_path":dist_path,
                            "src_path":src_path,
                            "file":file,
                            "abs_file_path_name":abs_file_path_name
                        })
                        # action1_sc_to_tc(dist_path, src_path, file, abs_file_path_name)
                    elif pattern.match(file):
                        queue_datas.append({
                            "action":"2",
                            "dist_path":dist_path,
                            "src_path":src_path,
                            "file":file,
                            "abs_file_path_name":abs_file_path_name
                        })
                        # action2_other_json(dist_path, src_path, file, abs_file_path_name)
                    else:
                        queue_datas.append({
                            "action":"3",
                            "dist_path":dist_path,
                            "src_path":src_path,
                            "file":file,
                            "abs_file_path_name":abs_file_path_name
                        })
                        # action3_transfer_file(dist_path, src_path, file, abs_file_path_name)    
                elif os.path.isdir(abs_file_path_name):
                    logging.debug(f"{file} 是一個資料夾。")
                    # logging.debug(abs_file_path)
                    logging.debug("相對路徑: "+self._relate_path(abs_file_path_name,src_path))
                    # logging.debug(abs_file_path_name)
                    self._sub_open_dirt(abs_file_path_name,dist_path,src_path,queue_datas)
                else:
                    logging.debug(f"{file} 既不是檔案也不是資料夾。")
        except Exception as e:
            logging.error(f'sub_open_dirt 發生錯誤。 {e}')
    def _relate_path(self,folder_path,scr_path)->None:
        diff2 = os.path.relpath(os.path.dirname(folder_path), scr_path)
        return diff2
    def _contains_chinese(self,text)->bool:
        # 匹配中文字元的正則表達
        if text == None:
            return False
        pattern = re.compile(r'[\u4e00-\u9fff]')
        return bool(pattern.search(str(text)))
    def _get_tc_from_two_json(self,json1,json2)->json:
        """
        以 json1 翻譯優先!!!!
        因此json1 應該是目的地檔案
        """
        copy_json2 = copy.deepcopy(json2)
        for key, value in json2.items():
            if self._contains_chinese(value) == False and self._contains_chinese(json1.get(key)) :
                copy_json2[key] = json1.get(key)

        for key, value in json1.items():
            if self._contains_chinese(value) and self._contains_chinese(json2.get(key)) == False:
                copy_json2[key] = json1.get(key)
        return copy_json2
    def _open_file_to_json(self,file_path)->json:
        """
        開檔並回傳內容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f'open_file_to_json 發生錯誤。 {e}')
    def _parse_string_to_dict_list(self,_tmp_trans_dict_list_content=str)->list:
        # 分割字串成對
        try:
            pairs = _tmp_trans_dict_list_content.replace(" ","").replace("\r\n"," ").replace("\n"," ").split()   # 將 "a=1 b=2" 轉為 ["a=1", "b=2"]    
            # 將每個對分割成鍵值並轉換為字典
            dict_list = [{  str(pair.split('=')[0]): str(pair.split('=')[1])} for pair in pairs]
            return dict_list
        except Exception as e:
            logging.error(f'_parse_string_to_dict_list exception {e}')
            return []
    def _is_valid_file_path(self,path):
        try:
            Path(path).resolve()
            return True
        except (OSError, RuntimeError):
            return False
    def set_dist_path(self,value):
        """
        重新設定 目的地路徑
        """
        try:
            if self._is_valid_file_path(value):
                self.dist_path = value
            else :
                logging.warning(f'不是合法路徑: {value}')
            os.makedirs(self.dist_path)
        except Exception as e:
            logging.warning(f'dis_path 路徑設定失敗: 絕對路徑: {os.path.abspath(value)} Exception: {e}')
        logging.debug(f'重新設定 dist_path: {os.path.abspath(self.dist_path)}')
    def common_parse_interface(self,src_path=str):
        logging.info(f'common_parse_interface 輸入路徑 {src_path}')
        logging.info(f'common_parse_interface 輸入路徑資料夾 {os.path.isdir(src_path)}')
        logging.info(f'common_parse_interface 輸入路徑檔案 {os.path.isfile(src_path)}')
        if(os.path.isdir(src_path)):
            self.parse_dirt(src_path=src_path,folder_path=src_path)
            pass
        elif(os.path.isfile(src_path)  and src_path.endswith('jar') ):
            self.parse_jar(src_path=src_path)
            pass
        elif(os.path.isfile(src_path)):
            self.parse_file_to_path(file_path=src_path)
            pass
        else:
            logging.info(f'路徑不明不可翻譯 {src_path}')
    def _replace_text_by_list(self,text):
        for dict_word in self.trans_dict_list:
            for key, value in dict_word.items():
                text = text.replace(key, value)
        return text
if __name__ == '__main__':
    x = logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                            # logging.FileHandler('app.log', mode='w',encoding='utf-8'),  # 日誌檔案
                            logging.StreamHandler()  # 控制台輸出
                        ]
                    )
    # msctc = MinecraftSCtoTC(dist_path="a/b")
    # msctc.set_dist_path("c")
    # msctc = MinecraftSCtoTC(trans_dict_file="tt.txt")
    # msctc = MinecraftSCtoTC(dist_path="D:\\documents\\Python\\wokspace\\example")
    # msctc.
    