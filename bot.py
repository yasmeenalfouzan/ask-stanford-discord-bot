import discord
import asyncio


client = discord.Client()

# initialization
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# action
@client.event
async def on_message(message):

    channel = message.channel

    # MAIN

    if str(message.channel.id) == '586287643541766243' and message.content.startswith('TIME UP: NEXT QUESTION') and message.author == client.user:
        # publish answer to channel, and users
        question = await channel.history(limit=1, oldest_first=True).flatten()
        answers = await client.get_channel(586326481127604244).history(limit=500, oldest_first=True).flatten()
        embed = discord.Embed(
            title = 'Question',
            description = question[0].clean_content,
            color = discord.Color.dark_red()
        )
        if answers:
            answercount = 1
            for x in answers:
                embed.add_field(name=str(answercount), value = x.clean_content, inline = False)
                answercount += 1
        if not answers:
            embed.add_field(name='Oh no!', value = 'The question was not answered in time. If you are still curious, you may ask the question again to add it to the queue.', inline = False)

        await client.get_channel(586276996397662220).send(embed=embed)

        for member in message.guild.members:
            rolename = discord.utils.get(member.guild.roles, name='notification')
            if rolename  in member.roles:
                await member.send(embed=embed)
                await member.remove_roles(discord.utils.get(member.guild.roles, name='notification'))

        # clean slate
        async for message in channel.history(limit=10):
            await message.delete()
        async for message in client.get_channel(586326481127604244).history(limit=50):
            await message.delete()

        # next question
        flipStatus = True
        async for message in client.get_channel(586276247584374789).history(limit=500, oldest_first=True):
            while flipStatus:
                await client.get_channel(586287643541766243).send(message.clean_content)
                await message.delete()
                flipStatus = False
                #add timer
                await asyncio.sleep(120) #in seconds
                await client.get_channel(586287643541766243).send('TIME UP: NEXT QUESTION')

    # move users question, delete, send them a message
    if str(message.channel.id) == '586273366906896432' and message.content.endswith('?'):
        await client.get_channel(586276247584374789).send('**{}** {}'.format(message.clean_content, message.author.id))
        await message.delete()
        await message.author.send('Your question **"%s"** have been added to the queue.' % message.clean_content)

    if str(message.channel.id) == '586273366906896432' and not message.content.endswith('?'):
        await message.delete()
        await message.author.send('Your question was not recorded since it is not indicated with a question mark. Try again.')

    # trigger statement
    if str(message.channel.id) == '586273366906896432' and message.content.endswith('?'):
        past = await client.get_channel(586287643541766243).history(limit=1, oldest_first=True).flatten()
        if not past:
            # post next
            flipStatus = True
            async for message in client.get_channel(586276247584374789).history(limit=500, oldest_first=True):
                while flipStatus:
                    question = message.clean_content.rsplit(' ', 1)[0]
                    userid = message.clean_content.rsplit(' ', 1)[1]
                    await client.get_channel(586287643541766243).send(question)
                    await client.get_user(int(userid)).send('Your question is up!')
                    await message.delete()
                    flipStatus = False
                    # add timer
                    await asyncio.sleep(60)  # in seconds
                    await client.get_channel(586287643541766243).send(
                        'TIME UP: NEXT QUESTION')


    if message.author == client.user and str(message.channel.id) == '586287643541766243' and message.clean_content != 'TIME UP: NEXT QUESTION':
        await message.add_reaction('💡')
        await message.add_reaction('❗')

    if isinstance(channel, discord.DMChannel):
        counter = 0
        async for message in channel.history(limit=2, oldest_first=False):
            if counter == 0 and message.author != client.user:
                answer = message.clean_content
                answerer = message.author
                counter += 1
                continue
            if counter == 1 and message.content.startswith('You have chosen to answer') and message.author == client.user:
                await answerer.send('Thank you! Your answer: **%s** \n '
                            'was just recorded.' % answer)
                await client.get_channel(586326481127604244).send(
                '**{}**'.format(answer))



@client.event
async def on_reaction_add(reaction, user):
    #mild error to be fixed: first user has to press reaction twice to get it to work
    # NOTIFICATION
    if str(reaction.message.channel.id) == '586287643541766243' and reaction.emoji == '❗':

        if user != client.user:
            def check(reaction, user):
                return str(reaction.emoji) == '❗' and user != client.user
            res = await client.wait_for('reaction_add', check=check)
            reaction, user = res
            # send private message to confirm
            await user.send('You have chosen to be notified of the question: %s \n '
                            'An answer will be sent to you as soon as it is compiled.' % reaction.message.clean_content)
            # add notification role
            await user.add_roles(discord.utils.get(user.guild.roles, name='notification'))

    # USER HAS ANSWER
    if str(reaction.message.channel.id) == '586287643541766243' and reaction.emoji == '💡':

        if user != client.user:
            def check(reaction, user):
                return str(reaction.emoji) == '💡' and user != client.user
            res = await client.wait_for('reaction_add', check=check)
            reaction, user = res
            # send private message to confirm
            await user.send('You have chosen to answer the question: %s \n '
                            'Please write your answer in ONE message and hit enter.' % reaction.message.clean_content)


client.run('TOKEN')



