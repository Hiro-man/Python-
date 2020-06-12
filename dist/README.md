exeファイルはスクリプトを`pyinstaller`でexe化したものです.

以下のようにmain.pyをターゲットに実行してください．
実行前にmain.pyのあるディレクトリに`cd`で移動してから実行してください．
```
pyinstaller main.py -F
```
コンソール画面が不要な場合は`--noconsole`をオプションに付けて実行してください．

# 参考サイト
<!-- * <a href="" target="_blank"></a> -->

* <a href="https://qiita.com/y-tsutsu/items/f687cf4b57442557aade" target="_blank">PyInstallerがPython3.6をサポートしてくれた</a>
* <a href="https://teratail.com/questions/213332" target="_blank">Python 3.x - 複数あるパイソンファイルのexe化｜teratail</a>
* <a href="https://takeichi.work/pyinstaller-exe-add-binary/" target="_blank">pyinstallerを使ってPythonをexe化！seleniumや複数ファイルをexe化する方法！ ｜ タケイチの備忘録</a>
* <a href="https://qiita.com/TakamiChie/items/8dba8459343db898b335" target="_blank">PyInstallerを使ってみた - Qiita</a>