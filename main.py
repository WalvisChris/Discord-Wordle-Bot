import discord
from discord.ext import commands
import random

TOKEN = 'YeahIamNotSharingThatYouCanGetYourOwnOnTheDiscordDevelopersPortalGoodLuck'
# This will reset before I upload the video ^
FILE = 'valid_words.txt'

# intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# bot
bot = commands.Bot(command_prefix='!', intents=intents)

# discord emojis
translate_emoji = {
    'a': ':regional_indicator_a:',
    'b': ':regional_indicator_b:',
    'c': ':regional_indicator_c:',
    'd': ':regional_indicator_d:',
    'e': ':regional_indicator_e:',
    'f': ':regional_indicator_f:',
    'g': ':regional_indicator_g:',
    'h': ':regional_indicator_h:',
    'i': ':regional_indicator_i:',
    'j': ':regional_indicator_j:',
    'k': ':regional_indicator_k:',
    'l': ':regional_indicator_l:',
    'm': ':regional_indicator_m:',
    'n': ':regional_indicator_n:',
    'o': ':regional_indicator_o:',
    'p': ':regional_indicator_p:',
    'q': ':regional_indicator_q:',
    'r': ':regional_indicator_r:',
    's': ':regional_indicator_s:',
    't': ':regional_indicator_t:',
    'u': ':regional_indicator_u:',
    'v': ':regional_indicator_v:',
    'w': ':regional_indicator_w:',
    'x': ':regional_indicator_x:',
    'y': ':regional_indicator_y:',
    'z': ':regional_indicator_z:',
    'correct': ':green_square:',
    'present': ':yellow_square:'
}

wordlist = []
answer = []
gameCTX = None
isPlaying = False
guesses = [[":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
           [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
           [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
           [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
           [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
           [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"]]
guesses_copy = ["", "", "", "", "", ""]
absent = []
turn = 0

@bot.event
async def on_ready():
    global wordlist

    print(f"Logged in as {bot.user}")
    with open(FILE, 'r') as file:
        wordlist = [line.strip() for line in file.readlines()]
    print("Succes:", wordlist[:10])

@bot.event
async def on_message(message):
    global isPlaying, absent, gameCTX, guesses, turn, guesses_copy

    if message.author == bot.user:
        return

    if message.content == '!wordle' or message.content == '!stop' or '!custom' in message.content:
        await bot.process_commands(message)
        return
    
    if not isPlaying:
        return
    
    if len(message.content) != 5:
        return
    
    if message.content not in wordlist:
        await message.channel.send("That's not an official word.")
        return
    
    if message.content in guesses_copy:
        await message.channel.send("You already guessed this word.")
        return

    # check win
    if message.content.lower() == "".join(answer):
        
        guesses[turn] = [":green_square:", ":green_square:", ":green_square:", ":green_square:", ":green_square:"]
        guesses_copy[turn] = "".join(answer)
        leftovers = [str(letter + " ") for letter in 'abcdefghijlkmnopqrstuvwxyz' if letter not in absent]
        output = ""
        for i in range(len(guesses)):
            output += "\n" + "".join(guesses[i]) + " " + guesses_copy[i].upper()
        msg = f"@everyone **wordle**\n`{"".join(leftovers)}`\n{output}"
        await gameCTX.edit(content=msg)

        await message.channel.send(f"**{"".join(answer)}** was the correct answer!")
        await reset()
        return
    
    # setup letter checking
    compare = ["_", "_", "_", "_", "_"]
    guess = list(message.content.lower())
    count = {}
    for letter in answer:
        count[letter] = answer.count(letter)

    # correct
    for i in range(len(guess)):
        if guess[i] == answer[i]:
            compare[i] = translate_emoji['correct']
            count[guess[i]] -= 1

    # present
    for i, letter in enumerate(guess):
        if letter in answer and count[letter] > 0 and compare[i] == '_':
            compare[i] = translate_emoji['present']
            count[guess[i]] -= 1

    # absent
    for i in range(len(guess)):
        if compare[i] == '_':
            compare[i] = translate_emoji[guess[i]]
            absent.append(guess[i])

    # create the message
    guesses[turn] = compare
    guesses_copy[turn] = "".join(guess)
    leftovers = [str(letter + " ") for letter in 'abcdefghijlkmnopqrstuvwxyz' if letter not in absent]
    output = ""
    for i in range(len(guesses)):
        output += "\n" + "".join(guesses[i]) + " " + guesses_copy[i].upper()
    msg = f"@everyone **wordle**\n`{"".join(leftovers)}`\n{output}"
    await gameCTX.edit(content=msg)
    turn += 1

    if turn > 5:
        await message.channel.send(f"You ran out of attempts. The answer was **{"".join(answer)}**")
        await reset()
        return

@bot.command()
async def wordle(ctx):
    global isPlaying, answer, gameCTX

    if isPlaying:
        await ctx.send("A game is already being played.")
        return
    
    await reset()
    isPlaying = True
    answer = list(random.choice(wordlist))
    output = ""
    for word in guesses:
        for letter in word:
            output += ":blue_square:"
        output += "\n"
    gameCTX = await ctx.send("@everyone **wordle**\n" + output)

@bot.command()
async def stop(ctx):
    if isPlaying:
        await ctx.send("The game was stopped.")
        await reset()
        return
    
    await ctx.send("There is no active game.")

@bot.command()
async def custom(ctx, word: str):
    global isPlaying, answer, gameCTX
    
    if isPlaying:
        await ctx.message.delete()
        return
    
    if len(word) != 5:
        await ctx.message.delete()
        anonymous = ['#' for letter in list(word)]
        await ctx.send(f"`{"".join(anonymous)}` doesn't have 5 letters.")
        return
    
    await ctx.message.delete()    
    await reset()
    isPlaying = True
    answer = word
    output = ""
    for word in guesses:
        for letter in word:
            output += ":blue_square:"
        output += "\n"
    gameCTX = await ctx.send("@everyone **wordle**\n" + output)

async def reset():
    global answer, gameCTX, isPlaying, guesses, guesses_copy, absent, turn
    answer = []
    gameCTX = None
    isPlaying = False
    guesses = [[":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
            [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
            [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
            [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
            [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"],
            [":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:"]]
    guesses_copy = ["", "", "", "", "", ""]
    absent = []
    turn = 0

bot.run(TOKEN)