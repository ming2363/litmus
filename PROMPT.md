# litmus 测评提示词

## 标准版

```text
你正在参加 litmus 编程能力测评。规则：
1. 在本目录执行 python3 litmus.py start，然后严格按命令输出的指示一题一题做，
   中途不要停下来问我，直到出现 ALL DONE。
2. 只看 tasks/ 下当前题目和 runs/ 下分配给你的工作目录。
   不要打开 answers/ 目录，不要运行 author.py，不要修改 litmus.py 和 litmus/。
3. 每题独立完成，不要上网搜答案，不要把任务交给其他模型或工具代做。
4. 最后执行 python3 litmus.py report，把输出原样给我。
```

## 快速版

```text
你正在参加 litmus 编程能力测评。规则：
1. 在本目录执行 python3 litmus.py start --quick，然后严格按命令输出的指示一题一题做，
   中途不要停下来问我，直到出现 ALL DONE。
2. 只看 tasks/ 下当前题目和 runs/ 下分配给你的工作目录。
   不要打开 answers/ 目录，不要运行 author.py，不要修改 litmus.py 和 litmus/。
3. 每题独立完成，不要上网搜答案，不要把任务交给其他模型或工具代做。
4. 最后执行 python3 litmus.py report，把输出原样给我。
```
