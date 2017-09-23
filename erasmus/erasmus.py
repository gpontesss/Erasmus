from discord.ext import commands
from discord.message import Message
from discord.game import Game
import re

from .data import VerseRange, Passage
from .bible_manager import BibleManager
from .exceptions import DoNotUnderstandError, BibleNotSupportedError, ServiceNotSupportedError, BookNotUnderstoodError
from .json import JSONObject, load

number_re = re.compile(r'^\d+$')


class Context(commands.Context):
    async def send_passage(self, passage: Passage) -> Message:
        extra_len = len(self.author.mention) + 7
        text = str(passage)

        if len(text) + extra_len > 2000:
            text = passage.get_truncated(2000 - extra_len)

        return await self.send_to_author(text)

    async def send_to_author(self, text: str) -> Message:
        return await self.send(f'{self.author.mention}\n```{text}```')


class Erasmus(commands.Bot):
    bible_manager: BibleManager
    config: JSONObject

    def __init__(self, config_path, *args, **kwargs) -> None:
        with open(config_path, 'r') as f:
            self.config = load(f)

        kwargs['command_prefix'] = self.config.command_prefix

        super().__init__(*args, **kwargs)

        self.bible_manager = BibleManager(self.config)

        for name, description in self.bible_manager.get_versions():
            lookup_command = commands.Command(
                name=name,
                description=f'Look up a verse in {description}',
                hidden=True,
                pass_context=True,
                callback=self._version_lookup)
            search_command = commands.Command(
                name=f's{name}',
                description=f'Search in {description}',
                hidden=True,
                pass_context=True,
                callback=self._version_search)
            self.add_command(lookup_command)
            self.add_command(search_command)

        self.add_command(self.versions)

    def run(self, *args, **kwargs) -> None:
        super().run(self.config.api_key)

    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        await self.process_commands(message)

    async def process_commands(self, message: Message) -> None:
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is None:
            return

        await self.invoke(ctx)

    async def on_ready(self) -> None:
        print('-----')
        print(f'logged in as {self.user.name} {self.user.id}')

        if not self.config.get('dev', False):
            await self.change_presence(game=Game(name=f'| {self.command_prefix}versions'))

    @commands.command()
    async def versions(self, ctx: Context) -> None:
        lines = ['I support the following Bible versions:', '']
        for version, description in self.bible_manager.get_versions():
            version = f'{version}:'.ljust(6)
            lines.append(f'  {self.command_prefix}{version} {description}')

        lines.append("\nYou can search any version by prefixing the version command with 's' "
                     f"(ex. {self.command_prefix}sesv terms...)")

        output = '\n'.join(lines)
        await ctx.send_to_author(f'\n{output}\n')

    async def _version_lookup(self, ctx: Context, *, reference: str) -> None:
        version = ctx.command.name

        try:
            verses = VerseRange.from_string(reference)
        except BookNotUnderstoodError as err:
            await ctx.send_to_author(f'I do not understand the book "{err.book}"')
        else:
            if verses is not None:
                async with ctx.typing():
                    try:
                        passage = await self.bible_manager.get_passage(version, verses)
                    except DoNotUnderstandError:
                        await ctx.send_to_author('I do not understand that request')
                    except BibleNotSupportedError as err:
                        await ctx.send_to_author(f'~{err.version} is not supported')
                    except ServiceNotSupportedError:
                        await ctx.send_to_author(f'The service configured for ~{version} is not supported')
                    else:
                        await ctx.send_passage(passage)
            else:
                await ctx.send_to_author('I do not understand that request')

    async def _version_search(self, ctx: Context, *terms) -> None:
        version = ctx.command.name[1:]

        async with ctx.typing():
            try:
                results = await self.bible_manager.search(version, list(terms))
            except BibleNotSupportedError:
                await ctx.send_to_author(f'~{ctx.command.name} is not supported')
            else:
                verses = ', '.join([str(verse) for verse in results.verses])
                matches = 'match'

                if results.total == 0 or results.total > 1:
                    matches = 'matches'

                if results.total <= 20:
                    await ctx.send_to_author(f'I have found {results.total} {matches} to your search:\n{verses}')
                else:
                    await ctx.send_to_author(f'I have found {results.total} {matches} to your search. '
                                             f'Here are the first 20 {matches}:\n{verses}')


__all__ = ['Erasmus']
