# 运行前把语料按 corpus/human/*.txt 与 corpus/ai/*.txt 摆好；路径按需修改
import re, glob, statistics as st

CLICHE = ["综上所述","总的来说","总而言之","值得注意的是","不仅","更是","此外","与此同时","首先","其次","进一步","全面","显著","极大","赋能","打造","助力","彰显","一定程度上","具有重要意义","不可或缺","日益"]
PART = list("啊吧呢嘛啦呀哈哦嗯咯噢")
def feats(t):
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", t)
    han = re.findall(r"[\u4e00-\u9fff]", text)
    n = max(1, len(han))
    sents = [s for s in re.split(r"[。！？!?…\n]+", text) if len(re.findall(r"[\u4e00-\u9fff]", s)) > 0]
    lens = [len(re.findall(r"[\u4e00-\u9fff]", s)) for s in sents] or [0]
    paras = [p for p in text.split("\n") if len(re.findall(r"[\u4e00-\u9fff]", p)) > 0]
    digits = re.findall(r"\d+(?:\.\d+)?%?", text)
    quotes = re.findall(r"《[^》]*》|「[^」]*」|“[^”]*”|\"[^\"]*\"", text)
    latin  = re.findall(r"[A-Za-z][A-Za-z0-9_.\-]+", text)
    comma  = text.count("，") + text.count("、")
    cl = sum(text.count(w) for w in CLICHE)
    pt = sum(text.count(w) for w in PART)
    first = sum(text.count(w) for w in ["我们","我","你","您"])
    return dict(
        zh=n,
        mean_len=st.mean(lens),
        sd_len=st.pstdev(lens),
        short_ratio=sum(1 for l in lens if l<=8)/len(lens),
        comma_per_sent=comma/len(lens),
        digit_per_1k=1000*len(digits)/n,
        quote_per_1k=1000*len(quotes)/n,
        latin_per_1k=1000*len(latin)/n,
        particle_per_1k=1000*pt/n,
        cliche_per_1k=1000*cl/n,
        first_per_1k=1000*first/n,
        para_len=st.mean([len(re.findall(r"[\u4e00-\u9fff]",p)) for p in paras]) if paras else 0,
    )

def group(paths):
    rows=[feats(open(p,encoding="utf-8").read()) for p in paths]
    keys=rows[0].keys()
    w=sum(r["zh"] for r in rows)
    out={}
    for k in keys:
        if k=="zh": out[k]=w
        else: out[k]=sum(r[k]*r["zh"] for r in rows)/w
    return out

H=sorted(glob.glob("corpus/human/*.txt")); A=sorted(glob.glob("corpus/ai/*.txt"))
hg, ag = group(H), group(A)
print(f"{'指标':<16}{'人类(20年前后)':>16}{'AI文本':>12}   差值")
for k in hg:
    if k=="zh": continue
    print(f"{k:<16}{hg[k]:>16.2f}{ag[k]:>12.2f}   {hg[k]-ag[k]:+.2f}")
print()
print("样本字数：human",hg["zh"],"ai",ag["zh"],"| 文件数",len(H),len(A))
print()
print("--- 每个人类样本 ---")
for p in H:
    f=feats(open(p,encoding="utf-8").read())
    print(f"{p.split('/')[-1][:22]:<24}zh={f['zh']:>5} 句长={f['mean_len']:>5.1f} sd={f['sd_len']:>5.1f} 数字/千={f['digit_per_1k']:>6.1f} 套话/千={f['cliche_per_1k']:>5.1f}")

print("\n--- 同体裁对照 ---")
pairs=[("公告/公文","corpus/human/gov2015.txt","corpus/ai/deepseek_news.txt"),
       ("技术解释","corpus/human/cnblogs2015.txt","corpus/ai/sess_00.txt")]
for name,h,a in pairs:
    fh,fa=feats(open(h,encoding="utf-8").read()),feats(open(a,encoding="utf-8").read())
    print(f"\n[{name}] 人类 {fh['zh']}字 / AI {fa['zh']}字")
    for k in ["mean_len","sd_len","short_ratio","comma_per_sent","digit_per_1k","latin_per_1k","cliche_per_1k","first_per_1k","para_len"]:
        print(f"  {k:<16}{fh[k]:>8.2f}{fa[k]:>8.2f}")
