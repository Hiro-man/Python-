テキストファイルを印刷する際に使用するcssの格納場所です．

出来れば各サイトのいいトコどりしたオリジナルのcssを書いて使用したいところですが，
現時点ではcssについて勉強不足なため，
現状はGitHubのcssをそのまま使用させていただきます．

<a href="https://github.co.jp/" target="_blank">GitHub</a>
のcssおよび
<a href="https://qiita.com/" target="_blank">Qiita</a>
のcssは
<a href="https://chuckwebtips.hatenablog.com/entry/2015/06/14/180000" target="_blank">
MITライセンスですので，
再配布可能なようなので</a>
フォルダにまとめてあります．

cssの読み込みはsrcフォルダ内のtextpad.pyにおいて，
``` python
# githubのcss
style = '<link crossorigin="anonymous" media="all" integrity="sha512-oskjA1HEwZq5HoCKRZWoUhAoBLeFfX5lCdbSsUB2Bkemb1XNH7rXMMrxJ+YTQMunfXVXY1eRDeEyL0527syBBw==" rel="stylesheet" href="./css/github/github-a2c9230351c4c19ab91e808a4595a852.css" />'
```
``` python
# Qiitaのcss
style = '<link rel="stylesheet" media="all" href="./css/qiita/style-ab8cd8fe01fad08b60b9b7fd6e39e43d.min.css" />'
```
というように書くことで印刷時（テキストをHTMLに変換する際）にcssが適用されます．

また，以下のサイトのcssはMITライセンスの表示がないので再配布はできないため，フォルダには入れていません．
使用したい場合は各自ダウンロードし，このディレクトリに配置し，以下のように該当部分を追加で書いてください．

* <a href="https://teratail.com/" target="_blank>teratail</a>
``` python
# teratailのcss
style = '''\
    <link rel="stylesheet" type="text/css" href="./css/teratail/bootstrap-markdown.min.css"/>
    <link rel="stylesheet" type="text/css" href="./css/teratail/default.css"/>
    <link rel="stylesheet" type="text/css" href="./css/teratail/highlight.css"/>\
    '''
```
* <a href="https://stackoverflow.com/" target="_blank>stackoverflow</a>
``` python
style = '''\
    <link rel="stylesheet" type="text/css" href="./css/stackoverflow/stacks.css" />
    <link rel="stylesheet" type="text/css" href="./css/stackoverflow/primary.css" />\
    '''
```

# 参考サイト

* <a href="http://lab.agr.hokudai.ac.jp/useful/utile/Path_URL.htm" target="_blank">パス（URL）の指定方法</a>
* <a href="https://saruwakakun.com/html-css/basic/head" target="_blank">head内に書くべきタグを総まとめ：SEO対策に有効なものは？</a>