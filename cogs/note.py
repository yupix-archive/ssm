import asyncio
import itertools
import re

import discord
import typing

import mysql
from discord.ext import commands
from sqlalchemy import text, and_
from sqlalchemy.exc import IntegrityError

from main import Output_wav_name, check_variable, db_insert, db_reformat, db_search, embed_send, db_delete, check_args, logger, db_commit

import logging
from logging import getLogger, StreamHandler, Formatter

from settings import session
from sql.models.note import NotesUser, NotesCategory, NotesDetail


class NoteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def note(self, ctx):
        if ctx.invoked_subcommand is None:
            logger.debug('test')
            await ctx.send('このコマンドには引数が必要です')

    @note.command(name='add')
    async def _add(self, ctx, note, use_category=None, category_name=None):
        if re.findall('<@(.*?)>', f'{note}') or re.findall('<@(.*?)>', f'{category_name}'):
            await ctx.send('メンションは使用することができません')
            return
        logger.debug(note)
        variable = await check_variable(note, 'addを使用するにはnoteをつける必要性があります', ctx)
        if variable == 0:
            note_user_sql = text(f'insert into notes_user (user_id) values ({ctx.author.id}) ON CONFLICT DO NOTHING')
            note_user_res = session.execute(note_user_sql)
            print(note_user_res)

            if use_category is not None and use_category == '-c':
                logger.debug(f'オプションが付与されています: {category_name}')
            else:
                category_name = 'デフォルト'
            search_category_name = session.query(NotesCategory).filter(NotesCategory.category_name == f'{category_name}').all()
            if len(search_category_name) == 0:
                logger.debug(f'カテゴリ「{category_name}」が存在しないため作成します')
                await db_commit(NotesCategory(category_name=f'{category_name}'))
            add_note_result = await db_commit(NotesDetail(user_id=f'{ctx.author.id}', content=f'{note}', category_name=f'{category_name}'))
            if add_note_result != 'IntegrityError':
                search_notes_id = session.query(NotesDetail).filter(and_(NotesDetail.category_name == f'{category_name}', NotesDetail.content == f'{note}', NotesDetail.user_id == f'{ctx.author.id}')).all()
                for test in search_notes_id:
                    logger.debug(vars(test))
                embed = discord.Embed(title="ノートの登録に成功しました", description="このメッセージは10秒後に自動で削除されます", color=0xff7e70)
                embed.add_field(name="id", value=f"{search_notes_id}", inline=True)
                embed.add_field(name="ノート内容", value=f"{note}", inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send('重複した内容のnoteは追加できません')

    @note.command(name='remove')
    async def _remove(self, ctx, note_id: typing.Optional[int] = None):
        search_note_user_id = await db_search('user_id', 'notes_detail',
                                              f'id = {note_id}')
        if len(search_note_user_id) == 0:
            await ctx.send('存在しないidです')
            return
        if await db_reformat(search_note_user_id, 2) == ctx.author.id:
            print('ある')
            await db_delete('notes_detail', 'id = %s', f'{note_id}')

    @note.command(name='list')
    async def _list(self, ctx, note_author: typing.Optional[discord.User] = 'me', *, args: check_args = None):

        if note_author == 'me':
            note_author = ctx.author  # ユーザー指定
        if args is not None:
            if type(args) is not dict:
                await ctx.send(f'{args[1]}')
                return
            else:
                if '-c' in args and args.get('-c') is not None:
                    category_name = args.get('-c')
                    search_reaction_id = await db_search('content', 'notes_detail',
                                                         f'user_id = {note_author.id} AND content IS NOT NULL AND category_name = \'{category_name}\'')
                if '--type' in args and 'category' == args.get('--type'):
                    search_reaction_id = await db_search('category_name', 'notes_detail',
                                                         f'user_id = {note_author.id} AND content IS NOT NULL AND category_name IS NOT NULL')
        else:
            category_name = 'デフォルト'
            search_reaction_id = await db_search('content', 'notes_detail',
                                                 f'user_id = {note_author.id} AND content IS NOT NULL AND category_name = \'{category_name}\'')

        note_list = ''
        embed = discord.Embed(color=0x859fff)
        for i in search_reaction_id:
            custom_message = ''
            for emoji in re.finditer('e!(.*?)!e', f'{search_reaction_id}'):
                base_message = re.sub("\(|\)|\'", "", f'{i}').replace(',', '\n')
                for n in emoji.groups():  # emoji
                    check_emoji_type = re.sub("\\D", "", n)
                    if len(str(check_emoji_type)) == 18:
                        get_emoji = self.bot.get_emoji(int(check_emoji_type))
                        print(get_emoji)
                    else:
                        get_emoji = discord.utils.get(ctx.guild.emojis, name=f'{n}'.replace(':', ''))
                    if len(custom_message) == 0:
                        custom_message = base_message.replace(',', '\n').replace(f'e!{n}!e', f'{get_emoji}')
                    else:
                        custom_message = custom_message.replace(',', '\n').replace(f'e!{n}!e', f'{get_emoji}')
            if 'emoji' not in locals():
                custom_message = await db_reformat(i, 1) + '\n'
            print(custom_message)
            r_custom_message = await db_reformat(i, 1)
            if args is not None and '--type' in args and 'category' == args.get('--type'):
                search_notes_id = await db_reformat(await db_search('id', 'notes_category', f'category_name = \'{r_custom_message}\''), 2)
            search_notes_id = await db_reformat(await db_search('id', 'notes_detail', f'user_id = {note_author.id} '
                                                                                      f'AND content = \'{r_custom_message}\''), 2)
            embed.add_field(name=f"ID: {search_notes_id}", value=f"{custom_message}", inline=True)
        # note_list += custom_message
        if not embed:
            await embed_send(ctx, self.bot, 0, 'INFO', 'ノートは空のようです', 0x859fff)
            return

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(NoteCog(bot))
