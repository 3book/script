# 任意公司文档转换

- 实现任意markdown文件转换为pptx
- 可重用的脚本，可针对目录批量执行，
- 可重用的模板，配色 公司 logo 标题 作者部门等元信息来自markdown文件metainfo

  ```yaml
  Company:
    name: BOEING
    logo: ./assets/boeing-logo.png
  Document:
    Title: RAG 从零开始：概念、原理与实现
    Font : <!-- 数字分别对应文档标题/section标题/列段落/正文的字体大小，#后16进制数代表字体颜色 -->
        48 : #880000
        36 : #005566
        24 : #000088
        16 : #660088
    FontColor ： #555555/#cccccc#000000
    docCode: DOC0227703
    docRev: 1.0
    First Made Date: 5/22/2024
    First Made By (Author): 二大爷
  output: pptx
  ```

- 支持公司信息和页码添加到页眉或页脚可选
- 支持首页 包含标题 作者 日期 部门，加或不加背景图
- 支持尾页 包含公司信息和结束语，加或不加背景图

## markdown转pptx

- 主要针对项目进展汇报/立项材料/问题回溯报告/技术培训
- "##" 作为section 标题
- "###" 作为section内的列
- '-' 作为文字列表
- 支持1列/2列/3列/4列 section 背景图可选
- 支持2列文字和图片并行，比例来自markdown
- 支持 markdown引用图片语法后的{}，描述图片大小透明度等排版属性
  - 举例 ![last](./assets/bg2.jpg){traansparency:50,size:100\*400,}
