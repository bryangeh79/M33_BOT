# Bet 玩法规则

## 大区
- MN
- MT
- MB

## 金额规则
- 1n = 1
- 支持小数
  - 0.5n 有效
  - 1.2n 有效

## 号码长度
- 2c = 2 位数字
- 3c = 3 位数字
- 4c = 4 位数字

## MN 区域
- Tg = tien giang
- Kg = kien giang
- Dl = da lat
- Tp = hcm
- Dt = dong thap
- Cm = ca mau
- Vt = vung tau
- Bt = ben tre
- Bl = bac lieu
- Dn = dong nai
- Ct = can tho
- St = soc trang
- Tn = tay ninh
- Ag = an giang
- Bth = binh thuan
- Bd = binh duong
- Vl = vinh long
- Tv = tra vinh
- La = long an
- Bp = binh phuoc
- Hg = hau giang

## MT 区域
- Tth = hue
- Py = phu yen
- Dla = dac lac
- Qna = quang nam
- Dna = da nang
- Kh = khanh hoa
- Bdi = binh dinh
- Qtr = quang tri
- Qbi = quang binh
- Gl = gia lai
- Nth = ninh thuan
- Qng = quang ngai
- Dno = dac nong
- Kt = kon tum

## MB 规则
- MB 只有一个区域

## 输入方式 
- **支持一条消息多行**
- 一行一笔
- 一条消息中只要有一行错，则整批失败

## 成功回执格式
```plaintext
OK - MN N1
N1 tp 11 lo1n : 18
N2 tp 22 dd1n : 2
N3 tp 123 xc1n : 2

Total: 22
```