### ip地址正则校验

```python
((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)
或者
((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))

```

- 250-255   25[0-5]
- 200-249   2[0-4]\d
- \\.
- 0-199         [01]?\d\d?

1. 为什么三位数的匹配放在二位数/一位数的前面？ 更高的优先级

2. ?:的作用？

ref: "非捕获性分组语法为(?:pattern),即将pattern部分组合成一个可统一操作的组合项，但不把这部分内容当作子匹配捕获."





https://my.oschina.net/u/553266/blog/374625