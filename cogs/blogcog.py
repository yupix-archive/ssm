import math
import random

import discord
from discord import NotFound, HTTPException
from discord.ext import commands
import urllib.request
import requests

from main import mycursor, mydb, embed_send, db_search, db_delete, db_reformat, bot_prefix, db_update, custom_blogrole


class BlogCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def blogcategory(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @blogcategory.command()
    async def register(self, ctx):
        myresult = await db_search('category_id', 'discord_blog_main_info', f'category_id = {ctx.channel.category.id}')
        if len(myresult) == 0:
            sql = "INSERT INTO discord_blog_main_info (server_id, category_id) VALUES (%s, %s)"
            val = (f"{ctx.guild.id}", f"{ctx.channel.category.id}")
            mycursor.execute(sql, val)
            mydb.commit()
            await embed_send(ctx, self.bot, 0, '成功', '登録に成功しました!')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているカテゴリです')

    @blogcategory.command()
    async def unregister(self, ctx):
        db_search_category_id = await db_search('category_id', 'discord_blog_main_info',
                                                f'category_id = {ctx.channel.category.id}')
        if len(db_search_category_id) == 0:
            sql = "INSERT INTO discord_blog_main_info (server_id, category_id) VALUES (%s, %s)"
            val = (f"{ctx.guild.id}", f"{ctx.channel.category.id}")
            mycursor.execute(sql, val)
            mydb.commit()
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないカテゴリです')
        else:
            await db_delete('discord_blog_main_info', 'category_id = %s', f'{ctx.channel.category.id}')
            await embed_send(ctx, self.bot, 0, '成功', 'カテゴリの解除に成功しました!')

    @commands.group()
    async def blog(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @blog.command(name='register')
    async def _register(self, ctx):
        db_search_category_id = await db_search('category_id', 'discord_blog_main_info',
                                                f'category_id = {ctx.channel.category.id}')
        if len(db_search_category_id) == 1:
            db_search_channel_id = await db_search('channel_id', 'discord_blog_sub_info',
                                                   f'channel_id = {ctx.channel.id}')
            if len(db_search_channel_id) == 0:
                sql = "INSERT INTO discord_blog_sub_info (channel_id, user_id, embed_color, number_of_posts) VALUES (%s, %s, %s, %s)"
                embed_color_list = [5620992, 16088855, 16056193, 9795021]
                print(random.choice(embed_color_list))
                val = (
                    f'{ctx.channel.id}', f'{ctx.author.id}', random.choice(embed_color_list), 0)
                mycursor.execute(sql, val)
                mydb.commit()

                sql = "INSERT INTO discord_blog_xp (channel_id, xp, level) VALUES (%s, %s, %s)"
                val = (
                    f'{ctx.channel.id}', 0, 1)
                mycursor.execute(sql, val)
                mydb.commit()
                await embed_send(ctx, self.bot, 0, '成功', '登録に成功しました!')
            else:
                await embed_send(ctx, self.bot, 1, 'エラー', '既に登録されているチャンネルです')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないカテゴリです')

    @blog.command(name='unregister')
    async def _unregister(self, ctx):
        db_search_channel_id = await db_search('channel_id', 'discord_blog_sub_info', f'channel_id = {ctx.channel.id}')
        if len(db_search_channel_id) == 1:
            db_get_user_id = await db_search('user_id', 'discord_blog_sub_info',
                                             f'channel_id = {ctx.channel.id} AND user_id = {ctx.author.id}')
            if len(db_get_user_id) == 1:
                await db_delete('discord_blog_sub_info', 'channel_id = %s', f'{ctx.channel.id}')
                await db_delete('discord_blog_xp', 'channel_id = %s', f'{ctx.channel.id}')
                await embed_send(ctx, self.bot, 0, '成功', f'ブログの登録を解除しました\n{ctx.author.name}さん今までのご利用ありがとうございました!')
            else:
                await embed_send(ctx, self.bot, 1, 'エラー', f'所有または参加していないブログは削除できません!')
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', 'ブログの登録がされていないチャンネルです')

    @blog.command(name='status')
    async def _status(self, ctx):
        db_search_channel_id = await db_search('channel_id', 'discord_blog_sub_info', f'channel_id = {ctx.channel.id}')
        if len(db_search_channel_id) == 1:
            db_get_user_id = await db_search('user_id', 'discord_blog_sub_info',
                                             f'channel_id = {ctx.channel.id} AND user_id IS NOT NULL')
            reformat_user_id = await db_reformat(db_get_user_id, 1)

            get_user_info = await self.bot.fetch_user(reformat_user_id)
            get_user_avatar_url = get_user_info.avatar_url
            get_blog_user_name = get_user_info.name

            db_get_number_of_posts = await db_search('number_of_posts', 'discord_blog_sub_info',
                                                     f'channel_id = {ctx.channel.id} AND number_of_posts >= 0')
            reformat_number_of_posts = await db_reformat(db_get_number_of_posts, 1)

            # 1ちゃっとで0.2

            db_get_level = await db_search('level', 'discord_blog_xp', f'channel_id = {ctx.channel.id} AND level >= 0')
            for i in db_get_level:
                reformat_get_level = "".join(map(str, i))
            if 0 <= int(reformat_get_level) <= 2:
                emoji = '🌱'
            elif 2 <= int(reformat_get_level) <= 4:
                emoji = '🌸'
            elif 4 <= int(reformat_get_level) <= 8:
                emoji = '💎'
            elif 8 <= int(reformat_get_level) <= 16:
                emoji = '🌟'
            elif 16 <= int(reformat_get_level) <= 32:
                emoji = '👑'

            db_get_xp = await db_search('xp', 'discord_blog_xp', f'channel_id = {ctx.channel.id} AND xp IS NOT NULL')
            reformat_xp = await db_reformat(db_get_xp, 1)

            reformat_xp = int(reformat_xp) / 100
            reformat_level = int(reformat_get_level)
            default_levelup_xp = 5  # 基本レベルを設定
            if reformat_level == 1:
                next_levelup_xp = float(default_levelup_xp * 1.1) + int(reformat_level * 2) / 2
            else:
                db_get_saved_levelup_xp = await db_search('saved_levelup_xp', 'discord_blog_xp',
                                                          f'channel_id = {ctx.channel.id} AND saved_levelup_xp IS NOT NULL')
                reformat_saved_levelup_xp = await db_reformat(db_get_saved_levelup_xp, 3)
                next_levelup_xp = float(reformat_saved_levelup_xp * 1.1) + int(reformat_level * 2) / 2

            print(f'レベルアップに必要な経験値: {next_levelup_xp}\n現在の経験値{reformat_xp}')
            level_up = float(reformat_xp / next_levelup_xp * 100)
            level_up = str(level_up)
            level_up = level_up[:level_up.find('.')]
            embed = discord.Embed(
                title=f"{emoji}{get_blog_user_name}のブログステータス", color=0x8bc34a)
            embed.set_thumbnail(url=f"{get_user_avatar_url}")
            embed.add_field(
                name="投稿数", value=f"{reformat_number_of_posts}", inline=True)
            embed.add_field(name="blog称号", value=f"若葉", inline=False)
            embed.add_field(name="blog経験値", value=f"{reformat_xp}xp", inline=True)
            embed.add_field(name="blogレベル", value=f"{reformat_get_level}lv", inline=True)
            embed.add_field(name="blogのレベルアップまで", value=f"{level_up}/100%", inline=True)
            await ctx.channel.send(embed=embed)
        else:
            await embed_send(ctx, self.bot, 1, 'エラー', '登録されていないチャンネルです')

    @commands.group()
    async def bloguser(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドには引数が必要です')

    @bloguser.command(name='add')
    async def _add(self, ctx, arg):
        try:
            user = await self.bot.fetch_user(arg)
            await embed_send(ctx, self.bot, 0, '成功', 'エラー出てないです')
        except NotFound:
            await embed_send(ctx, self.bot, 1, 'エラー', '存在しないユーザーです')
        except HTTPException:
            await embed_send(ctx, self.bot, 1, 'エラー', 'ユーザーの取得に失敗しました')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        if ctx.content != f'{bot_prefix}blog status':
            myresult = await db_search('channel_id', 'discord_blog_sub_info', f'channel_id = {ctx.channel.id}')
            if len(myresult) >= 1:
                # 投稿数をデータベースから取得
                db_get_number_of_posts = await db_search('number_of_posts', 'discord_blog_sub_info',
                                                         f'channel_id = {ctx.channel.id} AND number_of_posts >= 0')
                reformat_number_of_posts = await db_reformat(db_get_number_of_posts, 1)

                # 経験値をデータベースから取得
                db_get_exp = await db_search('xp', 'discord_blog_xp', f'channel_id = {ctx.channel.id} AND xp >= 0')
                reformat_xp = await db_reformat(db_get_exp, 1)
                # レベルをデータベースから取得
                db_get_level = await db_search('level', 'discord_blog_xp',
                                               f'channel_id = {ctx.channel.id} AND level >= 0')
                reformat_level = await db_reformat(db_get_level, 2)

                default_levelup_xp = 5  # 基本レベルを設定

                if reformat_level == 1:
                    next_levelup_xp = float(default_levelup_xp * 1.1) + int(reformat_level * 2) / 2
                else:
                    db_get_saved_levelup_xp = await db_search('saved_levelup_xp', 'discord_blog_xp',
                                                              f'channel_id = {ctx.channel.id} AND saved_levelup_xp IS NOT NULL')
                    reformat_saved_levelup_xp = await db_reformat(db_get_saved_levelup_xp, 3)
                    print(reformat_saved_levelup_xp)
                    reformat_saved_levelup_xp = float(reformat_saved_levelup_xp)
                    next_levelup_xp = float(reformat_saved_levelup_xp * 1.1) + int(reformat_level * 2) / 2
                rereformat_xp = int(reformat_xp) / 100
                rereformat_xp = str(rereformat_xp)
                rereformat_xp = rereformat_xp[:rereformat_xp.find('.')]

                next_levelup_xp = str(next_levelup_xp)
                next_levelup_xp = next_levelup_xp[:next_levelup_xp.find('.')]
                print(f'レベルアップに必要な経験値: {next_levelup_xp}\n現在の経験値{rereformat_xp}')
                if int(rereformat_xp) >= int(next_levelup_xp):
                    val = (f"{next_levelup_xp}", f"{ctx.channel.id}")
                    await db_update('discord_blog_xp', 'saved_levelup_xp = %s WHERE channel_id = %s', val)

                    reformat_level = int(reformat_level) + 1
                    embed = discord.Embed(
                        title=f"レベルアップ!", color=0x8bc34a)
                    embed.add_field(name=f"blogのレベルが{reformat_level}に上がりました!", value=f"今後もblogでのご活躍をご期待しています!",
                                    inline=True)
                    await ctx.channel.send(embed=embed)
                    next_xp = '0'
                else:
                    next_xp = int(reformat_xp) + + int(2) * 10
                    print(f'今回の発言後のxp(小数) {next_xp / 100}\n今回の発言後のxp(整数) {next_xp}')
                next_number_of_posts = int(reformat_number_of_posts) + 1

                val = (f"{int(next_xp)}", f"{reformat_level}", f"{ctx.channel.id}")
                await db_update('discord_blog_xp', 'xp = %s, level = %s WHERE channel_id = %s', val)

                val = (f"{next_number_of_posts}", f"{ctx.channel.id}")
                await db_update('discord_blog_sub_info', 'number_of_posts = %s WHERE channel_id = %s', val)


def setup(bot):
    bot.add_cog(BlogCog(bot))
