#S18_project
#プロジェクト名:マネートラベル 
why
複数人で旅行した時に、清算が面倒なので解決できたら良い。

what
1.旅行始まる前にメンバーを登録する。

2.旅行の最中は入力(支払った人、後で支払うべき人、金額、メモ)をタスクのように登録する。(割り勘なども設定できたら良い、後で支払うべき人を複数人追加、割る値の設定)
追加(money for ward APIを使ってレシートを写真撮って追加)

3.2.の結果を踏まえメンバーごとに金額を合計し、表示させる。

how
webアプリケーション
フレームワーク:flask
メインプログラム:python
web表示:html, CSS,javascript
データベース:Mysql

#なぜこのようなプロジェクトにしたか
自分が大学１年の時に、友達4人で北海道に旅行した。その際、ホテル代、レンタカー代、飛行機代、特急列車代など様々なところで料金が発生したのだが、支払っている人が毎回違ったために旅行最終日の清算が非常に大変であった。料金の合計の計算自体は難しくはないのだが、誰が誰に何円払うかということを考えることが非常に面倒であった。結局別日に落ち着いて計算し、清算した。自分は旅行が好きなのでこれを幾度となく経験した。それ故この面倒を解消すべく、このプロジェクトに決めた。

#工夫した点
工夫している点は３つほどある。１つ目は旅行後に誰が誰に払うべきか明確にしている点である。先程述べた通り、単純な料金計算だけであれば電卓を使えば可能である。しかし、これでは誰が誰に何円払うべきかが分からなくなってしまう。ユーザーの目線からこの点が分かるよう、プロジェクトを進めた。２つ目はスマートフォンに合わせた画面設計になっている点である。一般的に旅行中にパソコンを持ち歩いている人は少ないので、スマートフォンから払った金額等を入力できるよう、レスポンシブデザインに重きを置いた。３つ目は視覚的に誰が払っているか分かるよう円グラフを用いた点である。人間は何かを理解する際、視覚的理解する方が素早く、楽である。そのため、視覚的に結果を理解できるようにした。