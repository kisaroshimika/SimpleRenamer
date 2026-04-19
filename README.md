# SimpleRenamer + TimeDropper

![Hero Image](docs/simplerenamer_hero.png)

**SimpleRenamer** は、ファイルの大量リネームとタイムスタンプ変更を同時に、かつ直感的に行えるモダンなGUIツールです。
クリエイターやエンジニアの作業効率を最大化するために設計された、プレミアムなユーザー体験を提供します。

---

## 🚀 主な機能 (Key Features)

### 📁 高度なリネーム (Powerful Renaming)
- **一括連番付与**: 独自のベース名に連番（例: `uzura_001.png`）を付けて一括リネーム。
- **柔軟なソート**: タイムスタンプ（旧→新 / 新→旧）やファイル名の昇順・降順に基づいて順序を決定。
- **桁数・開始番号指定**: 連番の桁数（001, 0001など）や開始番号を自由にカスタマイズ。

### 📅 タイムスタンプ変更 (Timestamp Modification)
- **日時一括設定**: 指定した日時に瞬時に書き換え。
- **インクリメンタル更新**: 1秒ずつずらして設定することで、OS上のソート順を完全にコントロール。
- **現在時刻同期**: ワンクリックで現在時刻をセット。

### 🛠️ ユーザーフレンドリーな設計 (User-Centric Design)
- **ドラッグ＆ドロップ**: 面倒なファイル選択は不要。エクスプローラーから直接ドロップするだけ。
- **リアルタイムプレビュー**: 実行前に変更後のファイル名をひと目で確認。
- **強力な Undo (元に戻す)**: 間違えて実行しても大丈夫。リネームも日時変更も直前の状態に復元可能。
- **プレミアム・ダークUI**: `CustomTkinter` を採用した、目に優しく洗練されたサファイアブルーのテーマ。

---

## 💻 動作環境 (Environment)

- **OS**: Windows 10 / 11
- **Python**: 3.8以上 (ソースから実行する場合)

---

## 🛠️ インストール・実行方法 (Installation)

### 実行可能ファイル (.exe) を使用する場合
1. [GitHub Releases](https://github.com/kisaroshimika/SimpleRenamer/releases/) から最新の `SimpleRenamer.exe` をダウンロードします。
2. ダウンロードしたファイルをダブルクリックして実行するだけです。（Pythonのインストールは不要です）

### ソースコードから実行する場合
必要なライブラリをインストールしてから起動します。

```bash
pip install customtkinter tkinterdnd2
python SimpleRenamer.py
```

---

## 🏗️ 開発者向け (Development)

### ビルド方法
PyInstaller を使用して exe を生成する場合のコマンド例：

```bash
pyinstaller --onefile --noconsole --icon SimpleRenamer.ico --collect-all customtkinter --collect-all tkinterdnd2 --name SimpleRenamer SimpleRenamer.py
```

---

## 📝 ライセンス (License)

このプロジェクトは個人利用・商用利用を問わず自由にご利用いただけます。
(No specific license provided by the author)

---

## 🤝 貢献 (Contribution)

不具合報告や機能要望は GitHub の Issues までお気軽にどうぞ！
