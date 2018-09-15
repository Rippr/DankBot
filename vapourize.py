from telegram.ext.dispatcher import run_async

a = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`-=~!@#$%^&*()_+[];'\,./{}:"|<>?'''
b = '''ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ１２３４５６７８９０`－＝~！＠＃＄％^＆＊（）_＋[]；＇\，．／{}："|<>？'''
vapourtext = {a[x]: b[x] for x in range(len(a))}
vapourtext[' '] = '   '


@run_async
def vapourize(update, text):
	r = []
	for i in text:
		if i in vapourtext:
			r.append(vapourtext[i])
		else:
			r.append(i)
	update.message.reply_text("".join(r))
