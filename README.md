# Python製メモ帳
文字数制限（～文字以上・～文字以内）のある入力のために，Windouwsのメモ帳に常に文字数が表示されるものを使いたいと考え，
PythonのGUIモジュールwxPythonを使用して作成したスクリプトです．

exeファイルはスクリプトをpyinstallerでexe化したものです．
WindowsやLinuxのWineであれば実行できると思います．
exe化については以下のリンクを参照してください．
<br><a href="https://qiita.com/y-tsutsu/items/f687cf4b57442557aade" target="_blank">PyInstallerがPython3.6をサポートしてくれた</a>
                                                                      
## Windouwsのメモ帳との違い
作成したスクリプトに関して，

* 文字数が表示される（常に更新）ため，文字数制限のある入力の下書きに便利
* タブ表示でき，一つのウィンドウで複数のファイルを切り替えて表示

といった特徴があります．

## 現状の課題
### 2020/05/03
検索など，Windouwsのメモ帳が持つ機能を追加できていないため，方法が見つかれば実装したいと考えています．

また，印刷に関して，使用しているwx.htmlはcssが取り扱えないため，自動で折り返しての印刷ができず，
一行の文字数をカウントすることで強引に改行文字を入れて折り返しているように印刷データを作成しています．
そのため，上手く折り返されずに印刷の枠から切れてしまったり，可笑しな位置での改行があるかもしれません．
できるだけそのようなことがないように調整しましたが，印刷機能に関して完全とは言えません．
wx.html2はcssが使用できるようですが，wx.htmlのような使い方ができず，wx.html2の中でもSetPageメソッドはcssを読み込めずエラーが出ます．
cssが使用できれば印刷時に自動で折り返せると考えておりますが，現状解決策は見つかっていません．

基本的な機能以外にも，wxPythonのモジュールを用いてcsvやtsvファイルを読み込んでの表の表示やmp3といったオーディオファイルの再生を考えていますが，
wx.mediaによるオーディオファイル再生が中々上手く実装できません．．．
## 参考リンク
<!-- * <a href="" target="_blank"></a> -->
* <a href="https://wxpython.org/Phoenix/docs/html/wx.html.1moduleindex.html" target="_blank">wx.html</a>
* <a href="https://wxpython.org/Phoenix/docs/html/wx.aui.AuiNotebook.html" target="_blank">wx.aui.AuiNotebook</a>
* <a href="https://wiki.wxpython.org/Printing%20framework%20%28Phoenix%29" target="_blank">Printing framework (Phoenix) - wxPyWiki</a> 
* <a href="https://www.python-izm.com/gui/" target="_blank">GUI  |  Python-izm</a>
* <a href="https://www.it-swarm.dev/ja/python/pythonから標準プリンターに印刷しますか%EF%BC%9F/1068950658/" target="_blank">python — Pythonから標準プリンターに印刷しますか？</a> 
* <a href="https://stackoverflow.com/questions/54617358/print-multiple-pages-with-wxpython" target="_blank">python - Print multiple Pages with wxPython - Stack Overflow</a>
* <a href="https://pashango-p.hatenadiary.org/entry/20110609/1307630616" target="_blank">wxPythonでクリップボード操作 - Pashango’s Blog</a>

* <a href="https://teratail.com/questions/95988" target="_blank">wxpython 現在の時間をリエルタイムで表示｜teratail</a>
* <a href="https://www.tagindex.com/html_tag/elements/" target="_blank">HTMLタグ/HTML要素一覧 - TAG index</a>
* <a href="https://water2litter.net/rum/post/python_unicodedata_east_asian_width/" target="_blank">Pythonで文字を全角か半角か判別する</a>
* <a href="http://2no.hatenablog.com/entry/2014/11/17/210829" target="_blank">【wxPython】Markdown をライブプレビュー - 2noの日記</a>
* <a href="https://qiita.com/masakuni-ito/items/593b9d753c44da61937b" target="_blank">Pythonでmarkdownをhtmlにコンバートする - Qiita</a> 
* <a href="https://qiita.com/koara-local/items/6b47f3156ca66f28b4ab" target="_blank">[Python][chardet] ファイルの文字コードの自動判別 - Qiita</a>
