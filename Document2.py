import discord
import glob
from discord.ext import commands,tasks
import gspread
import random  # おみくじで使用
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import pandas as pd
import datetime
import os
import urllib.request, urllib.error
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from datetime import timedelta


scope = ['https://spreadsheets.google.com/feeds',
			'https://www.googleapis.com/auth/drive']

sheet_token = os.environ['SHEET_TOKEN']
bot_token = os.environ['DISCORD_BOT_TOKEN']

client = discord.Client()  # 接続に使用するオブジェクト

credentials = ServiceAccountCredentials.from_json_keyfile_name('okashi-55fd53c0b60c.json', scope)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = sheet_token
workbook = gc.open_by_key(SPREADSHEET_KEY)
worksheet = workbook.worksheet("!参加")

def dayedit(day):
	index = day.find("'")
	return day[index:-2]
	
def idedit(id):
	return id[3:-1]
	
def set_cell(user):
	today = datetime.date.today()
	today = today.strftime("%Y/%m/%d")
	array = np.zeros((14,2))
	row_cell = 0
	col_cell = 0
	df = pd.DataFrame(worksheet.get_all_values())
	
	df1 = df.iloc[:2,5:19].T
	df1.columns = ["_","day"]
	row_cell = df1[df1["day"] == today].index[0] + 1
	
	print(row_cell)
			
	df2 = df.iloc[:,19:22]
	df2.columns=["count","_","discord"]
	col_cell = df2[df2["discord"] == "<@!"+str(user)+">"]
	count = 0
	if col_cell.empty:
		col_cell = 0
	else:
		count = col_cell.values
		count = int(count[0,0]) + 1
		print(count)
		col_cell = col_cell.index[0] + 1
	print(col_cell)
	return row_cell,col_cell,count

def uranai(url):
	html = urllib.request.urlopen(url)
	soup = BeautifulSoup(html)
	df2 = pd.DataFrame(soup.find_all("a"))
	bbbb = str(df2[0][17])
	bbb = bbbb.split("「")
	bbb = bbb[1].split("」")
	bbb = bbb[0]

	df = pd.DataFrame(soup.find_all("td"))
	test = str(df[0][1])
	n = test.split("=")

	df4 = pd.DataFrame(soup.find_all("p"))
	test2 = str(df4[0][4])
	mm = test2.split("=")
	mmm = mm[0].split(">")[1].split("<")[0].split("。")

	ccc = str(soup.find_all("meta")[7]).split("=")
	ddd = ccc[1][1:-10]
	
	list = []
	list.append(n[3].split(" ")[0][1:-1])
	list.append(n[6].split(" ")[0][1:-1])
	list.append(n[9].split(" ")[0][1:-1])
	list.append(n[12].split(" ")[0][1:-1])
	list.append(bbb)
	return list,ddd

def yari():
	imagepicture = glob.glob("maplembuki/1_sensi/yari/*.png")
	result = random.choices(imagepicture, k=1)
	return result

@client.event
async def on_ready():
	"""起動時に通知してくれる処理"""
	print('ログインしました')
	print(client.user.name)  # ボットの名前
	print(client.user.id)  # ボットのID
	print(discord.__version__)  # discord.pyのバージョン
	print('------')

@client.event
async def on_member_join(member):
	CHANNEL_ID = 576797690906673154
	setumei = 641052750699954187
	jikosyoukai = 577531306632806415
	channel = client.get_channel(CHANNEL_ID)
	await channel.send(f"{member.mention} さんこんにちはしゃくし～です")
	await channel.send(f"まずは<#{setumei}>の確認と<#{jikosyoukai}>の記入をお願いします")
	await channel.send(f"これからよろしくお願いします!")
	
@client.event
async def on_message(message):
	"""メッセージを処理"""
	if message.author.bot:  # ボットのメッセージをハネる
		return
	
	elif message.content == "!参加":
	# チャンネルへメッセージを送信
		cell_1,cell_2,count = set_cell(message.author.id)
		if cell_2 == 0:
			await message.channel.send(f"{message.author.mention}さん シートにIDがありません")  # f文字列（フォーマット済み文字列リテラル）
			
		else:
			worksheet.update_cell(cell_2,cell_1,"〇")
			await message.channel.send(f"{message.author.mention}さん 参加確認しました\n今シーズンの参加回数は累計{count}回です")  # f文字列（フォーマット済み文字列リテラル）

	elif message.content == "!星空":
		if message.author.id == 573911598008107009:
			cell_1,cell_2,count = set_cell(506660639964659768)
			if cell_2 == 0:
				await message.channel.send(f"星空さん シートにIDがありません")  # f文字列（フォーマット済み文字列リテラル）
			else:
				worksheet.update_cell(cell_2,cell_1,"〇")
				await message.channel.send(f"星空さん 参加確認しました\n今シーズンの参加回数は累計{count}回です")  # f文字列（フォーマット済み文字列リテラル）
		else:await message.channel.send(f"それはニートちゃんしか使えないよ")
	
	elif message.content == "!きゃすん":
		embed = discord.Embed(title="個通相手募集～", description=f"{message.author.mention}さんが個通相手を募集しています！",color=0xFF6EC7)
		embed.set_thumbnail(url=message.author.avatar_url)
		await message.channel.send(embed=embed)
	
	elif message.content == "!ビビデバビデブー":
		if message.author.id == 303215008802930699:
			day = datetime.date.today() + timedelta(days=(7-datetime.date.today().weekday()))
			youbi = np.array(["月","火","水","木","金","土","日","月","火","水","木","金","土","日"])
			await message.channel.send(f"@everyone 来シーズンの出欠席\nチェックお願いします")
			await message.channel.send(f"日付の下の:relaxed::o::x::question:を押して貰えれば\nチェック完了です:ok_hand::skin-tone-1::sparkles:")
			await message.channel.send(f":relaxed: ▷優先的に参加にします\n:o:▷参加可能の日\n:x:▷参加不可の日\n:question:▷どちらか未定の日")
			await message.channel.send(f":o:の人が20人いない場合は:question:の人も呼び出す事があるので出られない場合は無理せず")
			await message.channel.send(f"#要塞戦出席表 に出れないと書いて貰えれば待機してくれる人がいるので、お願いします🤲")
			await message.channel.send(f"ちなみに、このシステムはほぼ手動なので後から:x:に変更しても気付かない場合があるのでその場合も\n #要塞戦出席表 に書いてもらえると助かります:strawberry:")
			await message.channel.send(f"全部❌でも怒られないので")
			await message.channel.send(f"リアクションおしてくれると助かります:macs: ")
			await message.channel.send(f"残りの今シーズンも頑張りましょう:daynogal:")
			for i in range(14):
				q = await message.channel.send(f"{(day+timedelta(days=i)).month}/{(day+timedelta(days=i)).day}({youbi[i]})")
				[await q.add_reaction(i) for i in ('😊','⭕','❌','❓')]

		else:await message.channel.send(f"それはまあこしか使えないよ")
		
	elif message.content == "!やるじゃん":
		await message.channel.send(f"ありがとう")
		
	elif message.content == "!Esprit":
		await message.channel.send(f"抜けたほうがいいですよ")
		
	elif message.content == "!えっち":
		await message.channel.send(f'きゃー！{message.author.mention}さんのえっち！！', file=discord.File("4ba65a1c.jpg"))
		
	elif message.content == "!くるみ":
		await message.channel.send(f'zeulon、私たちはもう終わりよ', file=discord.File("kurumi.png"))
		
	elif message.content == "!ドッグラン":
		await message.channel.send(file=discord.File("dogrun.jpg"))
		
	elif message.content == "!ヘリコプター":
		await message.channel.send(file=discord.File("herineet.png"))

	elif message.content == "!まあこ":
		await message.channel.send(f"寝てるよ")
		
	elif message.content == "!ハンバーグ":
		await message.channel.send(f"ハンバアアアアアアアアアアアアアアアアアアアアアアアアアアアグ！！！！！！")
	
	elif message.content == "!やってないじゃん":
		await message.channel.send(f"ごめんなさい")
		
	elif message.content == "!ゆきやこんこ":
		await message.channel.send(f"⛄雪や⛄\n\n❄❅❆❄❅❆❄❅❆❄\n▉▉▉ ◥◣　　 ▉▉▉ \n　　▉ 　　◢◤ 　　▉ \n▉▉▉ ◢▉◤　 ▉▉▉ \n❄❅❆❄❅❆❄❅❆❄\n\n🚽ケツから🚽\n\n💩💩💩💩💩💩💩💩\n　▉\n▉▉▉▉◥◣　　▉▉▉\n▉　◢◤　　◢◤　　▉\n　◢◤　◢▉◤　▉▉▉\n💩💩💩💩💩💩💩💩")
	elif message.content == "juruli":
		await message.channel.send(f"そのキャラはキャラデリしました")
		
	elif message.content == "!ままん":
		await message.channel.send(f"ままぁ\nあああん\nあああああん\nままああああ\nああん\nあああああああああああああああああああああああああああああああああああああああああああ\nあああああああああああああああああああああああああああｂｂ")
		
	elif message.content == "!にーと":
		await message.channel.send(f"にーとくさい")	
		
	elif message.content == "!マルガリタ":
		await message.channel.send(f"抜けませんでした")
	
	elif message.content == "!かてぽん":
		await message.channel.send(f"ブルブルブルブルアイ！:v:(՞ਊ՞:v:三:v:՞ਊ՞):v:アイ！:v:(՞ਊ՞:v:三:v:՞ਊ՞):v:ブ・ル・ベ・リ・アイ！！:v:(՞ਊ՞:v:三:v:՞ਊ՞):v:ブルブルブルブルアイ！:v:(՞ਊ՞:v:三:v:՞ਊ՞):v:アイ！:v:(՞ਊ՞:v:三:v:՞ਊ՞):v:ブ・ル・ベ・リ・アイ！！:v:(՞ਊ՞:v:三:v:՞ਊ՞):v:")
	
	
	elif message.content == "!投票":
	# リアクションアイコンを付けたい
		msg = await message.channel.send("あなたは右利きですか？")
		[await msg.add_reaction(i) for i in ('⭕')]  # for文の内包表記

	elif message.content == "!おみくじ":
		# Embedを使ったメッセージ送信 と ランダムで要素を選択
		embed = discord.Embed(title="おみくじ", description=f"{message.author.mention}さんの今日の運勢は！",color=0x2ECC69)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="[運勢] ", value=random.choice(('大吉', '吉', '凶', '大凶')), inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!ダイス":
		embed = discord.Embed(title="ダイス", description=f"{message.author.mention}さんの結果",color=0x2ECC69)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="[結果] ", value=random.randint(0,100), inline=False)
		await message.channel.send(embed=embed)
		
	elif message.content == "!ダイレクトメッセージ":
		# ダイレクトメッセージ送信
		dm = await message.author.create_dm()
		await dm.send(f"{message.author.mention}さんにダイレクトメッセージ")

	elif message.content == "!おひつじ座":
		url = "https://fortune.yahoo.co.jp/12astro/aries"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!おうし座":
		url = "https://fortune.yahoo.co.jp/12astro/taurus"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!ふたご座":
		url = "https://fortune.yahoo.co.jp/12astro/gemini"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!かに座":
		url = "https://fortune.yahoo.co.jp/12astro/cancer"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!しし座":
		url = "https://fortune.yahoo.co.jp/12astro/leo"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!おとめ座":
		url = "https://fortune.yahoo.co.jp/12astro/virgo"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!てんびん座":
		url = "https://fortune.yahoo.co.jp/12astro/libra"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!さそり座":
		url = "https://fortune.yahoo.co.jp/12astro/scorpio"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!いて座":
		url = "https://fortune.yahoo.co.jp/12astro/sagittarius"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!やぎ座":
		url = "https://fortune.yahoo.co.jp/12astro/capricorn"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!みずがめ座":
		url = "https://fortune.yahoo.co.jp/12astro/aquarius"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

	elif message.content == "!うお座":
		url = "https://fortune.yahoo.co.jp/12astro/pisces"
		kekka,ddd = uranai(url)
		embed = discord.Embed(title="星座占い", description=f"{message.author.mention}さんの今日の運勢は！",color=0x00FF00)
		embed.set_thumbnail(url=message.author.avatar_url)
		embed.add_field(name="総合運",value=kekka[0],inline=False)
		embed.add_field(name="恋愛運",value=kekka[1],inline=False)
		embed.add_field(name="金運",value=kekka[2],inline=False)
		embed.add_field(name="仕事運",value=kekka[3],inline=False)
		embed.add_field(name="コメント",value=kekka[4],inline=False)
		embed.add_field(name="====",value=ddd,inline=False)
		await message.channel.send(embed=embed)

@tasks.loop(minutes=15)
async def loop():
	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	sheet_token = os.environ['SHEET_TOKEN']
	bot_token = os.environ['DISCORD_BOT_TOKEN']
	client = discord.Client()  # 接続に使用するオブジェクト
	credentials = ServiceAccountCredentials.from_json_keyfile_name('okashi-55fd53c0b60c.json', scope)
	gc = gspread.authorize(credentials)
	SPREADSHEET_KEY = sheet_token
	workbook = gc.open_by_key(SPREADSHEET_KEY)
	worksheet = workbook.worksheet("!参加")

loop.start()
# botの接続と起動
# （botアカウントのアクセストークンを入れてください）
client.run(bot_token)
