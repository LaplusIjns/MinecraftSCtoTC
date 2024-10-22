<h1 class="code-line" data-line-start=0 data-line-end=1 ><a id="MinecraftSCtoTC_0"></a>MinecraftSCtoTC</h1>
<p class="has-line-data" data-line-start="2" data-line-end="5">主要使用 <a href="https://github.com/jamebal/jmal-cloud-view/blob/master/LICENSE">opencc</a> 翻譯簡體到繁體<br>
針對資料夾或檔案(.json or .md or .gui)或jar檔搜尋轉換 如果檔名為zh_cn則改為zh_tw<br>
請注意並不包含遊戲內專有名詞(如下界、終界等)翻譯僅為簡轉繁</p>
<h2 class="code-line" data-line-start=6 data-line-end=7 ><a id="Features_6"></a>Features</h2>
<ul>
<li class="has-line-data" data-line-start="7" data-line-end="8">針對單檔或資料夾遞迴轉換文檔</li>
<li class="has-line-data" data-line-start="8" data-line-end="9">可自定義替代字典 (請優先放多字的字典在前並且為繁體詞替代繁體詞 詳見 example.txt範例)</li>
<li class="has-line-data" data-line-start="9" data-line-end="11">如果目的地已有翻譯 json 則會優先保留原有翻譯 並嘗試將新翻譯 json 合併進原有文檔</li>
</ul>
<h2 class="code-line" data-line-start=11 data-line-end=12 ><a id="_11"></a>使用</h2>
<p class="has-line-data" data-line-start="13" data-line-end="14">請先確認本機已安裝python</p>
<pre><code class="has-line-data" data-line-start="16" data-line-end="18" class="language-python">  pip install -r requirements.txt
</code></pre>
<p class="has-line-data" data-line-start="19" data-line-end="22">安裝相依套件<br>
之後直接執行 <code>python gui.py</code> 即可有圖形介面程式<br>
或者自行引入MinecraftSCtoTC.py並使用class</p>
