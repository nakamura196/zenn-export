# zenn-export

[Zenn](https://zenn.dev) の記事（Articles）とBook をMarkdownファイルとしてエクスポートするCLIツールです。

## インストール

```bash
pip install git+https://github.com/nakamura196/zenn-export.git
```

開発用：

```bash
git clone https://github.com/nakamura196/zenn-export.git
cd zenn-export
pip install -e .
```

## 使い方

### CLI

```bash
# 記事 + Book をエクスポート
zenn-export <username>

# 出力先を指定
zenn-export <username> -o ./my-articles

# 記事のみ
zenn-export <username> --articles-only

# Book のみ
zenn-export <username> --books-only

# 既存ファイルを上書き
zenn-export <username> --force
```

### Python API

```python
from zenn_export import ZennClient, export_articles, export_books

# 記事をエクスポート
export_articles("nakamura196", "./output")

# Book をエクスポート
export_books("nakamura196", "./output")

# API クライアントを直接使う
client = ZennClient()
articles = client.fetch_articles("nakamura196")
detail = client.fetch_article_detail("some-slug")
```

## 出力形式

### 記事

```markdown
---
title: "記事タイトル"
emoji: "📝"
type: "tech"
topics: ["python", "cli"]
published: true
published_at: "2024-01-01T00:00:00.000+09:00"
source: "https://zenn.dev/username/articles/slug"
---

本文（Markdown）
```

### Book

各Bookはディレクトリとして出力されます。

```
output/
└── book-slug/
    ├── config.md       # Book メタデータ（タイトル、トピック、チャプター一覧）
    ├── chapter1.md     # 各チャプター
    └── chapter2.md
```

## License

MIT
