# Python製メモ帳
文字数制限（～文字以上・～文字以内）のある入力のために，Windouwsのメモ帳に常に文字数が表示されるものを使いたいと考え，
PythonのGUIモジュールwxPythonを使用して作成したスクリプトです．

## 実行環境
基本的にはWindows10を想定したスクリプトおよびexeファイルになっています．
exeファイルはWindowsやLinuxのWineであれば実行できると思います．
                  
## Windouwsのメモ帳との違い
作成したスクリプトに関して，

* 文字数が表示されるため（常に更新されます），文字数制限のある入力の下書きに便利
* タブ表示でき，一つのウィンドウで複数のファイルを切り替えて表示
* テキストファイル以外にも対応でき，マークダウン表記にも対応できます
* テキストファイル以外のファイルにも対応した多機能さ
    * csvやtsvをGUIで操作できます
    * バックでmp3やmp4を再生しながらテキストを編集できます
    * PDFの表示も可能です

といった特徴があります．

## 必要なモジュール
本スクリプトで使用したモジュールです．`pip`で事前にPythonにインストール，もしくは最新版に更新しておいてください．

* `wxPython`
* `PyMuPDF`
* `markdown`

```
pip install wxPython PyMuPDF markdown
```

使用したモジュールでPythonにデフォルトで入っているモジュールは以下に示します．

* `sys`
* `re`
* `os`
<!-- * `unicodedata` コレ使ってないかも．．．っということで削除．-->
* `pprint`
* `ast`
* `codecs`
* `platform`
* `pickle`：<a href="https://docs.python.org/ja/3/library/pickle.html" target="_blank">3.8以降のPythonにはデフォルトで入っている模様</a>ですので，`pip`で入れる必要はありませんが，
デフォルトで入っていない場合は`pip install pickle-mixin`で入れてください．
逆に3.8以降のPythonで`pip install pickle-mixin`を実行するとエラーが発生します．
    * <a href="https://www.lifewithpython.com/2013/05/pickle.html" target="_blank">ライブラリ&#65306;pickle - Life with Python</a>
    * <a href="view-source:https://stackoverflow.com/questions/48477949/not-able-to-pip-install-pickle-in-python-3-6" target="_blank">Not able to pip install pickle in python 3.6 - Stack Overflow</a>

## 更新情報と現状の課題など
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

### 2020/05/13
スクリプトとexeファイルを更新．

サイズや使用するクラスなどを変更したため，印刷の方式が前のと変わっています．
テキストの印刷にwx.html2のLoadURLを使用しており，印刷時に”printout.html”というファイルが作成されますので，
”printout.html”というファイルを削除しないでください．
また，GitHubのMITライセンスのcssを本スクリプトもしくはexeファイルと同じディレクトリに保存してください．
これによりcssが読み込まれ，印刷時に自動で文字が折り返されたりします．
同じディレクトリにcssがない場合は読み込まれず，文字の折り返し等が行われないまま印刷プレビュー画面が起動します．
cssに関して，ファイルの保存の際に，
”github.css”・”github-frameworks.css”・”github-site.css”というファイル名にしてください．
別のファイル名にする場合は本スクリプトの該当する部分を変更してください．

まだ調整段階ではありますが，今回の更新で，テキストファイル以外にもいくつかファイルを扱えるようになりました．
mp3やcsvといったファイルです．
音楽ファイルや動画ファイルの再生ができます．
また，PDFの表示もできます．

課題としては他のテキストエディタと比べ，テキストエディタとしての機能の実装が少ないことです．
検索機能は実装することができましたが，柔軟な検索機能の実装がまだ実装できておりません．
全体としても改善が必要であると考えています．

### 2020/05/15
課題等は5/13と同じ．

表ファイルの読み込みや保存におけるエラーの修正ならびにwxPythonのクローズイベントを拒否してもエラーが起きないように修正しました．
メニューも変更しました．

また，大きめのファイルを開く際には時間がかかります．

### 2020/06/12
ディレクトリの階層を大きく変更しました．

表の操作を追加しました．

印刷に関して，exeファイルではファイルが見つからないというエラーが出ます．
現状改善策が思いつかないので，exeファイルでの印刷機能は使わないことを推奨します．

また，印刷時のcssの読み込みに関してイマイチなので今後改善できればなぁと．．．

## 参考リンク
随時追加予定．．．
<!-- * <a href="" target="_blank"></a> -->
* <a href="https://wxpython.org/Phoenix/docs/html/wx.1moduleindex.html" target="_blank">wx — wxPython Phoenix 4.1.1a1 documentation</a>
    * <a href="https://wxpython.org/Phoenix/docs/html/wx.html.1moduleindex.html" target="_blank">wx.html — wxPython Phoenix 4.1.1a1 documentation</a>
    * <a href="https://wxpython.org/Phoenix/docs/html/wx.aui.AuiNotebook.html" target="_blank">wx.aui.AuiNotebook — wxPython Phoenix 4.1.1a1 documentation</a>
    * <a href="https://wxpython.org/Phoenix/docs/html/wx.TextCtrl.html" target="_blank">wx.TextCtrl — wxPython Phoenix 4.1.1a1 documentation</a>
    * <a href="https://wxpython.org/Phoenix/docs/html/wx.functions.html#wx.Sleep" target="_blank">https://wxpython.org/Phoenix/docs/html/wx.functions.html#wx.Sleep</a>
    * <a href="https://wxpython.org/Phoenix/docs/html/wx.lib.agw.flatmenu.html#module-wx.lib.agw.flatmenu" target="_blank">wx.lib.agw.flatmenu — wxPython Phoenix 4.1.1a1 documentation</a>
    * <a href="https://wxpython.org/Phoenix/docs/html/wx.grid.Grid.html" target="_blank">wx.grid.Grid — wxPython Phoenix 4.1.1a1 documentation</a>
    * <a href="https://wxpython.org/Phoenix/docs/html/wx.grid.GridTableBase.html" target="_blank">wx.grid.GridTableBase — wxPython Phoenix 4.1.1a1 documentation</a>
* <a href="https://wiki.wxpython.org/Printing%20framework%20%28Phoenix%29" target="_blank">Printing framework (Phoenix) - wxPyWiki</a> 
* <a href="https://www.python-izm.com/gui/" target="_blank">GUI  |  Python-izm</a>
* <a href="https://www.it-swarm.dev/ja/python/pythonから標準プリンターに印刷しますか%EF%BC%9F/1068950658/" target="_blank">python — Pythonから標準プリンターに印刷しますか？</a> 
* <a href="https://stackoverflow.com/questions/54617358/print-multiple-pages-with-wxpython" target="_blank">python - Print multiple Pages with wxPython - Stack Overflow</a>
* <a href="https://pashango-p.hatenadiary.org/entry/20110609/1307630616" target="_blank">wxPythonでクリップボード操作 - Pashango’s Blog</a>
* <a href="https://maku77.github.io/python/wxpython/statusbar.html" target="_blank">wxPytnon - StatusBar（ステータスバー） | まくまくPythonノート</a>
* <a href="https://maku77.github.io/python/wxpython/dialog.html" target="_blank">>wxPython - Dialog（ダイアログ） | まくまくPythonノート</a>
* <a href="https://srad.jp/~tuneo/journal/352723/" target="_blank">あれげメモ：wxPythonプログラミング事始め－アプリケーションの終了 | tuneoの日記 | スラド</a>
* <a href="http://wxpython.at-ninja.jp/layout.html" target="_blank">レイアウト管理</a>
* <a href="https://python-minutes.blogspot.com/2016/11/pythongui-notebook.html" target="_blank">python入門ブログ: pythonでGUIツールを作る&#12288;&#65374; Notebook&#12288;ノートブック &#65374;</a>
* <a href="https://torina.top/detail/205/" target="_blank">wxPythonで、タブ（Notebook） - naritoブログ</a>
* <a href="https://ja.coder.work/so/python/561309" target="_blank">python - wxPython TextCtrlウィジェットのフォントを変更する - ITツールウェブ</a>
* <a href="http://wxpython-users.1045709.n5.nabble.com/wxGrid-reload-table-td2311585.html" target="_blank">wxPython-users - wxGrid reload table</a>
* <a href="https://ideal-user-interface.hatenablog.com/entry/20101118/1290058840" target="_blank">グリッドテーブル - 理想のユーザ・インターフェイスを求めて</a>
* <a href="https://maku77.github.io/python/wxpython/grid.html" target="_blank">wxPython - Grid（グリッド） | まくまくPythonノート</a>

* <a href="https://tatzyr.hatenablog.com/entry/2017/01/27/153800" target="_blank">Pythonで大きいファイルを読み込む時にプログレスバーを表示 - ぼろぼろ平原</a>
* <a href="https://qiita.com/everycamel/items/da9651db9d4807cb144d" target="_blank">wx.ProgressDialog の AUTO_HIDE では明示的な Destroy() が必要 - Qiita</a>
* <a href="https://wxpython.org/Phoenix/docs/html/wx.ProgressDialog.html" target="_blank">wx.ProgressDialog — wxPython Phoenix 4.1.1a1 documentation</a>

* <a href="https://teratail.com/questions/95988" target="_blank">wxpython 現在の時間をリエルタイムで表示｜teratail</a>
* <a href="https://www.tagindex.com/html_tag/elements/" target="_blank">HTMLタグ/HTML要素一覧 - TAG index</a>
* <a href="https://water2litter.net/rum/post/python_unicodedata_east_asian_width/" target="_blank">Pythonで文字を全角か半角か判別する</a>
* <a href="http://2no.hatenablog.com/entry/2014/11/17/210829" target="_blank">【wxPython】Markdown をライブプレビュー - 2noの日記</a>
* <a href="https://qiita.com/masakuni-ito/items/593b9d753c44da61937b" target="_blank">Pythonでmarkdownをhtmlにコンバートする - Qiita</a> 
* <a href="https://qiita.com/koara-local/items/6b47f3156ca66f28b4ab" target="_blank">[Python][chardet] ファイルの文字コードの自動判別 - Qiita</a>
* <a href="https://ja.m.wikipedia.org/wiki/等幅フォント" target="_blank">等幅フォント - Wikipedia</a>

* <a href="https://qiita.com/arata-honda/items/be5b0adf6ab432881749" target="_blank">python3でUnicodeDecodeErrorが出た時の応対 - Qiita</a>
* <a href="https://qiita.com/kouhara/items/ac1ce8b78bd0bfc06d6c" target="_blank">python3で複数文字コードが含まれるファイルをUnicodeDecodeErrorが出る行を飛ばして処理する - Qiita</a>
* <a href="https://python.civic-apps.com/file-io/" target="_blank">ファイル読み書き file open read write  | Python Snippets</a>
* <a href="https://docs.python.org/ja/3/howto/unicode.html" target="_blank">Unicode HOWTO &#8212; Python 3.8.3 ドキュメント</a>
* <a href="https://docs.python.org/ja/3/library/codecs.html" target="_blank">codecs --- codec レジストリと基底クラス &#8212; Python 3.8.3 ドキュメント</a>

* <a href="https://www.gixo.jp/blog/12445/amp/" target="_blank">分析しやすい「ファイル形式」｜データ分析のお作法 - GiXo Ltd.</a>
* <a href="https://blog.amedama.jp/entry/2015/12/05/132520" target="_blank">Python: オブジェクトを漬物 (Pickle) にする - CUBE SUGAR CONTAINER</a>
* <a href="https://ermanii.wordpress.com/2009/07/16/%e3%83%ad%e3%83%bc%e3%82%ab%e3%83%ab%e3%83%95%e3%82%a1%e3%82%a4%e3%83%ab%e3%81%aeurl/" target="_blank">ローカルファイルのURL | Ermanii's memo-random</a>

* <a href="https://www.lifewithpython.com/2017/12/python-tuple-list-difference.html" target="_blank">Python のタプルとリストの違い&#12289;タプルの使いどころ - Life with Python</a>
* <a href="https://note.nkmk.me/python-tuple-operation/" target="_blank">Pythonでタプルの要素を追加・変更・削除 | note.nkmk.me</a>
* <a href="https://www.javadrive.jp/python/dictionary/index6.html" target="_blank">辞書から要素を削除する | Python入門</a>

* <a href="http://blog.livedoor.jp/pythonsuezo/archives/10165277.html" target="_blank">wxpythonの使い方 wxFrame編 : 初心者のpython備忘録</a>

* <a href="https://www.haya-programming.com/entry/2018/11/30/230228" target="_blank">【python】実行スクリプトからの相対パスでファイルを開く - 静かなる名辞</a>
